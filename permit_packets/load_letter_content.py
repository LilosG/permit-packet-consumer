"""Electrical load letter page: copy, form fields, validation and the pure build_letter() function.

wave2.py routes it (page and /api/load-letter); this module holds no framework code. The letter is a planning
template: the arithmetic is voltage x current (x sqrt(3) on three-phase) and the 125% continuous-load factor, and
the page says plainly that a licensed electrician or engineer and the utility make the final call."""
from __future__ import annotations

import datetime
import math
import re
from dataclasses import dataclass

PATH = "/permit-documents/electrical-load-letter/"
NAME = "Electrical Load Letter"
TITLE = "Electrical Load Letter Sample & Template (Utility Guide)"
DESCRIPTION = ("Download or copy a free electrical load letter sample template for utility service upgrades and commercial permits. "
               "Learn what utilities require and how it differs from an NEC load calculation.")
H1 = "Electrical Load Letter: Free Sample & Template"
CARD = "Free fill-in template for the letter a utility asks for with a service upgrade, EV charger or commercial permit."
ANSWER = ("An electrical load letter is a short signed statement of a project's existing and new electrical load, in kVA and amps, "
          "that a utility or building department uses to confirm the service can carry it. Fill in the fields below to build one, "
          "then copy or print it.")
DISCLAIMER = ("Template for planning. Utility requirements, NEC adoption and plan-review rules vary by utility and by authority having "
              "jurisdiction (AHJ). Check the current requirements with yours; a licensed electrician or engineer must verify the numbers before anyone signs.")

# ---- Form ----

SYSTEMS: dict[str, tuple[str, int, bool]] = {  # key: (label, line-to-line volts, three-phase)
    "1ph-240": ("120/240 V single-phase", 240, False),
    "3ph-208": ("120/208 V three-phase", 208, True),
    "3ph-240": ("240 V three-phase", 240, True),
    "3ph-480": ("277/480 V three-phase", 480, True),
}
SERVICE_SIZES = (60, 100, 125, 150, 200, 225, 400, 600, 800, 1000, 1200, 2000)
BASES: dict[str, tuple[str, str]] = {
    "220.82": ("NEC 220.82 optional dwelling calculation", "calculated per NEC 220.82 (optional calculation for dwelling units)"),
    "220.87": ("NEC 220.87 measured existing demand", "taken from maximum demand measured over 12 months of utility billing data or a 30-day recording, at 125%, per NEC 220.87"),
    "220.40": ("NEC Article 220 standard calculation", "calculated per NEC Article 220 (standard method)"),
}


@dataclass(frozen=True)
class LField:
    name: str
    label: str
    kind: str  # text | number | select | date
    default: object
    hint: str = ""
    options: tuple[tuple[str, str], ...] = ()
    min: float = 0
    max: float = 0
    step: str = "any"


FIELDS: tuple[LField, ...] = (
    LField("project", "Project name", "text", "Example Residence: EV Charger and Panel Upgrade"),
    LField("address", "Service address", "text", "123 Example Street, Anytown, ST 00000"),
    LField("utility", "Utility", "text", "Example Electric Utility", hint="The utility the letter is addressed to."),
    LField("system", "Service voltage and phase", "select", "1ph-240", options=tuple((k, v[0]) for k, v in SYSTEMS.items())),
    LField("service_amps", "Main service rating (amps)", "select", 200, options=tuple((str(a), f"{a} A") for a in SERVICE_SIZES)),
    LField("existing_amps", "Existing demand (amps)", "number", 110, min=0, max=4000, step="1", hint="Calculated or measured demand on the existing service."),
    LField("basis", "Existing demand basis", "select", "220.82", options=tuple((k, v[0]) for k, v in BASES.items()),
           hint="NEC 220.87 adds 125% to measured demand."),
    LField("cont_kva", "New continuous load (kVA)", "number", 11.52, min=0, max=5000,
           hint="Runs 3 hours or more, such as an EV charger (48 A x 240 V = 11.52 kVA). Counted at 125%."),
    LField("noncont_kva", "New non-continuous load (kVA)", "number", 0, min=0, max=5000, hint="Counted at 100%."),
    LField("contractor", "Contractor or engineer", "text", "", hint="Optional. Left as a placeholder if blank."),
    LField("license", "License or PE number", "text", "", hint="Optional. Your state license or PE stamp number."),
    LField("date", "Letter date", "date", "", hint="Optional. Left as a placeholder if blank."),
)
FIELD_NAMES = tuple(f.name for f in FIELDS)
TEXT_MAX = 120
CONTINUOUS_FACTOR = 1.25  # NEC 210.20(A) and 625.41
EXISTING_DEMAND_FACTOR = 1.25  # NEC 220.87(1)


