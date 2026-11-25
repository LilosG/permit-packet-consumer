"""NEC audit of the eight calculators: hand-worked values, guardrails, input validation and fail guidance."""
import itertools
import re

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import calculators as calc
from permit_packets import wave2


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app, raise_server_exceptions=False)


def run(slug, **inputs):
    """Through the same parser the page and API use, so unspecified fields take their defaults."""
    fields, fn = wave2.CALC_RUN[slug]
    values, errors = calc.parse(fields, inputs)
    assert not errors, errors
    return fn(values)


def row(result, start):
    return next(value for label, value in result["rows"] if label.startswith(start))


LOAD = "residential-load-calculator"
EV = "ev-charger-load-calculator"
WIRE = "ev-charger-wire-breaker-size"
SUB = "subpanel-feeder-calculator"
SOLAR = "solar-120-percent-rule-calculator"
TUB = "hot-tub-breaker-wire-size"
FILL = "conduit-fill-trench-depth-calculator"
GEN = "generator-interlock-wire-calculator"
SLUGS = (LOAD, EV, WIRE, SUB, SOLAR, TUB, FILL, GEN)


def test_every_calculator_is_covered():
    assert set(SLUGS) == set(wave2.CALC_RUN)


# ---- 220.82 ----

def test_220_82_worked_example():
    # 6,000 general + 4,500 circuits + 21,500 appliances = 32,000; 10,000 + 40% of 22,000 = 18,800; + 4,800 A/C
    result = run(LOAD)
    assert result["computed_amps"] == 98.3 and result["status"] == "ok" and result["guidance"] is None
    assert row(result, "Subtotal") == "32,000 VA" and row(result, "Remainder") == "8,800 VA"


def test_220_82_under_10kva_has_no_remainder():
    result = run(LOAD, sq_ft=400, range_va=0, dryer_va=0, water_heater_va=0, cooling_va=0)
    assert row(result, "First 10,000") == "5,700 VA" and row(result, "Remainder") == "0 VA"


def test_other_fixed_appliances_enter_the_demand_pool_at_40_percent():
    assert run(LOAD, other_va=5000)["computed_amps"] == round((23600 + 2000) / 240, 1)


def test_ev_check_includes_hot_tub():
    assert run(EV, hot_tub_or_pool_va=6000)["computed_amps"] == round((23600 + 2400 + 11520) / 240, 1)


@pytest.mark.parametrize("inputs,hvac", [
    (dict(heating_va=10000), 10000),                                       # heat pump or other at 100%
    (dict(heating_va=20000, heating_type=1), 13000),                       # 65%
    (dict(heating_va=20000, heating_type=2), 8000),                        # 40%
    (dict(heating_va=5000, supplemental_va=10000), 11500),                 # 100% compressor + 65% backup
    (dict(heating_va=5000, supplemental_va=10000, heat_lockout=1), 6500),  # cannot run together
    (dict(heating_va=9000, supplemental_va=4000, heat_lockout=1), 9000),
    (dict(heating_va=4000, heating_type=2), 4800),                         # cooling is the larger selection
])
def test_220_82_c_heating_and_cooling(inputs, hvac):
    result = run(LOAD, **inputs)
    assert result["computed_amps"] == round((18800 + hvac) / 240, 1)


def test_backup_heat_is_never_dropped_from_the_packet_prefill():
    assert run(LOAD, heating_va=5000, supplemental_va=10000)["prefill"] == {"heating_va": 11500}
    assert run(LOAD, heating_va=20000, heating_type=2)["prefill"] == {}  # packet keeps the 20,000 nameplate


@pytest.mark.parametrize("query", ["supplemental_va=5000", "heating_va=9000&heating_type=1&supplemental_va=5000"])
def test_inconsistent_backup_heat_is_rejected(client, query):
    response = client.get(f"/api/calc/{LOAD}?{query}")
    assert response.status_code == 422 and response.json()["errors"]


