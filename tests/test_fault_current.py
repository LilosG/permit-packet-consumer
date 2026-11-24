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
        "name": "Interrupting rating", "result": "Enter the utility's available fault current", "passed": False, "assumed": True}
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


def test_summary_shows_assumed_for_defaults_and_the_verdict_ignores_it():
    from permit_packets.core import capacity_summary as cs
    checks = [{"name": "Service capacity", "result": "ok", "passed": True},
              {"name": "Interrupting rating", "result": "x", "passed": False, "assumed": True}]
    assert cs.verdict(checks)[0] is True
    only = [{"name": "Interrupting rating", "result": "x", "passed": False}]
    assert cs.verdict(only)[0] is False and cs.verdict([{**only[0], "assumed": True}] + checks[:0])[0] is True
    assert cs.job_label("ev_charger") == "EV charger"
    assert cs.method_label({"peak_demand_kw": 5}).startswith("NEC 220.87")


def test_entered_aic_is_pass_and_default_aic_is_assumed():
    from permit_packets.core.panel_data import interrupting_rating_check
    from permit_packets.core.schemas import JobRequestBase
    Job = lambda **kw: JobRequestBase(customer='a', address='b', contractor='c', **kw)
    base = {"available_fault_current_a": 8_000}
    assert interrupting_rating_check(Job(**base)).assumed is True
    entered = interrupting_rating_check(Job(**base, equipment_aic_ka=22))
    assert entered.passed and not entered.assumed
    assert interrupting_rating_check(Job(available_fault_current_a=30_000, equipment_aic_ka=10)).passed is False
