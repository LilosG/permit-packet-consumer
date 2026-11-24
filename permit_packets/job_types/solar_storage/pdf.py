"""Render a residential Solar PV & Battery Storage (ESS) permit packet as an 8-page PDF."""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, Spacer

from permit_packets.core.conductors import BUS_BACKFEED_FACTOR, wire_label
from permit_packets.core.equipment import attach_data_sheets, find_equipment
from permit_packets.core.job_inputs import display_number
from permit_packets.core.panel_data import checklist_row as panel_row, one_line_data, panel_header
from permit_packets.core.panel_schedule import (
    PANEL_SCHEDULE_ITEM, ScheduleRow, existing_rows, panel_schedule_page, panel_schedule_row,
)
from permit_packets.core.pdf_base import (
    CONTENT, COPPER, GREEN, H1, H2, INK, MUTED, PALE, SMALL, SOFT,
    _heads, _p, _table, application_page, build_document, content_w, cover_page,
    demo_title, diagram, fit_page, heat_block, load_page, review_page,
)
from permit_packets.core.site_plan import PlanMarker, printed_scale, site_plan_page
from permit_packets.core.title_block import contractor_with_license, title_block_for
from permit_packets.job_types.solar_storage.calc import (
    COUPLING_LABELS, DEGREE, INTERCONNECTION_LABELS, LOCATION_LABELS, SolarStoragePacket,
)

SECTION_PAGES = {"application": 2, "site_plan": 3, "one_line": 4, "load": 5, "panel_schedule": 6, "equipment": 7, "review": 8}


def _size(packet: SolarStoragePacket) -> str:
    return wire_label(packet.branch.wire.size)


def _egc(packet: SolarStoragePacket) -> str:
    return wire_label(packet.branch.egc)


def _wire_text(packet: SolarStoragePacket) -> str:
    return f"3 {_size(packet)} Cu THWN-2 + {_egc(packet)} EGC"


