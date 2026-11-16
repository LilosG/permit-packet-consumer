"""Per-IP hourly limits on the property lookups and the free preview builds."""
import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app


@pytest.fixture(autouse=True)
def clean_counts():
    app_module._hits.clear()
    yield
    app_module._hits.clear()


def test_preview_builds_stop_at_the_limit_with_a_friendly_429(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PREVIEW", "2")
    client = TestClient(app)
    for _ in range(2):  # an empty body fails validation (422) but still counts as a use
        assert client.post("/api/public/preview/ev-charger", json={}).status_code == 422
    blocked = client.post("/api/public/preview/ev-charger", json={})
    assert blocked.status_code == 429
    assert "try again" in blocked.json()["detail"].lower()
    assert int(blocked.headers["retry-after"]) > 0


def test_each_ip_has_its_own_allowance(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PROPERTY", "1")
    client = TestClient(app)
    body = {"address": "10 Main", "job_type": "nope"}
    assert client.post("/api/property", json=body, headers={"x-real-ip": "1.1.1.1"}).status_code == 422
    assert client.post("/api/property", json=body, headers={"x-real-ip": "1.1.1.1"}).status_code == 429
    assert client.post("/api/property", json=body, headers={"x-real-ip": "2.2.2.2"}).status_code == 422


def test_property_routes_share_one_allowance(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PROPERTY", "1")
    client = TestClient(app)
    assert client.post("/api/property/aerial", json={}).status_code == 422
    assert client.post("/api/property", json={}).status_code == 429


def test_the_limit_can_be_switched_off(monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_SUGGEST", "0")
    client = TestClient(app)
    for _ in range(5):
        assert client.post("/api/property/suggest", json={}).status_code == 422
