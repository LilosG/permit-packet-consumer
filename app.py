"""Public permit packet generator: address to property, job to watermarked preview, payment to clean packet."""
from __future__ import annotations

import base64
import hashlib
import io
import json
import logging
import os
import re
import secrets
import threading
import time
import zipfile
from collections import deque
from contextlib import asynccontextmanager
from functools import lru_cache
from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import quote

import httpx
from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse, PlainTextResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.exception_handlers import http_exception_handler as default_http_exception_handler
from starlette.exceptions import HTTPException as StarletteHTTPException
from pydantic import ValidationError

from permit_packets import emails, orders, pages, payments, pricing, seo, sitedata
from permit_packets.core import capacity_summary
from permit_packets.core.pdf_base import COMPANY_NAME, CONTRACTOR_LOGO, DEMO_MARKS
from permit_packets.core.preview import packet_documents_zip, packet_page_images, packet_subset_pdf
from permit_packets.core.property_lookup import (
    AddressNotFound,
    AerialUnavailable,
    FoundProperty,
    fetch_aerial,
    find_property,
    property_at,
    suggest_addresses,
)
from permit_packets.core.property_plan import PlanView, zoomed_scale
from permit_packets.core.schemas import AerialRequest, LookupRequest, PropertyViewRequest, SuggestRequest
from permit_packets.job_types import REGISTRY, JobType, PacketResult, get_job_type
from permit_packets.jurisdictions import KNOWN, jurisdiction_by_key, jurisdiction_json

log = logging.getLogger("permit_packets")

STATIC = Path(__file__).parent / "permit_packets" / "static"
ASSETS = STATIC / "assets"
EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
# Order and admin pages hold one customer's job: keep them out of search results and caches.
PRIVATE_PAGE = {"Cache-Control": "no-store", "X-Robots-Tag": "noindex, nofollow, noarchive"}
PRIVATE_DATA = {"Cache-Control": "private, no-store"}


@asynccontextmanager
async def lifespan(_: FastAPI):
    try:
        orders.init_db()
    except Exception:  # the free preview keeps working while the database is down
        log.exception("Could not prepare the orders table")
    yield


app = FastAPI(title="Permit Packets", docs_url=None, redoc_url=None, openapi_url=None, lifespan=lifespan)


def _asset_version() -> str:
    """A short hash of the asset files, so a changed file gets a new URL."""
    digest = hashlib.sha256()
    for path in sorted(ASSETS.rglob("*")):
        if path.is_file():
            digest.update(path.relative_to(ASSETS).as_posix().encode())
            digest.update(path.read_bytes())
    return digest.hexdigest()[:10]


ASSET_VERSION = _asset_version()
ICONS = STATIC / "icons"
public_base_url = seo.public_base_url  # the site's public address, for canonical, social and sitemap URLs
pages.set_asset_version(ASSET_VERSION)


def _fill(html: str, *, redact_path: str | None = None) -> str:
    """Fill the placeholders in the static pages (order, admin, 404): footer, analytics, asset version, base URL."""
    if "{{FOOTER}}" in html:
        html = html.replace("{{FOOTER}}", pages.footer_html())
    return (
        html.replace("{{GA}}", str(seo.ga_snippet(redact_path=redact_path)))
        .replace("{{ASSET_VERSION}}", ASSET_VERSION)
        .replace("{{PP_PRICES}}", pages.prices_script())
        .replace("{{BASE_URL}}", public_base_url())
    )


# Only the assets folder is served as files. The other pages are routes below.
app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")


def _page(name: str) -> HTMLResponse:
    return HTMLResponse(_fill((STATIC / name).read_text(encoding="utf-8"), redact_path="/order/[redacted]" if name == "order.html" else None), headers=PRIVATE_PAGE)


def _not_found_page() -> HTMLResponse:
    return HTMLResponse(_fill((STATIC / "404.html").read_text(encoding="utf-8")), status_code=404, headers=PRIVATE_PAGE)


@app.exception_handler(StarletteHTTPException)
async def http_error(request: Request, error: StarletteHTTPException) -> Response:
    """A missing page gets the branded HTML 404. API routes keep their JSON errors."""
    if error.status_code == 404 and not request.url.path.startswith("/api/"):
        return _not_found_page()
    return await default_http_exception_handler(request, error)


ICON_FILES = {
    "/favicon.ico": ("favicon.ico", "image/x-icon"),
    "/favicon.svg": ("favicon.svg", "image/svg+xml"),
    "/apple-touch-icon.png": ("apple-touch-icon.png", "image/png"),
}


def _icon(name: str, media_type: str) -> FileResponse:
    return FileResponse(ICONS / name, media_type=media_type, headers={"Cache-Control": "public, max-age=86400"})


for _path, (_name, _type) in ICON_FILES.items():
    app.add_api_route(_path, lambda _n=_name, _t=_type: _icon(_n, _t), methods=["GET", "HEAD"], include_in_schema=False)


# The site pages (home, wizard, placeholders, legal, sitemaps, robots, llms.txt) live in permit_packets/pages.py.
app.include_router(pages.router)
app.middleware("http")(pages.trailing_slash)


# ---- Abuse protection: a small per-IP limit in memory ----
# Each server instance counts for itself, which is enough to stop one visitor hammering the lookups and the
# packet builds. Limits per IP per hour can be changed with RATE_LIMIT_<BUCKET> (suggest, property, preview).
RATE_WINDOW_SECONDS = 3600
RATE_LIMITS = {"suggest": 150, "property": 30, "preview": 12}  # suggest fires while typing, so it gets its own room
RATE_MESSAGES = {
    "suggest": "You've searched a lot of addresses this hour. Please wait a bit, or type the full address.",
    "property": "You've looked up a lot of properties this hour. Please try again in a little while.",
    "preview": "You've built a lot of previews this hour. Please try again in a little while, or finish an order you have open.",
}
_hits: dict[tuple[str, str], deque[float]] = {}
_hits_lock = threading.Lock()


