"""Item 4: available fault current and interrupting rating, on every job type."""
from pathlib import Path

import pytest

from permit_packets.job_types import REGISTRY
from tests.packet_helpers import build, packet_pages, sample

ALL = sorted(REGISTRY)
STATIC = Path(__file__).parent.parent / "permit_packets" / "static"


def _without_fault_current(key: str) -> dict:
    payload = sample(key)
    payload.pop("available_fault_current_a", None)
    return payload


def _check(body: dict) -> dict:
    return next(check for check in body["checks"] if check["name"] == "Interrupting rating")


@pytest.mark.parametrize("key", ALL)
def test_a_rating_at_or_above_the_available_current_passes(key):
    for fault, aic in ((9_999, 10), (10_000, 10), (22_000, 25)):
        body = build(key, {**sample(key), "available_fault_current_a": fault, "equipment_aic_ka": aic}).body
        assert _check(body)["passed"] is True, (fault, aic)
        assert "110.9" in _check(body)["result"]


@pytest.mark.parametrize("key", ALL)
def test_a_rating_below_the_available_current_fails_and_blocks_the_packet(key):
    body = build(key, {**sample(key), "available_fault_current_a": 14_000, "equipment_aic_ka": 10}).body
    assert _check(body)["passed"] is False
    assert "14 kA or more" in _check(body)["result"]
    assert body["ready"] is False


@pytest.mark.parametrize("key", ALL)
def test_a_missing_fault_current_says_so_and_the_packet_is_not_ready(key):
    body = build(key, _without_fault_current(key)).body
    assert _check(body) == {
        "name": "Interrupting rating", "result": "Enter the utility's available fault current", "passed": False}
    assert body["ready"] is False


@pytest.mark.parametrize("key", ALL)
def test_the_aic_defaults_to_10_ka(key):
    body = build(key, {**sample(key), "available_fault_current_a": 8_000}).body
    assert "10 kA" in _check(body)["result"]


@pytest.mark.parametrize("key", ALL)
def test_both_values_are_on_the_one_line_diagram(key):
    pages = packet_pages(build(key, {**sample(key), "available_fault_current_a": 18_000,
                                    "equipment_aic_ka": 22}).pdf)
    one_line = pages[3]
    assert "Available fault current at the service: 18,000 A" in one_line
    assert "interrupting rating: 22 kA" in one_line


def test_the_one_line_says_when_the_fault_current_was_not_entered():
    assert "not entered" in packet_pages(build("ev_charger", _without_fault_current("ev_charger")).pdf)[3]


@pytest.mark.parametrize("name", ["ev-charger", "service-upgrade", "subpanel", "appliance-circuit"])
def test_every_job_type_form_sends_both_fields(name):
    script = (STATIC / "assets" / "js" / "job-types" / f"{name}.js").read_text()
    assert "electricalFields(data)" in script
    shared = (STATIC / "assets" / "js" / "job-types" / "electrical.js").read_text()
    assert "available_fault_current_a" in shared and "equipment_aic_ka" in shared
    html = (STATIC.parent / "templates" / "start.html").read_text()
    assert 'name="available_fault_current_a"' in html and 'name="equipment_aic_ka"' in html
    assert html.count("From the utility's fault current letter or published table") == 2
    assert "job-types/electrical.js" in html


def test_a_nonsense_rating_is_a_422():
    with pytest.raises(Exception):
        build("ev_charger", {**sample("ev_charger"), "equipment_aic_ka": 0})
