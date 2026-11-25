"""The public calculators. Sizing and load numbers come from the same functions the packet generator calls
(build_ev_packet, calculate_load, size_circuit, size_branch, size_feeder). This module parses inputs and lays
the results out as rows for the page and the JSON endpoint. It also holds the guardrails that only the
calculators apply (220.82 heating selections, busbar and burial-depth cases, Schedule 80 fill); the core modules,
and so the packets, don't have them."""
from __future__ import annotations

import math
from dataclasses import dataclass, field

from permit_packets.core.circuits import CONTINUOUS_FACTOR, WIRES, conduit_size, size_circuit
from permit_packets.core.conductors import (
    COPPER_75C, SERVICE_CONDUIT_FILL_SQ_IN, SMALL_GROUND_AREA_SQ_IN, STANDARD_BREAKERS, branch_conduit,
    feeder_conduit, size_branch, size_feeder, solar_fits, wire_label,
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
    decimal: bool = False  # accepts fractions; every other field takes whole numbers


F_SQFT = Field("sq_ft", "Living area (sq ft)", 2000, 400, 10000, hint="Finished living area, not garage or unfinished basement.")
F_SERVICE = Field("service_amps", "Main service (amps)", 200, choices=SERVICE_SIZES)
F_CHARGER = Field("charger_amps", "Charger output (amps)", 48, choices=CHARGER_CHOICES, hint="A 48 A charger is on a 60 A breaker.")
F_RANGE = Field("range_va", "Electric range or oven + cooktop (VA)", 12000, 0, 30000, hint="Nameplate VA. Enter 0 for gas.")
F_DRYER = Field("dryer_va", "Electric dryer (VA)", 5000, 0, 15000, hint="Enter 0 for gas.")
F_WH = Field("water_heater_va", "Electric water heater (VA)", 4500, 0, 20000, hint="Enter 0 for gas.")
F_HEAT = Field("heating_va", "Electric heating (VA)", 0, 0, 60000, hint="Heat pump compressor or resistance heat nameplate. 0 for gas.")
F_HEAT_TYPE = Field("heating_type", "Heating type", 0, choices=(0, 1, 2), choice_labels={
    0: "Heat pump, or any other heat counted at 100%", 1: "Resistance space heat, 1 to 3 separate controls (65%)",
    2: "Resistance space heat, 4 or more separate controls (40%)"})
F_SUPP = Field("supplemental_va", "Heat pump backup (supplemental) electric heat (VA)", 0, 0, 60000, hint="Backup heat strips on a heat pump. 0 if none.")
F_LOCKOUT = Field("heat_lockout", "Can the compressor and backup heat run together?", 0, choices=(0, 1), choice_labels={
    0: "Yes, or not sure", 1: "No, the controls prevent it"})
F_OTHER = Field("other_va", "Other fixed appliances (VA)", 0, 0, 60000, hint="Total nameplate VA: dishwasher, disposal, built-in microwave, well pump and the like.")
F_COOL = Field("cooling_va", "Air conditioning (VA)", 4800, 0, 60000, hint="Condenser nameplate VA (amps x 240).")
F_TUB = Field("hot_tub_or_pool_va", "Hot tub or pool (VA)", 0, 0, 20000, hint="Nameplate VA. 0 if none.")
F_RUN = Field("run_ft", "One-way wire run, panel to charger (ft)", 40, 1, 300)
F_LOC = Field("detached", "Charger location", 0, choices=(0, 1), hint="")

F_TERMS = Field("terminals_75c", "Terminal rating at both ends", 1, choices=(0, 1), choice_labels={
    0: "60°C (NM-B cable or 60°C / unmarked terminals)", 1: "75°C (THWN-2 with 75°C terminals)"})
HVAC_FIELDS = (F_HEAT, F_HEAT_TYPE, F_SUPP, F_LOCKOUT, F_COOL)
LOAD_FIELDS = (F_SQFT, F_SERVICE, F_RANGE, F_DRYER, F_WH, *HVAC_FIELDS, F_TUB, F_OTHER)
EV_FIELDS = (F_SQFT, F_SERVICE, F_CHARGER, F_RANGE, F_DRYER, F_WH, *HVAC_FIELDS, F_TUB, F_OTHER)
WIRE_FIELDS = (F_CHARGER, F_RUN, F_LOC, F_TERMS)
DETACHED_LABELS = {0: "Attached garage or exterior wall", 1: "Detached garage"}


def parse(fields: tuple[Field, ...], params: dict) -> tuple[dict, list[str]]:
    """Numbers from query or JSON input; blank uses the default. Returns (values, errors). A rejected field
    keeps its default in `values` so the form can be redrawn; nothing is calculated when there are errors."""
    values, errors = {}, []
    for f in fields:
        values[f.name] = f.default
        raw = params.get(f.name)
        raw = raw.strip() if isinstance(raw, str) else raw
        if raw in (None, ""):
            continue
        try:
            number = float(str(raw).replace(",", ""))
        except (ValueError, OverflowError):
            errors.append(f"{f.label}: enter a number.")
            continue
        if not math.isfinite(number):
            errors.append(f"{f.label}: enter a number.")
        elif f.choices and number not in f.choices:
            errors.append(f"{f.label}: pick one of the listed options.")
        elif not f.choices and not f.min <= number <= f.max:
            errors.append(f"{f.label}: enter a value from {f.min:,} to {f.max:,}.")
        elif not f.decimal and not number.is_integer():
            errors.append(f"{f.label}: enter a whole number.")
        else:
            values[f.name] = int(number) if number.is_integer() else number
    return values, errors


HIRING_PATH = "/for/homeowners-hiring-an-electrician/"
MIN_220_82_SERVICE_AMPS = 100
RESISTANCE_HEAT_FACTOR = {1: 0.65, 2: 0.40}  # 220.82(C): space heat by number of separately controlled units
SUPPLEMENTAL_HEAT_FACTOR = 0.65  # 220.82(C): a heat pump's supplemental heat


def _guidance(job: str, summary: str, options: list[str]) -> dict:
    return {"summary": summary, "options": options, "links": [
        [HIRING_PATH, "Getting ready to hire an electrician"], [f"/start/?job={job}&role=diy", "Start a permit packet"]]}


def heating_load(v: dict) -> tuple[float, list[str]]:
    """The heating VA to compare with cooling under 220.82(C), and notes saying how it was figured."""
    heat, kind = v.get("heating_va", 0), v.get("heating_type", 0)
    supp, locked_out = v.get("supplemental_va", 0), v.get("heat_lockout", 0) == 1
    if supp:
        if kind != 0:
            raise ValueError("Backup heat applies to a heat pump. Pick the heat pump heating type, or enter 0 backup heat.")
        if not heat:
            raise ValueError("Enter the heat pump compressor VA in the electric heating field along with its backup heat.")
        backup = supp * SUPPLEMENTAL_HEAT_FACTOR
        if locked_out:
            return max(heat, backup), [
                f"Heat pump with backup heat that can't run with the compressor (220.82(C)): the larger of the "
                f"compressor at 100% ({heat:,.0f} VA) and the backup heat at 65% ({backup:,.0f} VA)."]
        return heat + backup, [
            f"Heat pump with backup heat (220.82(C)): compressor at 100% ({heat:,.0f} VA) plus backup heat at 65% "
            f"({backup:,.0f} VA). Enter the compressor as heating even if it is also the cooling unit."]
    if kind and heat:
        factor = RESISTANCE_HEAT_FACTOR[kind]
        return heat * factor, [
            f"Resistance space heat counted at {factor:.0%} of {heat:,.0f} VA (220.82(C)), based on the number of "
            "separately controlled units you picked. Electric thermal storage and other heat that runs at full "
            "nameplate continuously must be counted at 100%."]
    return heat, []


def _home(v: dict) -> HomeLoads:
    return HomeLoads(
        square_feet=v["sq_ft"], range_va=v.get("range_va", 0), dryer_va=v.get("dryer_va", 0),
        water_heater_va=v.get("water_heater_va", 0), heating_va=heating_load(v)[0],
        cooling_va=v.get("cooling_va", 0), hot_tub_or_pool_va=v.get("hot_tub_or_pool_va", 0),
        other_va=v.get("other_va", 0))


def _packet_prefill(v: dict) -> dict:
    """The packet builder has one heating field, counted at 100%. Hand it the larger of the nameplate and the
    220.82(C) figure, so the packet never counts less heating than this result did."""
    effective = math.ceil(heating_load(v)[0])
    return {"heating_va": effective} if effective > v.get("heating_va", 0) else {}


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
    if load.service_amps < MIN_220_82_SERVICE_AMPS:
        return "tight", f"Not verified: this method needs a service of at least {MIN_220_82_SERVICE_AMPS} A"
    if load.percent_of_service >= 80:
        return "tight", f"Fits, at {load.percent_of_service:.0f}% of the service"
    return "ok", f"Fits, at {load.percent_of_service:.0f}% of the service"


def _service_notes(load) -> list[str]:
    if load.service_amps >= MIN_220_82_SERVICE_AMPS:
        return []
    return [f"220.82 applies only where the service or feeder is rated {MIN_220_82_SERVICE_AMPS} A or more. For a "
            f"{load.service_amps} A service these numbers are for reference: have an electrician run the standard "
            "method (Article 220 Part III) or the existing-dwelling method (220.83) where it applies."]


def _load_guidance(load, job: str, new_load: bool) -> dict | None:
    over = load.computed_amps > load.service_amps
    if not over and load.service_amps >= MIN_220_82_SERVICE_AMPS:
        return None
    summary = ("On paper this service is over capacity. That is common and usually solvable. It does not by itself "
               "mean something is unsafe today." if over else
               "This method can't confirm capacity on a service this small. An electrician can check it another way.")
    options = [
        "Check the inputs against the nameplates. Gas appliances count as 0 VA.",
        "Ask about measured demand (220.87): 12 months of utility maximum demand, or a 30-day recording, at 125% "
        "plus the new load. Your building department decides whether it accepts it, and solar or load shaving can limit it.",
    ]
    if new_load:
        options.append("Use a listed energy management system or load management for the new load (EVEMS, 625.42 and "
                       "Article 750). The load calculation then uses the maximum the system allows.")
        options.append("Pick a smaller load, such as a lower charger setting that the equipment lists and can lock in.")
    else:
        options.append("Before adding anything new, ask about listed energy management (625.42 and Article 750 for EV charging).")
    options.append("Upgrade the service or panel, sized by a new load calculation.")
    return _guidance(job, summary, options)


def residential_load(v: dict) -> dict:
    load = calculate_load(_home(v), service_amps=v["service_amps"])
    status, text = _status(load)
    return {"status": status, "headline": f"{load.computed_amps:.1f} A of {load.service_amps} A. {text}.",
            "rows": _load_rows(load), "computed_amps": round(load.computed_amps, 1), "spare_amps": round(load.spare_amps, 1),
            "nec": ["220.82", "220.87"], "notes": [
                *_service_notes(load), *heating_load(v)[1],
                "Optional dwelling method (220.82). Gas appliances count as 0 VA. When adding load to an existing home, "
                "some building departments ask for 220.83 instead.",
                "If this shows the service is over capacity, 12 months of utility demand data may support a different "
                "result (220.87). Your building department decides whether it accepts that."],
            "guidance": _load_guidance(load, "panel-upgrade", new_load=False), "prefill": _packet_prefill(v)}


def ev_load(v: dict) -> dict:
    job = EvJob(customer="", address="", contractor="", license_number="", home=_home(v), service_amps=v["service_amps"],
                open_breaker_spaces=2, charger_amps=v["charger_amps"], location="attached_garage", run_ft=25, trench_ft=0)
    packet = build_ev_packet(job)  # the packet generator itself
    load = packet.load
    status, text = _status(load)
    notes = [f"The charger counts at 100% of its output: {v['charger_amps']} A x {VOLTS} V = {packet.charger_va:,} VA. "
             "The 125% continuous-load factor (625.41) sizes the breaker and wire.",
             *_service_notes(load), *heating_load(v)[1]]
    with_125 = load.computed_amps + (CONTINUOUS_FACTOR - 1) * v["charger_amps"]
    if status != "over" and with_125 > load.service_amps:
        status, text = "tight", f"Fits at 100%, but not if the charger is counted at 125% ({with_125:.1f} A)"
        notes.append("Some reviewers ask for a charger without load management to count at 125% in the service "
                     "calculation too. Ask your building department before relying on this result.")
    if packet.charger_va < 7200:
        notes.append("If your city uses the standard method instead, the 2023 NEC counts EV charging equipment at "
                     "7,200 VA or nameplate, whichever is larger (220.57).")
    if status == "over" and load.service_amps >= MIN_220_82_SERVICE_AMPS:
        fits = largest_charger_that_fits(load, packet.charger_va)
        notes.append(f"A {fits} A charger fits this service." if fits else "No common charger size fits this service.")
        notes.append("Options: load management, a service upgrade, or 12 months of utility demand data (220.87).")
    return {"status": status, "headline": f"{load.computed_amps:.1f} A of {load.service_amps} A with a {v['charger_amps']} A charger. {text}.",
            "rows": _load_rows(load), "computed_amps": round(load.computed_amps, 1), "spare_amps": round(load.spare_amps, 1),
            "nec": ["220.82", "220.87", "625.41"], "notes": notes,
            "guidance": _load_guidance(load, "ev-charger", new_load=True), "prefill": _packet_prefill(v)}


VD_NOTE = ("The 3% voltage drop limit is an NEC informational note (a design recommendation, with 5% for feeder and "
           "branch combined), not an enforceable rule unless your city or the equipment maker requires it.")
SCH40_FILL, SCH40_NAME = SERVICE_CONDUIT_FILL_SQ_IN["PVC"], "Schedule 40 PVC"
# NEC Chapter 9 Table 4, Article 352 Schedule 80, 40% fill.
PVC80_FILL_SQ_IN = (('3/4"', 0.164), ('1"', 0.275), ('1-1/4"', 0.495), ('1-1/2"', 0.684),
                    ('2"', 1.150), ('2-1/2"', 1.647), ('3"', 2.577))


def _wire_area(size: str) -> float:
    return SMALL_GROUND_AREA_SQ_IN.get(size) or next(c.area_sq_in for c in COPPER_75C if c.size == size)


def _sch80_notes(conduit_type: str, fill_sq_in: float, sch40_size: str) -> list[str]:
    """PVC sizes here are Schedule 40. Schedule 80 has a smaller bore, so say when it needs a larger size."""
    if conduit_type != "PVC":
        return []
    size = next((name for name, capacity in PVC80_FILL_SQ_IN if fill_sq_in <= capacity), None)
    if size == sch40_size:
        return []
    need = f"needs {size}" if size else "is too small even at 3 inch"
    return [f"This PVC size is for Schedule 40. Schedule 80, required where the conduit is exposed to physical damage "
            f"such as risers out of the ground, {need} for these conductors (Chapter 9 Table 4)."]


def wire_breaker(v: dict) -> dict:
    amps, run = v["charger_amps"], v["run_ft"]
    terms_75c = v.get("terminals_75c", 1) == 1
    circuit = size_circuit(amps, run, continuous=True, volts=VOLTS)  # as build_ev_packet does
    breaker, wire, ground = circuit.breaker, circuit.wire.size, circuit.ground
    ampacity, drop, percent = circuit.wire.ampacity_75c, circuit.voltage_drop_volts, circuit.voltage_drop_percent
    upsized, emt = circuit.upsized_for_voltage_drop, conduit_size(circuit, "EMT")
    if not terms_75c:
        branch = size_branch(breaker=breaker, load_amps=amps, run_ft=run, terminals_75c=False)
        wire, ground, upsized = branch.wire.size, branch.egc, branch.upsized
        ampacity, drop, percent = branch.wire.ampacity_60c, branch.vd_volts, branch.vd_percent
        emt = branch_conduit(branch, 2, "EMT")
    column = 75 if terms_75c else 60
    disconnect = v["detached"] == 1 or amps > DISCONNECT_REQUIRED_ABOVE_AMPS
    rows = [["Continuous load", f"{amps} A x 125% = {circuit.required_amps:g} A"],
            ["Breaker", f"{breaker} A, 2-pole"],
            [f"Copper conductors ({column}°C column)", f"#{wire} AWG, rated {ampacity} A"],
            ["Equipment ground", f"#{ground} AWG"],
            ["Voltage drop", f"{drop:.1f} V, {percent:.1f}% over {run} ft"],
            ["EMT conduit (2 hots + ground)", emt],
            ["Disconnect", "Likely required" if disconnect else "Not required by this check"]]
    notes = []
    if upsized:
        notes.append(f"The wire was upsized to #{wire} AWG to hold voltage drop to 3%, so the ground is #{ground} AWG (250.122(B)).")
    if percent > 3:
        notes.append("Voltage drop is above 3% even at the largest wire size. Shorten the run or redesign the circuit.")
    notes.append(VD_NOTE)
    if disconnect:
        notes.append("A disconnect is flagged for a detached garage or a breaker over 60 A. Your city may differ.")
    if terms_75c:
        notes.append("Sized at the 75°C column. Confirm the charger and breaker terminals are marked for 75°C "
                     "(110.14(C)(1)(a)). NM-B cable must use the 60°C choice (334.80) and is not allowed in wet or underground locations.")
    else:
        notes.append("Sized at the 60°C column. NM-B cable is for dry indoor locations only, not outdoors or in underground conduit.")
    return {"status": "ok" if percent <= 3 else "over",
            "headline": f"{breaker} A breaker, #{wire} AWG copper, #{ground} AWG ground.",
            "rows": rows, "breaker": breaker, "wire": wire, "ground": ground,
            "nec": ["625.41", "210.19(A)(1)", "240.4(D)", "310.16", "110.14(C)", "250.122"], "notes": notes}


BUS_SIZES = (100, 125, 150, 200, 225, 400)
MAIN_BREAKER_SIZES = (60, 100, 125, 150, 175, 200, 225)
PV_BREAKER_SIZES = (15, 20, 25, 30, 35, 40, 45, 50, 60, 70, 80)
SUBPANEL_BREAKER_SIZES = (40, 50, 60, 70, 80, 90, 100, 125, 150, 200)
HOT_TUB_AMPS_CHOICES = (20, 24, 30, 32, 36, 40, 48)
SUBPANEL_FIELDS = (
    Field("breaker_amps", "Feeder breaker size (amps)", 100, choices=SUBPANEL_BREAKER_SIZES),
    Field("material", "Conductor material", 0, choices=(0, 1), choice_labels={0: "Aluminum (THWN-2 / XHHW-2)", 1: "Copper (THWN-2)"}),
    Field("run_ft", "One-way feeder length (ft)", 50, 1, 400),
    Field("conduit", "Conduit type", 0, choices=(0, 1), choice_labels={0: "PVC (Schedule 40)", 1: "EMT (Metal)"}),
    Field("detached", "Subpanel location", 0, choices=(0, 1), choice_labels={0: "Same building or attached garage", 1: "Detached building or shed"}),
)
SOLAR_FIELDS = (
    Field("bus_amps", "Main panel busbar rating (amps)", 200, choices=BUS_SIZES),
    Field("main_amps", "Main breaker rating (amps)", 200, choices=MAIN_BREAKER_SIZES),
    Field("pv_breaker_amps", "Solar PV backfeed breaker (amps)", 40, choices=PV_BREAKER_SIZES),
    Field("inverter_amps", "Inverter max continuous output (amps, optional)", 0, 0, 100, hint="From the inverter data sheet; add up all inverters. 0 checks with the breaker rating instead.", decimal=True),
    Field("panel_layout", "Where is the solar breaker on the bus?", 0, choices=(0, 1, 2), choice_labels={
        0: "Opposite end from the main breaker", 1: "Not at the opposite end, or not sure", 2: "Center-fed panel (main in the middle)"}),
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
    notes = ["Isolate neutral and ground buses in the subpanel (NEC 250.24(A)(5)).",
             "Sized at the 75°C column: confirm both breaker and panel lugs are marked 75°C (110.14(C)). NM-B cable, or "
             "SE cable run in thermal insulation, is limited to the 60°C column and usually needs a larger size.",
             f"This sizes the conductors to the {breaker} A breaker. It does not check that the load fits: run a load "
             "calculation for the subpanel loads and for the main service.", VD_NOTE]
    if material == "aluminum":
        notes.append("Conduit fill uses THWN-2 wire areas. XHHW-2 and compact aluminum differ, so check the actual "
                     "wire in Chapter 9 Table 5 or 5A.")
    fill = 3 * feeder.conductor.area_sq_in + _wire_area(feeder.egc)
    notes += _sch80_notes(conduit_type, fill, raceway)
    if feeder.upsized:
        notes.append(f"Upsized to {wire_label(feeder.conductor.size)} for voltage drop; EGC upsized to {wire_label(feeder.egc)} (NEC 250.122(B)).")
    if detached:
        notes.append("Detached building requires disconnect (NEC 225.31) and ground rods (NEC 250.32(A)). Plan on two "
                     "rods unless one is shown to measure 25 ohms or less (250.53(A)(2)).")
    guidance = None if feeder.vd_percent <= 3 else _guidance(
        "subpanel", f"Voltage drop is {feeder.vd_percent:.1f}%, above the 3% design target, even at the largest size this "
        "tool checks. This is a design problem with practical fixes.", [
            "Shorten the route, or move the subpanel closer to the main panel.",
            "Calculate the real subpanel load. This check assumes 80% of the breaker; a smaller calculated load or feeder breaker drops less.",
            "Have an electrician design a larger conductor or parallel run and confirm the lugs accept it.",
            "If the added load is the issue, ask about load management (Article 750), or re-evaluate the main breaker and service with a new load calculation.",
        ])
    return {
        "status": "ok" if feeder.vd_percent <= 3 else "over",
        "guidance": guidance,
        "headline": f"{wire_label(feeder.conductor.size)} {mat} hots & neutral, {wire_label(feeder.egc)} ground in {raceway} {conduit_type}.",
        "rows": rows, "wire": feeder.conductor.size, "ground": feeder.egc, "conduit": raceway,
        "nec": ["310.16", "250.122", "250.24(A)(5)", "250.32", "300.5"], "notes": notes,
    }


def solar_120_rule(v: dict) -> dict:
    bus, main, pv = v["bus_amps"], v["main_amps"], v["pv_breaker_amps"]
    inverter, layout = v.get("inverter_amps", 0), v.get("panel_layout", 0)
    # The rule adds 125% of the inverter output. Without it, the breaker (never smaller than that) stands in.
    source = inverter * CONTINUOUS_FACTOR if inverter else pv  # compared unrounded
    opposite = layout == 0
    percent = 120 if opposite else 100
    max_total = bus * percent // 100
    actual_total = main + source
    max_pv_allowed = max(0, max_total - main) if main <= bus else 0
    problems = []
    if main > bus:
        problems.append(f"The {main} A main breaker is larger than the {bus} A busbar. Check both ratings on the panel label (408.36).")
    if inverter and pv < source:
        problems.append(f"The {pv} A solar breaker is smaller than 125% of the inverter output ({source:g} A) (690.9(B), 705.30).")
    within = solar_fits(bus, main, source) if opposite else actual_total <= bus
    fits = within and not problems
    source_text = f"{inverter:g} A x 125% = {source:g} A" if inverter else f"{pv} A solar breaker"
    rows = [
        ["Panel busbar rating", f"{bus} A"],
        [f"{percent}% busbar limit (NEC 705.12)", f"{bus} A x {percent}% = {max_total} A"],
        ["Solar source counted", source_text],
        ["Main breaker + solar source", f"{main} A + {source:g} A = {actual_total:g} A"],
        ["Maximum solar source with this main", f"{max_pv_allowed} A"],
        ["PV breaker placement", "Opposite end of the busbar from the main breaker" if opposite else
         "Center-fed: counted at 100%" if layout == 2 else "Not at the opposite end: counted at 100%"],
    ]
    notes = [*problems,
             "The 120% busbar rule is 705.12(B)(3)(2) in the 2020 NEC and 705.12(B)(2) in the 2023 NEC. Use the edition your city enforces."]
    if inverter:
        notes.append("The rule counts 125% of the inverter's continuous output current, not the breaker size. Some reviewers still compare breaker ratings.")
    else:
        notes.append("The code adds 125% of inverter output current. This used the breaker rating, which is the same or more. "
                     "Enter the inverter output for the code figure.")
    if layout == 2:
        notes.append("The 2023 NEC allows the 120% rule at one end (not both) of a center-fed panelboard in a dwelling. "
                     "Earlier editions don't without engineering, so this check uses 100%. Confirm with your city.")
    if opposite:
        notes.append("The solar breaker must stay at the far end, with a permanent warning label not to relocate it. "
                     "A plug-in backfed breaker also needs to be secured (408.36(D)).")
    guidance = None
    if fits:
        notes.append(f"Passes with {max_total - actual_total:g} A of busbar margin remaining.")
    else:
        options = []
        if not within:
            notes.append(f"Exceeds the {percent}% limit by {actual_total - max_total:g} A.")
        if inverter and pv < source:
            options.append(f"Use a solar breaker of at least {source:g} A that the inverter instructions allow, then check the bus again.")
        if not within and not inverter:
            options.append("Enter the inverter's continuous output above. The code counts 125% of it, which can be less than the breaker rating.")
        derated = [] if within else [size for size in MAIN_BREAKER_SIZES if size <= bus and size < main and size + source <= max_total]
        if derated:
            options.append(f"Re-evaluate the main breaker: {max(derated)} A or smaller meets this busbar limit, only if "
                           "a new Article 220 load calculation fits under it and the panel lists that breaker.")
        needed = next((size for size in BUS_SIZES if main <= size and main + source <= size * percent / 100), None)
        if needed and needed > bus:
            options.append(f"Replace the panel with one that has at least a {needed} A busbar, sized with the service and load calculation.")
        options += [] if within else [
            "Use a smaller inverter, or a listed power control system that limits current (705.13).",
            "Have an electrician check another 705.12 busbar method, such as the sum of all breakers excluding the main staying within the bus rating, or engineered supervision.",
            "Connect on the supply side of the main (705.11), designed by a qualified installer and accepted by the utility.",
        ]
        if main > bus:
            options.insert(0, "Confirm the busbar and main breaker ratings on the panel label. A panel can't be protected above its rating.")
        if not opposite and not within:
            options.insert(0, "See whether the solar breaker can go at the opposite end of an end-fed bus, which allows 120%.")
        guidance = _guidance("solar-battery", "This combination does not pass this busbar check. Several code-compliant "
                             "routes may still work.", options)
    return {
        "status": "ok" if fits else "over",
        "headline": f"{'PASS' if fits else 'FAIL'}: {actual_total:g} A combined vs {max_total} A max allowed ({bus} A bus x {percent}%)."
                    + (" Check the breaker ratings." if problems else ""),
        "rows": rows, "fits": fits, "max_pv_allowed": max_pv_allowed,
        "nec": ["705.12(B)(3)(2)", "705.11", "408.36"], "notes": notes, "guidance": guidance,
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
        ["PVC conduit (40% fill)", f"{pvc} {SCH40_NAME} (18 in cover in general locations, NEC 300.5)"],
        ["Disconnect (NEC 680.13)", "At least 5 ft from water, within sight of spa"],
    ]
    notes = ["Outdoor spas require an insulated green copper EGC (NEC 680.42(A)(1)) and a disconnect >= 5 ft from water (NEC 680.13)."]
    if branch.upsized:
        notes.append(f"Upsized to #{branch.wire.size} AWG for voltage drop; ground upsized to #{branch.egc} AWG (NEC 250.122(B)).")
    notes += [
        "The equipment nameplate and instructions govern: don't exceed the maximum breaker size, and meet the minimum circuit ampacity they list (110.3(B)).",
        "NM-B cable is not allowed outdoors, in wet locations or underground. Use wet-rated conductors in raceway there.",
        "Burial depth changes under driveways and slabs, and direct-buried UF-B needs more cover. Check the conduit and trench calculator.",
        VD_NOTE,
    ]
    notes += _sch80_notes("PVC", n_cond * branch.wire.area_sq_in + _wire_area(branch.egc), pvc)
    return {
        "status": "ok" if branch.vd_percent <= 3 else "over",
        "headline": f"{breaker} A 2-pole GFCI breaker, #{branch.wire.size} AWG copper, #{branch.egc} AWG insulated ground.",
        "rows": rows, "breaker": breaker, "wire": branch.wire.size, "ground": branch.egc,
        "nec": ["680.44", "680.13", "310.16", "250.122", "300.5"], "notes": notes,
    }


NEC_TEXT = {
    "220.82": "Optional dwelling load calculation (service or feeder of 100 A or more): 3 VA per sq ft, small appliance and laundry circuits, nameplate appliances, first 10,000 VA at 100% and the rest at 40%, plus the largest heating or cooling selection.",
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
    "300.5": "Minimum underground cover depends on wiring method and location. In general locations: 18 in for PVC conduit, 6 in for RMC, 24 in for UF-B cable. Driveways, streets, slabs and buildings differ.",
    "110.14(C)": "Conductor ampacity is limited by the temperature rating of the terminals it lands on.",
    "Chapter 9": "Table 1 conduit fill: 53% for one conductor, 31% for two, 40% for three or more. Table 4 gives raceway areas, Table 5 conductor areas.",
    "310.15(C)(1)": "Ampacity adjustment when more than three current-carrying conductors share a raceway.",
    "702.5": "Transfer equipment, including a listed interlock, must keep the generator and utility from being connected together.",
    "702.7": "Signs identifying an on-site standby power source.",
    "250.30": "Grounding for a separately derived system, where the transfer equipment switches the neutral.",
    "705.11": "Supply-side (line-side) connection of a power source.",
    "408.36": "Overcurrent protection of panelboards; backfed plug-in breakers must be secured.",
    "705.12(B)(3)(2)": "Main breaker plus solar PV breaker may not exceed 120% of the panel busbar rating.",
    "680.44": "GFCI protection is required for spa and hot tub outlets and circuits.",
    "680.13": "Maintenance disconnect must be accessible, within sight, and at least 5 ft from the spa.",
})

CONDUIT_WIRE_CHOICES = (12, 10, 8, 6, 4, 3, 2, 1, 101, 201, 301, 401)
CONDUIT_WIRE_LABELS = {
    12: "#12 AWG THWN-2", 10: "#10 AWG THWN-2", 8: "#8 AWG THWN-2", 6: "#6 AWG THWN-2",
    4: "#4 AWG THWN-2", 3: "#3 AWG THWN-2", 2: "#2 AWG THWN-2", 1: "#1 AWG THWN-2",
    101: "#1/0 AWG THWN-2", 201: "#2/0 AWG THWN-2", 301: "#3/0 AWG THWN-2", 401: "#4/0 AWG THWN-2",
}
_WIRE_CODE_TO_SIZE = {101: "1/0", 201: "2/0", 301: "3/0", 401: "4/0"}
CONDUIT_FIELDS = (
    Field("wire_size", "Current-carrying conductor gauge", 6, choices=CONDUIT_WIRE_CHOICES, choice_labels=CONDUIT_WIRE_LABELS),
    Field("conductor_count", "Number of current-carrying wires (hots + neutral)", 2, 1, 12),
    Field("ground_size", "Equipment ground wire gauge", 10, choices=(12, 10, 8, 6, 4), choice_labels={k: f"#{k} AWG" for k in (12, 10, 8, 6, 4)}),
    Field("conduit_type", "Conduit material", 0, choices=(0, 1, 2, 3), choice_labels={0: "Schedule 40 PVC", 1: "EMT (Electrical Metallic Tubing)", 2: "RMC (Rigid Metal Conduit)", 3: "Schedule 80 PVC"}),
    Field("underground", "Installation location", 1, choices=(0, 1), choice_labels={0: "Indoor or above-ground wall", 1: "Underground trench (NEC Table 300.5)"}),
    Field("surface", "What is above the trench? (underground only)", 0, choices=(0, 1, 2, 3, 4, 5), choice_labels={
        0: "Yard or other general location", 1: "One- or two-family home driveway or parking area",
        2: "Street, road, alley, or other driveway or parking lot", 3: "2 in concrete cover in the trench",
        4: "4 in exterior concrete slab, no vehicles, extending 6 in past the run", 5: "Under a building"}),
    Field("gfci_20a", "Residential branch circuit, 120 V, 20 A or less, GFCI protected?", 0, choices=(0, 1), choice_labels={0: "No", 1: "Yes (shallower cover exception)"}),
)
# NEC Table 300.5 minimum cover in inches by location: (direct-burial cable, RMC/IMC, PVC, 120 V 20 A GFCI circuit)
BURIAL_COVER_IN = ((24, 6, 18, 12), (18, 18, 18, 12), (24, 24, 24, 24), (18, 6, 12, 6), (18, 4, 4, 4), (0, 0, 0, 0))


def conduit_fill_trench(v: dict) -> dict:
    area_map = {w.size: w.area_sq_in for w in WIRES}
    area_map.update({c.size: c.area_sq_in for c in COPPER_75C})
    w_size = _WIRE_CODE_TO_SIZE.get(v["wire_size"], str(v["wire_size"]))
    g_size = str(v["ground_size"])
    n_wires = v["conductor_count"]
    ctype = {0: "PVC", 1: "EMT", 2: "RMC", 3: "PVC"}[v["conduit_type"]]
    sch80 = v["conduit_type"] == 3
    name = "Schedule 80 PVC" if sch80 else ctype
    underground = v["underground"] == 1
    surface, gfci = v.get("surface", 0), v.get("gfci_20a", 0) == 1
    total_area = n_wires * area_map[w_size] + area_map[g_size]
    # Chapter 9 Table 1: two conductors (one wire plus the ground) are held to 31%, three or more to 40%.
    percent = 31 if n_wires + 1 == 2 else 40
    table = PVC80_FILL_SQ_IN if sch80 else SERVICE_CONDUIT_FILL_SQ_IN[ctype]
    chosen = next(((sz, cap * percent / 40) for sz, cap in table if total_area <= cap * percent / 40), None)
    emt_buried = underground and ctype == "EMT"
    notes = [f"NEC Chapter 9 Table 1: this raceway holds {n_wires + 1} conductors, so fill is limited to {percent}%. "
             "The tool starts at 3/4 inch."]
    if underground:
        column = BURIAL_COVER_IN[surface]
        depth = column[1] if ctype == "RMC" else column[2]
        if gfci:
            depth = min(depth, column[3])
        if emt_buried:
            cover = "Not selected by this check for earth burial (use PVC or RMC)"
        elif surface == 5:
            cover = "0 inches: under a building, the conductors must be in a raceway"
        else:
            cover = f"{depth} inches minimum {'soil cover' if surface < 3 else 'cover'}"
        if ctype == "PVC" and depth:
            notes.append(f"Cover is measured to the top of the conduit. Dig at least {depth} in plus the pipe's outside "
                         "diameter and any bedding (NEC Table 300.5).")
        if emt_buried:
            notes.append("EMT in earth is allowed only with suitable corrosion protection and approval (358.10, 300.6). "
                         "Schedule 40/80 PVC or RMC is the usual choice underground.")
        else:
            if surface != 5:
                notes.append(f"Direct-buried UF-B cable, not in this conduit, needs {min(column[0], column[3]) if gfci else column[0]} in here.")
            if gfci:
                notes.append("The shallower figure applies only to residential branch circuits of 120 V or less, with "
                             "GFCI protection and overcurrent protection of 20 A or less. It never covers a 240 V circuit.")
        notes.append("Underground raceway is a wet location: use wet-rated conductors such as THWN-2 (300.5(B)). "
                     "Cities and utilities can require more depth. Call 811 before digging.")
    else:
        cover = "Above grade (secure within 3 ft of boxes)"
    if n_wires > 3:
        factor = 80 if n_wires <= 6 else 70 if n_wires <= 9 else 50
        notes.append(f"Conduit fill is not ampacity. If all {n_wires} wires carry current, derate their ampacity to "
                     f"{factor}% (310.15(C)(1)). A neutral carrying only the unbalanced current of a 120/240 V circuit may not count.")
    notes.append("Check the equipment ground against the breaker size (250.122). This tool does not know the breaker.")
    if ctype == "PVC" and not sch80 and chosen:
        notes += _sch80_notes("PVC", total_area, chosen[0]) if percent == 40 else [
            "Schedule 80 PVC has less room than Schedule 40. Select it above if the run needs it."]
    if not chosen:
        notes.append("Split the circuits into more than one raceway, or have an electrician design a larger raceway.")
    if chosen:
        headline = f"{chosen[0]} {name} conduit ({total_area:.3f} sq in of {chosen[1]:.3f} sq in {percent}% fill limit)."
        if emt_buried:
            headline += " EMT is not selected for burial."
    else:
        headline = "Wire bundle exceeds 3-inch conduit capacity."
    return {
        "status": "ok" if chosen and not emt_buried else "over",
        "headline": headline,
        "rows": [
            ["Conductors in raceway", f"{n_wires} x #{w_size} AWG + 1 x #{g_size} AWG ground ({n_wires + 1} wires)"],
            ["Total conductor cross-section", f"{total_area:.4f} sq in (NEC Chapter 9 Table 5)"],
            [f"Minimum {name} trade size ({percent}% fill)", f"{chosen[0]} {name} (max {percent}% fill: {chosen[1]:.3f} sq in)" if chosen else f"Exceeds 3\" {name} capacity"],
            ["NEC Table 300.5 burial / mounting rule", cover],
        ],
        "conduit": chosen[0] if chosen else "", "total_area": round(total_area, 4),
        "nec": ["Chapter 9", "300.5", "310.15(C)(1)", "250.122"], "notes": notes,
    }


GEN_INLET_CHOICES = (30, 50, 100, 150, 200)
GEN_FIELDS = (
    Field("inlet_amps", "Generator inlet / transfer breaker (amps)", 50, choices=GEN_INLET_CHOICES, hint="30A (L14-30) covers up to 7.2 kW; 50A (SS2-50) covers up to 12 kW."),
    Field("transfer_type", "Transfer equipment type", 0, choices=(0, 1, 2), choice_labels={0: "Main-breaker interlock kit (2-pole)", 1: "Transfer switch, neutral not switched (or not sure)", 2: "Transfer switch that switches the neutral"}),
    Field("run_ft", "One-way feeder length, panel to inlet (ft)", 30, 1, 300),
    Field("conduit_type", "Conduit type", 0, choices=(0, 1), choice_labels={0: "Schedule 40 PVC", 1: "EMT (Metal)"}),
    Field("terminals_75c", "Terminal rating (100 A and smaller)", 0, choices=(0, 1), choice_labels={
        0: "60°C, or not sure", 1: "75°C: inlet, breaker and every terminal marked"}),
)


def generator_feeder(v: dict) -> dict:
    amps, run = v["inlet_amps"], v["run_ft"]
    transfer = v["transfer_type"]
    ctype = "EMT" if v["conduit_type"] == 1 else "PVC"
    large = amps > 100  # above 100 A, terminations are sized at 75°C (110.14(C)(1)(b))
    terms_75c = large or v.get("terminals_75c", 0) == 1
    if large:  # past the branch table's #1: size it as a feeder
        feeder = size_feeder(amps, "copper", load_amps=amps * 0.8, one_way_ft=run)
        wire, ground, percent, volts = feeder.conductor.size, feeder.egc, feeder.vd_percent, feeder.vd_volts
        raceway, area = feeder_conduit(feeder, ctype), feeder.conductor.area_sq_in
    else:
        branch = size_branch(breaker=amps, load_amps=amps * 0.8, run_ft=run, terminals_75c=terms_75c)
        wire, ground, percent, volts = branch.wire.size, branch.egc, branch.vd_percent, branch.vd_volts
        raceway, area = branch_conduit(branch, 3, ctype), branch.wire.area_sq_in
    inlet_plug = "NEMA L14-30P flanged inlet" if amps == 30 else ("NEMA SS2-50P or CS6375 flanged inlet" if amps == 50 else f"{amps} A transfer feeder")
    column = 75 if terms_75c else 60
    neutral = ("Separately derived: generator neutral bonded at the generator (NEC 250.30)" if transfer == 2 else
               "Floating neutral: no neutral-ground bond at the generator")
    rows = [
        ["Maximum 240V generator output", f"{amps * 240 / 1000:.1f} kW ({amps} A at 240 V)"],
        ["Breaker / inlet specification", f"{amps} A, 2-pole — {inlet_plug}"],
        [f"Copper conductors (4 wires, {column}°C)", f"3 x {wire_label(wire)} (2 hots + neutral) + 1 x {wire_label(ground)} ground"],
        ["Voltage drop (at 80% continuous)", f"{volts:.1f} V, {percent:.1f}% over {run} ft"],
        [f"{ctype} conduit (4 wires, 40% fill)", f"{raceway} {ctype}"],
        ["Generator neutral requirement", neutral],
    ]
    notes = [
        "The neutral stays bonded at the house service. With an interlock or a solid-neutral transfer switch, the "
        "generator must not bond neutral to ground. Change a bonded portable only as its maker allows." if transfer != 2 else
        "Because the transfer switch opens the neutral, the generator is a separately derived system and needs its own "
        "neutral-ground bond and grounding as 250.30 and the maker require.",
        "The generator's own breaker or inlet protection must not exceed what the cord, inlet and these conductors are rated for. "
        "The inlet's current rating must cover the generator connection.",
        "A manual transfer setup needs you to keep loads within the generator's output. An automatic one must be sized for the connected load (702.4).",
        "Install a permanent backup-power warning plaque at the service entrance and meter (NEC 702.7).",
    ]
    if transfer == 0:
        notes.append("Interlock kit must be UL-listed specifically for your main panel brand and model (NEC 702.5). "
                     "Secure a plug-in backfed breaker (408.36(D)).")
    if large:
        notes.append("Above 100 A this is a fixed standby feeder, not a portable cord and inlet. Have the equipment and design confirmed.")
    elif terms_75c:
        notes.append("Sized at 75°C only because you confirmed every terminal is marked for it (110.14(C)(1)(a)). Many inlets are not.")
    else:
        notes.append("Sized at the 60°C column. If the inlet, breaker and all terminals are marked 75°C, a smaller wire may be allowed.")
    notes.append("Run wet-rated conductors in any outdoor or underground raceway.")
    notes.append(VD_NOTE)
    notes += _sch80_notes(ctype, 3 * area + _wire_area(ground), raceway)
    return {
        "status": "ok" if percent <= 3 else "over",
        "headline": f"{amps} A breaker, {wire_label(wire)} AWG 4-wire copper, {wire_label(ground)} AWG ground in {raceway} {ctype}.",
        "rows": rows, "breaker": amps, "wire": wire, "ground": ground,
        "nec": ["310.16", "110.14(C)", "250.122", "702.5", "702.7", "300.5"] + (["250.30"] if transfer == 2 else []), "notes": notes,
    }


def nec_rows(refs: list[str]) -> list[tuple[str, str]]:
    return [(f"NEC {ref}", NEC_TEXT[ref]) for ref in refs if ref in NEC_TEXT]
