"""Phase 3: Standby generator interlock & transfer switch permit type, /generator-permit/ hub & calculator."""
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets.job_types.generator.calc import GeneratorJob, build_generator_packet
from permit_packets.core.load_calculation import HomeLoads
from permit_packets.jurisdictions import KNOWN, jurisdiction_by_key
from tests.packet_helpers import build, complete_inputs, packet_pages, sample


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def test_generator_hub_and_calculator_render(client):
    hub = client.get("/generator-permit/")
    assert hub.status_code == 200
    assert "Generator Interlock &amp; Transfer Switch Permit Plans" in hub.text
    calc = client.get("/tools/generator-interlock-wire-calculator/")
    assert calc.status_code == 200
    assert "NEC 702" in calc.text


def test_generator_neutral_and_interlock_validation(client):
    bonded = GeneratorJob(
        customer="Test", address="123 Main St", contractor="Owner", license_number="",
        home=HomeLoads(square_feet=2000), service_amps=200, open_breaker_spaces=4,
        transfer_type="interlock", generator_kw=9.5, inlet_amps=50, neutral_type="bonded",
    )
    pkt = build_generator_packet(bonded)
    assert pkt.ready is False
    bad = client.post("/api/jobs/generator/packet", json={**sample("generator"), "transfer_type": "interlock", "inlet_amps": 100})
    assert bad.status_code == 422


def test_dallas_generator_fuel_type_shows_on_the_one_line_and_the_checklist():
    dallas = jurisdiction_by_key("dallas-tx")
    payload = complete_inputs("generator", dallas)
    assert payload["fuel_type"] == "natural_gas"
    result = build("generator", payload)
    assert any("Fuel: Natural gas" in page for page in packet_pages(result.pdf))
    row = next(r for r in result.body["checklist_status"] if r["item"].startswith("Fuel type listed"))
    assert row["status"] == "Ready" and "fuel type on the one-line" in row["where"]

    payload.pop("fuel_type")
    body = build("generator", payload).body
    row = next(r for r in body["checklist_status"] if r["item"].startswith("Fuel type listed"))
    assert row["status"] == "Open"


def test_every_generator_packet_has_the_equipment_layout_sheet():
    cities = [j for j in KNOWN.values() if "generator" in j.checklists]
    assert cities
    for jurisdiction in cities:
        pages = packet_pages(build("generator", complete_inputs("generator", jurisdiction)).pdf)
        assert any("Equipment Layout and Working Space" in page for page in pages), jurisdiction.key
        assert any("NEC 110.26 working space" in page for page in pages), jurisdiction.key
