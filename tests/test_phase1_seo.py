"""Phase 1 SEO, Schema.org, /compare/ hub, and programmatic location enrichments."""
import json
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import seo


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def _blocks(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_production_domain_and_vercel_redirects():
    assert seo.DEFAULT_BASE_URL == "https://myelectricalpermit.com"
    vercel = json.loads((Path(__file__).resolve().parents[1] / "vercel.json").read_text(encoding="utf-8"))
    sources = {r["has"][0]["value"]: r["destination"] for r in vercel["redirects"]}
    assert sources["permit-packet-consumer.vercel.app"] == "https://myelectricalpermit.com/$1"
    assert sources["www.myelectricalpermit.com"] == "https://myelectricalpermit.com/$1"
    headers = {h["key"]: h["value"] for h in vercel["headers"][0]["headers"]}
    assert headers["Referrer-Policy"] == "strict-origin-when-cross-origin"


def test_home_schema_includes_website_organization_and_product(client):
    types = {b["@type"] for b in _blocks(client.get("/").text)}
    assert {"WebSite", "Organization", "Product", "FAQPage"} <= types


def test_compare_hub_is_indexable_linked_and_in_sitemap(client):
    res = client.get("/compare/")
    assert res.status_code == 200
    assert '<meta name="robots" content="index,follow">' in res.text
    for slug in ("mysiteplan", "fiverr-drafters", "cad-drafter"):
        assert f'href="/compare/{slug}/"' in res.text
    assert "/compare/</loc>" in client.get("/sitemap-pages.xml").text
    assert "/compare/" in client.get("/llms.txt").text
    assert 'href="/compare/"' in client.get("/pricing/").text


def test_city_job_pages_have_service_schema_engineering_table_and_city_links(client):
    sf = client.get("/permits/ca/san-francisco/ev-charger/").text
    types = {b["@type"] for b in _blocks(sf)}
    assert {"BreadcrumbList", "FAQPage", "Service"} <= types
    assert "Local engineering &amp; utility parameters in San Francisco" in sf
    assert "Pacific Gas and Electric (PG&amp;E)" in sf
    assert 'href="/permits/ca/san-francisco/"' in sf
    assert 'href="/permits/ca/san-francisco/panel-upgrade/"' in sf
    assert 'href=""' not in sf


def test_robots_disallows_tool_and_compare_query_params(client):
    robots = client.get("/robots.txt").text
    assert "Disallow: /tools/*?" in robots
    assert "Disallow: /compare/*?" in robots
