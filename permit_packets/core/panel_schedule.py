"""Panel schedule: the panel's circuit directory with the new work marked, for every job type.

When the electrician enters the panel's existing circuits, the schedule lists them as entered.
Otherwise it lists the circuits the load calculation implies (general lighting, the required
20 A small-appliance and laundry circuits, and each appliance in the home), with the breaker left
to verify on site, and the packet flags it so the real directory goes in before submittal.
"""
from __future__ import annotations

from dataclasses import dataclass

from reportlab.lib.units import inch
from reportlab.platypus import Spacer

from permit_packets.core.load_calculation import HomeLoads
from permit_packets.core.pdf_base import BODY, CELL_BOLD, CONTENT, H1, H2, SMALL, _heads, _p, _table

VERIFY = "Verify on site"
DIRECTORY_NOTE = ("Update the panel directory on site so every circuit is legibly identified "
                  "(NEC 408.4(A)).")
MISSING_FLAG = ("The panel schedule lists the circuits the load calculation implies. Enter the panel's "
                "actual circuits before submitting.")

# HomeLoads field, label, poles (240 V appliances take two)
APPLIANCES = (
    ("range_va", "Range", 2), ("cooktop_va", "Cooktop", 2), ("oven_va", "Wall oven", 2),
    ("dryer_va", "Clothes dryer", 2), ("water_heater_va", "Water heater", 2),
    ("dishwasher_va", "Dishwasher", 1), ("disposal_va", "Disposal", 1), ("microwave_va", "Microwave", 1),
    ("hot_tub_or_pool_va", "Hot tub or pool equipment", 2), ("heating_va", "Heating", 2),
    ("cooling_va", "Air conditioner or heat pump", 2), ("other_va", "Other fixed appliance", 2),
)


@dataclass(frozen=True)
class ExistingCircuit:
    label: str
    amps: int
    poles: int = 1


@dataclass(frozen=True)
class ScheduleRow:
    label: str
    breaker: str
    poles: int
    status: str  # New, Existing, Transferred, Planned


def existing_rows(home: HomeLoads | None, entered: tuple[ExistingCircuit, ...], status: str = "Existing"
                  ) -> list[ScheduleRow]:
    if entered:
        return [ScheduleRow(c.label, f"{c.amps} A", c.poles, status) for c in entered]
    if home is None:
        return []
    rows = [
        ScheduleRow(f"General lighting and receptacles ({home.square_feet:,} sq ft)", VERIFY, 1, status),
        ScheduleRow(f"Kitchen small-appliance circuits ({home.small_appliance_circuits})", "20 A each", 1, status),
    ]
    if home.laundry_circuits:
        rows.append(ScheduleRow("Laundry circuit", "20 A", 1, status))
    for field, label, poles in APPLIANCES:
        va = getattr(home, field)
        if va:
            rows.append(ScheduleRow(f"{label} ({va:,} VA)", VERIFY, poles, status))
    return rows


def existing_circuits(entered: list[dict]) -> tuple[ExistingCircuit, ...]:
    return tuple(ExistingCircuit(**circuit) for circuit in entered)


def _rows_table(rows: list[ScheduleRow]):
    body = [_heads("Circuit", "Breaker", "Poles", "Status")]
    for row in rows:
        style = CELL_BOLD if row.status == "New" else None
        cell = (lambda text: _p(text, style)) if style else _p
        body.append([cell(row.label), cell(row.breaker), cell(str(row.poles)), cell(row.status)])
    return _table(body, [CONTENT - 3.3 * inch, 1.3 * inch, 0.8 * inch, 1.2 * inch])


def panel_schedule_page(panels: list[tuple[str, list[ScheduleRow]]], *, entered: bool,
                        spaces_note: str | None = None) -> list:
    """One table per panel. `panels` pairs a heading (e.g. "Main panel, 200 A") with its rows."""
    story = [
        _p("Panel Schedule", H1),
        _p("Circuit directory with the new work marked. "
           + ("Existing circuits as entered by the electrician." if entered else
              "Existing circuits are taken from the load calculation; replace them with the panel's "
              "actual directory before submitting."), SMALL),
        Spacer(1, 8),
    ]
    for heading, rows in panels:
        story += [_p(heading, H2), _rows_table(rows), Spacer(1, 10)]
    if spaces_note:
        story.append(_p(spaces_note, BODY))
        story.append(Spacer(1, 4))
    story.append(_p(DIRECTORY_NOTE, SMALL))
    return story
