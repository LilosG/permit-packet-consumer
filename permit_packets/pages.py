"""The public site pages: templates, routes, sitemaps, robots and the trailing-slash rule.

Pages render through Jinja templates in permit_packets/templates (base.html is the layout). Pages whose
content has not shipped yet are placeholders: they answer with noindex,follow and stay out of the sitemaps
until their entry in seo.PAGES is flipped to indexable=True.
"""
from __future__ import annotations

import datetime
import json
import logging
import re
from pathlib import Path
from types import SimpleNamespace

from fastapi import APIRouter, HTTPException
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from markupsafe import Markup
from jinja2 import Environment, FileSystemLoader, select_autoescape
from starlette.requests import Request

from permit_packets import content, seo, sitedata
from permit_packets import faq as faq_data
from permit_packets.jurisdictions import KNOWN

log = logging.getLogger("permit_packets")

TEMPLATES = Path(__file__).parent / "templates"
SAMPLE_ADDRESS = "453 Brockton St, El Cajon, CA 92020"  # the sample job (tools/make_sample.py)
CONTENT_DATE = "2026-11-16"  # when the pages registered below last changed
LAST_REVIEWED = datetime.date.fromisoformat(CONTENT_DATE).strftime("%B %-d, %Y")

env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=select_autoescape(["html"]), trim_blocks=False)
env.globals.update(
    nav_who=sitedata.NAV_WHO, nav_links=sitedata.NAV_LINKS,
    jobs=list(sitedata.JOBS.values()), sample_address=SAMPLE_ADDRESS, asset_version="")



def permits_live() -> bool:
    """True once /permits/ is an indexable page. Until then no page links to it."""
    entry = seo.PAGES.get("/permits/")
    return bool(entry and entry.indexable)


def fill(text: str) -> Markup:
    """Replace {permits}: a link to the city guides once they are live, plain words until then."""
    link = '<a href="/permits/">our city permit guides</a>' if permits_live() else "your city's building department"
    return Markup(text.replace("{permits}", link))


env.filters["fill"] = fill
env.globals.update(last_reviewed=LAST_REVIEWED, author=seo.AUTHOR, tiers=content.TIERS)

router = APIRouter()
NO_CACHE = {"Cache-Control": "no-cache"}
PUBLIC_PAGE = {"Cache-Control": "public, max-age=300"}


def set_asset_version(version: str) -> None:
    env.globals["asset_version"] = version


def _context() -> dict:
    """Header and footer data. Links to the /permits/ pages stay out until those pages are indexable."""
    live = permits_live()
    return {"popular_cities": sitedata.popular_cities() if seo.LOCATIONS_INDEXABLE else [],
            "nav_permits": [item for item in sitedata.NAV_PERMITS if live or item[1] != "/permits/"],
            "city_count": len(KNOWN), "ga": seo.ga_snippet()}


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


JOB_CARDS = {
    "ev-charger": "Site plan, single-line diagram and load calc for a Level 2 charger",
    "panel-upgrade": "Riser diagram and load calculation for a service or panel upgrade",
    "subpanel": "Feeder schedule, voltage drop and load calc for a new subpanel",
    "hot-tub-240v": "Plans for a hot tub, sauna, heat pump or mini-split circuit",
}


@router.api_route("/", methods=["GET", "HEAD"])
def home() -> Response:
    qas = [(_plain(question), _plain(answer)) for question, answer in faq_data.FAQ]
    return render(
        "home.html", meta=seo.page_meta(seo.HOME_TITLE, seo.HOME_DESCRIPTION, "/", robots=seo.robots_for("/")),
        jsonld=[seo.organization(), seo.faq(qas)], final_cta=True, headers=NO_CACHE,
        faq=faq_data.FAQ, verification=seo.verification_tags(),
        who_cards=who_cards(), job_links=job_links())


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
        "/start/", robots="noindex,follow")
    return render(
        "start.html", meta=meta, prefill=prefill, roles=sitedata.ROLES, job_map_json=json.dumps(JOB_TYPE_MAP),
        jsonld=[seo.webapp("Permit Packets", "/start/")], crumbs=[("Home", "/"), ("Start", "/start/")],
        headers=NO_CACHE)


