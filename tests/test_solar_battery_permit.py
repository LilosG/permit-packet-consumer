"""Phase 4: Residential Solar PV & Battery Storage (ESS) permit type, /solar-battery-permit/ hub & 120% rule checks."""
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets.job_types.solar_storage.calc import SolarStorageJob, build_solar_storage_packet
from permit_packets.core.load_calculation import HomeLoads
from permit_packets.jurisdictions import KNOWN, jurisdiction_by_key
from tests.packet_helpers import build, complete_inputs, packet_pages, sample


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def test_solar_battery_hub_and_city_pages_render(client):
    hub = client.get("/solar-battery-permit/")
    assert hub.status_code == 200
    assert "Solar PV &amp; Battery Storage Permit Plans" in hub.text
    city = client.get("/permits/ca/san-diego/solar-battery/")
    assert city.status_code == 200
    assert "Solar &amp; Battery Permit in San Diego, CA" in city.text


def test_solar_120_percent_busbar_and_ac_coupled_validation(client):
    over_bus = SolarStorageJob(
        customer="Test", address="123 Main St", contractor="Owner", license_number="",
        home=HomeLoads(square_feet=2000), service_amps=200, bus_amps=200, open_breaker_spaces=4,
        coupling="ac_coupled", pv_kw_dc=8.4, pv_breaker_amps=40, battery_kwh=13.5, battery_breaker_amps=30,
    )
    pkt = build_solar_storage_packet(over_bus)
    assert pkt.ready is False
    bad = client.post("/api/jobs/solar-battery/packet", json={**sample("solar_storage"), "coupling": "ac_coupled", "battery_breaker_amps": 0})
    assert bad.status_code == 422


def test_every_solar_packet_has_the_warning_labels_sheet():
    cities = [j for j in KNOWN.values() if "solar_storage" in j.checklists]
    assert cities
    for jurisdiction in cities:
        pages = packet_pages(build("solar_storage", complete_inputs("solar_storage", jurisdiction)).pdf)
        assert any("PV Warning Labels and Signage" in page for page in pages), jurisdiction.key
        assert any("reflective, weather-resistant material" in page for page in pages), jurisdiction.key


def test_only_san_diego_solar_packets_carry_the_general_notes_sheet():
    san_diego = jurisdiction_by_key("san-diego-ca")
    assert san_diego.solar_general_notes
    pages = packet_pages(build("solar_storage", complete_inputs("solar_storage", san_diego)).pdf)
    notes_page = next(page for page in pages if "General Notes" in page)
    flat = " ".join(notes_page.split())
    assert "General notes (City of San Diego Residential Solar PV Project Plan Template)" in flat
    for number, note in enumerate(san_diego.solar_general_notes, start=1):
        assert f"{number}. {note}" in flat, number

    other = jurisdiction_by_key("phoenix-az")
    other_pages = packet_pages(build("solar_storage", complete_inputs("solar_storage", other)).pdf)
    assert not any("General Notes" in page for page in other_pages)
