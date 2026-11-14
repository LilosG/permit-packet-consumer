"""The gap-blocking test: a complete packet for every city and job type must show nothing open.

For every jurisdiction in jurisdictions/ and every job type it has a checklist for, build a packet
from complete inputs (all fields filled, a library charger or panel, the panel's existing circuits,
the utility's fault current, a plan with a parcel number) and check that the packet could go to the
city as is. If a city adds a requirement the packet cannot show as Ready, or a check the packet cannot
pass, this test fails, and the fix is to teach the packet to show it, not to loosen the test.
"""
import importlib
import os
import pkgutil

import pypdfium2
import pytest
from fastapi.testclient import TestClient

import permit_packets.jurisdictions as jurisdictions_package
from app import app
from permit_packets.core.equipment import attachment_span
from permit_packets.job_types import REGISTRY
from permit_packets.jurisdictions import KNOWN, Jurisdiction
from tests.packet_helpers import build, complete_inputs, packet_pages

os.environ["DEMO_PASSWORD"] = "test-password"

# A checklist item the electrician submits to the utility rather than to the city shows "Send".
UTILITY_SECTIONS = {"utility"}
CASES = [(j, key) for j in KNOWN.values() for key in sorted(j.checklists)]
IDS = [f"{j.key}-{key}" for j, key in CASES]
SHEET_POINTS = {"letter": (612, 792), "tabloid": (1224, 792)}


@pytest.fixture(scope="module")
def client() -> TestClient:
    signed_in = TestClient(app)
    assert signed_in.post("/api/signin", json={"password": "test-password"}).status_code == 200
    return signed_in


def test_every_city_module_is_registered_so_it_cannot_dodge_this_test():
    found = []
    for module_info in pkgutil.iter_modules(jurisdictions_package.__path__):
        if module_info.name == "general":
            continue
        module = importlib.import_module(f"permit_packets.jurisdictions.{module_info.name}")
        found += [value for value in vars(module).values() if isinstance(value, Jurisdiction)]
    assert found, "no city modules found"
    assert {j.key for j in found} == {j.key for j in KNOWN.values()}


def test_every_city_has_a_checklist_for_a_registered_job_type():
    for jurisdiction in KNOWN.values():
        assert jurisdiction.checklists, jurisdiction.key
        assert set(jurisdiction.checklists) <= set(REGISTRY), jurisdiction.key


def _utility_items(jurisdiction: Jurisdiction, key: str) -> set[str]:
    return {r.item for r in jurisdiction.checklist_for(key).items if r.section in UTILITY_SECTIONS}


@pytest.mark.parametrize("jurisdiction,key", CASES, ids=IDS)
def test_a_complete_packet_shows_every_checklist_item_ready(jurisdiction, key):
    body = build(key, complete_inputs(key, jurisdiction)).body
    utility = _utility_items(jurisdiction, key)
    cities = {r.item for r in jurisdiction.checklist_for(key).items}
    shown = {row["item"]: row for row in body["checklist_status"]}
    assert cities <= set(shown), "the cover lists every requirement the city has"
    for item, row in shown.items():
        allowed = {"Ready", "Send"} if item in utility else {"Ready"}
        assert row["status"] in allowed, f"{jurisdiction.key}/{key}: '{item}' is {row['status']} ({row['where']})"


@pytest.mark.parametrize("jurisdiction,key", CASES, ids=IDS)
def test_a_complete_packet_passes_every_engineering_check(jurisdiction, key):
    body = build(key, complete_inputs(key, jurisdiction)).body
    failing = [f"{c['name']}: {c['result']}" for c in body["checks"] if not c["passed"]]
    assert not failing, f"{jurisdiction.key}/{key}: {failing}"
    assert body["ready"] is True
    names = {c["name"] for c in body["checks"]}
    assert {"Interrupting rating", "Panel schedule", "Existing GEC"} <= names


