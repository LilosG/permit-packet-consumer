"""The three public calculators. No new math: every number comes from the same functions the packet generator
calls (build_ev_packet, calculate_load, size_circuit, conduit_size). This module only parses inputs and lays
the results out as rows for the page and the JSON endpoint."""
from __future__ import annotations

from dataclasses import dataclass, field

from permit_packets.core.circuits import CONTINUOUS_FACTOR, conduit_size, size_circuit
from permit_packets.core.conductors import (
    BUS_BACKFEED_FACTOR, STANDARD_BREAKERS, branch_conduit, feeder_conduit,
    size_branch, size_feeder, solar_fits, wire_label,
)
from permit_packets.core.load_calculation import HomeLoads, calculate_load
from permit_packets.job_types.ev_charger.calc import (
    CHARGER_SIZES, DISCONNECT_REQUIRED_ABOVE_AMPS, VOLTS, EvJob, build_ev_packet, largest_charger_that_fits)

SERVICE_SIZES = (60, 100, 125, 150, 200, 225, 400)
CHARGER_CHOICES = tuple(sorted(CHARGER_SIZES))


@dataclass(frozen=True)
class Field:
    name: str
    label: str
    default: int
    min: int = 0
    max: int = 0
    choices: tuple[int, ...] = ()  # when set, a select
    hint: str = ""
    choice_labels: dict[int, str] = field(default_factory=dict)


F_SQFT = Field("sq_ft", "Living area (sq ft)", 2000, 400, 10000, hint="Finished living area, not garage or unfinished basement.")
F_SERVICE = Field("service_amps", "Main service (amps)", 200, choices=SERVICE_SIZES)
F_CHARGER = Field("charger_amps", "Charger output (amps)", 48, choices=CHARGER_CHOICES, hint="A 48 A charger is on a 60 A breaker.")
F_RANGE = Field("range_va", "Electric range or oven + cooktop (VA)", 12000, 0, 30000, hint="Nameplate VA. Enter 0 for gas.")
F_DRYER = Field("dryer_va", "Electric dryer (VA)", 5000, 0, 15000, hint="Enter 0 for gas.")
F_WH = Field("water_heater_va", "Electric water heater (VA)", 4500, 0, 20000, hint="Enter 0 for gas.")
F_HEAT = Field("heating_va", "Electric heating (VA)", 0, 0, 60000, hint="Heat pump or strip heat nameplate. 0 for gas.")
F_COOL = Field("cooling_va", "Air conditioning (VA)", 4800, 0, 60000, hint="Condenser nameplate VA (amps x 240).")
F_TUB = Field("hot_tub_or_pool_va", "Hot tub or pool (VA)", 0, 0, 20000, hint="Nameplate VA. 0 if none.")
F_RUN = Field("run_ft", "One-way wire run, panel to charger (ft)", 40, 1, 300)
F_LOC = Field("detached", "Charger location", 0, choices=(0, 1), hint="")

LOAD_FIELDS = (F_SQFT, F_SERVICE, F_RANGE, F_DRYER, F_WH, F_HEAT, F_COOL, F_TUB)
EV_FIELDS = (F_SQFT, F_SERVICE, F_CHARGER, F_RANGE, F_DRYER, F_WH, F_HEAT, F_COOL)
WIRE_FIELDS = (F_CHARGER, F_RUN, F_LOC)
DETACHED_LABELS = {0: "Attached garage or exterior wall", 1: "Detached garage"}


def parse(fields: tuple[Field, ...], params: dict) -> tuple[dict[str, int], list[str]]:
    """Whole-number values from query or JSON input; blank uses the default. Returns (values, errors)."""
    values, errors = {}, []
    for f in fields:
        raw = params.get(f.name)
        if raw in (None, ""):
            values[f.name] = f.default
            continue
        try:
            number = int(float(str(raw).replace(",", "")))
        except ValueError:
            errors.append(f"{f.label}: enter a number.")
            continue
        if f.choices and number not in f.choices:
            errors.append(f"{f.label}: pick one of the listed options.")
        elif not f.choices and not f.min <= number <= f.max:
            errors.append(f"{f.label}: enter a value from {f.min:,} to {f.max:,}.")
        else:
            values[f.name] = number
    return values, errors


