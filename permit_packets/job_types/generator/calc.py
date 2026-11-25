"""Residential generator interlock & transfer switch engineering checks (NEC Article 702)."""
from __future__ import annotations

from dataclasses import dataclass, field, replace
from typing import Literal

from permit_packets.core.checks import Check
from permit_packets.core.conductors import (
    FEEDER_VOLTS, MAX_FEEDER_VOLTAGE_DROP_PERCENT, Branch, branch_conduit, size_branch, wire_label,
)
from permit_packets.core.heat import exposure_flags
from permit_packets.core.job_inputs import display_number
from permit_packets.core.load_calculation import HomeLoads, LoadCalculation, calculate_load
from permit_packets.core.panel_data import gec_check, interrupting_rating_check, panel_flags
from permit_packets.core.panel_schedule import ExistingCircuit, MISSING_FLAG, panel_schedule_check
from permit_packets.core.property_plan import PropertyPlan
from permit_packets.core.raceways import above_ground, outdoor_cable
from permit_packets.jurisdictions import ORO_VALLEY, Jurisdiction

TransferType = Literal["interlock", "manual_transfer_switch", "automatic_transfer_switch"]
NeutralType = Literal["floating", "bonded"]
GenLocation = Literal["exterior_wall", "detached_pad"]
Wiring = Literal["PVC", "EMT", "cable"]

TRANSFER_LABELS = {
    "interlock": "UL-listed main-breaker interlock kit",
    "manual_transfer_switch": "manual transfer switch",
    "automatic_transfer_switch": "automatic transfer switch (ATS)",
}
TRANSFER_TITLES = {
    "interlock": "Generator Interlock",
    "manual_transfer_switch": "Manual Transfer Switch",
    "automatic_transfer_switch": "Standby Generator & ATS",
}
LOCATION_LABELS = {"exterior_wall": "exterior wall inlet", "detached_pad": "exterior pad"}
FUEL_LABELS = {
    "natural_gas": "Natural gas",
    "propane": "Propane",
    "diesel": "Diesel",
    "gasoline": "Gasoline",
}
DEGREE = "\N{DEGREE SIGN}"
BURIAL_COVER_IN = 18


@dataclass(frozen=True)
class GeneratorJob:
    customer: str
    address: str
    contractor: str
    license_number: str
    home: HomeLoads
    service_amps: int
    open_breaker_spaces: int
    transfer_type: TransferType
    generator_kw: float
    inlet_amps: int
    generator_model: str = ""
    fuel_type: Literal["natural_gas", "propane", "diesel", "gasoline"] | None = None
    neutral_type: NeutralType = "floating"
    location: GenLocation = "exterior_wall"
    wiring: Wiring = "PVC"
    run_ft: int = 25
    trench_ft: int = 0
    terminals_75c: bool = True
    jurisdiction: Jurisdiction = ORO_VALLEY
    plan: PropertyPlan | None = None
    existing_circuits: tuple[ExistingCircuit, ...] = ()
    available_fault_current_a: int | None = None
    equipment_aic_ka: int = 10
    panel_location: str = ""
    panel_bus_amps: int | None = None
    panel_main: str | None = None
    gec_size: str = ""
    data_sheet_attached: bool = False

    @property
    def sun_exposed(self) -> bool:
        return True

    @property
    def design_ambient_f(self) -> int | None:
        return self.jurisdiction.design_ambient_f

    @property
    def generator_amps(self) -> float:
        return round(self.generator_kw * 1000 / FEEDER_VOLTS, 1)

    @property
    def spaces_needed(self) -> int:
        return 2 if self.transfer_type == "interlock" else 0


@dataclass(frozen=True)
class GeneratorPacket:
    job: GeneratorJob
    load: LoadCalculation
    breaker: int
    branch: Branch
    conduit_size: str | None
    checks: list[Check]
    flags: list[str] = field(default_factory=list)
    raceway_text: str = ""

    @property
    def cable_type(self) -> str | None:
        return None if self.conduit_size is not None else "UF-B"

    @property
    def ready(self) -> bool:
        return all(check.passed or check.neutral for check in self.checks)