def client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-real-ip") or request.headers.get("x-forwarded-for", "").split(",")[0].strip()
    return forwarded or (request.client.host if request.client else "unknown")


def _limit_for(bucket: str) -> int:
    try:
        return int(os.environ.get(f"RATE_LIMIT_{bucket.upper()}", RATE_LIMITS[bucket]))
    except ValueError:
        return RATE_LIMITS[bucket]


def rate_limit(bucket: str):
    """A dependency that answers 429 once an IP has used up its hourly allowance for the bucket."""
    def check(request: Request) -> None:
        limit = _limit_for(bucket)
        if limit <= 0:  # 0 switches the limit off
            return
        now = time.monotonic()
        key = (bucket, client_ip(request))
        with _hits_lock:
            hits = _hits.setdefault(key, deque())
            while hits and now - hits[0] > RATE_WINDOW_SECONDS:
                hits.popleft()
            if len(hits) >= limit:
                retry = max(1, int(RATE_WINDOW_SECONDS - (now - hits[0])))
                raise HTTPException(
                    status.HTTP_429_TOO_MANY_REQUESTS, RATE_MESSAGES[bucket], headers={"Retry-After": str(retry)})
            hits.append(now)
            if len(_hits) > 5000:  # forget visitors whose hour has passed
                for stale in [k for k, v in _hits.items() if not v or now - v[-1] > RATE_WINDOW_SECONDS]:
                    del _hits[stale]
    return check


# ---- Public property lookup ----

@app.post("/api/property/suggest", dependencies=[Depends(rate_limit("suggest"))])
def address_suggestions(payload: SuggestRequest) -> dict:
    return {"suggestions": suggest_addresses(payload.text)}


def _known_job_type(key: str) -> str:
    if key not in REGISTRY:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Unknown job type")
    return key


def _property_json(found: FoundProperty, job_type: str) -> dict:
    return {
        "address": found.address,
        "city": found.city,
        "state": found.state,
        "county_fips": found.county_fips,
        "house_number": found.house_number,
        "located_by": found.located_by,
        "address_confirmed": found.address_confirmed,
        "parcel_house_number": found.parcel_house_number,
        "anchor": {"latitude": found.anchor[0], "longitude": found.anchor[1]},
        "jurisdiction": jurisdiction_json(found.jurisdiction, job_type),
        "view": {
            "latitude": found.view.latitude,
            "longitude": found.view.longitude,
            "scale_ft_per_in": found.view.scale_ft_per_in,
            "feet_per_unit": found.view.feet_per_unit,
        },
        "buildings": found.buildings,
        "primary_building": found.primary_building,
        "lot": found.lot,
        "parcel_number": found.parcel_number,
        "credits": found.credits,
    }


# "Try with a sample address" answers from lookup results saved in the repo (permit_packets/data), so the sample never
# depends on, or calls, the live lookup services. tools/make_sample.py's address is the sample.
DATA = Path(__file__).parent / "permit_packets" / "data"
SAMPLE_ADDRESS = "453 Brockton St, El Cajon, CA 92020"
SAMPLE_JURISDICTION = "el-cajon-ca"


def _is_sample_address(address: str) -> bool:
    return " ".join(address.lower().split()) == SAMPLE_ADDRESS.lower()


@lru_cache(maxsize=1)
def _sample_data() -> dict[str, Any]:
    return {
        "property": json.loads((DATA / "sample_property.json").read_text(encoding="utf-8")),
        "aerial": base64.b64encode((DATA / "sample_aerial.jpg").read_bytes()).decode(),
        "credit": (DATA / "sample_aerial_credit.txt").read_text(encoding="utf-8").strip(),
    }


def _sample_property(job_type: str) -> dict:
    return {**_sample_data()["property"], "jurisdiction": jurisdiction_json(jurisdiction_by_key(SAMPLE_JURISDICTION), job_type)}


def _is_sample_view(view: PlanView) -> bool:
    saved = _sample_data()["property"]["view"]
    return (abs(view.latitude - saved["latitude"]) < 1e-6 and abs(view.longitude - saved["longitude"]) < 1e-6
            and abs(view.scale_ft_per_in - saved["scale_ft_per_in"]) < 1e-6)


@app.post("/api/property", dependencies=[Depends(rate_limit("property"))])
def look_up_property(payload: LookupRequest) -> dict:
    job_type = _known_job_type(payload.job_type)
    if _is_sample_address(payload.address):
        return _sample_property(job_type)
    try:
        found = find_property(payload.address)
    except AddressNotFound as error:
        raise HTTPException(status.HTTP_404_NOT_FOUND, str(error)) from error
    return _property_json(found, job_type)


@app.post("/api/property/view", dependencies=[Depends(rate_limit("property"))])
def change_property_view(payload: PropertyViewRequest) -> dict:
    fields = dict(
        address=payload.address, city=payload.city, state=payload.state,
        county_fips=payload.county_fips, house_number=payload.house_number,
    )
    job_type = _known_job_type(payload.job_type)
    if _is_sample_address(payload.address):  # the sample keeps its saved view; no live lookup
        return _sample_property(job_type)
    view = PlanView(payload.latitude, payload.longitude, payload.scale_ft_per_in)
    if payload.tap:
        found = property_at(**fields, point=view.to_latlon(*payload.tap), located_by="tap")
    else:
        scale = zoomed_scale(payload.scale_ft_per_in, payload.zoom or 0)
        found = property_at(
            **fields, point=(payload.anchor_latitude, payload.anchor_longitude), located_by=payload.located_by,
            scale=scale, center=(payload.latitude, payload.longitude),
        )
    return _property_json(found, job_type)


@app.post("/api/property/aerial", dependencies=[Depends(rate_limit("property"))])
def property_aerial(payload: AerialRequest) -> dict:
    view = PlanView(payload.latitude, payload.longitude, payload.scale_ft_per_in)
    if _is_sample_view(view):
        return {"image": _sample_data()["aerial"], "credit": _sample_data()["credit"]}
    try:
        image, credit = fetch_aerial(view)
    except AerialUnavailable as error:
        raise HTTPException(status.HTTP_502_BAD_GATEWAY, str(error)) from error
    return {"image": base64.b64encode(image).decode(), "credit": credit}