# ---- Content pages: job hubs, audience pages, sample, pricing, FAQ, about ----

def who_cards() -> list[tuple[str, str, str]]:
    return [(a.path, a.crumb, a.benefit) for a in content.AUDIENCES.values()]


def job_links() -> list[tuple[str, str, str]]:
    return [(h.path, h.crumb, JOB_CARDS[h.slug]) for h in content.HUBS.values()]


def _qas(pairs) -> list[tuple[str, str]]:
    """(question, plain answer) for the FAQPage structured data from (question, answer, ...) tuples."""
    return [(_plain(str(fill(item[0]))), _plain(str(fill(item[1])))) for item in pairs]


def _register_content(path: str, name: str) -> None:
    seo.register(path, name, indexable=True, lastmod=CONTENT_DATE)


def _hub_page(hub: content.Hub):
    _register_content(hub.path, hub.h1)
    cities = [city.label for city in sitedata.known_cities() if city.known_for(hub.type_key)]

    def handler() -> Response:
        return render(
            "hub.html", meta=seo.page_meta(hub.title, hub.description, hub.path, robots=seo.robots_for(hub.path)),
            jsonld=[seo.product_offers(), seo.faq(_qas(hub.faqs))],
            crumbs=[("Home", "/"), (hub.crumb, hub.path)], final_cta=True,
            hub=hub, cities=cities, who_cards=who_cards())

    router.add_api_route(hub.path, handler, methods=["GET", "HEAD"], include_in_schema=False)


def _audience_page(aud: content.Audience):
    _register_content(aud.path, aud.h1)
    tier = next(t for t in content.TIERS if t[0] == aud.tier_key)

    def handler() -> Response:
        return render(
            "audience.html", meta=seo.page_meta(aud.title, aud.description, aud.path, robots=seo.robots_for(aud.path)),
            jsonld=[seo.faq(_qas(aud.faqs))],
            crumbs=[("Home", "/"), (aud.crumb, aud.path)],
            final_cta=True, aud=aud, tier=tier, job_links=job_links())

    router.add_api_route(aud.path, handler, methods=["GET", "HEAD"], include_in_schema=False)


for _hub in content.HUBS.values():
    _hub_page(_hub)
for _aud in content.AUDIENCES.values():
    _audience_page(_aud)

SAMPLE_PATH = "/sample-packet/"
SAMPLE_H1 = "Sample EV Charger Permit Packet (El Cajon, CA)"
_register_content(SAMPLE_PATH, SAMPLE_H1)


@router.api_route(SAMPLE_PATH, methods=["GET", "HEAD"], include_in_schema=False)
def sample_packet() -> Response:
    sheets = []
    for stem, number, title, _size, notes in content.SAMPLE_SHEETS:
        label = f"Sheet {number}: {title}" if number else title
        sheets.append({"stem": stem, "label": label, "title": title, "notes": notes})
    images = [seo.image_object(f"Sample EV charger permit packet, {sheet['label']}",
                               f"/assets/samples/{sheet['stem']}-1000.webp", sheet["notes"][0], 1000, 1294)
              for sheet in sheets]
    meta = seo.page_meta(
        "Sample EV Charger Permit Packet (El Cajon, CA)",
        "See a finished EV charger permit packet sheet by sheet: site plan, single-line diagram, load calculation and data sheet. El Cajon, CA.",
        SAMPLE_PATH, robots=seo.robots_for(SAMPLE_PATH))
    return render("sample.html", meta=meta, jsonld=images, crumbs=[("Home", "/"), ("Sample Packet", SAMPLE_PATH)],
                  final_cta=True, sheets=sheets, hubs=list(content.HUBS.values()))


PRICING_PATH = "/pricing/"
_register_content(PRICING_PATH, "Permit Packet Pricing")