def _home(v: dict[str, int]) -> HomeLoads:
    return HomeLoads(
        square_feet=v["sq_ft"], range_va=v.get("range_va", 0), dryer_va=v.get("dryer_va", 0),
        water_heater_va=v.get("water_heater_va", 0), heating_va=v.get("heating_va", 0),
        cooling_va=v.get("cooling_va", 0), hot_tub_or_pool_va=v.get("hot_tub_or_pool_va", 0))


def _load_rows(load) -> list[list[str]]:
    rows = [[f"{line.label} ({line.basis})", f"{line.va:,.0f} VA"] for line in load.lines]
    rows += [["Subtotal before demand factor", f"{load.subtotal_va:,.0f} VA"],
             ["First 10,000 VA at 100%", f"{load.first_va:,.0f} VA"],
             ["Remainder at 40%", f"{load.remainder_va:,.0f} VA"],
             [f"{load.hvac_label} (larger of heating and cooling)", f"{load.hvac_va:,.0f} VA"]]
    rows += [[f"{line.label} ({line.basis})", f"{line.va:,.0f} VA"] for line in load.added_loads]
    rows += [["Total demand", f"{load.total_va:,.0f} VA"], ["Computed service current", f"{load.computed_amps:.1f} A"],
             ["Service rating", f"{load.service_amps} A"]]
    return rows


def _status(load) -> tuple[str, str]:
    if load.computed_amps > load.service_amps:
        return "over", f"Over capacity by {-load.spare_amps:.1f} A"
    if load.percent_of_service >= 80:
        return "tight", f"Fits, at {load.percent_of_service:.0f}% of the service"
    return "ok", f"Fits, at {load.percent_of_service:.0f}% of the service"


def residential_load(v: dict[str, int]) -> dict:
    load = calculate_load(_home(v), service_amps=v["service_amps"])
    status, text = _status(load)
    return {"status": status, "headline": f"{load.computed_amps:.1f} A of {load.service_amps} A. {text}.",
            "rows": _load_rows(load), "computed_amps": round(load.computed_amps, 1), "spare_amps": round(load.spare_amps, 1),
            "nec": ["220.82", "220.87"], "notes": [
                "Optional method for an existing dwelling (220.82). Gas appliances count as 0 VA.",
                "If this shows the service is over capacity, 12 months of utility demand data may support a different "
                "result (220.87). Your building department decides whether it accepts that."]}


def ev_load(v: dict[str, int]) -> dict:
    job = EvJob(customer="", address="", contractor="", license_number="", home=_home(v), service_amps=v["service_amps"],
                open_breaker_spaces=2, charger_amps=v["charger_amps"], location="attached_garage", run_ft=25, trench_ft=0)
    packet = build_ev_packet(job)  # the packet generator itself
    load = packet.load
    status, text = _status(load)
    notes = [f"The charger counts at 100% of its output: {v['charger_amps']} A x {VOLTS} V = {packet.charger_va:,} VA."]
    if status == "over":
        fits = largest_charger_that_fits(load, packet.charger_va)
        notes.append(f"A {fits} A charger fits this service." if fits else "No common charger size fits this service.")
        notes.append("Options: load management, a service upgrade, or 12 months of utility demand data (220.87).")
    return {"status": status, "headline": f"{load.computed_amps:.1f} A of {load.service_amps} A with a {v['charger_amps']} A charger. {text}.",
            "rows": _load_rows(load), "computed_amps": round(load.computed_amps, 1), "spare_amps": round(load.spare_amps, 1),
            "nec": ["220.82", "220.87"], "notes": notes}


