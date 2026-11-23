"""Phase 4: Residential Solar PV & Battery Storage (ESS) permit type, /solar-battery-permit/ hub & 120% rule checks."""
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets.job_types.solar_storage.calc import SolarStorageJob, build_solar_storage_packet
from permit_packets.core.load_calculation import HomeLoads
from tests.packet_helpers import sample


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