@router.api_route(PRICING_PATH, methods=["GET", "HEAD"], include_in_schema=False)
def pricing() -> Response:
    meta = seo.page_meta(
        "Permit Packet Pricing: $39, $89 and $169 | Permit Packets",
        "Three packages: $39 load calc and panel audit, $89 complete permit packet, $169 city-checked within 24 hours. Free watermarked preview.",
        PRICING_PATH, robots=seo.robots_for(PRICING_PATH))
    return render("pricing.html", meta=meta, jsonld=[seo.product_offers(), seo.faq(_qas(content.PRICING_FAQS))],
                  crumbs=[("Home", "/"), ("Pricing", PRICING_PATH)], final_cta=True, faqs=content.PRICING_FAQS)


FAQ_PATH = "/faq/"
_register_content(FAQ_PATH, "Permit Packets FAQ")


def _faq_groups() -> list[tuple[str, str, list[tuple[str, str]]]]:
    """(heading, id, [(question, answer html)]). The hub and audience answers live on their own pages: here each
    gets a one-line summary and a link, so no answer is worded twice."""
    home = list(faq_data.FAQ)
    money = [qa for qa in home if qa[0] in ("How does payment work?", "Can I get a refund?")]
    general = [qa for qa in home if qa not in money]
    pricing_items = [(q, f'{short} <a href="{PRICING_PATH}">See pricing</a>.') for q, _a, short in content.PRICING_FAQS[:4]]
    by_job = [(q, f'{short} <a href="{hub.path}#faq">Details on the {hub.crumb} page</a>.')
              for hub in content.HUBS.values() for q, _a, short in hub.faqs]
    by_role = [(q, f'{short} <a href="{aud.path}#faq">Details for {aud.crumb.lower()}</a>.')
               for aud in content.AUDIENCES.values() for q, _a, short in aud.faqs]
    return [("General", "general", general), ("Pricing & refunds", "pricing", money + pricing_items),
            ("By job", "by-job", by_job), ("By role", "by-role", by_role)]


@router.api_route(FAQ_PATH, methods=["GET", "HEAD"], include_in_schema=False)
def faq_page() -> Response:
    groups = _faq_groups()
    meta = seo.page_meta(
        "Permit Packets FAQ: Pricing, Jobs, Cities | Permit Packets",
        "Answers about electrical permit packets: what is included, pricing and refunds, each job type and who it is for.",
        FAQ_PATH, robots=seo.robots_for(FAQ_PATH))
    qas = [(_plain(q), _plain(str(fill(a)))) for _h, _i, items in groups for q, a in items]
    return render("faq.html", meta=meta, jsonld=[seo.faq(qas)], crumbs=[("Home", "/"), ("FAQ", FAQ_PATH)],
                  final_cta=True, groups=groups)


ABOUT_PATH = "/about/"
_register_content(ABOUT_PATH, "About Permit Packets")


@router.api_route(ABOUT_PATH, methods=["GET", "HEAD"], include_in_schema=False)
def about() -> Response:
    meta = seo.page_meta(
        "About Permit Packets | Permit Packets",
        "Permit Packets is an automated drafting and NEC calculation tool by Lilos Growth. How packets are built and how city checklists are verified.",
        ABOUT_PATH, robots=seo.robots_for(ABOUT_PATH))
    cities = [{"label": city.label, "verified": city.last_verified, "url": city.website,
               "source": city.website_label or "Official source"} for city in sitedata.known_cities()]
    return render("about.html", meta=meta, jsonld=[seo.organization()], crumbs=[("Home", "/"), ("About", ABOUT_PATH)],
                  final_cta=True, build_steps=content.ABOUT_STEPS, cities=cities)


# ---- Placeholders: an H1 and "Coming soon", noindex until their content prompt ships ----

def _placeholder(path: str, h1: str, crumb: str, parents: list[tuple[str, str]] | None = None) -> None:
    title = f"{h1} | {seo.SITE_NAME}"
    seo.register(path, h1)

    def handler() -> Response:
        meta = seo.page_meta(title, f"{h1}. This page is coming soon.", path, robots=seo.robots_for(path))
        crumbs = [("Home", "/"), *(parents or []), (crumb, path)]
        return render("placeholder.html", meta=meta, h1=h1, crumbs=crumbs)

    router.add_api_route(path, handler, methods=["GET", "HEAD"], include_in_schema=False)


_placeholder("/permits/", "Electrical Permits by City", "Permits")

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