@pytest.mark.parametrize("slug", [LOAD, EV])
def test_service_below_100a_is_not_verified(slug):
    result = run(slug, service_amps=60, sq_ft=400, range_va=0, dryer_va=0, water_heater_va=0, cooling_va=0,
                 charger_amps=16) if slug == EV else run(
        slug, service_amps=60, sq_ft=400, range_va=0, dryer_va=0, water_heater_va=0, cooling_va=0)
    assert result["status"] == "tight" and "Not verified" in result["headline"] and result["guidance"]


# ---- EV ----

def test_ev_load_counts_nameplate_not_125_percent():
    result = run(EV)
    assert result["computed_amps"] == 146.3 and result["status"] == "ok"


def test_ev_that_fits_only_without_125_percent_is_flagged():
    # 146.3 A on 150 A; at 125% it is 158.3 A
    result = run(EV, service_amps=150)
    assert result["status"] == "tight" and "158.3 A" in result["headline"] and result["computed_amps"] == 146.3


def test_small_charger_mentions_standard_method_minimum():
    assert any("220.57" in note for note in run(EV, charger_amps=24)["notes"])
    assert not any("220.57" in note for note in run(EV, charger_amps=32)["notes"])


@pytest.mark.parametrize("slug,job", [(EV, "ev-charger"), (LOAD, "panel-upgrade")])
def test_over_capacity_guidance(slug, job):
    result = run(slug, service_amps=60)
    assert result["status"] == "over"
    text = " ".join(result["guidance"]["options"])
    assert "220.87" in text and "625.42" in text and "Upgrade the service" in text
    assert [href for href, _ in result["guidance"]["links"]] == [calc.HIRING_PATH, f"/start/?job={job}&role=diy"]


# ---- EV wire and breaker ----

@pytest.mark.parametrize("amps,breaker,wire75,wire60,ground", [
    (16, 20, "12", "12", "12"), (24, 30, "10", "10", "10"), (32, 40, "8", "8", "10"), (40, 50, "8", "6", "10"),
    (48, 60, "6", "4", "10"), (64, 80, "4", "3", "8"), (80, 100, "3", "1", "8"),
])
def test_wire_and_breaker_at_both_terminal_ratings(amps, breaker, wire75, wire60, ground):
    hot = run(WIRE, charger_amps=amps, run_ft=1)
    cool = run(WIRE, charger_amps=amps, run_ft=1, terminals_75c=0)
    assert (hot["breaker"], hot["wire"], hot["ground"]) == (breaker, wire75, ground)
    assert (cool["breaker"], cool["wire"]) == (breaker, wire60)
    assert breaker in calc.STANDARD_BREAKERS


def test_wire_voltage_drop_upsizes_ground_in_proportion():
    result = run(WIRE, charger_amps=48, run_ft=300)
    assert result["wire"] == "3" and result["ground"] == "6"
    assert float(re.search(r"([\d.]+)%", row(result, "Voltage drop"))[1]) <= 3


# ---- Subpanel ----

@pytest.mark.parametrize("breaker,material,wire,ground", [
    (60, 0, "4", "8"), (60, 1, "6", "10"), (100, 0, "1", "6"), (100, 1, "3", "8"),
    (200, 0, "250", "4"), (200, 1, "3/0", "6"),
])
def test_feeder_sizes(breaker, material, wire, ground):
    result = run(SUB, breaker_amps=breaker, material=material, run_ft=1)
    assert (result["wire"], result["ground"]) == (wire, ground)


def test_feeder_excess_drop_gets_guidance():
    # 160 A, 400 ft, 350 kcmil Al: 2 x 21.2 x 160 x 400 / 350,000 = 7.75 V = 3.23%
    result = run(SUB, breaker_amps=200, material=0, run_ft=400)
    assert result["status"] == "over" and "3.2%" in row(result, "Voltage drop")
    assert result["guidance"]["links"][0][0] == calc.HIRING_PATH
    assert run(SUB)["guidance"] is None


