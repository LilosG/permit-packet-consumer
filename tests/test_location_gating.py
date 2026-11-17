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


# ---- the gate ----

def test_a_complete_city_job_is_indexable():
    assert locations.job_indexable(BELLEVUE, "ev-charger") and locations.missing_fields(BELLEVUE, "ev-charger") == []


@pytest.mark.parametrize("field,value", [
    ("permit_rules_verified", ""), ("permit_required", {}), ("nec_edition", ""), ("who_may_pull", ""), ("sources", ()),
])
def test_each_missing_field_gates_the_page(field, value):
    city = dataclasses.replace(BELLEVUE, **{field: value})
    assert field in locations.missing_fields(city, "ev-charger") and not locations.job_indexable(city, "ev-charger")


def test_fewer_than_three_checklist_items_gates_the_page():
    short = Checklist(items=BELLEVUE.checklists["ev_charger"].items[:2])
    city = dataclasses.replace(BELLEVUE, checklists={"ev_charger": short})
    assert "checklist" in locations.missing_fields(city, "ev-charger")


def test_permit_required_is_per_job():
    assert not locations.job_indexable(BELLEVUE, "hot-tub-240v")  # unconfirmed by an official source
    assert locations.indexable_jobs(BELLEVUE) == ["ev-charger", "panel-upgrade", "subpanel"]


def test_city_hub_needs_two_indexable_jobs():
    one = dataclasses.replace(BELLEVUE, permit_required={"ev_charger": True})
    two = dataclasses.replace(BELLEVUE, permit_required={"ev_charger": True, "subpanel": True})
    assert not locations.city_indexable(one) and locations.city_indexable(two)


def test_state_hub_and_permits_follow_their_cities(monkeypatch):
    assert locations.state_indexable("wa") and locations.state_indexable("ca") and locations.permits_indexable()
    assert not locations.state_indexable("az") and not locations.state_indexable("tn")
    monkeypatch.setattr(locations, "indexable_cities", lambda state=None: [])
    assert not locations.permits_indexable()


def test_unconfirmed_cities_are_gated():
    for key in ("chandler", "charlotte", "mesa", "nashville", "el cajon", "oro valley"):
        city = next(c for c in sitedata.known_cities() if c.name.lower() == key)
        assert not locations.city_indexable(city), key


# ---- noindex on gated pages, index on passing pages ----

GATED = ["/permits/az/", "/permits/tn/", "/permits/nc/charlotte/", "/permits/az/mesa/", "/permits/tn/nashville/ev-charger/",
         "/permits/az/chandler/panel-upgrade/", "/permits/wa/bellevue/hot-tub-240v/", "/permits/ca/el-cajon/ev-charger/"]


@pytest.mark.parametrize("path", GATED)
def test_gated_pages_are_noindex_and_out_of_sitemap_and_llms(client, path):
    page = client.get(path)
    assert page.status_code == 200 and '<meta name="robots" content="noindex,follow">' in page.text
    assert f"{path}</loc>" not in client.get("/sitemap-locations.xml").text and path not in client.get("/llms.txt").text


@pytest.mark.parametrize("path", [p for p, _ in locations.location_paths()])
def test_passing_pages_are_index_and_in_the_sitemap(client, path):
    page = client.get(path)
    assert page.status_code == 200 and '<meta name="robots" content="index,follow">' in page.text
    assert f"{path}</loc>" in client.get("/sitemap-locations.xml").text


def test_sitemap_locations_lastmod_is_rules_date(client):
    body = client.get("/sitemap-locations.xml").text
    entries = re.findall(r"<url><loc>[^<]+(/permits/[^<]*)</loc><lastmod>([^<]+)</lastmod></url>", body)
    assert len(entries) == len(locations.location_paths()) == 11
    assert {lastmod for _, lastmod in entries} == {BELLEVUE.rules_date, SF.rules_date}


# ---- no unverified city in any link ----

def test_no_link_anywhere_points_to_a_gated_location_page(client):
    pages = ["/", "/pricing/", "/faq/", "/about/", "/sample-packet/", "/for/diy-homeowners/"]
    pages += [job.url for job in sitedata.JOBS.values()] + [path for path, _ in locations.location_paths()]
    for path in pages:
        for link in hrefs(client.get(path).text):
            target = link.split("#")[0].split("?")[0]
            if target.startswith("/permits/"):
                assert locations.path_indexable(target), f"{path} links to the gated {link}"


def test_job_hubs_link_cities_only_when_indexable(client):
    html = client.get("/ev-charger-permit/").text
    assert 'href="/permits/wa/bellevue/ev-charger/"' in html and 'href="/permits/ca/san-francisco/ev-charger/"' in html
    assert "/permits/az/mesa/" not in html
    hot_tub = client.get("/hot-tub-240v-permit/").text
    main = hot_tub[hot_tub.index("<main"):hot_tub.index("</main>")]
    assert not [h for h in hrefs(main) if h.startswith("/permits/")]


def test_nav_and_footer_cities_are_the_indexable_ones(client):
    html = client.get("/pricing/").text
    assert ">All cities<" in html
    footer = html[html.index("<footer"):]
    assert {h for h in hrefs(footer) if h.startswith("/permits/")} == {"/permits/wa/bellevue/", "/permits/ca/san-francisco/"}


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
    assert 600 <= _words(html) <= 1000
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
