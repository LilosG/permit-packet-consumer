"""Item 7: NEC 310.15(B)(1) temperature correction, shown as math, for runs outdoors or in the sun."""
import re

import pytest

from permit_packets.core.circuits import size_circuit
from permit_packets.core.conductors import service_conductor, size_feeder
from permit_packets.core.heat import correction_factor, heat_calc
from permit_packets.job_types import REGISTRY
from permit_packets.jurisdictions import MESA, ORO_VALLEY
from tests.packet_helpers import build, packet_pages, sample

ALL = sorted(REGISTRY)
MESA_JOB = {"jurisdiction_key": "mesa-az", "city": "Mesa", "state": "AZ"}


def _ev(**changes) -> dict:
    return {**sample("ev_charger"), **MESA_JOB, "charger_amps": 48, "location": "exterior_wall",
            "run_ft": 40, "trench_ft": 0, **changes}


def _heat(body: dict):
    return next((c for c in body["checks"] if c["name"] == "Temperature correction"), None)


def test_mesa_carries_the_design_temperature_and_its_source():
    assert MESA.design_ambient_f == 109
    assert MESA.design_ambient_source.startswith("https://ashrae-meteo.info/")
    assert ORO_VALLEY.design_ambient_f is None


def test_the_correction_table_by_ambient():
    assert correction_factor(86) == 1.00      # 30 C
    assert correction_factor(95) == 0.96      # 35 C
    assert correction_factor(104) == 0.91     # 40 C, the top of the 36-40 C row
    assert correction_factor(105) == 0.87     # 40.6 C is in the 41-45 C row
    assert correction_factor(113) == 0.87     # 45 C
    assert correction_factor(114) == 0.82     # 45.6 C
    with pytest.raises(ValueError):
        correction_factor(200)


def test_a_48_amp_charger_on_a_mesa_exterior_wall_worked_by_hand():
    circuit = size_circuit(48, 40, continuous=True, ambient_f=MESA.design_ambient_f)
    heat = circuit.heat
    assert circuit.breaker == 60 and circuit.wire.size == "6"
    assert heat.base_90c == 75                       # #6 THWN-2 at 90 C
    assert heat.factor == 0.87                       # 109 F is 42.8 C
    assert heat.corrected_a == pytest.approx(65.25)  # 75 x 0.87
    assert heat.cap_a == 65 and heat.usable_a == 65  # capped at the 75 C termination ampacity
    assert heat.passed and heat.carries_a == 60


def test_the_one_line_page_shows_the_calculation_for_that_charger():
    result = build("ev_charger", _ev())
    check = _heat(result.body)
    assert check["passed"] is True
    assert check["result"].startswith("#6 Cu THWN-2: 75 A at 90\N{DEGREE SIGN}C x 0.87")
    assert "= 65.2 A, limited to 65 A by the 75\N{DEGREE SIGN}C terminals; breaker 60 A: OK" in check["result"]
    page = re.sub(r"\s+", " ", packet_pages(result.pdf)[3])
    assert "Temperature correction, outdoor conductors (NEC 310.15(B)(1))" in page
    for shown in ("Base ampacity", "Correction factor", "Corrected ampacity", "Breaker", "75 A", "0.87", "65.2 A", "60 A"):
        assert shown in page, shown
    assert "109\N{DEGREE SIGN}F" in page and "ashrae-meteo.info" in page


def test_a_conductor_that_falls_below_the_breaker_when_corrected_is_upsized():
    # 40 A charger: 50 A breaker. #8 is 50 A at 75 C, but 55 A x 0.87 = 47.9 A, so #6 it is.
    plain = size_circuit(40, 40, continuous=True)
    hot = size_circuit(40, 40, continuous=True, ambient_f=109)
    assert plain.wire.size == "8" and hot.wire.size == "6"
    assert hot.heat.passed and hot.heat.corrected_a == pytest.approx(65.25)
    body = build("ev_charger", _ev(charger_amps=40)).body
    assert "#6 AWG Cu" in next(c for c in body["checks"] if c["name"] == "Conductors")["result"]