def wire_breaker(v: dict[str, int]) -> dict:
    amps, run = v["charger_amps"], v["run_ft"]
    circuit = size_circuit(amps, run, continuous=True, volts=VOLTS)  # as build_ev_packet does
    disconnect = v["detached"] == 1 or amps > DISCONNECT_REQUIRED_ABOVE_AMPS
    rows = [["Continuous load", f"{amps} A x 125% = {circuit.required_amps:g} A"],
            ["Breaker", f"{circuit.breaker} A, 2-pole"],
            ["Copper conductors (THWN-2, 75°C)", f"#{circuit.wire.size} AWG, rated {circuit.wire.ampacity_75c} A"],
            ["Equipment ground", f"#{circuit.ground} AWG"],
            ["Voltage drop", f"{circuit.voltage_drop_volts:.1f} V, {circuit.voltage_drop_percent:.1f}% over {run} ft"],
            ["EMT conduit (2 hots + ground)", conduit_size(circuit, "EMT")],
            ["Disconnect", "Likely required" if disconnect else "Not required by this check"]]
    notes = []
    if circuit.upsized_for_voltage_drop:
        notes.append(f"The wire was upsized to #{circuit.wire.size} AWG to hold voltage drop to 3%, so the ground is #{circuit.ground} AWG (250.122(B)).")
    if circuit.voltage_drop_percent > 3:
        notes.append("Voltage drop is above 3% even at the largest wire size. Shorten the run or redesign the circuit.")
    if disconnect:
        notes.append("A disconnect is flagged for a detached garage or a breaker over 60 A. Your city may differ.")
    notes.append("Sized at the 75°C column. Confirm the charger and breaker terminals are marked for 75°C (110.14(C)(1)(a)).")
    return {"status": "ok" if circuit.voltage_drop_percent <= 3 else "over",
            "headline": f"{circuit.breaker} A breaker, #{circuit.wire.size} AWG copper, #{circuit.ground} AWG ground.",
            "rows": rows, "breaker": circuit.breaker, "wire": circuit.wire.size, "ground": circuit.ground,
            "nec": ["625.41", "210.19(A)(1)", "240.4(D)", "310.16", "250.122"], "notes": notes}


