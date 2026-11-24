"""Generator interlock / transfer switch: from validated request to packet PDF and JSON."""
from __future__ import annotations

from fastapi import HTTPException, status
from pydantic import BaseModel

from permit_packets.core.conductors import wire_label
from permit_packets.core.job_inputs import build_on_sheet, display_number, property_plan, sample_address
from permit_packets.core.load_calculation import HomeLoads
from permit_packets.core.panel_schedule import existing_circuits
from permit_packets.core.preview import pdf_page_count
from permit_packets.core.site_plan import printed_scale
from permit_packets.core.title_block import contractor_with_license
from permit_packets.job_types import Document, PacketResult
from permit_packets.job_types.generator.calc import (
    TRANSFER_LABELS, GeneratorJob, GeneratorPacket, build_generator_packet,
)
from permit_packets.job_types.generator.pdf import (
    application_fields, checklist_rows, render_generator_packet_pdf, scope_of_work,
)
from permit_packets.job_types.generator.schema import GeneratorRequest
from permit_packets.jurisdictions import jurisdiction_by_key, jurisdiction_json

JOB_TYPE_KEY = "generator"
FEATURE_PAGE = 2
DOCUMENTS = (
    Document("01-checklist-and-checks", "Checklist and checks"),
    Document("02-permit-application-data", "Permit data"),
    Document("03-site-plan", "Site plan"),
    Document("04-one-line-diagram", "One-line diagram"),
    Document("05-load-calculation", "Load calculation"),
    Document("06-panel-schedule", "Panel schedule"),
    Document("07-equipment-data", "Equipment data"),
    Document("08-pre-submittal-review", "Pre-submittal review"),
)


def to_job(request: GeneratorRequest) -> GeneratorJob:
    fields = request.model_dump(exclude={"home", "plan", "city", "state", "jurisdiction_key", "sample_mode"})
    fields["existing_circuits"] = existing_circuits(fields["existing_circuits"])
    fields.pop("sheet_size", None)
    if request.sample_mode:
        fields["address"] = sample_address(request)
    return GeneratorJob(
        home=HomeLoads(**request.home.model_dump()),
        jurisdiction=jurisdiction_by_key(request.jurisdiction_key, request.city, request.state),
        plan=property_plan(request, ("panel", "inlet")),
        **fields,
    )


def _build_response(request: BaseModel) -> PacketResult:
    assert isinstance(request, GeneratorRequest)
    try:
        packet = build_generator_packet(to_job(request))
    except ValueError as error:
        raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, str(error)) from error
    pdf = render_generator_packet_pdf(packet)
    jurisdiction = packet.job.jurisdiction
    wire = wire_label(packet.branch.wire.size)
    site = f"Site plan drawn to scale at 1 in = {printed_scale(packet.job.plan)} ft" if packet.job.plan else "Schematic site plan drawn"
    body = {
        "job_type": JOB_TYPE_KEY,
        "ready": packet.ready,
        "computed_amps": round(packet.load.computed_amps, 1),
        "service_amps": packet.job.service_amps,
        "breaker_amps": packet.breaker,
        "conductor": f"{wire} Cu",
        "egc": f"{wire_label(packet.branch.egc)} Cu",
        "conduit": f"Type {packet.cable_type} cable" if packet.conduit_size is None else packet.raceway_text,
        "voltage_drop_percent": round(packet.branch.vd_percent, 1),
        "checks": [
            {"name": c.name, "result": c.result, "passed": c.passed, **({"neutral": True} if c.neutral else {}), **({"assumed": True} if c.assumed else {})}
            for c in packet.checks
        ],
        "flags": packet.flags,
        "checklist_status": [{"item": i, "where": w, "status": s} for i, w, s in checklist_rows(packet)],
        "jurisdiction": jurisdiction_json(jurisdiction, JOB_TYPE_KEY),
        "address": packet.job.address,
        "fields": [
            *({"label": label, "value": value} for label, value in application_fields(packet)),
            {"label": "Scope of work", "value": scope_of_work(packet)},
        ],
        "documents": [{"file_stem": d.file_stem, "title": d.title} for d in DOCUMENTS],
        "feature_page": FEATURE_PAGE,
        "summary": [
            {"label": "Generator", "value": f"{display_number(packet.job.generator_kw)} kW"},
            {"label": "Inlet / Breaker", "value": f"{packet.breaker} A"},
            {"label": "Wire", "value": wire},
            {"label": "Voltage drop", "value": f"{display_number(round(packet.branch.vd_percent, 1))}%"},
        ],
        "build_steps": [
            f"{jurisdiction.label} checklist applied, {len(jurisdiction.checklist_for(JOB_TYPE_KEY).items)} items",
            f"Transfer check: {TRANSFER_LABELS[packet.job.transfer_type]}, {packet.breaker} A",
            f"Feeder sized: {wire} Cu, {packet.breaker} A breaker",
            site,
            f"Permit data filled in, {pdf_page_count(pdf)} pages built",
        ],
        "submission_email": {
            "subject": f"Generator transfer permit submittal: {packet.job.address}",
            "body": (
                f"Hello,\n\nAttached is an electrical permit submittal for a residential {TRANSFER_LABELS[packet.job.transfer_type]} "
                f"({display_number(packet.job.generator_kw)} kW, {packet.breaker} A, 120/240 V).\n\n"
                f"Address: {packet.job.address}\nContractor: {contractor_with_license(packet.job.contractor, packet.job.license_number, ', license ')}\n\n"
                f"Please let me know if anything else is needed.\n\nThank you,\n{packet.job.contractor}"
            ),
        },
    }
    return PacketResult(pdf=pdf, body=body)


def build_response(request: BaseModel) -> PacketResult:
    return build_on_sheet(request, _build_response)
