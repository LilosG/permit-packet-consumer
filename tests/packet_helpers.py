"""Shared helpers: build a packet for any job type and read its pages."""
from __future__ import annotations

import json
from pathlib import Path

import pypdfium2

from permit_packets.core.equipment import attachment_span
from permit_packets.job_types import REGISTRY, PacketResult

from tests.test_ev_golden import GOLDEN, to_current_request

SAMPLES = Path(__file__).parent / "samples"
SAMPLE_FILES = {
    "ev_charger": "oro_valley_attached_no_plan", "service_upgrade": "service_upgrade", "subpanel": "subpanel",
    "appliance_circuit": "appliance_circuit",
}


def sample(key: str) -> dict:
    if key == "ev_charger":
        return to_current_request(json.loads((GOLDEN / "cases" / f"{SAMPLE_FILES[key]}.json").read_text()))
    return json.loads((SAMPLES / f"{SAMPLE_FILES[key]}.json").read_text())


def build(key: str, payload: dict) -> PacketResult:
    job_type = REGISTRY[key]
    return job_type.build_response(job_type.request_model.model_validate(payload))


def page_texts(pdf: bytes) -> list[str]:
    document = pypdfium2.PdfDocument(pdf)
    try:
        return [page.get_textpage().get_text_bounded() for page in document]
    finally:
        document.close()


def packet_pages(pdf: bytes) -> list[str]:
    """The text of every packet page, leaving out attached manufacturer data sheets."""
    texts = page_texts(pdf)
    span = attachment_span(pdf)
    if span:
        after, count = span
        return texts[:after] + texts[after + count:]
    return texts
