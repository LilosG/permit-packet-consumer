"""The public site pages: templates, routes, sitemaps, robots and the trailing-slash rule.

Pages render through Jinja templates in permit_packets/templates (base.html is the layout). Pages whose
content has not shipped yet are placeholders: they answer with noindex,follow and stay out of the sitemaps
until their entry in seo.PAGES is flipped to indexable=True.
"""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from types import SimpleNamespace

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.requests import Request

from permit_packets import faq as faq_data
from permit_packets import seo, sitedata
from permit_packets.jurisdictions import KNOWN

log = logging.getLogger("permit_packets")

TEMPLATES = Path(__file__).parent / "templates"
SAMPLE_ADDRESS = "453 Brockton St, El Cajon, CA 92020"  # the sample job (tools/make_sample.py)
CONTENT_DATE = "2026-11-16"  # when the pages registered below last changed

env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]), trim_blocks=False)
env.globals.update(
    nav_who=sitedata.NAV_WHO, nav_permits=sitedata.NAV_PERMITS, nav_links=sitedata.NAV_LINKS,
    jobs=list(sitedata.JOBS.values()), sample_address=SAMPLE_ADDRESS, asset_version="")

router = APIRouter()
NO_CACHE = {"Cache-Control": "no-cache"}
PUBLIC_PAGE = {"Cache-Control": "public, max-age=300"}


def set_asset_version(version: str) -> None:
    env.globals["asset_version"] = version


def _context() -> dict:
    return {"popular_cities": sitedata.popular_cities(), "city_count": len(KNOWN), "ga": seo.ga_snippet()}


def render(template: str, *, meta, jsonld: list[dict] | None = None, crumbs: list[tuple[str, str]] | None = None,
           final_cta: bool = False, status_code: int = 200, headers: dict | None = None, **context) -> HTMLResponse:
    blocks = list(jsonld or [])
    if crumbs:
        blocks.append(seo.breadcrumb(crumbs))
    body = env.get_template(template).render(
        meta=meta, jsonld=seo.jsonld_scripts(blocks), crumbs=crumbs, final_cta=final_cta, **_context(), **context)
    return HTMLResponse(body, status_code=status_code, headers=headers or PUBLIC_PAGE)


def footer_html() -> str:
    """The site footer as a string, for the pages that are still plain static HTML (order, admin, 404)."""
    return env.get_template("partials/footer.html").render(**_context())


# ---- The trailing-slash rule ----

SLASH_EXEMPT_PREFIXES = ("/api/", "/order/", "/admin", "/assets/")


async def trailing_slash(request: Request, call_next):
    """A GET without the trailing slash is a 301 to the slash version. Files (/robots.txt, /sitemap.xml,
    /favicon.ico, /llms.txt), /api/*, /order/* and /admin* are left alone."""
    path = request.url.path
    if (request.method in ("GET", "HEAD") and path != "/" and not path.endswith("/")
            and not path.startswith(SLASH_EXEMPT_PREFIXES) and "." not in path.rsplit("/", 1)[-1]):
        target = path + "/" + (f"?{request.url.query}" if request.url.query else "")
        return RedirectResponse(target, status_code=301)
    return await call_next(request)


# ---- Home ----

seo.register("/", "Home", indexable=True, lastmod=CONTENT_DATE)


def _plain(fragment: str) -> str:
    import html as htmllib
    return htmllib.unescape(re.sub(r"<[^>]+>", "", fragment)).strip()


@router.api_route("/", methods=["GET", "HEAD"])
def home() -> Response:
    qas = [(_plain(question), _plain(answer)) for question, answer in faq_data.FAQ]
    return render(
        "home.html", meta=seo.page_meta(seo.HOME_TITLE, seo.HOME_DESCRIPTION, "/", robots=seo.robots_for("/")),
        jsonld=[seo.organization(), seo.faq(qas)], final_cta=True, headers=NO_CACHE,
        faq=faq_data.FAQ, verification=seo.verification_tags())


# ---- The wizard ----

JOB_TYPE_MAP = {job.slug: job.type_key for job in sitedata.JOBS.values()}


