"""Stage 6: Responsive srcset/LCP images, Google Image Sitemap, ItemList hubs, og:image:alt & 30 guides."""
import json
import re
import pytest
from fastapi.testclient import TestClient
import app as app_module


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def _blocks(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_sample_and_home_use_responsive_srcset_and_lcp_hints(client):
    sample = client.get("/sample-packet/").text
    assert 'srcset="/assets/samples/01-cover-300.webp 300w, /assets/samples/01-cover-1000.webp 1000w, /assets/samples/01-cover-2000.webp 2000w"' in sample
    assert 'fetchpriority="high"' in sample
    home = client.get("/").text
    assert 'srcset="/assets/samples/02-site-plan-300.webp 300w, /assets/samples/02-site-plan-1000.webp 1000w"' in home


def test_sitemap_pages_includes_google_image_extensions_for_sample_packet(client):
    xml = client.get("/sitemap-pages.xml").text
    assert 'xmlns:image="http://www.google.com/schemas/sitemap-image/1.1"' in xml
    assert "<image:loc>https://myelectricalpermit.com/assets/samples/02-site-plan-2000.webp</image:loc>" in xml


def test_og_image_alt_and_theme_color_present(client):
    html = client.get("/").text
    assert '<meta name="theme-color" content="#1d4ed8">' in html
    assert '<meta property="og:image:alt"' in html
    assert '<meta name="twitter:image:alt"' in html


def test_directory_hubs_emit_itemlist_jsonld(client):
    for hub in ("/tools/", "/permit-documents/", "/compare/"):
        types = {b["@type"] for b in _blocks(client.get(hub).text)}
        assert {"ItemList", "BreadcrumbList"} <= types, hub


def test_guides_hub_has_search_and_category_counts(client):
    html = client.get("/guides/").text
    assert 'id="guide-search"' in html
    assert "All (30)" in html
