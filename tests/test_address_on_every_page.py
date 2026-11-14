"""Item 8: the project address is on every page of the packet, whatever the size or job."""
import pytest

from permit_packets.jurisdictions import KNOWN
from permit_packets.job_types import REGISTRY
from tests.packet_helpers import build, complete_inputs, packet_pages, plan_for, sample

ADDRESS = "4821 E Mesa Test Ave Unit 12, Mesa, AZ 85205"


@pytest.mark.parametrize("sheet", ["letter", "tabloid"])
@pytest.mark.parametrize("key", sorted(REGISTRY))
def test_every_non_attachment_page_contains_the_project_address(key, sheet):
    payload = {**complete_inputs(key, KNOWN[("mesa", "AZ")]), "address": ADDRESS, "sheet_size": sheet}
    result = build(key, payload)
    pages = packet_pages(result.pdf)
    assert len(pages) == len(result.body["documents"])
    for number, text in enumerate(pages, start=1):
        assert ADDRESS in text, f"page {number} of the {key} packet on {sheet}"


def test_a_very_long_address_still_fits_the_title_block_and_stays_whole():
    long_address = "10450 N Some Very Long Boulevard Name East, Building C, Unit 2204, Oro Valley, AZ 85737-1234"
    pages = packet_pages(build("ev_charger", {**sample("ev_charger"), "address": long_address}).pdf)
    flat = [" ".join(page.split()) for page in pages]
    assert all(long_address in page for page in flat)


def test_sample_mode_puts_the_sample_address_on_every_page_not_the_real_one():
    payload = {**sample("ev_charger"), "address": "77 Real Customer Way, Mesa, AZ", "sample_mode": True,
               "city": "Mesa", "state": "AZ", "plan": plan_for("ev_charger", parcel="123-45-678")}
    pages = packet_pages(build("ev_charger", payload).pdf)
    assert all("123 Sample St, Mesa, AZ" in " ".join(page.split()) for page in pages)
    assert not any("Real Customer" in page for page in pages)
    assert all("000-00-000-000" in page for page in pages), "the sample parcel stands in for the real one"