def defaults() -> dict:
    return {f.name: f.default for f in FIELDS}


def parse(params) -> tuple[dict, list[str]]:
    """Validated values from query or JSON input; blank uses the default. Returns (values, errors).
    Text is whitespace-collapsed and length-limited; numbers must be finite and in range."""
    values, errors = defaults(), []
    for f in FIELDS:
        raw = params.get(f.name)
        if raw is None or (str(raw).strip() == "" and f.kind != "text"):
            continue
        raw = str(raw)
        if f.kind == "text":
            text = re.sub(r"\s+", " ", raw).strip()
            if len(text) > TEXT_MAX:
                errors.append(f"{f.label}: keep it under {TEXT_MAX} characters.")
            else:
                values[f.name] = text
        elif f.kind == "select":
            if raw not in {v for v, _ in f.options}:
                errors.append(f"{f.label}: pick one of the listed options.")
            else:
                values[f.name] = int(raw) if f.name == "service_amps" else raw
        elif f.kind == "date":
            try:
                values[f.name] = datetime.date.fromisoformat(raw.strip()).isoformat()
            except ValueError:
                errors.append(f"{f.label}: use the format YYYY-MM-DD.")
        else:
            try:
                number = float(raw.replace(",", ""))
            except ValueError:
                errors.append(f"{f.label}: enter a number.")
                continue
            if not math.isfinite(number) or not f.min <= number <= f.max:
                errors.append(f"{f.label}: enter a value from {f.min:,.0f} to {f.max:,.0f}.")
            else:
                values[f.name] = number
    if not errors and not (values["existing_amps"] or values["cont_kva"] or values["noncont_kva"]):
        errors.append("Enter an existing demand or a new load greater than zero.")
    return values, errors


# ---- Letter ----

def _n(value: float, places: int = 2) -> str:
    return f"{value:,.{places}f}"


