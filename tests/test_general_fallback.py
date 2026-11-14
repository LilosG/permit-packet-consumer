"""Item 10: a city with no published checklist gets the general NEC checklist plus its state's amendments,
and the packet keeps saying so."""
import pytest

from permit_packets.jurisdictions import (
    EL_CAJON, ORO_VALLEY, jurisdiction_for, jurisdiction_json,
)
from permit_packets.jurisdictions.general import GENERAL_CHECKLISTS, STATE_AMENDMENTS
from permit_packets.job_types import REGISTRY
from tests.packet_helpers import build, packet_pages, sample

GENERAL_NOTE = "General checklist, city rules added in setup"
SMOKE_CO = "California: permit work over $1,000 can trigger smoke and CO alarm requirements. Confirm with the city."


@pytest.mark.parametrize("key", sorted(REGISTRY))
def test_an_unknown_city_gets_the_general_checklist_and_the_packet_says_so(key):
    payload = {**sample(key), "city": "Yuma", "state": "AZ"}
    payload.pop("jurisdiction_key", None)
    result = build(key, payload)
    assert result.body["jurisdiction"]["known"] is False
    assert result.body["jurisdiction"]["checklist"] == [r.item for r in GENERAL_CHECKLISTS[key].items]
    assert GENERAL_NOTE in " ".join(packet_pages(result.pdf)[0].split())


def test_a_known_city_without_its_own_checklist_for_a_job_type_says_so_too():
    payload = {**sample("subpanel"), "jurisdiction_key": "oro-valley-az"}
    result = build("subpanel", payload)
    assert result.body["jurisdiction"]["known"] is False
    assert GENERAL_NOTE in " ".join(packet_pages(result.pdf)[0].split())


def test_state_amendments_ride_with_the_general_checklist():
    yuma, chula_vista = jurisdiction_for("Yuma", "AZ"), jurisdiction_for("Chula Vista", "CA")
    assert yuma.checklist_for("ev_charger") is GENERAL_CHECKLISTS["ev_charger"]
    general = GENERAL_CHECKLISTS["ev_charger"]
    with_state = chula_vista.checklist_for("ev_charger")
    assert with_state.items == general.items
    assert with_state.notes == general.notes + STATE_AMENDMENTS["CA"]


@pytest.mark.parametrize("key", ["service_upgrade", "subpanel", "appliance_circuit", "ev_charger"])
def test_an_unknown_california_city_flags_the_state_requirement_once(key):
    payload = {**sample(key), "city": "Chula Vista", "state": "CA"}
    payload.pop("jurisdiction_key", None)
    flags = build(key, payload).body["flags"]
    assert flags.count(SMOKE_CO) == 1


def test_a_known_california_city_keeps_the_state_requirement_on_its_own_checklist():
    assert SMOKE_CO in [n.text for n in EL_CAJON.checklist_for("ev_charger").notes]
    assert build("subpanel", {**sample("subpanel"), "jurisdiction_key": "el-cajon-ca", "city": "El Cajon",
                              "state": "CA"}).body["flags"].count(SMOKE_CO) == 1
    assert SMOKE_CO not in build("subpanel", sample("subpanel")).body["flags"]


def test_a_state_with_no_amendments_changes_nothing():
    assert STATE_AMENDMENTS.get("AZ") is None
    assert ORO_VALLEY.checklist_for("ev_charger") is ORO_VALLEY.checklists["ev_charger"]
    assert jurisdiction_json(ORO_VALLEY, "ev_charger")["known"] is True
