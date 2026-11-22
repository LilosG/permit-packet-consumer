"""Stage 3 SEO, rendering, schema, city hub, and calculator-prefill regression tests."""
import json
import re
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets import guides_content as gc


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def _blocks(html: str) -> list[dict]:
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_ev_hub_renders_html_links_without_escaping(client):
    html = client.get("/ev-charger-permit/").text
    assert "&lt;strong&gt;" not in html and "&lt;a " not in html
    assert 'href="/guides/what-is-an-appliance-cut-sheet-for-electrical-permit/"' in html


def test_sample_packet_renders_all_four_job_hub_cards(client):
    html = client.get("/sample-packet/").text
    for path in ("/ev-charger-permit/", "/panel-upgrade-permit/", "/subpanel-permit/", "/hot-tub-240v-permit/"):
        assert f'href="{path}"' in html


def test_guides_emit_article_og_type_and_main_entity_of_page(client):
    html = client.get("/guides/hot-tub-gfci-disconnect-wire-size-permit-guide/").text
    assert '<meta property="og:type" content="article">' in html
    art = next(b for b in _blocks(html) if b["@type"] == "Article")
    assert art["mainEntityOfPage"]["@id"].endswith("/guides/hot-tub-gfci-disconnect-wire-size-permit-guide/")
    assert len(gc.GUIDES) == 34


def test_city_hub_renders_local_utility_and_code_summary(client):
    html = client.get("/permits/ca/san-diego/").text
    assert "Local utility &amp; code summary" in html
    assert "San Diego Gas &amp; Electric (SDG&amp;E)" in html


def test_pricing_and_home_link_to_compare_hub(client):
    assert 'href="/compare/"' in client.get("/pricing/").text
    assert 'href="/compare/"' in client.get("/").text
