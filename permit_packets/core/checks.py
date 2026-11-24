"""One engineering check on a packet: what was checked, the result and whether it passed."""
from __future__ import annotations

from dataclasses import dataclass

ASSUMED_NOTE = ("Uses a typical residential default; get the utility's fault current letter and the panel's label "
                "to confirm.")


@dataclass(frozen=True)
class Check:
    name: str
    result: str
    passed: bool
    neutral: bool = False  # an optional item left empty: shown as a note, not a failure
    assumed: bool = False  # relies on a default the buyer did not enter: shown as ASSUMED, not PASS