def build_generator_packet(job: GeneratorJob) -> GeneratorPacket:
    notes: list[str] = []
    if job.wiring == "cable":
        drawn = outdoor_cable(job.jurisdiction, "cable", outdoors=True)
    else:
        drawn = above_ground(job.jurisdiction, job.wiring, "generator feeder")
    if drawn.note:
        notes.append(drawn.note)
    if drawn.kind != job.wiring and job.wiring == "cable":
        job = replace(job, wiring=drawn.kind)
    if job.wiring == "cable" and job.terminals_75c:
        job = replace(job, terminals_75c=False)
        notes.append("UF-B cable conductors are sized at the 60\N{DEGREE SIGN}C column (340.80).")

    load = calculate_load(job.home, service_amps=job.service_amps, volts=FEEDER_VOLTS)
    breaker = job.inlet_amps
    design_load = min(job.generator_amps, breaker * 0.8)
    branch = size_branch(
        breaker=breaker, load_amps=design_load, run_ft=job.run_ft,
        terminals_75c=job.terminals_75c, ambient_f=job.design_ambient_f,
    )
    if job.wiring == "cable":
        conduit = None
        raceway_text = ""
    elif job.trench_ft > 0 and job.wiring == "EMT":
        conduit = branch_conduit(branch, 3, "PVC")
        above = branch_conduit(branch, 3, "EMT")
        raceway_text = f"{conduit} PVC underground, {above} EMT above ground"
    else:
        conduit = branch_conduit(branch, 3, job.wiring)
        raceway_text = f"{conduit} {job.wiring}"

    neutral_ok = job.transfer_type != "interlock" or job.neutral_type == "floating"
    neutral_msg = (
        "Switched-neutral transfer equipment (NEC 250.30)"
        if job.transfer_type != "interlock"
        else ("Floating-neutral generator paired with 2-pole interlock (NEC 250.30)"
              if neutral_ok else "Bonded-neutral generator requires a 3-pole switched-neutral transfer switch (250.30)")
    )
    spaces_ok = job.open_breaker_spaces >= job.spaces_needed
    checks: list[Check] = [
        Check("Transfer & interlock (NEC 702.5)", f"{TRANSFER_LABELS[job.transfer_type].capitalize()}, {breaker} A", True),
        Check("Neutral & grounding (NEC 250.30)", neutral_msg, neutral_ok),
        Check("Panel spaces", f"{job.open_breaker_spaces} open, {job.spaces_needed} needed", spaces_ok),
        Check(
            "Conductors",
            f"3 #{branch.wire.size} Cu + #{branch.egc} EGC, {branch.wire.ampacity(job.terminals_75c)} A at {75 if job.terminals_75c else 60}{DEGREE}C",
            True,
        ),
        Check("Voltage drop", f"{branch.vd_volts:.1f} V, {branch.vd_percent:.1f}% over {job.run_ft} ft",
              branch.vd_percent <= MAX_FEEDER_VOLTAGE_DROP_PERCENT),
    ]
    if conduit:
        checks.append(Check("Conduit fill", f"4 wires in {raceway_text}, 40% fill", True))
    if job.transfer_type == "automatic_transfer_switch":
        ats_ok = load.computed_amps <= breaker
        checks.append(Check("ATS load capacity (NEC 702.4)", f"{load.computed_amps:.1f} A home demand vs {breaker} A ATS", ats_ok))
    checks += [
        interrupting_rating_check(job),
        panel_schedule_check(job),
    ]
    gec = gec_check(job, service_amps=job.service_amps)
    if gec:
        checks.append(gec)

    flags = ["Confirm UL listing of the interlock kit or transfer switch for the exact panel model (NEC 702.5)."]
    flags += notes
    flags.append("Install permanent backup-power warning plaque at the service entrance and meter (NEC 702.7).")
    if job.trench_ft:
        flags.append(f"Call 811 before trenching. Confirm {BURIAL_COVER_IN} in of cover for PVC (300.5).")
    flags += exposure_flags(job)
    if not job.existing_circuits:
        flags.append(MISSING_FLAG)
    flags += panel_flags(job, service_amps=job.service_amps)
    if job.plan is None:
        flags.append("This site plan is a schematic. Replace it with the property's plan before submitting.")
    checklist = job.jurisdiction.checklist_for("generator")
    flags += [note.text for note in checklist.notes if note.when in ({"always"} | ({"trench"} if job.trench_ft else set()))]
    flags.append(checklist.code_note)

    return GeneratorPacket(
        job=job, load=load, breaker=breaker, branch=branch, conduit_size=conduit,
        checks=checks, flags=flags, raceway_text=raceway_text,
    )
