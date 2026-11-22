"""Stage 5: /llms-full.txt, city-hub FAQPage schema, calculator HowTo schema, doc/compare links & 40-city coverage."""
import json
import re
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets import sitedata


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def _blocks(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_llms_full_txt_served_and_excluded_from_sitemaps(client):
    assert "/llms-full.txt" in client.get("/llms.txt").text
    full = client.get("/llms-full.txt")
    assert full.status_code == 200
    assert "Complete Technical Reference" in full.text
    assert "Salt Lake City, UT" in full.text
    for sm in ("/sitemap.xml", "/sitemap-pages.xml", "/sitemap-locations.xml", "/sitemap-guides.xml"):
        assert "llms-full.txt" not in client.get(sm).text


def test_city_hubs_emit_faqpage_schema_and_render_answers(client):
    html = client.get("/permits/mn/minneapolis/").text
    types = {b["@type"] for b in _blocks(html)}
    assert {"Dataset", "FAQPage", "BreadcrumbList"} <= types
    assert "Electrical permit questions in Minneapolis" in html
    assert "Xcel Energy" in html


def test_calculators_emit_howto_and_webapp_schema(client):
    html = client.get("/tools/ev-charger-load-calculator/").text
    types = {b["@type"] for b in _blocks(html)}
    assert {"WebApplication", "HowTo", "FAQPage", "BreadcrumbList"} <= types


def test_doc_and_compare_pages_link_to_tools_guides_and_pricing(client):
    doc_html = client.get("/permit-documents/site-plan/").text
    assert 'href="/tools/conduit-fill-trench-depth-calculator/"' in doc_html
    assert 'href="/guides/ev-charger-trench-depth-conduit-rules-nec-300-5/"' in doc_html
    cmp_html = client.get("/compare/mysiteplan/").text
    assert 'href="/pricing/"' in cmp_html
    assert 'href="/guides/do-you-need-an-engineer-stamp-for-residential-electrical-permit/"' in cmp_html


def test_40_cities_registered_and_indexable(client):
    assert len(sitedata.known_cities()) == 40
    for path in ("/permits/fl/miami/", "/permits/mn/minneapolis/", "/permits/oh/columbus/", "/permits/ut/salt-lake-city/"):
        assert client.get(path).status_code == 200
        assert f"{path}</loc>" in client.get("/sitemap-locations.xml").text