def test_feeder_schedule_80_note():
    assert any("Schedule 80" in note and "needs" in note for note in run(SUB)["notes"])
    assert not any("Schedule 80" in note for note in run(SUB, conduit=1)["notes"])


# ---- Solar ----

@pytest.mark.parametrize("bus,main,pv,fits", [
    (200, 200, 40, True), (200, 200, 45, False), (225, 200, 70, True), (125, 100, 50, True),
    (100, 100, 20, True), (100, 100, 25, False),
])
def test_solar_boundaries(bus, main, pv, fits):
    assert run(SOLAR, bus_amps=bus, main_amps=main, pv_breaker_amps=pv)["fits"] is fits


def test_solar_main_larger_than_bus_fails():
    result = run(SOLAR, bus_amps=200, main_amps=225, pv_breaker_amps=15)
    assert result["fits"] is False and result["max_pv_allowed"] == 0 and "408.36" in " ".join(result["notes"])


def test_solar_uses_125_percent_of_inverter_output():
    ok = run(SOLAR, bus_amps=200, main_amps=200, pv_breaker_amps=40, inverter_amps="31.7")
    assert ok["fits"] and "31.7 A x 125% = 39.625 A" in row(ok, "Solar source")
    # a 45 A breaker on 32 A of inverter output passes by the code's current figure, not by the breaker sum
    assert run(SOLAR, pv_breaker_amps=45)["fits"] is False
    assert run(SOLAR, pv_breaker_amps=45, inverter_amps=32)["fits"] is True
    assert run(SOLAR, pv_breaker_amps=45, inverter_amps="32.1")["fits"] is False


def test_solar_breaker_smaller_than_inverter_requires_fails():
    result = run(SOLAR, main_amps=175, pv_breaker_amps=30, inverter_amps=32)
    assert result["fits"] is False and "690.9(B)" in " ".join(result["notes"])
    text = " ".join(result["guidance"]["options"])
    assert "solar breaker of at least 40 A" in text and "main breaker" not in text


@pytest.mark.parametrize("layout", [1, 2])
def test_solar_without_opposite_end_is_held_to_100_percent(layout):
    assert run(SOLAR, panel_layout=layout)["fits"] is False
    assert run(SOLAR, panel_layout=layout, main_amps=150, pv_breaker_amps=50)["fits"] is True


def test_solar_fail_guidance():
    result = run(SOLAR, pv_breaker_amps=50)
    text = " ".join(result["guidance"]["options"])
    assert "175 A or smaller" in text and "225 A busbar" in text and "705.11" in text and "705.13" in text
    assert calc.HIRING_PATH in [href for href, _ in result["guidance"]["links"]]
    assert run(SOLAR)["guidance"] is None


# ---- Hot tub ----

@pytest.mark.parametrize("amps,breaker", [(20, 25), (24, 30), (30, 40), (32, 40), (36, 45), (40, 50), (48, 60)])
def test_hot_tub_breaker(amps, breaker):
    assert run(TUB, load_amps=amps)["breaker"] == breaker


def test_hot_tub_terminal_columns_and_small_conductor_limit():
    assert run(TUB, load_amps=40, run_ft=1)["wire"] == "8"
    assert run(TUB, load_amps=40, run_ft=1, terminals_75c=0)["wire"] == "6"
    assert run(TUB, load_amps=20, run_ft=1)["wire"] == "10"  # #12 is limited to a 20 A breaker (240.4(D))


# ---- Conduit and trench ----

def fill(**inputs):
    return run(FILL, **inputs)


def test_two_conductors_are_held_to_31_percent():
    # #2/0 + #6 = 0.2730 sq in: inside 40% of 1 in PVC (0.333) but over 31% of it (0.258)
    result = fill(wire_size=201, conductor_count=1, ground_size=6)
    assert result["conduit"] == '1-1/4"' and "31% fill" in result["headline"]