def _job_type_json(job_type: JobType) -> dict:
    return {
        "key": job_type.key,
        "slug": job_type.slug,
        "label": job_type.label,
        "short_label": job_type.short_label,
        "blurb": job_type.blurb,
        "icon": job_type.icon,
        "markers": [asdict(marker) for marker in job_type.markers],
        "route_between": list(job_type.route_between) if job_type.route_between else None,
        "uses_home_loads": job_type.uses_home_loads,
        "documents": [asdict(document) for document in job_type.documents],
        "feature_page": job_type.feature_page,
    }


@app.get("/api/job-types")
def job_types() -> dict:
    return {"job_types": [_job_type_json(job_type) for job_type in REGISTRY.values()]}


# ---- Building a packet ----

MAX_LOGO_BASE64 = 700_000


def _contractor_logo(payload: dict[str, Any]) -> bytes | None:
    """The optional contractor logo: a PNG or JPEG, base64, shown on the cover and page headers."""
    encoded = payload.pop("contractor_logo_base64", None)
    if not encoded:
        return None
    if not isinstance(encoded, str) or len(encoded) > MAX_LOGO_BASE64:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The logo must be a PNG or JPEG under 500 KB")
    try:
        logo = base64.b64decode(encoded, validate=True)
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The logo is not valid base64") from error
    if not (logo.startswith(b"\x89PNG") or logo.startswith(b"\xff\xd8")):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "The logo must be a PNG or JPEG")
    return logo


def _job_type(slug: str) -> JobType:
    job_type = get_job_type(slug)
    if job_type is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "That job type isn't available")
    return job_type


def _validated(job_type: JobType, payload: dict[str, Any]):
    try:
        return job_type.request_model.model_validate(payload)
    except ValidationError as error:
        raise RequestValidationError(error.errors(include_url=False)) from error


def _build(slug: str, payload: dict[str, Any], *, preview: bool) -> tuple[JobType, PacketResult]:
    """Build the packet. A preview carries the PREVIEW marks; a paid packet carries none."""
    job_type = _job_type(slug)
    payload = dict(payload)  # the logo is popped below, and an order's saved payload must stay whole
    payload.pop("tier", None)  # the wizard tells the preview which package is chosen; the packet itself does not care
    logo = _contractor_logo(payload)
    request = _validated(job_type, payload)
    tokens = (
        (CONTRACTOR_LOGO, CONTRACTOR_LOGO.set(logo)),
        (DEMO_MARKS, DEMO_MARKS.set(preview)),
        (COMPANY_NAME, COMPANY_NAME.set("")),
    )
    try:
        return job_type, job_type.build_response(request)
    finally:
        for var, token in tokens:
            var.reset(token)


def _summary_pdf(payload: dict[str, Any], result: PacketResult, *, preview: bool) -> bytes:
    """Page one of a Panel Capacity Report, built from what the packet computed."""
    token = DEMO_MARKS.set(preview)
    try:
        return capacity_summary.summary_pdf({k: v for k, v in payload.items() if k != "tier"}, result.body)
    finally:
        DEMO_MARKS.reset(token)


def _with_summary(payload: dict[str, Any], result: PacketResult, pdf: bytes, *, preview: bool) -> bytes:
    return capacity_summary.prepend_summary(_summary_pdf(payload, result, preview=preview), pdf)


def _single_pdf_only(payload: dict[str, Any]) -> bool:
    city = jurisdiction_by_key(payload.get("jurisdiction_key"), payload.get("city"), payload.get("state"))
    return city.single_pdf_only


def _page_images(result: PacketResult) -> list[str]:
    return [base64.b64encode(page).decode() for page in packet_page_images(result.pdf)]


def _documents_response(job_type: JobType, result: PacketResult, zip_name: str) -> Response:
    stems = tuple(document.file_stem for document in job_type.documents)
    return Response(
        content=packet_documents_zip(result.pdf, stems),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{zip_name}"', **PRIVATE_DATA},
    )


# What payment unlocks: the filled-in portal fields and the ready-to-send submission email.
PAID_ONLY = ("fields", "submission_email")


@app.post("/api/public/preview/{slug}", dependencies=[Depends(rate_limit("preview"))])
def public_preview(slug: str, payload: dict[str, Any] = Body(...)) -> dict:
    """The free, watermarked look at a packet: the engineering check summary and its pages as JPEGs."""
    _, result = _build(slug, payload, preview=True)
    body = {key: value for key, value in result.body.items() if key not in PAID_ONLY}
    if payload.get("tier") == "load_calc":  # the Panel Capacity Report opens with its summary page
        pages_pdf = _with_summary(payload, result, result.pdf, preview=True)
        return {**body, "packet_page_images": [base64.b64encode(p).decode() for p in packet_page_images(pages_pdf)]}
    return {**body, "packet_page_images": _page_images(result)}


# The original review-screen routes stay for the page's own script. They are public and always watermarked:
# a clean packet only ever comes from a paid order.
@app.post("/api/jobs/{slug}/packet", dependencies=[Depends(rate_limit("preview"))])
def build_packet(slug: str, payload: dict[str, Any] = Body(...)) -> dict:
    _, result = _build(slug, payload, preview=True)
    return {**result.body, "pages": _page_images(result)}


@app.post("/api/jobs/{slug}/pdf", dependencies=[Depends(rate_limit("preview"))])
def packet_pdf(slug: str, payload: dict[str, Any] = Body(...)) -> Response:
    """The watermarked packet as one PDF file."""
    _, result = _build(slug, payload, preview=True)
    return Response(content=result.pdf, media_type="application/pdf", headers={"Content-Disposition": "inline", **PRIVATE_DATA})


@app.post("/api/jobs/{slug}/documents", dependencies=[Depends(rate_limit("preview"))])
def packet_documents(slug: str, payload: dict[str, Any] = Body(...)) -> Response:
    if _single_pdf_only(payload):
        raise HTTPException(status.HTTP_409_CONFLICT, "This city takes one combined PDF, not separate plan sheets")
    job_type, result = _build(slug, payload, preview=True)
    return _documents_response(job_type, result, job_type.zip_name)