BUS_SIZES = (100, 125, 150, 200, 225, 400)
MAIN_BREAKER_SIZES = (60, 100, 125, 150, 175, 200, 225)
PV_BREAKER_SIZES = (15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80)
SUBPANEL_BREAKER_SIZES = (40, 50, 60, 70, 80, 90, 100, 125, 150, 200)
HOT_TUB_AMPS_CHOICES = (20, 24, 30, 32, 36, 40, 48)
SUBPANEL_FIELDS = (
    Field("breaker_amps", "Feeder breaker size (amps)", 100, choices=SUBPANEL_BREAKER_SIZES),
    Field("material", "Conductor material", 0, choices=(0, 1), choice_labels={0: "Aluminum (THWN-2 / XHHW-2)", 1: "Copper (THWN-2)"}),
    Field("run_ft", "One-way feeder length (ft)", 50, 1, 400),
    Field("conduit", "Conduit type", 0, choices=(0, 1), choice_labels={0: "PVC (Schedule 40/80)", 1: "EMT (Metal)"}),
    Field("detached", "Subpanel location", 0, choices=(0, 1), choice_labels={0: "Same building or attached garage", 1: "Detached building or shed"}),
)
SOLAR_FIELDS = (
    Field("bus_amps", "Main panel busbar rating (amps)", 200, choices=BUS_SIZES),
    Field("main_amps", "Main breaker rating (amps)", 200, choices=MAIN_BREAKER_SIZES),
    Field("pv_breaker_amps", "Solar PV backfeed breaker (amps)", 40, choices=PV_BREAKER_SIZES),
)
HOT_TUB_FIELDS = (
    Field("load_amps", "Hot tub or sauna nameplate (amps)", 36, choices=HOT_TUB_AMPS_CHOICES),
    Field("run_ft", "One-way wire run, panel to spa (ft)", 45, 1, 300),
    Field("terminals_75c", "Equipment terminal rating", 1, choices=(0, 1), choice_labels={0: "60°C (NM-B / UF-B or 60°C lugs)", 1: "75°C (THWN-2 with 75°C lugs)"}),
    Field("needs_neutral", "Neutral wire required?", 1, choices=(0, 1), choice_labels={0: "No (pure 240V 2-wire + ground)", 1: "Yes (240V/120V controls or pumps)"}),
)
def subpanel_feeder(v: dict[str, int]) -> dict:
    breaker, run, detached = v["breaker_amps"], v["run_ft"], v["detached"] == 1
    material = "copper" if v["material"] == 1 else "aluminum"
    conduit_type = "EMT" if v["conduit"] == 1 else "PVC"
    feeder = size_feeder(breaker, material, load_amps=breaker * 0.8, one_way_ft=run)
    raceway = feeder_conduit(feeder, conduit_type)
    mat = "Copper" if material == "copper" else "Aluminum"
    rows = [
        ["Feeder breaker (main panel)", f"{breaker} A, 2-pole (2 adjacent spaces)"],
        [f"{mat} hots & neutral (75°C)", f"{wire_label(feeder.conductor.size)} {mat}, rated {feeder.conductor.ampacity_75c} A"],
        ["Equipment ground (EGC)", f"{wire_label(feeder.egc)} {mat} (NEC 250.122)"],
        ["Voltage drop (at 80% load)", f"{feeder.vd_volts:.1f} V, {feeder.vd_percent:.1f}% over {run} ft"],
        [f"{conduit_type} conduit (4 wires, 40% fill)", f"{raceway} {conduit_type}"],
        ["Detached building grounding", "Grounding electrode required (NEC 250.32)" if detached else "Not required (same building)"],
    ]
    notes = ["Isolate neutral and ground buses in the subpanel (NEC 250.24(A)(5))."]
    if feeder.upsized:
        notes.append(f"Upsized to {wire_label(feeder.conductor.size)} for voltage drop; EGC upsized to {wire_label(feeder.egc)} (NEC 250.122(B)).")
    if detached:
        notes.append("Detached building requires disconnect (NEC 225.31) and ground rods (NEC 250.32(A)).")
    return {
        "status": "ok" if feeder.vd_percent <= 3 else "over",
        "headline": f"{wire_label(feeder.conductor.size)} {mat} hots & neutral, {wire_label(feeder.egc)} ground in {raceway} {conduit_type}.",
        "rows": rows, "wire": feeder.conductor.size, "ground": feeder.egc, "conduit": raceway,
        "nec": ["310.16", "250.122", "250.24(A)(5)", "250.32", "300.5"], "notes": notes,
    }


def solar_120_rule(v: dict[str, int]) -> dict:
    bus, main, pv = v["bus_amps"], v["main_amps"], v["pv_breaker_amps"]
    max_total = int(bus * BUS_BACKFEED_FACTOR)
    actual_total = main + pv
    max_pv_allowed = max(0, max_total - main)
    fits = solar_fits(bus, main, pv)
    rows = [
        ["Panel busbar rating", f"{bus} A"],
        ["120% busbar limit (NEC 705.12(B)(3)(2))", f"{bus} A x 120% = {max_total} A"],
        ["Main breaker + PV breaker", f"{main} A + {pv} A = {actual_total} A"],
        ["Maximum PV breaker allowed with this main", f"{max_pv_allowed} A"],
        ["PV breaker placement", "Opposite end of the busbar from the main breaker"],
    ]
    notes = ["NEC 705.12(B)(3)(2) limits main + PV breaker to 120% of busbar rating when PV breaker is at the opposite end of the bus."]
    if fits:
        notes.append(f"Passes with {max_total - actual_total} A of busbar margin remaining.")
    else:
        notes.append(f"Exceeds 120% limit by {actual_total - max_total} A. Derate main breaker, use a line-side tap (NEC 705.11), or upgrade to a 225A bus.")
    return {
        "status": "ok" if fits else "over",
        "headline": f"{'PASS' if fits else 'FAIL'}: {actual_total} A combined vs {max_total} A max allowed ({bus} A bus x 120%).",
        "rows": rows, "fits": fits, "max_pv_allowed": max_pv_allowed,
        "nec": ["705.12(B)(3)(2)", "220.82"], "notes": notes,
    }


