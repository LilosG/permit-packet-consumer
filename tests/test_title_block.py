"""Item 1 and 8: a title block on every drawing and data page, and the city's stamp box."""
import pypdfium2
import pytest

from permit_packets.jurisdictions import MESA, ORO_VALLEY
from permit_packets.job_types import REGISTRY
from tests.packet_helpers import build, packet_pages, page_texts, sample

ALL = sorted(REGISTRY)


def _model_sample(key: str) -> dict:
    payload = sample(key)
    if key == "ev_charger":
        payload["charger_model"] = "Tesla Wall Connector"
    return payload


@pytest.mark.parametrize("key", ALL)
def test_every_packet_page_has_the_title_block(key):
    payload = {**_model_sample(key), "address": "4821 E Mesa Test Ave, Mesa, AZ 85205",
               "contractor": "Desert Volt Electric", "license_number": "ROC 123456"}
    pages = packet_pages(build(key, payload).pdf)
    assert pages
    total = len(pages)
    for number, text in enumerate(pages, start=1):
        assert "4821 E Mesa Test Ave, Mesa, AZ 85205" in text, number
        assert "PROJECT ADDRESS" in text and "Parcel" in text
        assert f"E-{number}" in text
        assert f"Page {number} of {total}" in text
        assert "Desert Volt Electric" in text and "ROC 123456" in text
        assert "Prepared by" in text and "Signature" in text and "Date" in text


@pytest.mark.parametrize("key", ALL)
def test_the_sheet_title_names_the_page(key):
    pages = packet_pages(build(key, _model_sample(key)).pdf)
    assert "SHEET TITLE" in pages[0] and "Checklist and Checks" in pages[0]
    assert any("Site Plan" in page for page in pages)


def test_data_sheets_are_attached_untouched():
    result = build("ev_charger", _model_sample("ev_charger"))
    texts = page_texts(result.pdf)
    assert len(texts) > len(packet_pages(result.pdf))
    attached = [t for t in texts if "PROJECT ADDRESS" not in t]
    assert attached and all("Prepared by" not in t for t in attached)


def _stamp_payload(key: str, jurisdiction_key: str, city: str, state: str) -> dict:
    return {**_model_sample(key), "jurisdiction_key": jurisdiction_key, "city": city, "state": state}


@pytest.mark.parametrize("key", ALL)
def test_mesa_cover_reserves_a_four_inch_stamp_square(key):
    assert MESA.stamp_box_in == 4.0
    result = build(key, _stamp_payload(key, "mesa-az", "Mesa", "AZ"))
    cover = packet_pages(result.pdf)[0]
    assert "Reserved for city stamp" in cover
    document = pypdfium2.PdfDocument(result.pdf)
    try:
        page = document[0]
        boxes = [obj.get_bounds() for obj in page.get_objects()
                 if obj.type == pypdfium2.raw.FPDF_PAGEOBJ_PATH]
    finally:
        document.close()
    squares = [(r - l, t - b) for l, b, r, t in boxes if abs((r - l) - 288) < 2.5 and abs((t - b) - 288) < 2.5]
    assert squares, "a 4 in x 4 in square is drawn at true size"


def test_a_city_without_a_stamp_box_draws_none():
    assert ORO_VALLEY.stamp_box_in is None
    cover = packet_pages(build("ev_charger", sample("ev_charger")).pdf)[0]
    assert "Reserved for city stamp" not in cover


def test_the_cover_stays_one_page_with_the_stamp_box():
    result = build("ev_charger", _stamp_payload("ev_charger", "mesa-az", "Mesa", "AZ"))
    assert len(result.body["documents"]) == len(packet_pages(result.pdf))


OWNER_PAYLOAD = {"customer": "Sample Homeowner", "contractor": "Homeowner (Owner-Builder)", "license_number": "Owner-Builder"}


@pytest.mark.parametrize("key", ALL)
def test_owner_builder_title_block_has_no_designer_of_record(key):
    pages = packet_pages(build(key, {**_model_sample(key), **OWNER_PAYLOAD}).pdf)
    for number, text in enumerate(pages, start=1):
        flat = " ".join(text.split())
        assert "Prepared by: Sample Homeowner (Owner-Builder)" in flat, number
        assert "OWNER SIGNATURE" in text and "Signature" in text and "Date" in text
        assert "DESIGNER OF RECORD" not in text, number


@pytest.mark.parametrize("key", ALL)
def test_contractor_title_block_keeps_designer_of_record(key):
    pages = packet_pages(build(key, {**_model_sample(key), "contractor": "Desert Volt", "license_number": "ROC 1"}).pdf)
    assert all("ELECTRICIAN (DESIGNER OF RECORD)" in text and "ROC 1" in text for text in pages)


@pytest.mark.parametrize("key", ALL)
def test_footer_is_the_same_for_every_role(key):
    footer = ("Prepared with Permit Packets drafting software. Not PE-stamped. "
              "Confirm current city requirements before submitting.")
    for extra in (OWNER_PAYLOAD, {"contractor": "Desert Volt", "license_number": "ROC 1"}):
        for text in packet_pages(build(key, {**_model_sample(key), **extra}).pdf):
            assert footer in " ".join(text.split())
            assert "Draft for review by a licensed electrician" not in text


def test_single_line_title_replaces_one_line():
    pages = packet_pages(build("ev_charger", _model_sample("ev_charger")).pdf)
    assert any("Single-Line Diagram" in page for page in pages)
    assert not any("One-Line Diagram" in page for page in pages)


def test_empty_panel_schedule_is_a_note_not_a_fix():
    cover = " ".join(packet_pages(build("ev_charger", _model_sample("ev_charger")).pdf)[0].split())
    assert "left blank to fill in on site. Note" in cover


def test_last_verified_prints_only_where_set():
    from permit_packets.jurisdictions import KNOWN

    verified = {j.key: j.last_verified for j in KNOWN.values() if j.last_verified}
    assert verified == {"el-cajon-ca": "2026-11-16", "oro-valley-az": "2026-11-16"}
    el_cajon = {**_model_sample("ev_charger"), "jurisdiction_key": "el-cajon-ca", "city": "El Cajon", "state": "CA"}
    assert "City checklist last verified: 2026-11-16" in " ".join(packet_pages(build("ev_charger", el_cajon).pdf)[0].split())
    mesa = {**_model_sample("ev_charger"), "jurisdiction_key": "mesa-az", "city": "Mesa", "state": "AZ"}
    assert "last verified" not in " ".join(packet_pages(build("ev_charger", mesa).pdf)[0].split())
    general = {**_model_sample("ev_charger"), "jurisdiction_key": "general", "city": "Nowhere", "state": "KS"}
    assert "last verified" not in packet_pages(build("ev_charger", general).pdf)[0]