class SitePlan(Flowable):
    scale = 2.75

    def __init__(self, packet: SolarStoragePacket) -> None:
        super().__init__()
        self.packet = packet
        self.width = CONTENT
        self.height = 120 * self.scale + 36

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self) -> None:
        c = self.canv
        k = self.scale
        ox = (CONTENT - 80 * k) / 2 - 40
        oy = 24
        x = lambda v: ox + v * k
        y = lambda v: oy + v * k
        job = self.packet.job

        c.setStrokeColor(INK)
        c.setLineWidth(0.8)
        c.setDash(6, 3)
        c.rect(x(0), y(0), 80 * k, 120 * k, stroke=1, fill=0)
        c.setDash()

        c.setFillColor(PALE)
        c.setStrokeColor(INK)
        c.setLineWidth(1.2)
        c.rect(x(12), y(30), 54 * k, 44 * k, stroke=1, fill=1)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 8.2)
        c.drawCentredString(x(39), y(52) + 2, "EXISTING HOUSE & PV ARRAY")
        c.setFont("Helvetica", 7.2)
        c.drawCentredString(x(39), y(52) - 9, f"{display_number(job.pv_kw_dc)} kW DC PV")

        panel = (66, 58)
        inv = (66, 40)
        c.setStrokeColor(COPPER)
        c.setLineWidth(2.2)
        c.line(x(panel[0]), y(panel[1]), x(inv[0]), y(inv[1]))

        c.setFillColor(INK)
        c.rect(x(panel[0]) - 7, y(panel[1]) - 5, 7, 10, stroke=0, fill=1)
        c.setFillColor(GREEN)
        c.rect(x(inv[0]) - 7, y(inv[1]) - 5, 7, 10, stroke=0, fill=1)

        lx = x(80) + 20
        ly = y(112)
        ess_txt = f" + {display_number(job.battery_kwh)} kWh ESS" if job.battery_kwh > 0 else ""
        for i, (col, txt) in enumerate([
            (INK, f"Main panel, {job.bus_amps} A bus / {job.effective_main_amps} A main"),
            (GREEN, f"PV inverter{ess_txt} ({self.packet.breaker} A)"),
        ]):
            c.setFillColor(col)
            c.rect(lx, ly - i * 16, 8, 8, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont("Helvetica", 8)
            c.drawString(lx + 13, ly - i * 16, txt)
        c.setFont("Helvetica", 7.2)
        c.setFillColor(MUTED)
        c.drawString(lx, ly - 42, f"Output run: {job.run_ft} ft (schematic, not to scale).")


class OneLine(Flowable):
    def __init__(self, packet: SolarStoragePacket) -> None:
        super().__init__()
        self.packet = packet
        self.width = CONTENT
        self.height = 170

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self) -> None:
        c = self.canv
        packet = self.packet
        job = packet.job
        mid = 100
        box_w = 104
        box_h = 64

        def box(bx, title, lines, fill=colors.white):
            c.setFillColor(fill)
            c.setStrokeColor(INK)
            c.setLineWidth(1.3)
            c.roundRect(bx, mid - box_h / 2, box_w, box_h, 3, stroke=1, fill=1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 7.6)
            c.drawCentredString(bx + box_w / 2, mid + box_h / 2 + 6, title)
            c.setFont("Helvetica", 7)
            for i, line in enumerate(lines):
                c.drawCentredString(bx + box_w / 2, mid + 9 - i * 10, line)

        xs = [0, 180, CONTENT - box_w]
        box(xs[0], "UTILITY METER", ["Bidirectional", "120/240 V", "1-phase"])
        box(xs[1], "MAIN PANEL", [f"{job.bus_amps} A bus / {job.effective_main_amps} A main", f"{packet.breaker} A backfeed", "Opposite end of bus"], SOFT)
        ess_line = f"{display_number(job.battery_kwh)} kWh UL 9540 ESS" if job.battery_kwh > 0 else "NEC 690.12 Rapid Shutdown"
        box(xs[2], "SOLAR PV / ESS", [f"{display_number(job.pv_kw_dc)} kW DC Array", ess_line, f"{packet.breaker} A AC Output"])

        c.setStrokeColor(INK)
        c.setLineWidth(1.5)
        for left, right in zip(xs, xs[1:]):
            c.line(left + box_w, mid, right, mid)

        label_x = (xs[1] + box_w + xs[2]) / 2
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 7.2)
        c.drawCentredString(label_x, mid + 25, f"{packet.breaker} A, 2-pole")
        c.setFont("Helvetica", 6.8)
        c.drawCentredString(label_x, mid + 15, _wire_text(packet))
        c.drawCentredString(label_x, mid - 12, f"in {packet.raceway_text}")
        c.drawCentredString(label_x, mid - 22, f"{job.run_ft} ft one way")


def checklist_rows(packet: SolarStoragePacket) -> list[tuple[str, str, str]]:
    job = packet.job
    plan = job.plan
    rows = []
    for req in job.jurisdiction.checklist_for("solar_storage").items:
        sec = req.section
        if sec == "application":
            missing = job.jurisdiction.needs_parcel_number and not (plan and plan.parcel_number)
            rows.append((req.item, "Page 2: add the parcel number" if missing else "Page 2: fields ready", "Open" if missing else "Ready"))
        elif sec == "site_plan":
            rows.append((req.item, f"Page 3: to scale, 1 in = {printed_scale(plan)} ft" if plan else "Page 3: schematic only", "Ready" if plan else "Open"))
        elif sec == "equipment":
            has_doc = bool(find_equipment(job.system_model, "appliance") or job.data_sheet_attached)
            rows.append((req.item, "Page 7 + UL cut sheet attached" if has_doc else "Page 7: attach inverter/ESS UL 1741 & UL 9540 sheets", "Ready" if has_doc else "Attach"))
        else:
            shown = panel_row(job, sec, SECTION_PAGES["one_line"], burial=None)
            rows.append((req.item, *(shown or (f"Page {SECTION_PAGES.get(sec, 4)}", "Ready"))))
    return rows + [(PANEL_SCHEDULE_ITEM, *panel_schedule_row(job, SECTION_PAGES["panel_schedule"]))]