def hot_tub_circuit(v: dict[str, int]) -> dict:
    amps, run = v["load_amps"], v["run_ft"]
    terms_75c, needs_neutral = v["terminals_75c"] == 1, v["needs_neutral"] == 1
    required = amps * CONTINUOUS_FACTOR
    breaker = next(b for b in STANDARD_BREAKERS if b >= required)
    branch = size_branch(breaker=breaker, load_amps=amps, run_ft=run, terminals_75c=terms_75c)
    n_cond = 3 if needs_neutral else 2
    pvc = branch_conduit(branch, n_cond, "PVC")
    col = 75 if terms_75c else 60
    rows = [
        ["Continuous spa/heater load (125%)", f"{amps} A x 125% = {required:g} A"],
        ["GFCI breaker required (NEC 680.44)", f"{breaker} A, 2-pole GFCI"],
        [f"Copper conductors ({col}°C column)", f"#{branch.wire.size} AWG Cu ({n_cond} insulated + ground)"],
        ["Equipment ground", f"#{branch.egc} AWG Cu (insulated green outdoors, NEC 680.42)"],
        ["Voltage drop", f"{branch.vd_volts:.1f} V, {branch.vd_percent:.1f}% over {run} ft"],
        ["PVC conduit (40% fill)", f"{pvc} Schedule 40/80 PVC (18 in cover, NEC 300.5)"],
        ["Disconnect (NEC 680.13)", "At least 5 ft from water, within sight of spa"],
    ]
    notes = ["Outdoor spas require an insulated green copper EGC (NEC 680.42(A)(1)) and a disconnect >= 5 ft from water (NEC 680.13)."]
    if branch.upsized:
        notes.append(f"Upsized to #{branch.wire.size} AWG for voltage drop; ground upsized to #{branch.egc} AWG (NEC 250.122(B)).")
    return {
        "status": "ok" if branch.vd_percent <= 3 else "over",
        "headline": f"{breaker} A 2-pole GFCI breaker, #{branch.wire.size} AWG copper, #{branch.egc} AWG insulated ground.",
        "rows": rows, "breaker": breaker, "wire": branch.wire.size, "ground": branch.egc,
        "nec": ["680.44", "680.13", "310.16", "250.122", "300.5"], "notes": notes,
    }


NEC_TEXT = {
    "220.82": "Optional dwelling load calculation: 3 VA per sq ft, small appliance and laundry circuits, nameplate appliances, first 10,000 VA at 100% and the rest at 40%, plus the larger of heating or cooling.",
    "220.87": "Using 12 months of utility maximum demand (or a 30-day recording) at 125% instead of a calculated existing load.",
    "625.41": "EV supply equipment is a continuous load: the circuit is sized at 125% of the charger's current.",
    "210.19(A)(1)": "Branch-circuit conductors must carry at least the continuous load at 125% plus any noncontinuous load.",
    "240.4(D)": "Small conductors (#14, #12, #10 copper) have a maximum breaker size.",
    "310.16": "Conductor ampacity table, read here at the 75°C column.",
    "250.122": "Equipment grounding conductor size by breaker rating, upsized in step when the hot wire is upsized (250.122(B)).",
}



NEC_TEXT.update({
    "310.16": "Conductor ampacity table, read at the 60°C or 75°C terminal column.",
    "250.24(A)(5)": "Neutral and equipment grounding conductors must remain isolated in every subpanel.",
    "250.32": "Detached buildings supplied by a feeder require a local grounding electrode system and disconnect.",
    "300.5": "Minimum underground cover: 18 in for PVC conduit, 6 in for RMC, and 24 in for UF-B cable.",
    "705.12(B)(3)(2)": "Main breaker plus solar PV breaker may not exceed 120% of the panel busbar rating.",
    "680.44": "GFCI protection is required for spa and hot tub outlets and circuits.",
    "680.13": "Maintenance disconnect must be accessible, within sight, and at least 5 ft from the spa.",
})

def nec_rows(refs: list[str]) -> list[tuple[str, str]]:
    return [(f"NEC {ref}", NEC_TEXT[ref]) for ref in refs if ref in NEC_TEXT]
