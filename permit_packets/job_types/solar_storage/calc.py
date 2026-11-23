"""Residential Solar PV & Battery Storage (ESS) engineering checks (NEC Articles 690, 705, 706)."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from permit_packets.core.checks import Check
from permit_packets.core.conductors import (
    BUS_BACKFEED_FACTOR, FEEDER_VOLTS, MAX_FEEDER_VOLTAGE_DROP_PERCENT,
    Branch, branch_conduit, size_branch, solar_fits, wire_label,
)
from permit_packets.core.heat import exposure_flags
from permit_packets.core.job_inputs import display_number
from permit_packets.core.load_calculation import HomeLoads, LoadCalculation, calculate_load
from permit_packets.core.panel_data import gec_check, interrupting_rating_check, panel_flags
from permit_packets.core.panel_schedule import ExistingCircuit, MISSING_FLAG, panel_schedule_check
from permit_packets.core.property_plan import PropertyPlan
from permit_packets.core.raceways import above_ground
from permit_packets.jurisdictions import ORO_VALLEY, Jurisdiction

Coupling = Literal["dc_coupled", "ac_coupled", "solar_only"]
Interconnection = Literal["load_side_120", "supply_side_tap", "main_breaker_derate"]
SystemLocation = Literal["exterior_wall", "garage"]
Wiring = Literal["EMT", "PVC", "RMC"]

COUPLING_LABELS = {
    "dc_coupled": "DC-coupled hybrid solar + battery",
    "ac_coupled": "AC-coupled solar PV + battery ESS",
    "solar_only": "grid-tied solar PV system",
}
INTERCONNECTION_LABELS = {
    "load_side_120": "Load-side backfeed (NEC 705.12(B)(3)(2) 120% rule)",
    "supply_side_tap": "Supply-side service tap (NEC 705.11)",
    "main_breaker_derate": "Main breaker derate + 120% busbar rule",
}
LOCATION_LABELS = {"exterior_wall": "exterior wall", "garage": "attached garage"}
DEGREE = "\N{DEGREE SIGN}"
BURIAL_COVER_IN = 18


@dataclass(frozen=True)
class SolarStorageJob:
    customer: str
    address: str
    contractor: str
    license_number: str
    home: HomeLoads
    service_amps: int
    bus_amps: int
    open_breaker_spaces: int
    coupling: Coupling
    pv_kw_dc: float
    pv_breaker_amps: int
    battery_kwh: float = 0.0
    battery_breaker_amps: int = 0
    interconnection: Interconnection = "load_side_120"
    derated_main_amps: int | None = None
    system_model: str = ""
    location: SystemLocation = "exterior_wall"
    wiring: Wiring = "EMT"
    run_ft: int = 30
    trench_ft: int = 0
    rapid_shutdown: bool = True
    ess_disconnect: bool = True
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
        return self.location == "exterior_wall" or self.trench_ft > 0

    @property
    def design_ambient_f(self) -> int | None:
        return self.jurisdiction.design_ambient_f if self.sun_exposed else None

    @property
    def effective_main_amps(self) -> int:
        return self.derated_main_amps if (self.interconnection == "main_breaker_derate" and self.derated_main_amps) else self.service_amps

    @property
    def total_backfeed_amps(self) -> int:
        return self.pv_breaker_amps + (self.battery_breaker_amps if self.coupling == "ac_coupled" else 0)

    @property
    def spaces_needed(self) -> int:
        if self.interconnection == "supply_side_tap":
            return 0
        return 4 if self.coupling == "ac_coupled" else 2


@dataclass(frozen=True)
class SolarStoragePacket:
    job: SolarStorageJob
    load: LoadCalculation
    breaker: int
    branch: Branch
    conduit_size: str
    checks: list[Check]
    flags: list[str] = field(default_factory=list)
    raceway_text: str = ""

    @property
    def ready(self) -> bool:
        return all(check.passed or check.neutral for check in self.checks)


def build_solar_storage_packet(job: SolarStorageJob) -> SolarStoragePacket:
    notes: list[str] = []
    drawn = above_ground(job.jurisdiction, job.wiring, "solar/ESS output circuit")
    if drawn.note:
        notes.append(drawn.note)
    breaker = job.total_backfeed_amps
    branch = size_branch(
        breaker=breaker, load_amps=breaker * 0.8, run_ft=job.run_ft,
        terminals_75c=job.terminals_75c, ambient_f=job.design_ambient_f,
    )
    if job.trench_ft > 0 and job.wiring != "PVC":
        conduit = branch_conduit(branch, 3, "PVC")
        above = branch_conduit(branch, 3, drawn.kind)
        raceway_text = f"{conduit} PVC underground, {above} {drawn.kind} above ground"
    else:
        conduit = branch_conduit(branch, 3, drawn.kind)
        raceway_text = f"{conduit} {drawn.kind}"

    load = calculate_load(job.home, service_amps=job.effective_main_amps, volts=FEEDER_VOLTS)
    max_bus_total = int(job.bus_amps * BUS_BACKFEED_FACTOR)
    actual_bus_total = job.effective_main_amps + breaker
    if job.interconnection == "supply_side_tap":
        bus_ok = True
        bus_result = f"Supply-side tap ahead of {job.effective_main_amps} A main (NEC 705.11)"
    else:
        bus_ok = solar_fits(job.bus_amps, job.effective_main_amps, breaker)
        bus_result = f"{job.effective_main_amps} A main + {breaker} A backfeed = {actual_bus_total} A vs {max_bus_total} A max (120% of {job.bus_amps} A bus)"

    spaces_ok = job.open_breaker_spaces >= job.spaces_needed
    checks: list[Check] = [
        Check("Busbar 120% rule (NEC 705.12)", bus_result, bus_ok),
        Check("Service load capacity (NEC 220.82)", f"{load.computed_amps:.1f} A computed vs {job.effective_main_amps} A main breaker", load.computed_amps <= job.effective_main_amps),
        Check("Panel spaces", f"{job.open_breaker_spaces} open, {job.spaces_needed} needed", spaces_ok),
        Check("Rapid shutdown (NEC 690.12)", "Initiation & array boundary rapid shutdown included" if job.rapid_shutdown else "Rapid shutdown required for rooftop PV (NEC 690.12)", job.rapid_shutdown),
    ]
    if job.battery_kwh > 0:
        checks.append(Check("ESS disconnect (NEC 706.15)", f"{display_number(job.battery_kwh)} kWh UL 9540 ESS with lockable disconnect" if job.ess_disconnect else "Lockable ESS disconnect required (NEC 706.15)", job.ess_disconnect))
    checks += [
        Check("Conductors", f"3 #{branch.wire.size} Cu + #{branch.egc} EGC, {branch.wire.ampacity(job.terminals_75c)} A at {75 if job.terminals_75c else 60}{DEGREE}C", True),
        Check("Voltage drop", f"{branch.vd_volts:.1f} V, {branch.vd_percent:.1f}% over {job.run_ft} ft", branch.vd_percent <= MAX_FEEDER_VOLTAGE_DROP_PERCENT),
        Check("Conduit fill", f"4 wires in {raceway_text}, 40% fill", True),
        interrupting_rating_check(job),
        panel_schedule_check(job),
    ]
    gec = gec_check(job, service_amps=job.effective_main_amps)
    if gec:
        checks.append(gec)

    flags = ["Install solar backfeed breaker(s) at the opposite end of the busbar from the main breaker (NEC 705.12(B)(3)(2))."]
    flags += notes
    flags.append("Install permanent NEC 690.56(C) rapid-shutdown and NEC 705.10 / 706.21 directory placards at the service.")
    if job.battery_kwh > 0 and job.location == "garage":
        flags.append("Confirm IRC R328 / NFPA 855 battery spacing (3 ft separation) and heat detector / bollard protection in garage.")
    if job.trench_ft:
        flags.append(f"Call 811 before trenching. Confirm {BURIAL_COVER_IN} in of cover for PVC (300.5).")
    flags += exposure_flags(job)
    if not job.existing_circuits:
        flags.append(MISSING_FLAG)
    flags += panel_flags(job, service_amps=job.effective_main_amps)
    if job.plan is None:
        flags.append("This site plan is a schematic. Replace it with the property's plan before submitting.")
    checklist = job.jurisdiction.checklist_for("solar_storage")
    flags += [note.text for note in checklist.notes if note.when in ({"always"} | ({"trench"} if job.trench_ft else set()))]
    flags.append(checklist.code_note)

    return SolarStoragePacket(
        job=job, load=load, breaker=breaker, branch=branch, conduit_size=conduit,
        checks=checks, flags=flags, raceway_text=raceway_text,
    )
