"""Stage 2: /guides/ hub, 14 evergreen guides, 3 new NEC calculators, sitemaps, schema and internal linking."""
import json
import re

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import calculators as calc
from permit_packets import guides, seo
from permit_packets import guides_content as gc
from permit_packets.core.conductors import branch_conduit, feeder_conduit, size_branch, size_feeder, solar_fits

GUIDE_PATHS = [guides.guide_path(s) for s in gc.GUIDES]


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def _blocks(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_guides_hub_renders_and_links_every_guide(client):
    res = client.get("/guides/")
    assert res.status_code == 200
    assert len(re.findall(r"<h1[ >]", res.text)) == 1
    assert '<meta name="robots" content="index,follow">' in res.text
    assert f'<link rel="canonical" href="{seo.absolute("/guides/")}">' in res.text
    types = {b["@type"] for b in _blocks(res.text)}
    assert {"CollectionPage", "BreadcrumbList"} <= types
    for path in GUIDE_PATHS:
        assert f'href="{path}"' in res.text


@pytest.mark.parametrize("path", GUIDE_PATHS)
def test_every_guide_meets_seo_aeo_and_schema_standards(client, path):
    res = client.get(path)
    assert res.status_code == 200
    html = res.text
    assert len(re.findall(r"<h1[ >]", html)) == 1
    assert '<meta name="robots" content="index,follow">' in html
    assert f'<link rel="canonical" href="{seo.absolute(path)}">' in html
    title = re.search(r"<title>(.*?)</title>", html).group(1)
    assert len(title) <= 60, f"Title too long ({len(title)}): {title}"
    desc = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
    assert len(desc) <= 155, f"Description too long ({len(desc)}): {desc}"
    answer = re.search(r'class="answer">(.*?)</p>', html, re.S).group(1)
    answer_words = len(re.sub(r"<[^>]+>", "", answer).split())
    assert 40 <= answer_words <= 60, f"Answer block word count ({answer_words}) on {path}"
    main = re.sub(r"<script.*?</script>", "", re.search(r"<main.*?</main>", html, re.S).group(0), flags=re.S)
    words = len(re.sub(r"<[^>]+>", " ", main).split())
    assert words >= 550, f"Thin guide ({words} words) on {path}"
    types = {b["@type"] for b in _blocks(html)}
    assert {"Article", "FAQPage", "BreadcrumbList"} <= types
    slug = path.strip("/").split("/")[-1]
    if gc.GUIDES[slug].listicle_items:
        assert "ItemList" in types
    assert "/tools/" in main and "/start/?job=" in main


def test_sitemap_guides_and_llms_txt_include_all_guides(client):
    assert "/sitemap-guides.xml</loc>" in client.get("/sitemap.xml").text
    guides_xml = client.get("/sitemap-guides.xml").text
    llms = client.get("/llms.txt").text
    assert f"<loc>{seo.absolute('/guides/')}</loc>" in guides_xml
    for path in GUIDE_PATHS:
        assert f"<loc>{seo.absolute(path)}</loc>" in guides_xml
        assert seo.absolute(path) in llms


def test_no_orphaned_guides_and_bidirectional_linking(client):
    sources = ["/guides/", "/ev-charger-permit/", "/panel-upgrade-permit/", "/subpanel-permit/", "/hot-tub-240v-permit/"] + GUIDE_PATHS
    incoming: dict[str, int] = {p: 0 for p in GUIDE_PATHS}
    for src in sources:
        hrefs = set(re.findall(r'href="(/[^"#?]*)"', client.get(src).text))
        for target in GUIDE_PATHS:
            if target in hrefs and src != target:
                incoming[target] += 1
    for path, count in incoming.items():
        assert count >= 2, f"Guide {path} has too few incoming internal links ({count})"


def test_new_calculators_match_core_engineering_engine():
    sp = calc.subpanel_feeder({"breaker_amps": 100, "material": 0, "run_ft": 60, "conduit": 0, "detached": 1})
    expected_feeder = size_feeder(100, "aluminum", load_amps=80.0, one_way_ft=60)
    assert sp["wire"] == expected_feeder.conductor.size
    assert sp["ground"] == expected_feeder.egc
    assert sp["conduit"] == feeder_conduit(expected_feeder, "PVC")

    sol_pass = calc.solar_120_rule({"bus_amps": 200, "main_amps": 200, "pv_breaker_amps": 40})
    assert sol_pass["fits"] is solar_fits(200, 200, 40) is True
    sol_fail = calc.solar_120_rule({"bus_amps": 200, "main_amps": 200, "pv_breaker_amps": 50})
    assert sol_fail["fits"] is solar_fits(200, 200, 50) is False

    tub = calc.hot_tub_circuit({"load_amps": 36, "run_ft": 50, "terminals_75c": 1, "needs_neutral": 1})
    expected_branch = size_branch(breaker=45, load_amps=36, run_ft=50, terminals_75c=True)
    assert tub["breaker"] == 45
    assert tub["wire"] == expected_branch.wire.size
    assert tub["ground"] == expected_branch.egc
    assert branch_conduit(expected_branch, 3, "PVC") in tub["rows"][5][1]