def scope_of_work(packet: SolarStoragePacket) -> str:
    job = packet.job
    ess = f" and {display_number(job.battery_kwh)} kWh battery energy storage system" if job.battery_kwh > 0 else ""
    model = f" ({job.system_model})" if job.system_model else ""
    return (
        f"Install one {display_number(job.pv_kw_dc)} kW DC grid-tied {COUPLING_LABELS[job.coupling]}{ess}{model} "
        f"at {LOCATION_LABELS[job.location]}, interconnected via {INTERCONNECTION_LABELS[job.interconnection]} "
        f"({packet.breaker} A backfeed, {_wire_text(packet)} in {packet.raceway_text}, {job.run_ft} ft run)."
    )


def application_fields(packet: SolarStoragePacket) -> list[tuple[str, str]]:
    job = packet.job
    return [
        ("Project address", job.address),
        ("Parcel number", job.plan.parcel_number if job.plan and job.plan.parcel_number else "Not on file"),
        ("Jurisdiction", job.jurisdiction.label),
        ("Property owner", job.customer),
        ("Permit type", f"Electrical, residential {COUPLING_LABELS[job.coupling]}"),
        ("Equipment", job.system_model or f"{display_number(job.pv_kw_dc)} kW PV" + (f" + {display_number(job.battery_kwh)} kWh ESS" if job.battery_kwh > 0 else "")),
        ("Contractor", job.contractor),
        ("License number", job.license_number or "Owner-Builder"),
    ]


