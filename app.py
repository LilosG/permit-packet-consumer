"""Public permit packet generator: address to property, job to watermarked preview, payment to clean packet."""
from __future__ import annotations

import base64
import hashlib
import logging
import os
import re
import secrets
import threading
import time
from collections import deque
from contextlib import asynccontextmanager
from dataclasses import asdict
from pathlib import Path
from typing import Any

from fastapi import Body, Depends, FastAPI, HTTPException, Request, Response, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from pydantic import ValidationError

from permit_packets import orders
from permit_packets.core.pdf_base import COMPANY_NAME, CONTRACTOR_LOGO, DEMO_MARKS
from permit_packets.core.preview import packet_documents_zip, packet_page_images
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
from permit_packets.jurisdictions import jurisdiction_by_key, jurisdiction_json

log = logging.getLogger("permit_packets")

STATIC = Path(__file__).parent / "permit_packets" / "static"
ASSETS = STATIC / "assets"
# Each tier's Wave payment link, set in the environment; the link's price matches the tier.
WAVE_LINK_ENV = {"load_calc": "WAVE_LINK_39", "instant_packet": "WAVE_LINK_89", "city_checked_24h": "WAVE_LINK_169"}
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
INDEX_HTML = (STATIC / "index.html").read_text(encoding="utf-8").replace("{{ASSET_VERSION}}", ASSET_VERSION)
# Only the assets folder is served as files. The other pages are routes below.
app.mount("/assets", StaticFiles(directory=ASSETS), name="assets")


def _page(name: str) -> HTMLResponse:
    html = (STATIC / name).read_text(encoding="utf-8").replace("{{ASSET_VERSION}}", ASSET_VERSION)
    return HTMLResponse(html, headers=PRIVATE_PAGE)


@app.get("/")
def home() -> Response:
    return HTMLResponse(INDEX_HTML, headers={"Cache-Control": "no-cache"})


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


@app.post("/api/property", dependencies=[Depends(rate_limit("property"))])
def look_up_property(payload: LookupRequest) -> dict:
    job_type = _known_job_type(payload.job_type)
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

def _wave_link(tier: str) -> str:
    return os.environ.get(WAVE_LINK_ENV[tier], "").strip()


@app.post("/api/public/orders")
def create_order(body: dict[str, Any] = Body(...)) -> dict:
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
    working = dict(payload)
    _contractor_logo(working)  # refuse a bad logo now, not after the customer has paid
    request = _validated(job_type, working)
    city = jurisdiction_by_key(payload.get("jurisdiction_key"), payload.get("city"), payload.get("state"))
    order = orders.create_order(
        customer_email=email, tier=tier, job_slug=job_type.slug, address=request.address,
        jurisdiction_key=city.key, payload=payload,
    )
    if os.environ.get("DEV_AUTO_APPROVE", "").strip().lower() == "true":
        order = orders.set_status(order["id"], "paid") or order
    return {
        "order_code": order["order_code"],
        "access_token": order["access_token"],
        "order_url": f"/order/{order['access_token']}",
        "wave_checkout_url": _wave_link(tier),
    }


def _order_or_404(access_token: str) -> dict[str, Any]:
    order = orders.get_by_token(access_token)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "We can't find that order")
    return order


def _paid_order(access_token: str) -> dict[str, Any]:
    order = _order_or_404(access_token)
    if order["status"] not in ("paid", "delivered"):
        raise HTTPException(status.HTTP_402_PAYMENT_REQUIRED, "This order isn't paid yet")
    return order


@app.get("/order/{access_token}")
def order_page(access_token: str) -> Response:
    return _page("order.html")


@app.get("/api/orders/{access_token}")
def order_status(access_token: str) -> JSONResponse:
    order = _order_or_404(access_token)
    paid = order["status"] in ("paid", "delivered")
    view: dict[str, Any] = {
        "order_code": order["order_code"],
        "status": order["status"],
        "paid": paid,
        "tier": order["tier"],
        "address": order["address"],
        "wave_checkout_url": _wave_link(order["tier"]),
        "wave_instructions": f"Paste {order['order_code']} in the Wave note when you pay, so we can match your payment.",
    }
    if paid:
        _, result = _build(order["job_slug"], order["payload"], preview=False)
        view.update({
            "pdf_url": f"/api/orders/{access_token}/pdf",
            "documents_url": None if _single_pdf_only(order["payload"]) else f"/api/orders/{access_token}/documents",
            "jurisdiction": result.body.get("jurisdiction"),
            "portal_fields": result.body.get("fields", []),
            "submission_email": result.body.get("submission_email"),
        })
    return JSONResponse(view, headers=PRIVATE_DATA)


def _delivered(order: dict[str, Any]) -> None:
    if order["status"] == "paid":
        orders.set_status(order["id"], "delivered")


@app.get("/api/orders/{access_token}/pdf")
def order_pdf(access_token: str) -> Response:
    """The clean PDF, built on the fly so no file is stored."""
    order = _paid_order(access_token)
    _, result = _build(order["job_slug"], order["payload"], preview=False)
    _delivered(order)
    return Response(
        content=result.pdf,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="{order["order_code"]}-permit-packet.pdf"', **PRIVATE_DATA},
    )


@app.get("/api/orders/{access_token}/documents")
def order_documents(access_token: str) -> Response:
    order = _paid_order(access_token)
    if _single_pdf_only(order["payload"]):
        raise HTTPException(status.HTTP_409_CONFLICT, "This city takes one combined PDF, not separate plan sheets")
    job_type, result = _build(order["job_slug"], order["payload"], preview=False)
    _delivered(order)
    return _documents_response(job_type, result, job_type.zip_name.replace("-demo.zip", ".zip"))


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


@app.get("/admin", dependencies=[Depends(require_admin)])
def admin_page() -> Response:
    return _page("admin.html")


@app.get("/api/admin/orders", dependencies=[Depends(require_admin)])
def admin_orders() -> JSONResponse:
    keys = ("id", "order_code", "customer_email", "address", "tier", "status", "created_at")
    return JSONResponse(
        {"orders": [{key: order[key] for key in keys} for order in orders.list_recent(100)]}, headers=PRIVATE_DATA)


@app.post("/api/admin/orders/{order_id}/approve", dependencies=[Depends(require_admin)])
def approve_order(order_id: str) -> dict:
    """Mark a Wave payment as received. An order that is already paid or delivered stays as it is."""
    order = orders.get_by_id(order_id)
    if order is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "No such order")
    if order["status"] == "pending_payment":
        order = orders.set_status(order_id, "paid") or order
    return {"id": order["id"], "order_code": order["order_code"], "status": order["status"]}