# ---- Orders ----

def _base_url(request: Request) -> str:
    configured = os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")
    if configured:
        return configured
    proto = request.headers.get("x-forwarded-proto", request.url.scheme).split(",")[0].strip()
    host = request.headers.get("x-forwarded-host", request.headers.get("host", request.url.netloc)).split(",")[0].strip()
    return f"{proto}://{host}"


CREDIT_TIERS = ("instant_packet", "city_checked_24h")  # a paid Panel Capacity Report counts toward these


def _credit_quote(email: str, tier: str) -> tuple[dict[str, Any] | None, int]:
    """The paid load_calc order whose credit this checkout would use, and its value in cents (capped so $1 is still charged)."""
    if tier not in CREDIT_TIERS:
        return None, 0
    source = orders.find_load_calc_credit(email)
    if source is None:
        return None, 0
    return source, max(0, min(source["amount_cents"], pricing.price(tier) * 100 - 100))


def _fix_amount(order: dict[str, Any]) -> dict[str, Any]:
    """Settle what this order costs, once, when its first checkout is created: today's price less any Panel Capacity Report credit."""
    if order["amount_cents"] is not None:
        return order
    # The discount is only recorded here; the load_calc credit is claimed when the order is paid (_mark_paid).
    source, value = _credit_quote(order["customer_email"], order["tier"])
    credit_cents = value if source is not None else 0
    orders.set_amount(order["id"], pricing.price(order["tier"]) * 100 - credit_cents, credit_cents,
                      source["id"] if credit_cents else None)
    return orders.get_by_id(order["id"]) or order


def _checkout_url(order: dict[str, Any], request: Request) -> str:
    """A fresh Square checkout for this order at its fixed amount, or "" when Square isn't set up or fails."""
    if order["source"] == "credit":
        return ""
    order = _fix_amount(order)
    try:
        url, provider_order_id = payments.create_checkout(
            "order", order, order["amount_cents"], order["customer_email"],
            f"{_base_url(request)}/order/{order['access_token']}", pricing.TIER_NAMES[order["tier"]])
    except payments.PaymentError as error:
        log.error("%s", error)
        return ""
    orders.add_checkout_link(provider_order_id, "order", order["id"], order["amount_cents"])
    orders.set_provider_order_id(order["id"], provider_order_id)  # for display; payments are matched through checkout_links
    return url


@app.post("/api/public/preview/{slug}/email", dependencies=[Depends(rate_limit("preview"))])
def email_preview(request: Request, slug: str, body: dict[str, Any] = Body(...)) -> dict:
    email = str(body.get("customer_email") or "").strip()
    payload = body.get("payload")
    if not EMAIL.match(email) or len(email) > 200: raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid email address")
    if not isinstance(payload, dict): raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "payload must be the job's inputs")
    job_type = _job_type(slug)
    if body.get("role") in sitedata.ROLES: payload = {**payload, "role": body["role"]}
    working = dict(payload); _contractor_logo(working)
    job = _validated(job_type, working)
    city = jurisdiction_by_key(payload.get("jurisdiction_key"), payload.get("city"), payload.get("state"))
    tier = body.get("tier") if body.get("tier") in orders.TIERS else "instant_packet"
    _, result = _build(job_type.slug, payload, preview=True)
    order = orders.create_order(customer_email=email, tier=tier, job_slug=job_type.slug, address=job.address, jurisdiction_key=city.key, payload=payload, source="preview_saved")
    status_line = "NEC 220 & engineering check: Ready for submission." if result.body.get("ready") else "NEC 220 & engineering check: Some items need attention."
    _notify(emails.draft_saved, email, _order_link(request, order), order["address"], job_type.label, result.pdf, f"{order['order_code']}-preview.pdf", status_line)
    return {"order_code": order["order_code"], "order_url": f"/order/{order['access_token']}"}

@app.post("/api/public/orders")
def create_order(request: Request, body: dict[str, Any] = Body(...)) -> dict:
    """Save a pending_payment order for a job. Body: {job_slug, customer_email, tier, payload}."""
    email = str(body.get("customer_email") or "").strip()
    tier = body.get("tier")
    payload = body.get("payload")
    if not EMAIL.match(email) or len(email) > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid email address")
    if tier not in orders.TIERS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"tier must be one of {', '.join(orders.TIERS)}")
    if not isinstance(payload, dict):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "payload must be the job's inputs")
    job_type = _job_type(str(body.get("job_slug") or ""))
    role = body.get("role")
    if role in sitedata.ROLES:  # who the packet is for, kept with the order's inputs
        payload = {**payload, "role": role}
    working = dict(payload)
    _contractor_logo(working)  # refuse a bad logo now, not after the customer has paid
    job = _validated(job_type, working)
    city = jurisdiction_by_key(payload.get("jurisdiction_key"), payload.get("city"), payload.get("state"))
    order = orders.create_order(
        customer_email=email, tier=tier, job_slug=job_type.slug, address=job.address,
        jurisdiction_key=city.key, payload=payload, source="checkout",
    )
    if os.environ.get("DEV_AUTO_APPROVE", "").strip().lower() == "true":
        order = _mark_paid(_fix_amount(order), request)
        checkout_url = ""
    else:
        checkout_url = _checkout_url(order, request)
        _notify(emails.order_created, orders.get_by_id(order["id"]) or order, _order_link(request, order))
    return {
        "order_code": order["order_code"],
        "access_token": order["access_token"],
        "order_url": f"/order/{order['access_token']}",
        "checkout_url": checkout_url,
    }


# The Panel Capacity Report (load_calc) is only the NEC 220 load calculation and the panel schedule / capacity audit sheets.
LOAD_CALC_SHEETS = ("load-calculation", "panel-schedule")
REVIEW_HOURS = 24


def _order_link(request: Request, order: dict[str, Any]) -> str:
    return f"{_base_url(request)}/order/{order['access_token']}"


