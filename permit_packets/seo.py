"""SEO plumbing in one place: head tags, JSON-LD, the indexable-page registry, sitemaps, llms.txt, analytics.

THE INDEXABLE REGISTRY is `PAGES` below. A page is in a sitemap and in /llms.txt only when its entry has
indexable=True. A content prompt that ships a page flips that one flag (and sets its content date).
City, state and job pages under /permits/ are generated from the jurisdiction modules; they enter
/sitemap-locations.xml page by page: permit_packets/locations.py holds the gating rules.
"""
from __future__ import annotations

import html
import json
import logging
import os
import re
from dataclasses import dataclass
from xml.sax.saxutils import escape

from markupsafe import Markup

log = logging.getLogger("permit_packets")

SITE_NAME = "Permit Packets"
DEFAULT_BASE_URL = "https://myelectricalpermit.com"
DEFAULT_OG_IMAGE = "/assets/samples/02-site-plan-og.jpg"
AUTHOR = "Permit Packets by Lilos Growth"
TITLE_MAX = 60
DESCRIPTION_MAX = 155

# The homepage description: also the one-line description in /llms.txt.
HOME_TITLE = "Electrical Permit Packet Generator: Plans & Load Calcs"
HOME_DESCRIPTION = (
    "Generate a residential electrical permit packet from one address: site plan, single-line diagram, "
    "load calc and cut sheets. Free watermarked preview.")

# Each package and its price. The order page and the schema.org offers read these.
TIER_PRICES = {"load_calc": 39, "instant_packet": 89, "city_checked_24h": 169}
TIER_NAMES = {
    "load_calc": "Load Calc & Panel Audit",
    "instant_packet": "Instant Permit Packet",
    "city_checked_24h": "24-Hour City-Checked Packet",
}


def public_base_url() -> str:
    """The site's public address, for canonical, social and sitemap URLs."""
    return os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/") or DEFAULT_BASE_URL


def absolute(path_or_url: str) -> str:
    return path_or_url if re.match(r"^https?://", path_or_url) else f"{public_base_url()}{path_or_url}"


def canonical_path(path: str) -> str:
    """A path with a leading and a trailing slash (files such as /llms.txt are left alone)."""
    path = "/" + path.lstrip("/")
    return path if path.endswith("/") or "." in path.rsplit("/", 1)[-1] else path + "/"


# ---- Head tags ----

def page_meta(title: str, description: str, path: str, robots: str = "index,follow",
              og_image: str = DEFAULT_OG_IMAGE, og_type: str = "website") -> Markup:
    """Every head tag a page needs: title, description, canonical, robots, Open Graph and Twitter.

    The canonical is PUBLIC_BASE_URL plus the path with a trailing slash. A title over 60 characters or a
    description over 155 is logged as a warning (search results cut them off)."""
    if len(title) > TITLE_MAX:
        log.warning("SEO title is %d characters (max %d): %s", len(title), TITLE_MAX, title)
    if len(description) > DESCRIPTION_MAX:
        log.warning("SEO description is %d characters (max %d) on %s", len(description), DESCRIPTION_MAX, path)
    canonical = absolute(canonical_path(path))
    image = absolute(og_image)
    q = lambda value: html.escape(value, quote=True)  # noqa: E731
    tags = [
        f"<title>{html.escape(title)}</title>",
        f'<meta name="description" content="{q(description)}">',
        f'<link rel="canonical" href="{q(canonical)}">',
        f'<meta name="robots" content="{q(robots)}">',
        f'<meta property="og:title" content="{q(title)}">',
        f'<meta property="og:description" content="{q(description)}">',
        f'<meta property="og:type" content="{q(og_type)}">',
        f'<meta property="og:url" content="{q(canonical)}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:image" content="{q(image)}">',
        '<meta name="twitter:card" content="summary_large_image">',
        f'<meta name="twitter:title" content="{q(title)}">',
        f'<meta name="twitter:description" content="{q(description)}">',
        f'<meta name="twitter:image" content="{q(image)}">',
    ]
    return Markup("\n".join(tags))


def verification_tags() -> Markup:
    """Search console ownership tags, from GOOGLE_SITE_VERIFICATION and BING_SITE_VERIFICATION. Homepage only."""
    tags = []
    google = os.environ.get("GOOGLE_SITE_VERIFICATION", "").strip()
    bing = os.environ.get("BING_SITE_VERIFICATION", "").strip()
    if google:
        tags.append(f'<meta name="google-site-verification" content="{html.escape(google, quote=True)}">')
    if bing:
        tags.append(f'<meta name="msvalidate.01" content="{html.escape(bing, quote=True)}">')
    return Markup("\n".join(tags))


# ---- JSON-LD ----

def website() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "WebSite",
        "name": "MyElectricalPermit",
        "alternateName": SITE_NAME,
        "url": absolute("/"),
        "publisher": {"@type": "Organization", "name": "Lilos Growth", "url": "https://lilosgrowth.com"},
    }


