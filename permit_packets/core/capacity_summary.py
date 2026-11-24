"""The Panel Capacity Summary: page one of a Panel Capacity Report (the load_calc package).

Built only from what the packet already computes and checks. Nothing here adds an electrical calculation: the
verdict reads the packet's own service-capacity and panel-space checks."""
from __future__ import annotations

import re
from io import BytesIO

import pypdfium2
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph, Spacer

from permit_packets.core.checks import ASSUMED_NOTE
from permit_packets.core.layout import SHEETS, content_w, use_sheet
from permit_packets.core.pdf_base import (
    BODY, CELL, CELL_BOLD, H1, H2, SMALL, _heads, _p, _table, build_document, use_blank_area)
from permit_packets.core.title_block import REPORT_SET, SET_NUMBERS, TitleBlock
from permit_packets.jurisdictions import jurisdiction_by_key

STEM = "00-panel-capacity-summary"
TITLE = "Panel Capacity Summary"
PASS_VERDICT = "Your panel can take this job"
FAIL_VERDICT = "Your panel does not have room for this job as entered"
OPTIONS = (
    "Enter 12 months of utility peak-demand data to use the NEC 220.87 measured-demand method, which often shows more room",
    "A load management device",
    "A service upgrade (our panel upgrade packet covers it)",
)
# The checks that say whether the panel has room: service load against the rating, and open breaker spaces.
CAPACITY_CHECK = re.compile(r"capacity|spaces|feeder load|panel rating", re.I)


def capacity_checks(checks: list[dict]) -> list[dict]:
    live = [c for c in checks if not c.get("neutral") and not c.get("assumed")]  # an ASSUMED check never moves the verdict
    return [c for c in live if CAPACITY_CHECK.search(c.get("name", ""))] or live


def verdict(checks: list[dict]) -> tuple[bool, str]:
    ok = all(c.get("passed") for c in capacity_checks(checks))
    return ok, PASS_VERDICT if ok else FAIL_VERDICT


def _number(value) -> str:
    return f"{value:g}"


def summary_rows(payload: dict, body: dict) -> list[tuple[str, str]]:
    plan = payload.get("plan") if isinstance(payload.get("plan"), dict) else {}
    rows = [("Address", body.get("address") or payload.get("address") or "")]
    if plan.get("parcel_number"):
        rows.append(("Parcel", plan["parcel_number"]))
    service = body.get("service_amps") or payload.get("service_amps")
    if service:
        rows.append(("Service rating", f"{_number(service)} A"))
    if body.get("computed_amps") is not None:
        rows.append(("Calculated load", f"{_number(body['computed_amps'])} A"))
    spare = body.get("spare_amps")
    if spare is None and service and body.get("computed_amps") is not None:
        spare = round(service - body["computed_amps"], 1)
    if spare is not None:
        rows.append(("Spare amps", f"{_number(spare)} A"))
    if payload.get("open_breaker_spaces") is not None:
        rows.append(("Open breaker spaces", str(payload["open_breaker_spaces"])))
    return [(label, value) for label, value in rows if value]


def job_label(job_type: str) -> str:
    """"ev_charger" -> "EV charger"."""
    words = [("EV" if word == "ev" else word) for word in (job_type or "").replace("-", "_").split("_") if word]
    text = " ".join(words)
    return text[:1].upper() + text[1:]


def method_label(payload: dict) -> str:
    return "NEC 220.87 measured demand" if payload.get("peak_demand_kw") else "NEC 220.82 optional method"


def summary_pdf(payload: dict, body: dict) -> bytes:
    """One letter-size sheet with the packet's title block."""
    city = jurisdiction_by_key(payload.get("jurisdiction_key"), payload.get("city"), payload.get("state"))
    plan = payload.get("plan") if isinstance(payload.get("plan"), dict) else {}
    owner = payload.get("owner") or payload.get("customer") or ""
    block = TitleBlock(body.get("address") or payload.get("address") or "", plan.get("parcel_number") or "",
                       payload.get("contractor") or "", payload.get("license_number") or "", owner)
    checks = body.get("checks") or []
    ok, headline = verdict(checks)
    width = content_w()
    amber = colors.HexColor("#b26a00")

    def mark(check: dict):
        if check.get("assumed"):
            return Paragraph("ASSUMED", ParagraphStyle("assumed", parent=CELL_BOLD, textColor=amber))
        return _p("PASS" if check["passed"] else "FAIL", CELL_BOLD)

    def result(check: dict) -> str:
        return f"{check['result']} {ASSUMED_NOTE}" if check.get("assumed") else check["result"]

    story = [
        _p(TITLE, H1),
        _p(f"{job_label(body.get('job_type', ''))} · {method_label(payload)}", SMALL),
        Spacer(1, 10),
        _table([[_p(headline, H2)]], [width], head=False,
               extra=[("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e3f1e6" if ok else "#f8e1de"))]),
        Spacer(1, 10),
        _table([[_p(label, CELL_BOLD), _p(value)] for label, value in summary_rows(payload, body)],
               [2.0 * inch, width - 2.0 * inch], head=False),
        Spacer(1, 12),
        _p("Checks", H2),
        _table([_heads("Check", "Result", "")] + [
            [_p(c["name"], CELL_BOLD), _p(result(c)), mark(c)]
            for c in checks if not c.get("neutral")],
               [2.0 * inch, width - 3.0 * inch, 1.0 * inch]),
    ]
    if not ok:
        story += [Spacer(1, 12), _p("Your options", H2)]
        story += [_p(f"{index}. {text}.", BODY) for index, text in enumerate(OPTIONS, 1)]
    sheet = SHEETS["letter"]
    token = SET_NUMBERS.set(REPORT_SET)
    try:
        with use_sheet(sheet), use_blank_area(None):
            return build_document([story], title=TITLE, block=block, sheet_titles=[TITLE])
    finally:
        SET_NUMBERS.reset(token)


def prepend_summary(summary_bytes: bytes, pdf: bytes) -> bytes:
    """The summary page first, then the given PDF."""
    summary = pypdfium2.PdfDocument(summary_bytes)
    rest = pypdfium2.PdfDocument(pdf)
    try:
        summary.import_pages(rest)
        buffer = BytesIO()
        summary.save(buffer)
        return buffer.getvalue()
    finally:
        summary.close()
        rest.close()