def _notify(send, *args) -> None:
    """Run an email send. Whatever goes wrong, the order flow carries on."""
    try:
        send(*args)
    except Exception:
        log.exception("Order email failed")


def _city_name(order: dict[str, Any]) -> str:
    payload = order["payload"] if isinstance(order.get("payload"), dict) else {}
    city = jurisdiction_by_key(order["jurisdiction_key"], payload.get("city"), payload.get("state"))
    return city.name if city.known and city.name else (payload.get("city") or "your city")


def _mark_paid(order: dict[str, Any], request: Request) -> dict[str, Any]:
    """Record a payment. A city_checked_24h order goes into the review hold and does not unlock; the others unlock now."""
    link = _order_link(request, order)
    if order.get("credit_applied_cents") and order.get("credit_source_order_id"):
        if not orders.claim_load_calc_credit(order["credit_source_order_id"]):  # another paid order got there first: the buyer still paid the discounted amount
            log.warning("Order %s paid with a Panel Capacity Report credit that was already used (source order %s)",
                        order["order_code"], order["credit_source_order_id"])
    if order["tier"] == "city_checked_24h":
        order = orders.set_status(order["id"], "in_review") or order
        _notify(emails.in_review, order, link, _city_name(order))
        _notify(emails.review_alert, order, link, f"{_base_url(request)}/admin")
    else:
        order = orders.set_status(order["id"], "paid") or order
        _notify(emails.paid_ready, order, link)
    return order


def _allowed_sheets(order: dict[str, Any], job_type: JobType) -> frozenset[str] | None:
    """The file names this order may download, or None when it gets the whole packet."""
    if order["tier"] != "load_calc":
        return None
    return frozenset(
        [capacity_summary.STEM] + [document.file_stem for document in job_type.documents
                                   if document.file_stem.split("-", 1)[-1] in LOAD_CALC_SHEETS])


def _order_or_404(access_token: str) -> dict[str, Any]:
    order = orders.get_by_token(access_token)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "We can't find that order")
    return order


def _paid_order(access_token: str) -> dict[str, Any]:
    order = _order_or_404(access_token)
    if order["status"] == "in_review":
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This packet is being checked and hasn't been released yet")
    if order["status"] not in ("paid", "delivered"):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "This order isn't paid yet")
    return order


def _payment_ready(order: dict[str, Any]) -> bool:
    return order["source"] != "credit" and all(
        os.environ.get(name, "").strip() for name in ("SQUARE_ACCESS_TOKEN", "SQUARE_LOCATION_ID"))


@app.get("/api/orders/{access_token}/pay")
def pay_order(access_token: str, request: Request) -> Response:
    """Send the buyer to a fresh Square checkout for this order. The order page links here so polling never makes one."""
    order = _order_or_404(access_token)
    if order["status"] != "pending_payment":
        return RedirectResponse(f"/order/{access_token}", status_code=status.HTTP_303_SEE_OTHER)
    url = _checkout_url(order, request)
    if not url:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Payment isn't set up for this package yet")
    return RedirectResponse(url, status_code=status.HTTP_303_SEE_OTHER)


@app.api_route("/order/{access_token}", methods=["GET", "HEAD"])
def order_page(access_token: str) -> Response:
    try:
        known = orders.get_by_token(access_token) is not None
    except Exception:  # the page itself explains a database problem; only a clean miss is a 404
        log.exception("Could not look up the order for its page")
        known = True
    return _page("order.html") if known else _not_found_page()


@app.get("/api/orders/{access_token}")
def order_status(access_token: str) -> JSONResponse:
    order = _order_or_404(access_token)
    paid = order["status"] in ("paid", "delivered")
    view: dict[str, Any] = {
        "order_code": order["order_code"],
        "status": order["status"],
        "paid": paid,
        "in_review": order["status"] == "in_review",
        "tier": order["tier"],
        # What the buyer actually pays (or paid), not today's price.
        "price": order["amount_cents"] / 100 if order["amount_cents"] is not None else pricing.price(order["tier"]),
        "credit_applied": (order["credit_applied_cents"] or 0) / 100,
        "source": order["source"],
        "awaiting_credit_confirmation": order["source"] == "credit" and order["status"] == "pending_payment",
        "address": order["address"],
        # What the order page reports to analytics when the order shows paid.
        "job": sitedata.job_for_api_slug(order["job_slug"]),
        "city": order["jurisdiction_key"],
        "role": order["payload"].get("role", "") if isinstance(order.get("payload"), dict) else "",
        "checkout_url": f"/api/orders/{access_token}/pay" if _payment_ready(order) else "",
    }
    if view["in_review"]:
        view["city_name"] = _city_name(order)
    if not paid and not view["in_review"]:
        view["preview_pdf_url"] = f"/api/orders/{access_token}/preview-pdf"
        view["preview_pages_url"] = f"/api/orders/{access_token}/preview-pages"
    if paid:
        job_type = _job_type(order["job_slug"])
        only = _allowed_sheets(order, job_type)
        zip_ok = not _single_pdf_only(order["payload"])
        view.update({
            "pdf_url": f"/api/orders/{access_token}/pdf",
            "documents_url": f"/api/orders/{access_token}/documents" if zip_ok else None,
        })
        if only is not None:  # the Panel Capacity Report: just its two sheets, no city submission pages
            view["files"] = [{"title": capacity_summary.TITLE, "url": f"/api/orders/{access_token}/documents/{capacity_summary.STEM}"}] + [
                {"title": document.title, "url": f"/api/orders/{access_token}/documents/{document.file_stem}"}
                for document in job_type.documents if document.file_stem in only]
        else:
            _, result = _build(order["job_slug"], order["payload"], preview=False)
            view.update({
                "jurisdiction": result.body.get("jurisdiction"),
                "portal_fields": result.body.get("fields", []),
                "submission_email": result.body.get("submission_email"),
            })
    return JSONResponse(view, headers=PRIVATE_DATA)