def test_schedule_80_has_its_own_table():
    # three #6 + #10 = 0.1732 sq in: fits 3/4 in Sch 40 (0.203) but not 3/4 in Sch 80 (0.164)
    assert fill(wire_size=6, conductor_count=3)["conduit"] == '3/4"'
    assert fill(wire_size=6, conductor_count=3, conduit_type=3)["conduit"] == '1"'
    assert any('needs 1"' in note for note in fill(wire_size=6, conductor_count=3)["notes"])


@pytest.mark.parametrize("surface,pvc,rmc", [(0, 18, 6), (1, 18, 18), (2, 24, 24), (3, 12, 6), (4, 4, 4), (5, 0, 0)])
def test_table_300_5_cover(surface, pvc, rmc):
    for conduit_type, depth in ((0, pvc), (3, pvc), (2, rmc)):
        assert row(fill(surface=surface, conduit_type=conduit_type), "NEC Table 300.5").startswith(f"{depth} inches")


@pytest.mark.parametrize("surface,depth", [(0, 12), (1, 12), (2, 24), (3, 6), (4, 4), (5, 0)])
def test_gfci_20a_cover_exception(surface, depth):
    result = fill(surface=surface, gfci_20a=1)
    assert row(result, "NEC Table 300.5").startswith(f"{depth} inches")
    assert any("never covers a 240 V" in note for note in result["notes"])


def test_emt_burial_is_not_selected_and_derating_is_noted():
    assert fill(conduit_type=1)["status"] == "over" and fill(conduit_type=1, underground=0)["status"] == "ok"
    assert any("to 80%" in n for n in fill(conductor_count=4)["notes"])
    assert not any("derate" in n for n in fill(conductor_count=3)["notes"])


def test_oversize_bundle_fails_cleanly():
    result = fill(wire_size=401, conductor_count=12)
    assert result["status"] == "over" and result["conduit"] == ""


# ---- Generator ----

@pytest.mark.parametrize("inlet,terms,wire,ground", [
    (30, 0, "10", "10"), (30, 1, "10", "10"), (50, 0, "6", "10"), (50, 1, "8", "10"), (100, 0, "1", "8"),
    (150, 0, "1/0", "6"), (200, 0, "3/0", "6"),
])
def test_generator_conductors(inlet, terms, wire, ground):
    result = run(GEN, inlet_amps=inlet, terminals_75c=terms, run_ft=1)
    assert (result["wire"], result["ground"]) == (wire, ground)


def test_generator_defaults_to_60c():
    assert run(GEN)["wire"] == "6"


def test_generator_neutral_follows_transfer_equipment():
    for transfer in (0, 1):
        assert row(run(GEN, transfer_type=transfer), "Generator neutral").startswith("Floating neutral")
    switched = run(GEN, transfer_type=2)
    assert "bonded at the generator" in row(switched, "Generator neutral") and "250.30" in switched["nec"]


# ---- Input validation ----

BAD = ("nan", "inf", "-inf", "Infinity", "1e999", "-1", "-0.5", "1e30", "abc", "1.2.3", "0x10", "9" * 5000)


@pytest.mark.parametrize("slug", SLUGS)
def test_bad_values_give_422_never_500(client, slug):
    for f in wave2.CALC_RUN[slug][0]:
        for raw in BAD:
            response = client.get(f"/api/calc/{slug}", params={f.name: raw})
            assert response.status_code == 422, (f.name, raw[:20], response.status_code)
            assert response.json()["errors"][0].startswith(f.label)
        page = client.get(f"/tools/{slug}/", params={f.name: "inf"})
        assert page.status_code == 200 and "calc-error" in page.text and "Your result" not in page.text


