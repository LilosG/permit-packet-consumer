"""The three public calculators. No new math: every number comes from the same functions the packet generator
calls (build_ev_packet, calculate_load, size_circuit, conduit_size). This module only parses inputs and lays
the results out as rows for the page and the JSON endpoint."""
from __future__ import annotations

from dataclasses import dataclass

from permit_packets.core.circuits import conduit_size, size_circuit
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


NEC_TEXT = {
    "220.82": "Optional dwelling load calculation: 3 VA per sq ft, small appliance and laundry circuits, nameplate appliances, first 10,000 VA at 100% and the rest at 40%, plus the larger of heating or cooling.",
    "220.87": "Using 12 months of utility maximum demand (or a 30-day recording) at 125% instead of a calculated existing load.",
    "625.41": "EV supply equipment is a continuous load: the circuit is sized at 125% of the charger's current.",
    "210.19(A)(1)": "Branch-circuit conductors must carry at least the continuous load at 125% plus any noncontinuous load.",
    "240.4(D)": "Small conductors (#14, #12, #10 copper) have a maximum breaker size.",
    "310.16": "Conductor ampacity table, read here at the 75°C column.",
    "250.122": "Equipment grounding conductor size by breaker rating, upsized in step when the hot wire is upsized (250.122(B)).",
}


def nec_rows(refs: list[str]) -> list[tuple[str, str]]:
    return [(f"NEC {ref}", NEC_TEXT[ref]) for ref in refs if ref in NEC_TEXT]