def _downloaded(order: dict[str, Any]) -> None:
    """A clean file went out: the order is delivered, and the first time is recorded for the refund rule."""
    if order["status"] == "paid":
        orders.set_status(order["id"], "delivered")
    orders.mark_downloaded(order["id"])


def _pdf_download(content: bytes, name: str, inline: bool = False) -> Response:
    disposition = "inline" if inline else f'attachment; filename="{name}"'
    return Response(content=content, media_type="application/pdf", headers={"Content-Disposition": disposition, **PRIVATE_DATA})


@app.get("/api/orders/{access_token}/preview-pdf")
def order_preview_pdf(access_token: str) -> Response:
    order = _order_or_404(access_token)
    _, result = _build(order["job_slug"], order["payload"], preview=True)
    pdf = result.pdf
    if order["tier"] == "load_calc":
        pdf = _with_summary(order["payload"], result, pdf, preview=True)
    return _pdf_download(pdf, f'{order["order_code"]}-preview.pdf')


@app.get("/api/orders/{access_token}/preview-pages")
def order_preview_pages(access_token: str) -> JSONResponse:
    order = _order_or_404(access_token)
    _, result = _build(order["job_slug"], order["payload"], preview=True)
    pages_pdf = _with_summary(order["payload"], result, result.pdf, preview=True) if order["tier"] == "load_calc" else result.pdf
    return JSONResponse({"pages": [base64.b64encode(p).decode() for p in packet_page_images(pages_pdf)], "ready": bool(result.body.get("ready"))}, headers=PRIVATE_DATA)


@app.get("/api/orders/{access_token}/pdf")
def order_pdf(access_token: str) -> Response:
    """The clean PDF, built on the fly so no file is stored. A load_calc order gets just its two sheets."""
    order = _paid_order(access_token)
    job_type, result = _build(order["job_slug"], order["payload"], preview=False)
    pdf, name = result.pdf, f'{order["order_code"]}-permit-packet.pdf'
    only = _allowed_sheets(order, job_type)
    if only is not None:
        pdf = packet_subset_pdf(pdf, tuple(d.file_stem for d in job_type.documents), only)
        pdf = _with_summary(order["payload"], result, pdf, preview=False)
        name = f'{order["order_code"]}-load-calc-and-panel-audit.pdf'
    _downloaded(order)
    return _pdf_download(pdf, name)


@app.get("/api/orders/{access_token}/documents")
def order_documents(access_token: str) -> Response:
    order = _paid_order(access_token)
    if _single_pdf_only(order["payload"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "This city takes one combined PDF, not separate plan sheets")
    job_type, result = _build(order["job_slug"], order["payload"], preview=False)
    stems = tuple(document.file_stem for document in job_type.documents)
    zip_name = job_type.zip_name.replace("-demo.zip", ".zip")
    only = _allowed_sheets(order, job_type)
    content = packet_documents_zip(result.pdf, stems, only)
    if only is not None:
        buffer = io.BytesIO(content)
        with zipfile.ZipFile(buffer, "a", zipfile.ZIP_DEFLATED) as archive:
            archive.writestr(f"{capacity_summary.STEM}.pdf", _summary_pdf(order["payload"], result, preview=False))
        content = buffer.getvalue()
    _downloaded(order)
    return Response(content=content, media_type="application/zip",
                    headers={"Content-Disposition": f'attachment; filename="{zip_name}"', **PRIVATE_DATA})


@app.get("/api/orders/{access_token}/documents/{file_stem}")
def order_document(access_token: str, file_stem: str) -> Response:
    """One sheet of the packet as its own PDF. A load_calc order may only take its load calculation and panel schedule."""
    order = _paid_order(access_token)
    job_type = _job_type(order["job_slug"])
    only = _allowed_sheets(order, job_type)
    if only is not None and file_stem not in only:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "This package includes only the Panel Capacity Report")
    stems = tuple(document.file_stem for document in job_type.documents)
    if file_stem not in stems and not (only is not None and file_stem == capacity_summary.STEM):
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such sheet")
    if _single_pdf_only(order["payload"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "This city takes one combined PDF, not separate plan sheets")
    _, result = _build(order["job_slug"], order["payload"], preview=False)
    if file_stem == capacity_summary.STEM:
        _downloaded(order)
        return _pdf_download(_summary_pdf(order["payload"], result, preview=False), f'{order["order_code"]}-{file_stem}.pdf')
    content = packet_subset_pdf(result.pdf, stems, frozenset({file_stem}))
    _downloaded(order)
    return _pdf_download(content, f'{order["order_code"]}-{file_stem}.pdf')


# ---- Find my order ----

FIND_ORDER_MESSAGE = "If we have orders for that email, we've sent the links."


@app.post("/api/find-order")
def find_order(request: Request, body: dict[str, Any] = Body(...)) -> dict:
    """Email every order link for an address. The answer never says whether the address has orders."""
    email = str(body.get("email") or "").strip()
    if EMAIL.match(email) and len(email) <= 200:
        try:
            if orders.find_order_allowed(email):  # 3 requests per email per hour
                found = orders.list_by_email(email)
                if found:
                    _notify(emails.find_order, email, [(order, _order_link(request, order)) for order in found])
        except Exception:
            log.exception("Find my order failed")
    return {"message": FIND_ORDER_MESSAGE}


# ---- Admin ----

basic = HTTPBasic(auto_error=False)


def require_admin(credentials: HTTPBasicCredentials | None = Depends(basic)) -> None:
    """HTTP Basic with ADMIN_PASSWORD (any user name). Without ADMIN_PASSWORD the admin is switched off."""
    password = os.environ.get("ADMIN_PASSWORD", "")
    if not password:
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "ADMIN_PASSWORD is not set")
    if credentials is None or not secrets.compare_digest(credentials.password.encode(), password.encode()):
        raise HTTPException(
            status.HTTP_401_UNAUTHORIZED, "Admin sign-in required", headers={"WWW-Authenticate": 'Basic realm="Admin"'})


# ---- Payment webhook ----

