"""Wave 2: calculators, permit-document guides, comparisons, links, sitemap and parity with the packet engine."""
import json
import re

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import calculators as calc, locations, seo, wave2
from permit_packets import wave2_content as w2
from permit_packets.core.circuits import conduit_size, size_circuit
from permit_packets.core.load_calculation import HomeLoads, calculate_load
from permit_packets.job_types.ev_charger.calc import EvJob, build_ev_packet

CALC_PATHS = [wave2.calc_path(s) for s in w2.CALCS]
DOC_PATHS = [wave2.doc_path(s) for s in w2.DOCS]
CMP_PATHS = [wave2.compare_path(s) for s in w2.COMPARES]
HUBS = [w2.TOOLS_PATH, w2.DOCS_PATH]
NEW = HUBS + CALC_PATHS + DOC_PATHS + CMP_PATHS


@pytest.fixture
def client():
    return TestClient(app_module.app)


def blocks(html):
    return [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]


def test_new_pages_count():
    assert len(CALC_PATHS) == 6 and len(DOC_PATHS) == 5 and len(CMP_PATHS) == 3


@pytest.mark.parametrize("path", NEW)
def test_200_canonical_indexable_and_jsonld(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert f'<link rel="canonical" href="{seo.absolute(path)}">' in page.text
    assert '<meta name="robots" content="index,follow">' in page.text
    types = {b["@type"] for b in blocks(page.text)}  # every block parses
    assert "BreadcrumbList" in types
    if path in CALC_PATHS:
        assert {"WebApplication", "FAQPage"} <= types
    if path in DOC_PATHS + CMP_PATHS:
        assert "FAQPage" in types


@pytest.mark.parametrize("path", CALC_PATHS)
def test_calculator_page_has_disclaimer_cta_and_works_without_js(client, path):
    page = client.get(path)
    assert w2.DISCLAIMER in page.text and "/start/?job=" in page.text and "&amp;role=" in page.text
    assert 'method="get"' in page.text and "NEC sections applied" in page.text
    words = len(re.sub(r"<[^>]+>", " ", page.text.split("<main")[1].split("</main>")[0]).split())
    assert words >= 450
    # canonical stays the bare path with a query
    assert f'href="{seo.absolute(path)}"' in client.get(path + "?run_ft=50").text


def test_calculator_json_and_errors(client):
    ok = client.get("/api/calc/ev-charger-load-calculator?sq_ft=2000&service_amps=200&charger_amps=48").json()
    assert ok["ok"] and ok["result"]["computed_amps"] > 0 and ok["disclaimer"] == w2.DISCLAIMER
    assert client.get("/api/calc/ev-charger-load-calculator?sq_ft=abc").status_code == 422
    assert client.get("/api/calc/nope").status_code == 404
    assert "Enter a" not in client.get("/tools/ev-charger-load-calculator/").text.split('id="result"')[1][:200]
    assert "enter a number" in client.get("/tools/ev-charger-load-calculator/?sq_ft=abc").text


@pytest.mark.parametrize("sq_ft,service,charger,range_va,cooling", [(2000, 200, 48, 12000, 4800), (1200, 100, 32, 0, 0), (3500, 225, 80, 12000, 9600)])
def test_ev_load_parity_with_packet_engine(sq_ft, service, charger, range_va, cooling):
    values = {"sq_ft": sq_ft, "service_amps": service, "charger_amps": charger, "range_va": range_va, "dryer_va": 5000,
              "water_heater_va": 0, "heating_va": 0, "cooling_va": cooling}
    home = HomeLoads(square_feet=sq_ft, range_va=range_va, dryer_va=5000, cooling_va=cooling)
    packet = build_ev_packet(EvJob(customer="x", address="x", contractor="", license_number="", home=home, service_amps=service,
                                   open_breaker_spaces=2, charger_amps=charger, location="attached_garage", run_ft=30, trench_ft=0))
    result = calc.ev_load(values)
    assert result["computed_amps"] == round(packet.load.computed_amps, 1)
    assert result["spare_amps"] == round(packet.load.spare_amps, 1)
    assert [f"{l.va:,.0f} VA" for l in packet.load.lines] == [r[1] for r in result["rows"][:len(packet.load.lines)]]


def test_residential_load_parity_with_calculate_load():
    v = {"sq_ft": 2400, "service_amps": 150, "range_va": 12000, "dryer_va": 5000, "water_heater_va": 4500,
         "heating_va": 10000, "cooling_va": 6000, "hot_tub_or_pool_va": 6000}
    load = calculate_load(HomeLoads(square_feet=2400, range_va=12000, dryer_va=5000, water_heater_va=4500, heating_va=10000,
                                    cooling_va=6000, hot_tub_or_pool_va=6000), service_amps=150)
    result = calc.residential_load(v)
    assert result["computed_amps"] == round(load.computed_amps, 1) and result["spare_amps"] == round(load.spare_amps, 1)


@pytest.mark.parametrize("amps,run", [(48, 40), (32, 150), (80, 200)])
def test_wire_breaker_parity_with_packet_circuit(amps, run):
    packet = build_ev_packet(EvJob(customer="x", address="x", contractor="", license_number="", home=HomeLoads(square_feet=2000),
                                   service_amps=200, open_breaker_spaces=2, charger_amps=amps, location="attached_garage",
                                   run_ft=run, trench_ft=0))
    result = calc.wire_breaker({"charger_amps": amps, "run_ft": run, "detached": 0})
    assert (result["breaker"], result["wire"], result["ground"]) == (packet.circuit.breaker, packet.circuit.wire.size, packet.circuit.ground)
    assert ["EMT conduit (2 hots + ground)", conduit_size(size_circuit(amps, run, continuous=True), "EMT")] in result["rows"]


def test_sitemap_and_llms_include_every_new_page(client):
    sitemap = client.get("/sitemap-pages.xml").text
    llms = client.get("/llms.txt").text
    for path in NEW:
        assert f"<loc>{seo.absolute(path)}</loc><lastmod>2026-11-17</lastmod>" in sitemap
        assert seo.absolute(path) in llms


def internal_hrefs(html):
    return {h.split("#")[0].split("?")[0] for h in re.findall(r'href="(/[^"]*)"', html)} - {""}


def indexable_paths():
    return {e.path for e in seo.PAGES.values() if e.indexable} | {p for p, _ in locations.location_paths()}


def test_no_links_to_noindex_pages(client):
    allowed = indexable_paths() | {"/start/", "/find-order/", "/favicon.svg", "/favicon.ico", "/apple-touch-icon.png"}
    pages = NEW + ["/ev-charger-permit/", "/panel-upgrade-permit/", "/subpanel-permit/", "/hot-tub-240v-permit/",
                   "/for/electricians/", "/for/diy-homeowners/", "/permits/", "/"]
    for path in pages:
        for href in internal_hrefs(client.get(path).text):
            assert href in allowed or href.startswith(("/assets/", "/permits/")), (path, href)  # navigation links every hub


def test_header_footer_and_contextual_links(client):
    home = client.get("/").text
    assert 'href="/tools/"' in home and 'href="/permit-documents/"' in home
    ev = client.get("/ev-charger-permit/").text
    assert "/tools/ev-charger-load-calculator/" in ev and "/permit-documents/site-plan/" in ev
    assert "/tools/residential-load-calculator/" in client.get("/panel-upgrade-permit/").text
    assert "/tools/" in client.get("/for/electricians/").text
    # a city or job page that passes the gate links to its calculator; gated ones are placeholders with no such links
    for path, _ in locations.location_paths():
        if path.count("/") == 5:
            assert "/tools/" in client.get(path).text


def test_comparisons_state_date_and_source(client):
    mysite = client.get("/compare/mysiteplan/").text
    assert "November 17, 2026" in mysite and "https://www.mysiteplan.com/" in mysite and "better choice" in mysite
    for path in ("/compare/fiverr-drafters/", "/compare/cad-drafter/"):
        text = client.get(path).text
        assert "Category comparison" in text and "better choice" in text and "/start/?job=" in text