@router.api_route("/start/", methods=["GET", "HEAD"])
def start(job: str = "", city: str = "", address: str = "", role: str = "", tier: str = "") -> Response:
    """The four-step wizard. job, city, address, role and tier prefill it; the canonical is always the bare /start/."""
    role = role if role in sitedata.ROLES else sitedata.DEFAULT_ROLE
    tier_key = sitedata.recommended_tier(role, tier)
    known_city = sitedata.city_by_key(city)
    prefill = SimpleNamespace(
        job_key=JOB_TYPE_MAP.get(job, ""), role=role, tier=tier_key, tier_key=tier_key,
        tier_explicit=tier in sitedata.TIER_PARAMS, address=address.strip()[:200],
        city_label=known_city.label if known_city else "")
    meta = seo.page_meta(
        "Start Your Free Permit Packet Preview | Permit Packets",
        "Enter any US property address to preview a residential electrical permit packet free. Starting at $39.",
        "/start/")
    return render(
        "start.html", meta=meta, prefill=prefill, roles=sitedata.ROLES, job_map_json=json.dumps(JOB_TYPE_MAP),
        jsonld=[seo.webapp("Permit Packets", "/start/")], crumbs=[("Home", "/"), ("Start", "/start/")],
        headers=NO_CACHE)


# ---- Placeholders: an H1 and "Coming soon", noindex until their content prompt ships ----

def _placeholder(path: str, h1: str, crumb: str, parents: list[tuple[str, str]] | None = None) -> None:
    title = f"{h1} | {seo.SITE_NAME}"
    seo.register(path, h1)

    def handler() -> Response:
        meta = seo.page_meta(title, f"{h1}. This page is coming soon.", path, robots=seo.robots_for(path))
        crumbs = [("Home", "/"), *(parents or []), (crumb, path)]
        return render("placeholder.html", meta=meta, h1=h1, crumbs=crumbs)

    router.add_api_route(path, handler, methods=["GET", "HEAD"], include_in_schema=False)


_placeholder("/for/diy-homeowners/", "Permit Packets for DIY Homeowners", "DIY Homeowners")
_placeholder("/for/homeowners-hiring-an-electrician/", "Permit Packets for Homeowners Hiring an Electrician",
             "Hiring an Electrician")
_placeholder("/for/electricians/", "Permit Packets for Electricians", "Electricians")
_placeholder("/for/contractors/", "Permit Packets for Contractors", "Contractors")
_placeholder("/ev-charger-permit/", "EV Charger Permit Packet", "EV Charger")
_placeholder("/panel-upgrade-permit/", "Panel Upgrade Permit Packet", "Panel Upgrade")
_placeholder("/subpanel-permit/", "Subpanel Permit Packet", "Subpanel")
_placeholder("/hot-tub-240v-permit/", "Hot Tub / 240V Circuit Permit Packet", "Hot Tub / 240V")
_placeholder("/permits/", "Electrical Permits by City", "Permits")
_placeholder("/sample-packet/", "Sample Permit Packet", "Sample Packet")
_placeholder("/pricing/", "Pricing", "Pricing")
_placeholder("/faq/", "Frequently Asked Questions", "FAQ")
_placeholder("/about/", "About Permit Packets", "About")

STATE_NAMES = {"az": "Arizona", "ca": "California", "nc": "North Carolina", "tn": "Tennessee", "wa": "Washington"}


def _state_name(state: str) -> str:
    return STATE_NAMES.get(state, state.upper())


def _location_page(title: str, h1: str, path: str, crumbs: list[tuple[str, str]]) -> Response:
    meta = seo.page_meta(title, f"{h1}. This page is coming soon.", path, robots=seo.location_robots())
    return render("placeholder.html", meta=meta, h1=h1, crumbs=crumbs)


@router.api_route("/permits/{state}/", methods=["GET", "HEAD"], include_in_schema=False)
def permits_state(state: str) -> Response:
    if state not in sitedata.cities_by_state():
        raise HTTPException(404)
    name = _state_name(state)
    h1 = f"Electrical Permits in {name}"
    return _location_page(f"{h1} | {seo.SITE_NAME}", h1, f"/permits/{state}/",
                          [("Home", "/"), ("Permits", "/permits/"), (name, f"/permits/{state}/")])