def _find_paid_record(provider_order_id: str):
    link = orders.get_checkout_link(provider_order_id)
    if link is None:
        return None
    record = orders.get_pack_order(link["record_id"]) if link["kind"] == "pack" else orders.get_by_id(link["record_id"])
    return (link["kind"], record, link["amount_cents"]) if record is not None else None


def _fulfil(kind: str, record: dict[str, Any], request: Request) -> None:
    """Unlock a paid order or credit a paid pack. Repeating it for the same record does nothing."""
    if kind == "pack":
        lot = orders.mark_pack_paid(record["id"])
        if lot is not None:
            log.info("Pack %s paid: %s credits for %s", record["id"], lot["credits_total"], record["customer_email"])
            _notify(emails.pack_ready, record["customer_email"], lot["credits_total"],
                    _date_label(lot["expires_at"]), f"{_base_url(request)}/start/")
        return
    if record["status"] == "pending_payment":
        paid = _mark_paid(record, request)
        log.info("Order %s paid through Square (now %s)", paid["order_code"], paid["status"])


def _date_label(iso: str) -> str:
    return datetime.fromisoformat(iso).strftime("%B %-d, %Y")


@app.post("/api/webhooks/square")
async def square_webhook(request: Request) -> dict:
    """Unlock an order (or credit a pack) when Square reports a completed payment. Only a correctly signed request is believed."""
    body = await request.body()
    return payments.handle_webhook(body, request.headers, _find_paid_record, lambda kind, record: _fulfil(kind, record, request))


# ---- Prepaid credits ----

CREDIT_MESSAGE = "If this email has credits, we've sent a confirmation link."


@app.post("/api/public/packs", dependencies=[Depends(rate_limit("preview"))])
def buy_pack(request: Request, body: dict[str, Any] = Body(...)) -> dict:
    """Start a Square checkout for a credit pack. Body: {pack, email}. Credits and price are fixed now."""
    email = str(body.get("email") or "").strip()
    pack = body.get("pack")
    if not EMAIL.match(email) or len(email) > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid email address")
    if pack not in pricing.PACKS:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, f"pack must be one of {', '.join(pricing.PACKS)}")
    credits = pricing.pack_credits(pack)
    record = orders.create_pack_order(email, pack, credits, pricing.pack_price(pack) * 100)
    try:
        url, provider_order_id = payments.create_checkout(
            "pack", record, record["amount_cents"], record["customer_email"],
            f"{_base_url(request)}/pro-credits/?purchased=1", f"Permit Packets prepaid credits: {credits} Instant Permit Packets")
    except payments.PaymentError as error:
        log.error("%s", error)
        raise HTTPException(status.HTTP_503_SERVICE_UNAVAILABLE, "Checkout isn't available right now. Try again shortly.") from None
    orders.add_checkout_link(provider_order_id, "pack", record["id"], record["amount_cents"])
    orders.set_pack_provider_order_id(record["id"], provider_order_id)
    return {"checkout_url": url}


@app.post("/api/public/credit-quote", dependencies=[Depends(rate_limit("preview"))])
def credit_quote(body: dict[str, Any] = Body(...)) -> dict:
    """The Panel Capacity Report credit a checkout for this email and tier would get, in dollars."""
    email = str(body.get("email") or "").strip()
    if not EMAIL.match(email) or len(email) > 200:
        return {"credit": 0}
    return {"credit": _credit_quote(email, str(body.get("tier") or ""))[1] / 100}


@app.post("/api/public/orders/credit", dependencies=[Depends(rate_limit("preview"))])
def create_credit_order(request: Request, body: dict[str, Any] = Body(...)) -> dict:
    """Save an Instant Permit Packet order to be paid with a prepaid credit and email a one-time confirm link.
    The answer never says whether the email has credits. Body: {job_slug, customer_email, payload, role}."""
    email = str(body.get("customer_email") or "").strip()
    payload = body.get("payload")
    if not EMAIL.match(email) or len(email) > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid email address")
    if not isinstance(payload, dict):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "payload must be the job's inputs")
    if body.get("role") not in ("electrician", "contractor"):
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Prepaid credits are for electricians and contractors")
    job_type = _job_type(str(body.get("job_slug") or ""))
    payload = {**payload, "role": body["role"]}
    working = dict(payload)
    _contractor_logo(working)
    job = _validated(job_type, working)
    city = jurisdiction_by_key(payload.get("jurisdiction_key"), payload.get("city"), payload.get("state"))
    order = orders.create_order(
        customer_email=email, tier="instant_packet", job_slug=job_type.slug, address=job.address,
        jurisdiction_key=city.key, payload=payload, source="credit", amount_cents=0)
    if orders.credits_available(email) > 0:
        token = orders.create_confirm_token(email, order["id"])
        _notify(emails.credit_confirm, email, f"{_base_url(request)}/credits/confirm?token={quote(token, safe='')}")
    return {"message": CREDIT_MESSAGE, "order_url": f"/order/{order['access_token']}"}


def _credit_page(title: str, message: str, link: tuple[str, str] | None = None, status_code: int = 200, form: str = "") -> HTMLResponse:
    from html import escape
    extra = form or (f'<p><a class="button" href="{escape(link[0])}">{escape(link[1])}</a></p>' if link else "")
    html = (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<meta name="robots" content="noindex, nofollow"><title>{escape(title)}</title>'
            f'<link rel="stylesheet" href="/assets/css/app.css?v={ASSET_VERSION}"></head><body><main class="page-main">'
            f'<h1>{escape(title)}</h1><p class="lead">{escape(message)}</p>{extra}</main></body></html>')
    return HTMLResponse(html, status_code=status_code, headers=PRIVATE_PAGE)