def organization() -> dict:
    return {
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": SITE_NAME,
        "url": absolute("/"),
        "logo": absolute("/apple-touch-icon.png"),
        "email": "hello@myelectricalpermit.com",
        "parentOrganization": {"@type": "Organization", "name": "Lilos Growth", "url": "https://lilosgrowth.com"},
    }


def breadcrumb(items: list[tuple[str, str]]) -> dict:
    """BreadcrumbList from (name, url) pairs. A relative url becomes absolute."""
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": position, "name": name, "item": absolute(url)}
        for position, (name, url) in enumerate(items, start=1)]}


def faq(qas: list[tuple[str, str]]) -> dict:
    """FAQPage from (question, plain-text answer) pairs."""
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": question, "acceptedAnswer": {"@type": "Answer", "text": answer}}
        for question, answer in qas]}


def tier_offers() -> list[dict]:
    return [
        {"@type": "Offer", "name": TIER_NAMES[tier], "price": str(price), "priceCurrency": "USD",
         "url": absolute(f"/start/?tier={price}")}
        for tier, price in TIER_PRICES.items()]


def product_offers() -> dict:
    """The three packages as one Product with an AggregateOffer."""
    prices = list(TIER_PRICES.values())
    return {"@context": "https://schema.org", "@type": "Product", "name": SITE_NAME,
            "brand": {"@type": "Brand", "name": SITE_NAME},
            "offers": {"@type": "AggregateOffer", "priceCurrency": "USD", "lowPrice": str(min(prices)),
                       "highPrice": str(max(prices)), "offerCount": len(prices), "offers": tier_offers()}}


def service(name: str, area_name: str, offers: list[dict] | None = None) -> dict:
    data = {"@context": "https://schema.org", "@type": "Service", "name": name,
            "provider": {"@type": "Organization", "name": "Lilos Growth", "url": "https://lilosgrowth.com"},
            "areaServed": {"@type": "AdministrativeArea", "name": area_name}}
    if offers:
        data["offers"] = offers
    return data


def article(headline: str, date_published: str, date_modified: str, author: str = AUTHOR,
            path: str = "", image: str = DEFAULT_OG_IMAGE) -> dict:
    data: dict = {
        "@context": "https://schema.org", "@type": "Article", "headline": headline,
        "datePublished": date_published, "dateModified": date_modified,
        "image": [absolute(image)],
        "author": {"@type": "Organization", "name": author},
        "publisher": {"@type": "Organization", "name": "Lilos Growth", "url": "https://lilosgrowth.com"},
    }
    if path:
        data["mainEntityOfPage"] = {"@type": "WebPage", "@id": absolute(canonical_path(path))}
    return data


def webapp(name: str, url: str) -> dict:
    return {"@context": "https://schema.org", "@type": "WebApplication", "name": name, "url": absolute(url),
            "applicationCategory": "BusinessApplication", "operatingSystem": "Any"}


def image_object(name: str, url: str, caption: str, width: int, height: int) -> dict:
    return {"@context": "https://schema.org", "@type": "ImageObject", "name": name, "caption": caption,
            "contentUrl": absolute(url), "encodingFormat": "image/webp", "width": width, "height": height}


def jsonld_script(data: dict) -> str:
    """One <script type="application/ld+json"> tag. "<" is escaped so no text can close the tag."""
    return ('<script type="application/ld+json">'
            + json.dumps(data, ensure_ascii=False).replace("<", "\\u003c") + "</script>")


def jsonld_scripts(blocks: list[dict]) -> Markup:
    return Markup("\n".join(jsonld_script(block) for block in blocks))


# ---- The indexable registry ----

@dataclass(frozen=True)
class PageEntry:
    path: str
    title: str  # the name shown in /llms.txt
    indexable: bool = False  # True: in the sitemap and /llms.txt, and served as index,follow
    lastmod: str = ""  # ISO date the page's content last changed. Never the build time.
    sitemap: str = "pages"  # "pages" or "guides"


PAGES: dict[str, PageEntry] = {}


def register(path: str, title: str, *, indexable: bool = False, lastmod: str = "", sitemap: str = "pages") -> PageEntry:
    entry = PageEntry(canonical_path(path), title, indexable, lastmod, sitemap)
    PAGES[entry.path] = entry
    return entry


def robots_for(path: str) -> str:
    """index,follow for a registered indexable page; noindex,follow for everything still a placeholder."""
    entry = PAGES.get(canonical_path(path))
    return "index,follow" if entry and entry.indexable else "noindex,follow"


# ---- Sitemaps and llms.txt ----

def _url_entry(path: str, lastmod: str = "") -> str:
    stamp = f"<lastmod>{escape(lastmod)}</lastmod>" if lastmod else ""
    return f"  <url><loc>{escape(absolute(path))}</loc>{stamp}</url>\n"