def render_solar_storage_packet_pdf(packet: SolarStoragePacket) -> bytes:
    job = packet.job
    jurisdiction = job.jurisdiction
    checklist_cell = (
        f"{jurisdiction.label}\n{jurisdiction.checklist_for('solar_storage').source_label}"
        if jurisdiction.known_for("solar_storage")
        else f"{jurisdiction.label}\nUsing the national NEC checklist. Confirm local amendments with {jurisdiction.name if jurisdiction.name != 'This area' else 'your city'}."
    )
    if jurisdiction.last_verified:
        checklist_cell += f"\nCity checklist last verified: {jurisdiction.last_verified}"
    parcel = f"\nParcel {job.plan.parcel_number}" if job.plan and job.plan.parcel_number else ""
    cover = cover_page(
        title="Solar PV & Battery Storage Permit Packet",
        address=job.address,
        job_cell=f"{job.home.square_feet:,} sq ft home{parcel}\n{display_number(job.pv_kw_dc)} kW PV" + (f" + {display_number(job.battery_kwh)} kWh ESS" if job.battery_kwh > 0 else "") + f"\nCustomer: {job.customer}",
        contractor_cell=contractor_with_license(job.contractor, job.license_number),
        checklist_cell=checklist_cell,
        checklist_rows=checklist_rows(packet),
        checks=[(c.name, c.result, c.passed, c.neutral, c.assumed) for c in packet.checks],
        flags=packet.flags,
        stamp_box_in=jurisdiction.stamp_box_in,
    )
    app_sec = application_page(
        rows=application_fields(packet), scope=scope_of_work(packet),
        inspections=[("Rough", "AC/DC raceways, grounding/bonding and ESS mounting before covering"), ("Final", "NEC 690.12 rapid shutdown, NEC 706.15 ESS disconnect, placards and utility PTO test")],
    )
    if job.plan is None:
        site_sec = [_p("Site Plan", H1), _p("Shows main panel, solar inverter / ESS and output circuit route.", SMALL), Spacer(1, 10), diagram(SitePlan(packet), share=0.8)]
    else:
        markers = [PlanMarker(job.plan.markers["panel"], INK, "P"), PlanMarker(job.plan.markers["inverter"], GREEN, "S")]
        site_sec = site_plan_page(
            address=job.address, plan=job.plan, markers=markers, underground=bool(job.trench_ft),
            legend=[f"P  Main panel ({job.bus_amps} A bus)", f"S  Solar PV / ESS ({packet.breaker} A)"],
            measures=[f"Output run: {job.run_ft} ft"], outline_over_aerial=jurisdiction.outline_over_aerial,
        )
    one_line_sec = fit_page([
        _p("Single-Line Diagram", H1),
        _p("Utility meter, main panel busbar interconnection, inverter / ESS and disconnects.", SMALL),
        Spacer(1, 10),
        diagram(OneLine(packet), legend=one_line_data(job)),
        Spacer(1, 8),
        _table([_heads("Segment", "Conductors", "Conduit", "Protection"),
                [_p("Inverter / ESS output"), _p(_wire_text(packet)), _p(packet.raceway_text), _p(f"{packet.breaker} A, 2-pole")]],
               [1.4 * inch, 2.4 * inch, 1.3 * inch, content_w() - 5.1 * inch]),
    ] + heat_block(packet.branch.heat, jurisdiction))
    max_bus = int(job.bus_amps * BUS_BACKFEED_FACTOR)
    load_sec = load_page(
        packet.load,
        method=f"Optional dwelling method, {jurisdiction.code_name} 220.82 + NEC 705.12(B)(3)(2) 120% busbar verification.",
        service_rows=[
            ("Panel busbar & 120% limit", f"{job.bus_amps} A bus x 120% = {max_bus} A max combined"),
            ("Main + PV/ESS backfeed", f"{job.effective_main_amps} A main + {packet.breaker} A backfeed = {job.effective_main_amps + packet.breaker} A"),
        ],
    )
    rows = existing_rows(job.existing_circuits)
    if job.interconnection != "supply_side_tap":
        rows.append(ScheduleRow("Solar PV backfeed (this permit)", f"{job.pv_breaker_amps} A", 2, "New"))
        if job.coupling == "ac_coupled" and job.battery_breaker_amps:
            rows.append(ScheduleRow("Battery ESS backfeed (this permit)", f"{job.battery_breaker_amps} A", 2, "New"))
    sched_sec = panel_schedule_page(
        [(f"Main panel, {job.bus_amps} A bus / {job.effective_main_amps} A main", rows)], entered=bool(job.existing_circuits),
        spaces_note=f"Open spaces: {job.open_breaker_spaces} before, {max(job.open_breaker_spaces - job.spaces_needed, 0)} after.",
        header=panel_header(job),
    )
    equip_rows = [
        ("System architecture", COUPLING_LABELS[job.coupling], "UL 1741 SB / UL 9540"),
        ("PV / ESS rating", f"{display_number(job.pv_kw_dc)} kW DC" + (f" / {display_number(job.battery_kwh)} kWh ESS" if job.battery_kwh > 0 else ""), f"{packet.breaker} A, 240 V"),
        ("Conductors & raceway", f"{_wire_text(packet)}, {packet.raceway_text}", f"{jurisdiction.code_name} 310.16"),
    ]
    equip_sec = [
        _p("Equipment Data", H1),
        _p("Attach manufacturer UL 1741 inverter and UL 9540 / UL 9540A battery cut sheets behind this page.", SMALL),
        Spacer(1, 10),
        _table([_heads("Item", "Specification", "Listing")] + [[_p(a), _p(b), _p(c)] for a, b, c in equip_rows],
               [1.6 * inch, content_w() - 3.5 * inch, 1.9 * inch]),
    ]
    rev_sec = review_page([
        "PV / ESS backfeed breaker(s) landed at opposite end of busbar from main breaker (NEC 705.12(B)(3)(2))",
        "NEC 690.12 rapid shutdown initiation verified at service disconnect",
        "NEC 706.15 lockable ESS disconnect and IRC R328 garage spacing / heat detector confirmed",
        "Permanent NEC 690.56(C) & 705.10 solar/ESS directory placards installed at meter and main panel",
    ])
    pdf = build_document(
        [cover, app_sec, site_sec, one_line_sec, load_sec, sched_sec, equip_sec, rev_sec],
        title=demo_title("Solar PV & Battery Storage Permit Packet"),
        block=title_block_for(job),
        sheet_titles=["Checklist and Checks", "Permit Application Data", "Site Plan", "Single-Line Diagram", "Load Calculation", "Panel Schedule", "Equipment Data", "Pre-Submittal Review"],
    )
    sheet = find_equipment(job.system_model, "appliance")
    return attach_data_sheets(pdf, [sheet] if sheet else [], after_title="Equipment Data")
