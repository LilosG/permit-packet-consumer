"""Prompt 1C: per-page indexing gate, noindex on gated pages, location sitemap, links and page content."""
import dataclasses
import json
import re

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import locations, sitedata
from permit_packets.jurisdictions import KNOWN, Checklist

BELLEVUE = KNOWN[("bellevue", "WA")]
SF = KNOWN[("san francisco", "CA")]


@pytest.fixture
def client():
    return TestClient(app_module.app)


def hrefs(html):
    return re.findall(r'href="([^"]+)"', html)


# ---- no gate: every known city with a state is indexable ----

def test_missing_fields_is_reporting_only():
    city = dataclasses.replace(BELLEVUE, permit_rules_verified="", last_verified="", who_may_pull="", sources=())
    assert {"permit_rules_verified", "who_may_pull", "sources"} <= set(locations.missing_fields(city, "ev-charger"))
    assert locations.job_indexable(city, "ev-charger") and locations.city_indexable(city)


def test_every_known_city_job_is_indexable():
    assert locations.MIN_JOBS_FOR_CITY_HUB == 1
    for city in sitedata.known_cities():
        assert locations.indexable_jobs(city) == list(sitedata.JOBS), city.key
        assert locations.city_indexable(city), city.key


def test_every_state_and_permits_are_indexable():
    states = set(sitedata.cities_by_state())
    assert {"az", "tn", "nc", "wa", "ca"} <= states
    assert set(locations.indexable_states()) == states and locations.permits_indexable()


def test_location_paths_cover_everything():
    paths = {p for p, _ in locations.location_paths()}
    cities = sitedata.known_cities()
    assert len(paths) == 1 + len(sitedata.cities_by_state()) + len(cities) * (1 + len(sitedata.JOBS))
    assert {"/permits/nc/charlotte/", "/permits/az/oro-valley/", "/permits/tn/", "/permits/tn/nashville/ev-charger/"} <= paths


# ---- every /permits/ page is index,follow, in the sitemap and in llms.txt ----

@pytest.mark.parametrize("path", [p for p, _ in locations.location_paths()])
def test_pages_are_index_and_in_the_sitemap_and_llms(client, path):
    page = client.get(path)
    assert page.status_code == 200 and '<meta name="robots" content="index,follow">' in page.text
    assert f"{path}</loc>" in client.get("/sitemap-locations.xml").text and path in client.get("/llms.txt").text


def test_sitemap_locations_lists_charlotte(client):
    assert "/permits/nc/charlotte/</loc>" in client.get("/sitemap-locations.xml").text


# ---- no unverified city in any link ----

ALL_CITY_HUBS = {"/permits/wa/bellevue/", "/permits/az/chandler/", "/permits/nc/charlotte/", "/permits/ca/el-cajon/",
                 "/permits/az/mesa/", "/permits/tn/nashville/", "/permits/az/oro-valley/", "/permits/ca/san-francisco/"}


def test_job_hubs_link_every_city_hub(client):
    html = client.get("/ev-charger-permit/").text
    assert 'href="/permits/wa/bellevue/ev-charger/"' in html and 'href="/permits/ca/san-francisco/ev-charger/"' in html
    assert 'href="/permits/az/mesa/ev-charger/"' in html
    hot_tub = client.get("/hot-tub-240v-permit/").text
    main = hot_tub[hot_tub.index("<main"):hot_tub.index("</main>")]
    linked = {h for h in hrefs(main) if h.startswith("/permits/")}
    assert {h + "hot-tub-240v/" for h in ALL_CITY_HUBS} <= linked


def test_nav_and_footer_link_all_cities_and_states(client):
    html = client.get("/pricing/").text
    assert ">All cities<" in html
    footer = html[html.index("<footer"):]
    links = {h for h in hrefs(footer) if h.startswith("/permits/")}
    assert ALL_CITY_HUBS <= links and {"/permits/az/", "/permits/ca/", "/permits/nc/", "/permits/tn/", "/permits/wa/"} <= links


@pytest.mark.parametrize("path", ["/permits/", "/permits/az/", "/permits/az/mesa/", "/permits/nc/charlotte/"])
def test_hubs_render_clean(client, path):
    html = client.get(path).text
    assert "Coming soon" not in html
    main = html[html.index("<main"):html.index("</main>")]
    assert "<td></td>" not in main and "Who may pull it" not in main


def test_city_hub_has_one_who_section_and_start_links(client):
    html = client.get("/permits/ca/san-francisco/").text
    assert html.count("Who may pull the permit") == 1 and "Code edition" in html
    mesa = client.get("/permits/az/mesa/").text
    assert "Who may pull the permit" not in mesa and "/start/?job=" in mesa and "city=mesa" in mesa


# ---- the pages themselves ----

def _words(html):
    main = re.sub(r"<script.*?</script>", "", re.search(r"<main.*?</main>", html, re.S).group(0), flags=re.S)
    return len(re.sub(r"<[^>]+>", " ", main).split())


def _blocks(html):
    return {b["@type"]: b for b in (json.loads(x) for x in re.findall(
        r'<script type="application/ld\+json">(.*?)</script>', html, re.S))}


@pytest.mark.parametrize("path", [p for p, _ in locations.location_paths() if p.count("/") == 5])
def test_job_page_content(client, path):
    html = client.get(path).text
    assert 400 <= _words(html) <= 1100
    assert f"/start/?job={path.split('/')[4]}" in html and "&amp;city=" in html or "&city=" in html
    assert "Official sources" in html and "Last verified" in html and "national model code" in html
    blocks = _blocks(html)
    assert {"BreadcrumbList", "FAQPage"} <= set(blocks) and len(blocks["FAQPage"]["mainEntity"]) >= 5
    assert len(re.search(r"<title>(.*?)</title>", html).group(1)) <= 60


def test_titles_and_descriptions_are_unique(client):
    titles, descriptions = set(), set()
    for path, _ in locations.location_paths():
        html = client.get(path).text
        title = re.search(r"<title>(.*?)</title>", html).group(1)
        description = re.search(r'<meta name="description" content="([^"]+)"', html).group(1)
        assert title not in titles and description not in descriptions, path
        titles.add(title)
        descriptions.add(description)


@pytest.mark.parametrize("path", ["/permits/", "/permits/wa/", "/permits/wa/bellevue/"])
def test_hubs_have_a_table_and_dataset_json_ld(client, path):
    html = client.get(path).text
    assert "<table" in html and "Dataset" in _blocks(html)


def test_page_text_comes_from_the_module(client):
    html = client.get("/permits/wa/bellevue/ev-charger/").text
    assert BELLEVUE.who_may_pull.split(".")[0] in html and BELLEVUE.nec_edition in html
    assert all(url in html for url in BELLEVUE.sources)


def test_fee_notes_never_invent_dollar_amounts():
    for city in sitedata.known_cities():
        assert "$" not in city.fee_note, city.key