@pytest.mark.parametrize("jurisdiction,key", CASES, ids=IDS)
def test_every_sheet_has_the_title_block_address_and_signature_line(jurisdiction, key):
    payload = complete_inputs(key, jurisdiction)
    result = build(key, payload)
    pages = packet_pages(result.pdf)
    assert len(pages) == len(result.body["documents"])
    total = len(pages)
    for number, text in enumerate(pages, start=1):
        where = f"{jurisdiction.key}/{key} sheet {number}"
        assert payload["address"] in text, where
        assert f"E-{number}" in text and f"Page {number} of {total}" in text, where
        assert payload["contractor"] in text and payload["license_number"] in text, where
        assert "Prepared by" in text and "Signature" in text and "Date" in text, where
        assert "482-110-22-00" in text, f"{where}: parcel number"


@pytest.mark.parametrize("jurisdiction,key", CASES, ids=IDS)
def test_the_stamp_box_exists_when_the_city_reserves_one(jurisdiction, key):
    result = build(key, complete_inputs(key, jurisdiction))
    cover = packet_pages(result.pdf)[0]
    document = pypdfium2.PdfDocument(result.pdf)
    try:
        sides = [(r - l, t - b) for l, b, r, t in
                 (o.get_bounds() for o in document[0].get_objects() if o.type == pypdfium2.raw.FPDF_PAGEOBJ_PATH)]
    finally:
        document.close()
    if jurisdiction.stamp_box_in is None:
        assert "Reserved for city stamp" not in cover
        return
    assert "Reserved for city stamp" in cover
    side = jurisdiction.stamp_box_in * 72
    assert any(abs(w - side) < 2.5 and abs(h - side) < 2.5 for w, h in sides), "a true-size square is drawn"


@pytest.mark.parametrize("jurisdiction,key", CASES, ids=IDS)
def test_the_page_size_matches_the_cities_sheet_size(jurisdiction, key):
    result = build(key, complete_inputs(key, jurisdiction))
    assert result.body["sheet_size"] == jurisdiction.sheet_size
    span = attachment_span(result.pdf)
    document = pypdfium2.PdfDocument(result.pdf)
    try:
        attached = set(range(span[0], span[0] + span[1])) if span else set()
        sizes = {(round(p.get_width()), round(p.get_height())) for i, p in enumerate(document) if i not in attached}
    finally:
        document.close()
    assert sizes == {SHEET_POINTS[jurisdiction.sheet_size]}


@pytest.mark.parametrize("jurisdiction,key", CASES, ids=IDS)
def test_the_zip_route_is_refused_where_the_city_takes_one_pdf_only(client, jurisdiction, key):
    slug = REGISTRY[key].slug
    response = client.post(f"/api/jobs/{slug}/documents", json=complete_inputs(key, jurisdiction))
    if jurisdiction.single_pdf_only:
        assert response.status_code == 409
        assert response.headers["content-type"].startswith("application/json")
    else:
        assert response.status_code == 200 and response.headers["content-type"] == "application/zip"
    body = client.post(f"/api/jobs/{slug}/packet", json=complete_inputs(key, jurisdiction)).json()
    assert body["jurisdiction"]["single_pdf_only"] is jurisdiction.single_pdf_only


def test_the_test_would_catch_a_requirement_the_packet_cannot_show_as_ready(monkeypatch):
    """Guard: a section nobody taught the packet to show stays Open, so the checks above would fail."""
    from dataclasses import replace

    from permit_packets.jurisdictions import Checklist, Requirement
    from permit_packets.jurisdictions.mesa_az import MESA

    base = MESA.checklists["subpanel"]
    stricter = replace(MESA, checklists={**MESA.checklists, "subpanel": Checklist(
        items=(*base.items, Requirement("Structural letter for the new panel", "structural")),
        source_url=base.source_url, notes=base.notes)})
    monkeypatch.setitem(KNOWN, ("mesa", "AZ"), stricter)
    body = build("subpanel", complete_inputs("subpanel", stricter)).body
    row = next(r for r in body["checklist_status"] if r["item"].startswith("Structural letter"))
    assert row["status"] == "Open"
