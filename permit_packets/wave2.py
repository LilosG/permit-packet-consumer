"""Wave 2 routes: /tools/, /permit-documents/ and /compare/. One template per page type; copy is in wave2_content.py.
Imported at the bottom of pages.py's page definitions, which own the router, render() and the registry."""
from __future__ import annotations

import datetime

from fastapi.responses import JSONResponse, Response
from starlette.requests import Request

from permit_packets import calculators as calc_math
from permit_packets import seo
from permit_packets import wave2_content as w2
from permit_packets.pages import _plain, env, render, router

WAVE2_DATE = "2026-11-17"

CALC_RUN = {"ev-charger-load-calculator": (calc_math.EV_FIELDS, calc_math.ev_load),
            "residential-load-calculator": (calc_math.LOAD_FIELDS, calc_math.residential_load),
            "ev-charger-wire-breaker-size": (calc_math.WIRE_FIELDS, calc_math.wire_breaker), "subpanel-feeder-calculator": (calc_math.SUBPANEL_FIELDS, calc_math.subpanel_feeder), "solar-120-percent-rule-calculator": (calc_math.SOLAR_FIELDS, calc_math.solar_120_rule), "hot-tub-breaker-wire-size": (calc_math.HOT_TUB_FIELDS, calc_math.hot_tub_circuit)}


def calc_path(slug: str) -> str:
    return f"{w2.TOOLS_PATH}{slug}/"


def doc_path(slug: str) -> str:
    return f"{w2.DOCS_PATH}{slug}/"


def compare_path(slug: str) -> str:
    return f"/compare/{slug}/"


for _p, _n in [(w2.TOOLS_PATH, "Free Electrical Permit Calculators"), (w2.DOCS_PATH, "Permit Documents Explained"),
               *[(calc_path(s), c.h1) for s, c in w2.CALCS.items()],
               *[(doc_path(s), d.h1) for s, d in w2.DOCS.items()],
               *[(compare_path(s), c.h1) for s, c in w2.COMPARES.items()]]:
    seo.register(_p, _n, indexable=True, lastmod=WAVE2_DATE)

# Calculators that fit each job; used for the contextual links on job hubs, audience and city pages.
JOB_CALCS = {"ev-charger": ("ev-charger-load-calculator", "ev-charger-wire-breaker-size"),
             "panel-upgrade": ("residential-load-calculator", "solar-120-percent-rule-calculator"),
             "subpanel": ("subpanel-feeder-calculator", "residential-load-calculator"),
             "hot-tub-240v": ("hot-tub-breaker-wire-size", "residential-load-calculator")}
JOB_DOCS = ("site-plan", "single-line-diagram", "load-calculation", "panel-schedule", "equipment-cut-sheets")


def related_links(job: str = "") -> list[tuple[str, str, str]]:
    """(url, title, text) for the tools, document guides and articles that match a job. Every target is indexable."""
    from permit_packets.guides import guide_links_for_job
    slugs = JOB_CALCS.get(job) or tuple(w2.CALCS)
    items = [(calc_path(s), w2.CALCS[s].crumb, w2.CALCS[s].card) for s in slugs[:1 if job else 2]]
    items += [(doc_path(s), w2.DOCS[s].name, w2.DOCS[s].card) for s in JOB_DOCS[:1 if job else 4]]
    items += guide_links_for_job(job, limit=1 if job else 2)
    return items


env.globals["related_links"] = related_links


def _qas(pairs):
    return [(q, _plain(a)) for q, a in pairs]


# ---- Hubs ----

def _hub(path, title, description, h1, intro, items, crumb):
    def handler() -> Response:
        meta = seo.page_meta(title, description, path, robots=seo.robots_for(path))
        return render("card_hub.html", meta=meta, crumbs=[("Home", "/"), (crumb, path)], final_cta=True,
                      h1=h1, intro=intro, items=items)
    router.add_api_route(path, handler, methods=["GET", "HEAD"], include_in_schema=False)


_hub(w2.TOOLS_PATH, w2.TOOLS_TITLE, w2.TOOLS_DESCRIPTION, "Free Electrical Permit Calculators", w2.TOOLS_INTRO,
     [(calc_path(s), c.crumb, c.card) for s, c in w2.CALCS.items()], "Tools")
_hub(w2.DOCS_PATH, w2.DOCS_TITLE, w2.DOCS_DESCRIPTION, "Electrical Permit Documents Explained", w2.DOCS_INTRO,
     [(doc_path(s), d.name, d.card) for s, d in w2.DOCS.items()], "Permit Documents")

COMPARE_PATH = "/compare/"
COMPARE_TITLE = "Compare Permit Packets vs CAD & Site Plan Tools"
COMPARE_DESCRIPTION = (
    "Compare Permit Packets against CAD drafters, Fiverr freelancers, and site-plan-only services for residential electrical permits."
)
seo.register(COMPARE_PATH, "Compare Permit Packets", indexable=True, lastmod=WAVE2_DATE)
_hub(COMPARE_PATH, COMPARE_TITLE, COMPARE_DESCRIPTION, "Compare Permit Packets",
     "See how automated residential electrical permit packets compare to CAD drafters, freelance drafters, and site-plan-only services.",
     [(compare_path(s), c.h1, c.card) for s, c in w2.COMPARES.items()], "Comparisons")