@app.api_route("/credits/confirm", methods=["GET", "HEAD"])
@app.api_route("/credits/confirm/", methods=["GET", "HEAD"], include_in_schema=False)
def confirm_credit_page(token: str = "") -> Response:
    """The emailed link only asks. It never spends a credit; the button below posts the token."""
    from html import escape
    order = orders.get_by_id(orders.peek_confirm_token(token) or "") if token else None
    if order is None:
        return _credit_page("This link can't be used", "It has expired or was already used. Start again from your packet's package step.",
                            ("/start/", "Start a packet"), status.HTTP_410_GONE)
    form = (f'<form method="post" action="/credits/confirm"><input type="hidden" name="token" value="{escape(token, quote=True)}">'
            '<button type="submit">Use 1 credit</button></form>')
    return _credit_page(f"Use 1 credit for {order['address']}?", "One prepaid credit pays for this Instant Permit Packet.", form=form)


@app.post("/credits/confirm")
@app.post("/credits/confirm/", include_in_schema=False)
async def confirm_credit(request: Request) -> Response:
    """Spend one credit on the order the token was made for, unlock it and go to the order page."""
    from urllib.parse import parse_qs
    token = (parse_qs((await request.body()).decode("utf-8", "ignore")).get("token") or [""])[0]
    outcome, order_id = orders.redeem_confirm_token(token) if token else ("invalid", None)
    if outcome == "invalid":
        return _credit_page("This link can't be used", "It has expired or was already used. Start again from your packet's package step.",
                            ("/start/", "Start a packet"), status.HTTP_410_GONE)
    if outcome == "no_credit":
        return _credit_page("No credits available", "There's no unexpired prepaid credit on this email right now.",
                            ("/pro-credits/", "Buy prepaid credits"))
    order = orders.get_by_id(order_id or "")
    if order is None:
        return _credit_page("This link can't be used", "We couldn't find that order.", ("/start/", "Start a packet"), status.HTTP_404_NOT_FOUND)
    if order["status"] == "pending_payment":
        order = _mark_paid(order, request)
    return RedirectResponse(f"/order/{order['access_token']}", status_code=status.HTTP_303_SEE_OTHER)


@app.api_route("/admin", methods=["GET", "HEAD"], dependencies=[Depends(require_admin)])
def admin_page() -> Response:
    return _page("admin.html")


def _hours_left(order: dict[str, Any]) -> float | None:
    """Hours left of the 24-hour check; negative once it is overdue."""
    if not order.get("paid_at"):
        return None
    paid = datetime.fromisoformat(order["paid_at"])
    if paid.tzinfo is None:
        paid = paid.replace(tzinfo=timezone.utc)
    return round(REVIEW_HOURS - (datetime.now(timezone.utc) - paid).total_seconds() / 3600, 1)


def _job_label(slug: str) -> str:
    job_type = get_job_type(slug)
    return job_type.label if job_type else slug


@app.get("/api/admin/orders", dependencies=[Depends(require_admin)])
def admin_orders(request: Request) -> JSONResponse:
    keys = ("id", "order_code", "customer_email", "address", "tier", "status", "created_at", "paid_at", "released_at", "downloaded_at")

    def row(order: dict[str, Any]) -> dict[str, Any]:
        return {**{key: order[key] for key in keys}, "downloaded": bool(order["downloaded_at"])}

    in_review = [
        {**row(order), "job_type": _job_label(order["job_slug"]), "hours_remaining": _hours_left(order),
         "order_url": f"/order/{order['access_token']}"}
        for order in orders.list_in_review()]
    return JSONResponse(
        {"in_review": in_review, "orders": [row(order) for order in orders.list_recent(100)]}, headers=PRIVATE_DATA)


@app.post("/api/admin/orders/{order_id}/approve", dependencies=[Depends(require_admin)])
def approve_order(order_id: str, request: Request) -> dict:
    """Mark a payment as received by hand, for a payment the webhook missed. Only a pending order changes: a city_checked_24h order goes to review like a webhook payment."""
    order = orders.get_by_id(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such order")
    if order["status"] == "pending_payment":
        order = _mark_paid(order, request)
    return {"id": order["id"], "order_code": order["order_code"], "status": order["status"]}


@app.post("/api/admin/orders/{order_id}/release", dependencies=[Depends(require_admin)])
def release_order(order_id: str, request: Request) -> dict:
    """End the review hold: the order unlocks, and the buyer is emailed."""
    order = orders.get_by_id(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such order")
    released = orders.release(order_id)
    if released is None:
        raise HTTPException(status.HTTP_409_CONFLICT, "This order isn't in review")
    _notify(emails.released, released, _order_link(request, released))
    return {"id": released["id"], "order_code": released["order_code"], "status": released["status"], "released_at": released["released_at"]}


@app.get("/api/admin/credits", dependencies=[Depends(require_admin)])
def admin_credits() -> JSONResponse:
    lots = [{"id": lot["id"], "email": lot["customer_email"], "total": lot["credits_total"], "used": lot["credits_used"],
             "remaining": lot["remaining"], "expires_at": lot["expires_at"], "reason": lot["reason"]} for lot in orders.list_lots()]
    return JSONResponse({"lots": lots}, headers=PRIVATE_DATA)


@app.post("/api/admin/credits/grant", dependencies=[Depends(require_admin)])
def admin_grant_credits(body: dict[str, Any] = Body(...)) -> dict:
    email = str(body.get("email") or "").strip()
    reason = str(body.get("reason") or "").strip()[:200]
    try:
        count = int(body.get("credits"))
    except (TypeError, ValueError):
        count = 0
    if not EMAIL.match(email) or len(email) > 200:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Enter a valid email address")
    if not 1 <= count <= 1000:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, "Credits must be a number from 1 to 1000")
    lot = orders.grant_credits(email, count, reason)
    log.info("Admin granted %s credits to %s (%s)", count, lot["customer_email"], reason or "no reason given")
    return {"id": lot["id"], "expires_at": lot["expires_at"]}


@app.get("/api/admin/orders/{order_id}/pdf", dependencies=[Depends(require_admin)])
def admin_order_pdf(order_id: str, download: int = 0) -> Response:
    """The order's clean packet for the reviewer. It never counts as the buyer's download."""
    order = orders.get_by_id(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such order")
    _, result = _build(order["job_slug"], order["payload"], preview=False)
    return _pdf_download(result.pdf, f'{order["order_code"]}-permit-packet.pdf', inline=not download)
