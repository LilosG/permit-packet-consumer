"""Phase 3: Standby generator interlock & transfer switch permit type, /generator-permit/ hub & calculator."""
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets.job_types.generator.calc import GeneratorJob, build_generator_packet
from permit_packets.core.load_calculation import HomeLoads
from tests.packet_helpers import sample


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