def _urlset(entries: list[str]) -> str:
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(entries) + "</urlset>\n")


def sitemap_index() -> str:
    """The index lists a child sitemap only when it holds at least one URL."""
    children = (("sitemap-pages.xml", sitemap_pages()), ("sitemap-locations.xml", sitemap_locations()),
                ("sitemap-guides.xml", sitemap_guides()))
    body = "".join(f"  <sitemap><loc>{escape(absolute('/' + name))}</loc></sitemap>\n"
                   for name, xml in children if "<url>" in xml)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<sitemapindex xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</sitemapindex>\n")


def _registered(kind: str) -> list[PageEntry]:
    return [entry for entry in PAGES.values() if entry.indexable and entry.sitemap == kind]


def sitemap_pages() -> str:
    return _urlset([_url_entry(entry.path, entry.lastmod) for entry in _registered("pages")])


def sitemap_guides() -> str:
    return _urlset([_url_entry(entry.path, entry.lastmod) for entry in _registered("guides")])


def sitemap_locations() -> str:
    from permit_packets import locations
    return _urlset([_url_entry(path, lastmod) for path, lastmod in locations.location_paths()])


def robots_txt() -> str:
    return (
        "User-agent: *\n"
        "Allow: /\n"
        "Disallow: /admin\n"
        "Disallow: /api/\n"
        "Disallow: /order/\n"
        "Disallow: /start/?\n"
        "Disallow: /tools/*?\n"
        "Disallow: /compare/*?\n\n"
        f"Sitemap: {public_base_url()}/sitemap.xml\n"
    )


def llms_txt() -> str:
    indexable = [entry for entry in PAGES.values() if entry.indexable]
    generators = [e for e in indexable if e.path in (
        "/", "/ev-charger-permit/", "/panel-upgrade-permit/", "/subpanel-permit/", "/hot-tub-240v-permit/",
        "/sample-packet/", "/pricing/"
    )]
    audiences = [e for e in indexable if e.path.startswith("/for/")]
    tools = [e for e in indexable if e.path.startswith("/tools/")]
    docs = [e for e in indexable if e.path.startswith("/permit-documents/")]
    compares = [e for e in indexable if e.path.startswith("/compare/")]
    guides = [e for e in indexable if e.sitemap == "guides"]
    categorized = {e.path for e in generators + audiences + tools + docs + compares + guides}
    other = [e for e in indexable if e.path not in categorized]

    lines = [f"# {SITE_NAME} (MyElectricalPermit)", "", f"> {HOME_DESCRIPTION}"]
    sections = [
        ("Core Permit Generators & Pricing", generators),
        ("Who It's For", audiences),
        ("Free NEC Electrical Calculators", tools),
        ("Electrical Permit Document Guides", docs),
        ("Comparisons", compares),
        ("Guides & Checklists", guides),
        ("Company & Policies", other),
    ]
    for heading, entries in sections:
        if entries:
            lines += ["", f"## {heading}", ""]
            lines += [f"- [{entry.title}]({absolute(entry.path)})" for entry in entries]

    from permit_packets import locations
    loc_paths = locations.location_paths()
    if loc_paths:
        lines += ["", "## City & State Electrical Permit Rules", ""]
        lines += [f"- [{path}]({absolute(path)})" for path, _ in loc_paths]
    return "\n".join(lines) + "\n"


# ---- Conversion tracking ----

def ga_measurement_id() -> str:
    value = os.environ.get("GA4_MEASUREMENT_ID", "").strip().upper()
    return value if re.fullmatch(r"G-[A-Z0-9]{4,20}", value) else ""


def ga_snippet(redact_path: str | None = None) -> Markup:
    """The gtag loader, when GA4_MEASUREMENT_ID is set. Left out of /admin by simply not being included there."""
    measurement = ga_measurement_id()
    if not measurement:
        return Markup("")
    config = (
        f"gtag('config','{measurement}',{{'page_location':location.origin+'{redact_path}'}});"
        if redact_path
        else f"gtag('config','{measurement}');"
    )
    return Markup(
        f'<script async src="https://www.googletagmanager.com/gtag/js?id={measurement}"></script>\n'
        "<script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}"
        f"gtag('js',new Date());{config}</script>")


def dataset(name: str, description: str, path: str, date_modified: str, keywords: list[str],
            places: list[str]) -> dict:
    """Dataset JSON-LD for a page whose main content is a table of verified permit facts."""
    return {"@context": "https://schema.org", "@type": "Dataset", "license": "https://creativecommons.org/licenses/by/4.0/", "name": name, "description": description,
            "url": absolute(canonical_path(path)), "dateModified": date_modified, "keywords": keywords,
            "isAccessibleForFree": True, "creator": {"@type": "Organization", "name": AUTHOR},
            "spatialCoverage": [{"@type": "Place", "name": place} for place in places]}