def test_a_64_amp_charger_uses_the_uncapped_corrected_value():
    heat = size_circuit(64, 40, continuous=True, ambient_f=109).heat
    assert heat.base_90c == 95 and heat.corrected_a == pytest.approx(82.65)
    assert heat.cap_a == 85 and heat.usable_a == pytest.approx(82.65) and heat.passed


@pytest.mark.parametrize("changes", [
    {"location": "attached_garage"},
    {"location": "detached_garage", "trench_ft": 0},
])
def test_a_run_that_stays_indoors_gets_no_correction(changes):
    body = build("ev_charger", _ev(**changes)).body
    assert _heat(body) is None
    assert "Temperature correction" not in packet_pages(build("ev_charger", _ev(**changes)).pdf)[3]


def test_trench_risers_are_exposed_even_from_an_attached_garage():
    body = build("ev_charger", _ev(location="attached_garage", trench_ft=20)).body
    assert _heat(body) is not None


def test_the_correction_never_makes_a_larger_breaker_pass_on_a_smaller_wire():
    for amps in (16, 24, 32, 40, 48, 64, 80):
        hot = size_circuit(amps, 30, continuous=True, ambient_f=109)
        assert hot.heat.passed and hot.heat.usable_a >= hot.breaker


def test_a_city_without_a_design_temperature_flags_the_exposed_run_instead():
    payload = {**_ev(), "jurisdiction_key": "oro-valley-az", "city": "Oro Valley"}
    body = build("ev_charger", payload).body
    assert _heat(body) is None
    assert any("310.15(B)(1) temperature correction" in flag and "isn't set up yet" in flag for flag in body["flags"])


def test_mesas_old_115_degree_note_is_gone():
    for checklist in MESA.checklists.values():
        assert not any("115" in note.text for note in checklist.notes)
    body = build("ev_charger", _ev()).body
    assert not any("115" in flag for flag in body["flags"])


def test_a_subpanel_feeder_in_a_trench_is_upsized_for_heat():
    plain = size_feeder(200, "copper", 100, 90)
    hot = size_feeder(200, "copper", 100, 90, ambient_f=109)
    assert plain.conductor.size == "3/0" and hot.conductor.size == "4/0"
    assert hot.heat.passed and hot.heat.corrected_a == pytest.approx(226.2)
    payload = {**sample("subpanel"), **MESA_JOB, "subpanel_amps": 200, "feeder_breaker_amps": 200}
    result = build("subpanel", payload)
    assert "4/0" in _heat(result.body)["result"]
    assert "Temperature correction" in packet_pages(result.pdf)[3]


def test_a_service_conductor_is_corrected_against_83_percent_of_the_main():
    plain = service_conductor(100, "copper")
    hot = service_conductor(100, "copper", 109)
    assert plain.size == "4" and hot.size == "3"   # 95 A x 0.87 = 82.7 A is under 83 A
    payload = {**sample("service_upgrade"), **MESA_JOB}
    result = build("service_upgrade", payload)
    assert _heat(result.body)["passed"] is True
    assert "Temperature correction" in packet_pages(result.pdf)[3]


def test_an_outdoor_appliance_circuit_is_capped_at_the_terminal_column_it_is_sized_for():
    payload = {**sample("appliance_circuit"), **MESA_JOB}
    result = build("appliance_circuit", payload)
    check = _heat(result.body)
    assert check["passed"] is True and "60\N{DEGREE SIGN}C terminals" in check["result"]
    assert re.search(r"limited to \d+ A by the 60", check["result"])
    hot = build("appliance_circuit", {**payload, "terminals_75c": True}).body
    assert "75\N{DEGREE SIGN}C terminals" in _heat(hot)["result"] or "x 0.87" in _heat(hot)["result"]


def test_heat_calc_says_too_small_when_it_is():
    heat = heat_calc("8", "copper", 109, cap_a=50, carries_a=50)
    assert not heat.passed and heat.line.endswith("breaker 50 A: TOO SMALL")
