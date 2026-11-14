"""What the one-line shows about the service and panel, and the checks that go with it."""
from __future__ import annotations

from permit_packets.core.checks import Check

MISSING_FAULT_CURRENT = "Enter the utility's available fault current"


def interrupting_rating_check(job) -> Check:
    """NEC 110.9 and 110.10: equipment must be rated to interrupt the fault current available at it."""
    fault = job.available_fault_current_a
    if not fault:
        return Check("Interrupting rating", MISSING_FAULT_CURRENT, False)
    rating = job.equipment_aic_ka * 1000
    if rating >= fault:
        return Check(
            "Interrupting rating",
            f"{job.equipment_aic_ka} kA ({rating:,} A) covers the {fault:,} A available (110.9, 110.10)", True)
    needed = -(-fault // 1000)
    return Check(
        "Interrupting rating",
        f"{job.equipment_aic_ka} kA ({rating:,} A) is below the {fault:,} A available: use equipment rated "
        f"{needed} kA or more (110.9, 110.10)", False)


def one_line_data(job) -> list[str]:
    """The lines under the one-line diagram."""
    fault = job.available_fault_current_a
    return [
        f"Available fault current at the service: {f'{fault:,} A' if fault else 'not entered'}",
        f"Panel and breaker interrupting rating: {job.equipment_aic_ka} kA (NEC 110.9, 110.10)",
    ]