def build_letter(values: dict) -> dict:
    """The letter text and its summary rows from validated values (see parse). Pure: no clock, no I/O.

    kVA = V x A x sqrt(3) / 1000 on three-phase and V x A / 1000 on single-phase. New continuous load is counted
    at 125% (NEC 210.20(A), 625.41) and, on the NEC 220.87 basis, so is the measured existing demand."""
    label, volts, three_phase = SYSTEMS[values["system"]]
    factor = math.sqrt(3) if three_phase else 1.0
    kva_per_amp = volts * factor / 1000
    service_amps = values["service_amps"]
    basis_name, basis_text = BASES[values["basis"]]

    existing_amps = values["existing_amps"]
    existing_kva = existing_amps * kva_per_amp
    existing_factor = EXISTING_DEMAND_FACTOR if values["basis"] == "220.87" else 1.0
    existing_counted = existing_kva * existing_factor
    cont = values["cont_kva"]
    cont_counted = cont * CONTINUOUS_FACTOR
    noncont = values["noncont_kva"]
    total_kva = existing_counted + cont_counted + noncont
    total_amps = total_kva / kva_per_amp
    capacity_kva = service_amps * kva_per_amp
    spare_kva = capacity_kva - total_kva
    percent = total_kva / capacity_kva * 100
    within = total_amps <= service_amps

    rows = [
        ["Service", f"{label}, {service_amps} A main ({_n(capacity_kva)} kVA)"],
        ["Existing demand", f"{_n(existing_amps, 1)} A = {_n(existing_kva)} kVA" + (f" x 125% = {_n(existing_counted)} kVA" if existing_factor != 1 else "")],
        ["New continuous load", f"{_n(cont)} kVA x 125% = {_n(cont_counted)} kVA"],
        ["New non-continuous load", f"{_n(noncont)} kVA x 100% = {_n(noncont)} kVA"],
        ["Total calculated load", f"{_n(total_kva)} kVA = {_n(total_amps, 1)} A"],
        ["Service utilization", f"{_n(percent, 1)}% of the {service_amps} A service"],
        ["Result", f"{_n(abs(spare_kva))} kVA {'spare capacity' if within else 'over the service rating'}"],
    ]

    date = values["date"] and datetime.date.fromisoformat(values["date"]).strftime("%B %-d, %Y") or "[Date]"
    utility = values["utility"] or "[Utility name]"
    conclusion = (f"The total calculated load of {_n(total_kva)} kVA ({_n(total_amps, 1)} A) is within the {service_amps} A service rating, "
                  f"leaving {_n(spare_kva)} kVA of spare capacity." if within else
                  f"The total calculated load of {_n(total_kva)} kVA ({_n(total_amps, 1)} A) EXCEEDS the {service_amps} A service rating by "
                  f"{_n(-spare_kva)} kVA. A service upgrade or load management is required before this project can proceed.")
    lines = [
        date, "",
        f"To: {utility}, Service Planning / New Service Department",
        f"Re: Electrical load letter: {values['project'] or '[Project name]'}",
        f"Service address: {values['address'] or '[Service address]'}", "",
        "To whom it may concern:", "",
        "This letter states the electrical load for the project above so the service can be reviewed.", "",
        f"Service:  {label}, {service_amps} A main service ({_n(capacity_kva)} kVA).",
        f"Existing demand:  {_n(existing_amps, 1)} A ({_n(existing_kva)} kVA), {basis_text}.", "",
        "Load summary",
        "------------",
        *[f"{name + ':':<28}{text}" for name, text in rows[1:5]],
        f"{'Total calculated load:':<28}{_n(total_kva)} kVA ({_n(total_amps, 1)} A)",
        f"{'Service utilization:':<28}{_n(percent, 1)}%", "",
        conclusion, "",
        "Continuous loads (3 hours or more, including EV charging equipment) are counted at 125% per NEC 210.20(A) and 625.41. "
        "Equipment ratings match the manufacturer cut sheets submitted with the permit application.", "",
        "Respectfully,", "", "",
        "______________________________",
        values["contractor"] or "[Contractor or engineer name]",
        f"License / PE no.: {values['license'] or '[License number]'}",
    ]
    return {"text": "\n".join(lines), "rows": rows, "status": "within" if within else "over",
            "total_kva": round(total_kva, 2), "total_amps": round(total_amps, 1),
            "capacity_kva": round(capacity_kva, 2), "utilization_percent": round(percent, 1),
            "basis": basis_name}


# ---- Page copy ----

SECTIONS: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("What is an electrical load letter?", (
        "An electrical load letter is a one-page statement, usually signed by the contractor or engineer of record, that tells the utility or building department how much electrical load a project has and whether the service can carry it. It gives the service voltage and phase, the existing load, the new load and the total in kVA and amps.",
        "Utilities ask for one when a project changes what they have to supply: a service upgrade, a new or relocated meter, an EV charger or solar and battery system, a commercial tenant improvement or a new commercial service. Requirements and form names vary by utility, so confirm what yours accepts before you submit.")),
    ("How is a load letter different from a load calculation?", (
        "The load calculation is the working. The load letter is the summary a utility can read in a minute. The calculation shows every NEC line item and demand factor; the letter reports the result and what it means for the service. Many projects need both.",)),
    ("What does the kVA math look like?", (
        "Single-phase kVA is volts times amps divided by 1,000. Three-phase kVA is volts times amps times 1.732 divided by 1,000. A 200 A, 120/240 V single-phase service is 48 kVA; a 200 A, 120/208 V three-phase service is about 72 kVA. Continuous loads are multiplied by 1.25 before they are added, so a 48 A EV charger at 240 V (11.52 kVA) counts as 14.4 kVA.",)),
)