@pytest.mark.parametrize("slug", SLUGS)
def test_bounds_blanks_and_zero(client, slug):
    for f in wave2.CALC_RUN[slug][0]:
        if f.choices:
            allowed, refused = f.choices, [max(f.choices) + 1]
            if 0 not in f.choices:
                refused.append(0)
        else:
            allowed, refused = [f.min, f.max], [f.min - 1, f.max + 1] + ([0] if f.min > 0 else [])
        for value in [*allowed, "", "  "]:
            response = client.get(f"/api/calc/{slug}", params={f.name: value})
            # the one cross-field rule: backup heat needs a heat pump entry
            expected = 422 if f.name == "supplemental_va" and value not in (0, "", "  ") else 200
            assert response.status_code == expected, (f.name, value, response.text[:200])
        for value in refused:
            assert client.get(f"/api/calc/{slug}", params={f.name: value}).status_code == 422, (f.name, value)


def test_fractions_only_where_allowed(client):
    assert client.get(f"/api/calc/{FILL}?conductor_count=2.5").status_code == 422
    assert client.get(f"/api/calc/{SOLAR}?inverter_amps=31.7").status_code == 200
    assert client.get(f"/api/calc/{LOAD}?sq_ft=2,000.0").status_code == 200


def test_rejected_field_redraws_with_its_default(client):
    page = client.get(f"/tools/{LOAD}/?service_amps=9999").text
    assert 'value="200" selected' in page


@pytest.mark.parametrize("slug", [WIRE, SUB, SOLAR, TUB, GEN, FILL])
def test_every_choice_combination_calculates(slug):
    fields, fn = wave2.CALC_RUN[slug]
    chosen = [f for f in fields if f.choices]
    runs = [{f.name: f.max} for f in fields if not f.choices] + [{f.name: f.min} for f in fields if not f.choices]
    base = calc.parse(fields, {})[0]
    for combo in itertools.product(*(f.choices for f in chosen)):
        for extreme in runs or [{}]:
            result = fn({**base, **dict(zip((f.name for f in chosen), combo)), **extreme})
            assert result["status"] in ("ok", "over", "tight") and result["headline"]
            assert not re.search(r"\b(nan|inf)\b", str(result))


@pytest.mark.parametrize("service", calc.SERVICE_SIZES)
@pytest.mark.parametrize("slug", [LOAD, EV])
def test_load_extremes_calculate(slug, service):
    fields = wave2.CALC_RUN[slug][0]
    for edge in ("min", "max"):
        inputs = {f.name: getattr(f, edge) for f in fields if not f.choices and f.name != "supplemental_va"}
        assert run(slug, service_amps=service, **inputs)["computed_amps"] > 0


# ---- Page, API and packet link ----

def test_guidance_renders_on_page_and_in_json(client):
    query = "bus_amps=200&main_amps=200&pv_breaker_amps=60"
    page = client.get(f"/tools/{SOLAR}/?{query}").text
    assert 'class="calc-guidance"' in page and f'href="{calc.HIRING_PATH}"' in page
    assert client.get(f"/api/calc/{SOLAR}?{query}").json()["result"]["guidance"]["options"]
    assert client.get(calc.HIRING_PATH).status_code == 200
    assert "r.guidance" in (app_module.STATIC / "assets" / "js" / "calculator.js").read_text()


def test_start_link_carries_only_valid_encoded_inputs(client):
    page = client.get(f"/tools/{LOAD}/?sq_ft=2400&dryer_va=inf&role=hiring%26tier%3Dx&junk=1").text
    href = re.search(r'data-start="([^"]*)"', page)[1]
    assert href == "/start/?job=panel-upgrade&amp;role=diy&amp;sq_ft=2400"


def test_start_link_includes_backup_heat(client):
    page = client.get(f"/tools/{LOAD}/?heating_va=5000&supplemental_va=10000").text
    assert "heating_va=11500" in re.search(r'data-start="([^"]*)"', page)[1]
