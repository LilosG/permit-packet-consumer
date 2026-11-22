"""Guides hub (/guides/) and guide article pages (/guides/{slug}/)."""
from __future__ import annotations

from fastapi import HTTPException
from fastapi.responses import Response

from permit_packets import guides_content as gc
from permit_packets import seo
from permit_packets import wave2_content as w2
from permit_packets.pages import _plain, env, render, router

GUIDES_DATE = "2026-11-20"


def guide_path(slug: str) -> str:
    return f"{gc.GUIDES_PATH}{slug}/"


seo.register(gc.GUIDES_PATH, "Electrical Permit Guides & Checklists", indexable=True, lastmod=GUIDES_DATE, sitemap="guides")
for _slug, _guide in gc.GUIDES.items():
    seo.register(guide_path(_slug), _guide.h1, indexable=True, lastmod=GUIDES_DATE, sitemap="guides")


JOB_GUIDES: dict[str, tuple[str, ...]] = {
    "ev-charger": ("hardwired-vs-plug-in-ev-charger-permit", "best-48a-hardwired-ev-chargers-for-permits",
                   "how-to-check-if-panel-can-handle-ev-charger", "nec-220-82-vs-220-87-load-calculation",
                   "what-is-an-appliance-cut-sheet-for-electrical-permit",
                   "tesla-wall-connector-gen-3-cut-sheet-permit", "emporia-classic-ev-charger-cut-sheet-permit",
                   "wallbox-pulsar-plus-cut-sheet-permit", "ev-charger-permit-packet-checklist-for-homeowners", "how-much-does-an-electrical-permit-cost"),
    "panel-upgrade": ("subpanel-vs-200a-panel-upgrade", "best-200a-meter-main-combo-panels",
                      "utility-service-upgrade-rules-pge-srp-aps-duke-pse", "2023-nec-and-california-electrical-code-permit-guide", "do-you-need-an-engineer-stamp-for-residential-electrical-permit"),
    "subpanel": ("best-subpanel-sizes-detached-garage-workshop-adu", "subpanel-vs-200a-panel-upgrade",
                 "ev-charger-trench-depth-conduit-rules-nec-300-5", "how-to-read-electrical-panel-label-aic-bus-rating"),
    "hot-tub-240v": ("hot-tub-gfci-disconnect-wire-size-permit-guide", "heat-pump-mini-split-electrical-permit-mca-mocp",
                     "ev-charger-trench-depth-conduit-rules-nec-300-5", "2023-nec-and-california-electrical-code-permit-guide", "do-you-need-an-engineer-stamp-for-residential-electrical-permit"),
}


def guide_links_for_job(job: str = "", limit: int = 2) -> list[tuple[str, str, str]]:
    slugs = JOB_GUIDES.get(job) or (
        "hardwired-vs-plug-in-ev-charger-permit", "subpanel-vs-200a-panel-upgrade",
        "best-48a-hardwired-ev-chargers-for-permits", "7-reasons-electrical-permits-fail-plan-check",
    )
    return [(guide_path(s), gc.GUIDES[s].crumb, gc.GUIDES[s].card) for s in slugs[:limit] if s in gc.GUIDES]


env.globals["guide_links_for_job"] = guide_links_for_job


def _qas(pairs: tuple[tuple[str, str], ...]) -> list[tuple[str, str]]:
    return [(_plain(q), _plain(a)) for q, a in pairs]


def _collection_schema() -> dict:
    return {
        "@context": "https://schema.org", "@type": "CollectionPage",
        "name": gc.GUIDES_TITLE, "description": gc.GUIDES_DESCRIPTION,
        "url": seo.absolute(gc.GUIDES_PATH),
        "publisher": {"@type": "Organization", "name": "Lilos Growth", "url": "https://lilosgrowth.com"},
    }


def _item_list_schema(name: str, items: tuple[str, ...]) -> dict:
    return {
        "@context": "https://schema.org", "@type": "ItemList", "name": name,
        "itemListElement": [{"@type": "ListItem", "position": idx, "name": item} for idx, item in enumerate(items, start=1)],
    }


@router.api_route(gc.GUIDES_PATH, methods=["GET", "HEAD"], include_in_schema=False)
def guides_hub(category: str = "") -> Response:
    meta = seo.page_meta(gc.GUIDES_TITLE, gc.GUIDES_DESCRIPTION, gc.GUIDES_PATH, robots=seo.robots_for(gc.GUIDES_PATH))
    grouped = [
        {"key": cat_key, "label": cat_label, "desc": cat_desc,
         "guides": [(guide_path(g.slug), g.h1, g.card, g.slug) for g in gc.GUIDES.values() if g.category == cat_key]}
        for cat_key, (cat_label, cat_desc) in gc.CATEGORIES.items()
    ]
    active_cat = category if category in gc.CATEGORIES else ""
    return render("guides_hub.html", meta=meta, jsonld=[_collection_schema()],
                  crumbs=[("Home", "/"), ("Guides", gc.GUIDES_PATH)], final_cta=True,
                  h1=gc.GUIDES_TITLE, intro=gc.GUIDES_INTRO, categories=gc.CATEGORIES,
                  grouped=grouped, active_cat=active_cat)


@router.api_route(f"{gc.GUIDES_PATH}{{slug}}/", methods=["GET", "HEAD"], include_in_schema=False)
def guide_detail(slug: str) -> Response:
    g = gc.GUIDES.get(slug)
    if g is None:
        raise HTTPException(404)
    path = guide_path(slug)
    meta = seo.page_meta(g.title, g.description, path, robots=seo.robots_for(path), og_type="article")
    blocks: list[dict] = [seo.article(g.h1, GUIDES_DATE, GUIDES_DATE, path=path), seo.faq(_qas(g.faqs))]
    if g.listicle_items:
        blocks.append(_item_list_schema(g.h1, g.listicle_items))
    related_cards: list[tuple[str, str, str]] = []
    for t_slug in g.tool_links:
        if t_slug in w2.CALCS:
            related_cards.append((f"{w2.TOOLS_PATH}{t_slug}/", w2.CALCS[t_slug].crumb, w2.CALCS[t_slug].card))
    for d_slug in g.doc_links:
        if d_slug in w2.DOCS:
            related_cards.append((f"{w2.DOCS_PATH}{d_slug}/", w2.DOCS[d_slug].name, w2.DOCS[d_slug].card))
    for r_slug in g.related_slugs:
        if r_slug in gc.GUIDES:
            related_cards.append((guide_path(r_slug), gc.GUIDES[r_slug].crumb, gc.GUIDES[r_slug].card))
    return render("guide.html", meta=meta, jsonld=blocks,
                  crumbs=[("Home", "/"), ("Guides", gc.GUIDES_PATH), (g.crumb, path)], final_cta=True,
                  g=g, cat_label=gc.CATEGORIES[g.category][0], cta_href=f"/start/?job={g.job}&role={g.role}",
                  related_cards=related_cards)