COMPARISON: tuple[tuple[str, str, str], ...] = (
    ("Purpose", "Tells the utility the total load and whether the service can carry it.", "Shows how the load is derived, line by line, under NEC Article 220."),
    ("Length", "One page.", "One or more pages, with a table of loads and demand factors."),
    ("Audience", "Utility service planning and the building department.", "Plan reviewer and inspector."),
    ("Contents", "Service voltage and phase, existing demand, new load, total kVA and amps, signature.", "Square footage, appliance and equipment loads, demand factors, NEC section for each line."),
    ("Signed by", "Contractor, or engineer where the utility or AHJ requires a PE stamp.", "Usually part of the permit set; signature depends on the AHJ."),
    ("Typical trigger", "Service upgrade, new meter, EV charger, solar and storage, commercial permits.", "Almost every permit that adds load to a service."),
)

CHECKLIST: tuple[tuple[str, str], ...] = (
    ("Voltage, phase and kVA math", "Use the actual service voltage and phase. kVA is V x A / 1,000 single-phase and V x A x 1.732 / 1,000 three-phase. The amps and kVA in the letter must agree with each other."),
    ("125% continuous load", "Loads that run 3 hours or more are counted at 125% (NEC 210.20(A)). EV charging equipment is a continuous load under NEC 625.41, so a 48 A charger is sized and counted as 60 A."),
    ("Existing demand basis (NEC 220.87)", "State how the existing load was found. NEC 220.87 allows maximum demand measured over 12 months of utility data (or a 30-day recording), taken at 125%, plus the new load. Attach or cite the data."),
    ("Equipment cut sheets match", "The nameplate amps and voltage in the letter match the manufacturer cut sheets in the permit set, including the charger, inverter or appliance model."),
    ("Active license or PE stamp", "The signer holds an active contractor license or professional engineer registration in the project's state, and the license number is printed on the letter. Some utilities require a PE stamp for larger loads."),
)

FAQS: tuple[tuple[str, str], ...] = (
    ("What is an electrical load letter?", "A short signed statement of a project's existing and new electrical load in kVA and amps, used by a utility or building department to confirm the service can carry it."),
    ("Is an electrical load letter the same as a load calculation?", "No. A load calculation shows the NEC Article 220 working line by line. A load letter summarizes the result for the utility. Many projects need both."),
    ("Who signs an electrical load letter?", "Usually the licensed electrical contractor or an engineer of record. Larger commercial loads, and some utilities, require a professional engineer's stamp. Ask your utility and AHJ."),
    ("Does an EV charger need a load letter?", "Some utilities ask for one when a charger is added, especially on a service upgrade or a dedicated meter. Many building departments accept the NEC load calculation alone. Check with both."),
    ("Why is a continuous load multiplied by 125%?", "NEC 210.20(A) requires the overcurrent device and conductors for a continuous load to carry 125% of it. NEC 625.41 applies the same rule to EV charging equipment."),
    ("Can I use 12 months of utility bills instead of a calculation?", "NEC 220.87 allows the existing load to come from measured maximum demand over 12 months (or a 30-day recording), taken at 125%. Your AHJ decides whether to accept it."),
    ("Is this template legally binding or a substitute for engineering?", DISCLAIMER),
)

LINKS: tuple[tuple[str, str, str], ...] = (
    ("/permit-documents/load-calculation/", "Load Calculation Guide", "The NEC Article 220 working behind the numbers in a load letter."),
    ("/permit-documents/equipment-cut-sheets/", "Equipment Cut Sheets Guide", "Match nameplate amps and volts to the manufacturer sheets."),
    ("/tools/residential-load-calculator/", "Residential Load Calculator", "Get the existing demand in amps with the NEC 220.82 method."),
    ("/tools/ev-charger-wire-breaker-size/", "EV Charger Wire & Breaker Calculator", "Size the 125% continuous-load breaker and wire for a charger."),
)
