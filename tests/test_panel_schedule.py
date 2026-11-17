"""Item 6: the panel schedule never invents circuits."""
import pytest

from permit_packets.job_types import REGISTRY
from tests.packet_helpers import build, packet_pages, sample

ALL = sorted(REGISTRY)
CIRCUITS = [{"label": "Pool pump", "amps": 30, "poles": 2}, {"label": "Garage lights", "amps": 15, "poles": 1}]
NONE_ENTERED = "Optional: none entered. The schedule is left blank to fill in on site."
FLAG = "Enter the panel's existing circuits for the panel schedule."


def _schedule(pdf: bytes) -> str:
    return next(page for page in packet_pages(pdf) if "Circuit directory" in page)


@pytest.mark.parametrize("sheet", ["letter", "tabloid"])
@pytest.mark.parametrize("key", ALL)
def test_no_entered_circuits_prints_an_empty_grid_not_load_calculation_circuits(key, sheet):
    payload = {**sample(key), "existing_circuits": [], "sheet_size": sheet}
    result = build(key, payload)
    page = _schedule(result.pdf)
    assert "Field verify and fill in" in page
    for invented in ("General lighting", "small-appliance", "Laundry circuit", "Verify on site",
                     "Clothes dryer", "Electric range", "Water heater"):
        assert invented not in page, invented
    assert "Ckt" in page
    assert len(packet_pages(result.pdf)) == len(result.body["documents"]), "still one sheet"


@pytest.mark.parametrize("key", ALL)
def test_no_entered_circuits_sets_the_checklist_item_and_a_neutral_check(key):
    body = build(key, {**sample(key), "existing_circuits": []}).body
    assert FLAG in body["flags"]
    check = next(c for c in body["checks"] if c["name"] == "Panel schedule")
    assert check == {"name": "Panel schedule", "result": NONE_ENTERED, "passed": False, "neutral": True}
    item = next(row for row in body["checklist_status"] if row["item"].startswith("Panel schedule"))
    assert item["status"] == "Open"


@pytest.mark.parametrize("key", ALL)
def test_entered_circuits_are_listed_as_entered_and_the_item_is_ready(key):
    result = build(key, {**sample(key), "existing_circuits": CIRCUITS})
    page = _schedule(result.pdf)
    assert "Pool pump" in page and "30 A" in page and "Garage lights" in page
    assert "Field verify and fill in" not in page
    assert FLAG not in result.body["flags"]
    check = next(c for c in result.body["checks"] if c["name"] == "Panel schedule")
    assert check["passed"] is True and "2 existing circuits entered" in check["result"]
    item = next(row for row in result.body["checklist_status"] if row["item"].startswith("Panel schedule"))
    assert item["status"] == "Ready"


@pytest.mark.parametrize("key", ALL)
def test_the_cover_checklist_lists_the_panel_schedule(key):
    cover = packet_pages(build(key, {**sample(key), "existing_circuits": []}).pdf)[0]
    assert "Panel schedule with the panel's existing circuits" in cover