@router.api_route("/permits/{state}/{city}/", methods=["GET", "HEAD"], include_in_schema=False)
def permits_city(state: str, city: str) -> Response:
    found = sitedata.find_city(state, city)
    if found is None:
        raise HTTPException(404)
    h1 = f"Electrical Permits in {found.label}"
    path = sitedata.city_path(found)
    return _location_page(f"{h1} | {seo.SITE_NAME}", h1, path,
                          [("Home", "/"), ("Permits", "/permits/"), (_state_name(state), f"/permits/{state}/"),
                           (found.label, path)])


@router.api_route("/permits/{state}/{city}/{job}/", methods=["GET", "HEAD"], include_in_schema=False)
def permits_job(state: str, city: str, job: str) -> Response:
    found = sitedata.find_city(state, city)
    if found is None or job not in sitedata.JOBS:
        raise HTTPException(404)
    label = sitedata.JOBS[job].label
    h1 = f"{label} Permit in {found.label}"
    path = f"{sitedata.city_path(found)}{job}/"
    return _location_page(f"{label} Permit: {found.label} | {seo.SITE_NAME}", h1, path,
                          [("Home", "/"), ("Permits", "/permits/"), (_state_name(state), f"/permits/{state}/"),
                           (found.label, sitedata.city_path(found)), (label, path)])


# ---- Legal and support pages ----

LEGAL = (
    ("/terms/", "terms.html", "Terms", "Terms | Permit Packets",
     "Terms for using Permit Packets, an automated drafting and NEC calculation tool provided by Lilos Growth."),
    ("/privacy/", "privacy.html", "Privacy Policy", "Privacy | Permit Packets",
     "What Permit Packets collects, why, and which service providers it uses."),
    ("/refund/", "refund.html", "Refund Policy", "Refund Policy | Permit Packets",
     "Full refund before you download your clean packet. How refunds work for Permit Packets."),
)
for _path, _template, _name, _title, _description in LEGAL:
    seo.register(_path, _name, indexable=True, lastmod=CONTENT_DATE)

    def _legal(_path=_path, _template=_template, _name=_name, _title=_title, _description=_description) -> Response:
        return render(_template, meta=seo.page_meta(_title, _description, _path, robots=seo.robots_for(_path)),
                      crumbs=[("Home", "/"), (_name, _path)])

    router.add_api_route(_path, _legal, methods=["GET", "HEAD"], include_in_schema=False)


@router.api_route("/find-order/", methods=["GET", "HEAD"], include_in_schema=False)
def find_order_page() -> Response:
    meta = seo.page_meta("Find my order | Permit Packets", "Get your Permit Packets order links by email.",
                         "/find-order/", robots="noindex")
    return render("find-order.html", meta=meta)


# ---- robots, sitemaps, llms.txt ----

@router.api_route("/robots.txt", methods=["GET", "HEAD"], include_in_schema=False)
def robots() -> Response:
    return PlainTextResponse(seo.robots_txt(), headers={"Cache-Control": "public, max-age=3600"})


def _xml(body: str) -> Response:
    return Response(body, media_type="application/xml", headers={"Cache-Control": "public, max-age=3600"})


@router.api_route("/sitemap.xml", methods=["GET", "HEAD"], include_in_schema=False)
def sitemap_index() -> Response:
    return _xml(seo.sitemap_index())


@router.api_route("/sitemap-pages.xml", methods=["GET", "HEAD"], include_in_schema=False)
def sitemap_pages() -> Response:
    return _xml(seo.sitemap_pages())


@router.api_route("/sitemap-locations.xml", methods=["GET", "HEAD"], include_in_schema=False)
def sitemap_locations() -> Response:
    return _xml(seo.sitemap_locations())


@router.api_route("/sitemap-guides.xml", methods=["GET", "HEAD"], include_in_schema=False)
def sitemap_guides() -> Response:
    return _xml(seo.sitemap_guides())


@router.api_route("/llms.txt", methods=["GET", "HEAD"], include_in_schema=False)
def llms() -> Response:
    return PlainTextResponse(seo.llms_txt(), headers={"Cache-Control": "public, max-age=3600"})