# ---- Calculators ----

def _compute(slug: str, params) -> tuple[dict, list[str], dict | None]:
    fields, run = CALC_RUN[slug]
    values, errors = calc_math.parse(fields, params)
    result = None
    if not errors:
        try:
            result = run(values)
        except ValueError as error:
            errors.append(str(error))
    return values, errors, result


def _example(slug: str) -> dict:
    fields, run = CALC_RUN[slug]
    values, _ = calc_math.parse(fields, {})
    return {"inputs": values, "result": run(values), "fields": fields}


def _result_view(result: dict | None) -> dict | None:
    return None if result is None else {**result, "nec_rows": calc_math.nec_rows(result["nec"])}


def _start_cta(job: str, slug: str, params) -> str:
    extra = []
    for k, v in params.items():
        if slug == "subpanel-feeder-calculator" and k == "breaker_amps":
            extra.extend([f"sp_breaker_amps={v}", f"sp_subpanel_amps={v}"])
        elif slug == "hot-tub-breaker-wire-size" and k == "load_amps":
            extra.append(f"ac_nameplate_amps={v}")
        else:
            extra.append(f"{k}={v}")
    return f"/start/?job={job}&role=diy" + ("&" + "&".join(extra) if extra else "")


def _calculator(slug: str):
    c = w2.CALCS[slug]
    path = calc_path(slug)
    fields, _run = CALC_RUN[slug]

    def handler(request: Request) -> Response:
        params = request.query_params
        used = any(f.name in params for f in fields)
        values, errors, result = _compute(slug, params) if used else (calc_math.parse(fields, {})[0], [], None)
        example = _example(slug)
        faqs = list(c.faqs) + [("Is this an engineering calculation?", w2.DISCLAIMER)]
        meta = seo.page_meta(c.title, c.description, path, robots=seo.robots_for(path))
        return render("calculator.html", meta=meta, jsonld=[seo.webapp(c.h1, path), seo.faq(_qas(faqs))],
                      crumbs=[("Home", "/"), ("Tools", w2.TOOLS_PATH), (c.crumb, path)], final_cta=True,
                      c=c, path=path, slug=slug, fields=fields, values=values, errors=errors,
                      result=_result_view(result), used=used, example=example,
                      example_nec=calc_math.nec_rows(example["result"]["nec"]), faqs=faqs, disclaimer=w2.DISCLAIMER,
                      detached_labels=calc_math.DETACHED_LABELS, cta_href=_start_cta(c.job, slug, request.query_params))

    router.add_api_route(path, handler, methods=["GET", "HEAD"], include_in_schema=False)


for _slug in w2.CALCS:
    _calculator(_slug)


@router.get("/api/calc/{slug}", include_in_schema=False)
def calc_json(slug: str, request: Request) -> Response:
    """The same calculation as the page, as JSON for the page's script. Query values, one per field."""
    if slug not in CALC_RUN:
        return JSONResponse({"ok": False, "errors": ["Unknown calculator."]}, status_code=404)
    _values, errors, result = _compute(slug, request.query_params)
    if errors:
        return JSONResponse({"ok": False, "errors": errors}, status_code=422)
    return JSONResponse({"ok": True, "result": _result_view(result), "disclaimer": w2.DISCLAIMER},
                        headers={"Cache-Control": "no-store"})


# ---- Document guides ----

def _doc(slug: str):
    d = w2.DOCS[slug]
    path = doc_path(slug)
    calc = "residential-load-calculator" if slug in ("load-calculation", "panel-schedule") else ""

    def handler() -> Response:
        meta = seo.page_meta(d.title, d.description, path, robots=seo.robots_for(path))
        return render("doc.html", meta=meta, jsonld=[seo.article(d.h1, WAVE2_DATE, WAVE2_DATE), seo.faq(_qas(d.faqs))],
                      crumbs=[("Home", "/"), ("Permit Documents", w2.DOCS_PATH), (d.name, path)], final_cta=True,
                      d=d, calc=(calc_path(calc), w2.CALCS[calc].crumb) if calc else None,
                      others=[(doc_path(s), x.name, x.card) for s, x in w2.DOCS.items() if s != slug],
                      cta_href="/start/?job=ev-charger&role=diy")

    router.add_api_route(path, handler, methods=["GET", "HEAD"], include_in_schema=False)


for _slug in w2.DOCS:
    _doc(_slug)


# ---- Comparisons ----

def _compare(slug: str):
    c = w2.COMPARES[slug]
    path = compare_path(slug)

    def handler() -> Response:
        checked = datetime.date.fromisoformat(c.checked).strftime("%B %-d, %Y")
        meta = seo.page_meta(c.title, c.description, path, robots=seo.robots_for(path))
        return render("compare.html", meta=meta, jsonld=[seo.article(c.h1, c.checked, c.checked), seo.faq(_qas(c.faqs))],
                      crumbs=[("Home", "/"), ("Comparisons", COMPARE_PATH), (c.h1, path)], final_cta=True, c=c, checked=checked,
                      cta_href="/start/?job=ev-charger&role=diy",
                      others=[(compare_path(s), x.h1, x.card) for s, x in w2.COMPARES.items() if s != slug])

    router.add_api_route(path, handler, methods=["GET", "HEAD"], include_in_schema=False)


for _slug in w2.COMPARES:
    _compare(_slug)
