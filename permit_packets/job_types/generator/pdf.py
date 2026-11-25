"""Render a residential standby generator interlock / transfer switch permit packet as an 8-page PDF."""
from __future__ import annotations

from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Flowable, Spacer

from permit_packets.core.conductors import wire_label
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
from permit_packets.job_types.generator.calc import (
    BURIAL_COVER_IN, DEGREE, FUEL_LABELS, LOCATION_LABELS, TRANSFER_LABELS, TRANSFER_TITLES, GeneratorPacket,
)

SECTION_PAGES = {"application": 2, "site_plan": 3, "one_line": 4, "load": 5, "panel_schedule": 6, "equipment": 7, "review": 8}
# New sheets go after every existing sheet, so no existing "Page N" reference moves.
EQUIPMENT_LAYOUT_TITLE = "Equipment Layout and Working Space"
EQUIPMENT_LAYOUT_PAGE = 9
WORKING_SPACE_LABEL = ("NEC 110.26 working space: 36 in deep x 30 in wide (or equipment width) "
                       "x 6.5 ft high")
EQUIPMENT_LAYOUT_NOTE = "SCHEMATIC - NOT TO SCALE. Field-verify locations and clearances."


def _size(packet: GeneratorPacket) -> str:
    return wire_label(packet.branch.wire.size)


def _egc(packet: GeneratorPacket) -> str:
    return wire_label(packet.branch.egc)


def _conduit(packet: GeneratorPacket) -> str:
    if packet.conduit_size is None:
        return f"Type {packet.cable_type} cable"
    return packet.raceway_text or f"{packet.conduit_size} {packet.job.wiring}"


def _wire_text(packet: GeneratorPacket) -> str:
    ins = "" if packet.conduit_size is None else " THWN-2"
    return f"3 {_size(packet)} Cu{ins} + {_egc(packet)} EGC"


class SitePlan(Flowable):
    scale = 2.75

    def __init__(self, packet: GeneratorPacket) -> None:
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
        c.drawCentredString(x(39), y(52) + 2, "EXISTING HOUSE")
        c.setFont("Helvetica", 7.2)
        c.drawCentredString(x(39), y(52) - 9, f"{job.home.square_feet:,} sq ft")

        panel = (66, 58)
        inlet = (74, 42) if job.location == "exterior_wall" else (74, 92)
        route = [panel, (74, 58), inlet]
        c.setStrokeColor(COPPER)
        c.setLineWidth(2.2)
        if job.trench_ft:
            c.setDash(7, 3)
        pts = [(x(a), y(b)) for a, b in route]
        c.lines([(*pts[i], *pts[i + 1]) for i in range(len(pts) - 1)])
        c.setDash()

        c.setFillColor(INK)
        c.rect(x(panel[0]) - 7, y(panel[1]) - 5, 7, 10, stroke=0, fill=1)
        c.setFillColor(GREEN)
        c.rect(x(inlet[0]) - 4, y(inlet[1]) - 5, 8, 10, stroke=0, fill=1)

        lx = x(80) + 20
        ly = y(112)
        for i, (col, txt) in enumerate([
            (INK, f"Main panel, {job.service_amps} A (existing)"),
            (GREEN, f"Generator / {self.packet.breaker} A inlet (new)"),
        ]):
            c.setFillColor(col)
            c.rect(lx, ly - i * 16, 8, 8, stroke=0, fill=1)
            c.setFillColor(INK)
            c.setFont("Helvetica", 8)
            c.drawString(lx + 13, ly - i * 16, txt)
        c.setFont("Helvetica", 7.2)
        c.setFillColor(MUTED)
        c.drawString(lx, ly - 42, f"Feeder run: {job.run_ft} ft (schematic, not to scale).")


class OneLine(Flowable):
    def __init__(self, packet: GeneratorPacket) -> None:
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
        meter_lines = ["Existing", "120/240 V", "1-phase"]
        if job.jurisdiction.utility_short:
            meter_lines.append(job.jurisdiction.utility_short)
        box(xs[0], "UTILITY METER", meter_lines)
        box(xs[1], "MAIN PANEL & INTERLOCK", [f"{job.service_amps} A service", f"{packet.breaker} A backfeed / transfer", "NEC 702.5 listed"], SOFT)
        inlet_lines = [f"{display_number(job.generator_kw)} kW ({display_number(job.generator_amps)} A)", f"{packet.breaker} A, 120/240 V", f"{job.neutral_type.capitalize()} neutral"]
        if job.fuel_type:
            inlet_lines.append(f"Fuel: {FUEL_LABELS[job.fuel_type]}")
        box(xs[2], "GENERATOR / INLET", inlet_lines)

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
        c.drawCentredString(label_x, mid - 12, f"in {_conduit(packet)}")
        c.drawCentredString(label_x, mid - 22, f"{job.run_ft} ft one way")


class EquipmentLayout(Flowable):
    """A plan-view schematic of the generator equipment and its NEC 110.26 working space.

    Not to scale: every value is the one the one-line and panel schedule already carry."""

    def __init__(self, packet: GeneratorPacket) -> None:
        super().__init__()
        self.packet = packet
        self.width = CONTENT
        self.height = 220

    def wrap(self, available_width, available_height):
        return self.width, self.height

    def draw(self) -> None:
        c = self.canv
        packet = self.packet
        job = packet.job
        top = self.height - 14

        c.setFillColor(MUTED)
        c.setFont("Helvetica-Bold", 7.4)
        c.drawString(0, top, EQUIPMENT_LAYOUT_NOTE)

        boxes = [
            (24, "MAIN PANEL", [f"{job.service_amps} A service", "Backfeed breaker landed", "opposite the main"]),
            (170, "TRANSFER EQUIPMENT", [TRANSFER_LABELS[job.transfer_type].capitalize(), f"{packet.breaker} A", "120/240 V"]),
        ]
        if job.location == "exterior_wall":
            inlet_title, inlet_lines = "GENERATOR INLET", ["Exterior wall", f"{packet.breaker} A inlet", "NEC 702.7 signage"]
        else:
            inlet_title, inlet_lines = "GENERATOR", ["Detached pad", f"{display_number(job.generator_kw)} kW", f"{packet.breaker} A"]
        boxes.append((316, inlet_title, inlet_lines))

        box_w, box_h = 122, 52
        box_y = 92
        for bx, title, lines in boxes:
            c.setFillColor(SOFT)
            c.setStrokeColor(INK)
            c.setLineWidth(1.2)
            c.rect(bx, box_y, box_w, box_h, stroke=1, fill=1)
            c.setFillColor(INK)
            c.setFont("Helvetica-Bold", 7.4)
            c.drawCentredString(bx + box_w / 2, box_y + box_h - 11, title)
            c.setFont("Helvetica", 6.9)
            for i, line in enumerate(lines):
                c.drawCentredString(bx + box_w / 2, box_y + box_h - 23 - i * 9, line)

        # The conduit run between the equipment, with its type, size and length.
        c.setStrokeColor(COPPER)
        c.setLineWidth(2.2)
        c.line(boxes[0][0] + box_w, box_y + box_h / 2, boxes[1][0], box_y + box_h / 2)
        c.line(boxes[1][0] + box_w, box_y + box_h / 2, boxes[2][0], box_y + box_h / 2)
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 6.9)
        mid_x = (boxes[0][0] + box_w + boxes[1][0]) / 2
        c.drawCentredString(mid_x, box_y + box_h / 2 + 6, _conduit(packet))
        c.drawCentredString(mid_x, box_y + box_h / 2 - 12, f"{job.run_ft} ft one way")
        c.setFont("Helvetica", 6.9)
        c.drawCentredString(mid_x, box_y + box_h / 2 - 22, _wire_text(packet))

        # The generator breaker's circuit number, its row in the panel schedule.
        c.setFillColor(INK)
        c.setFont("Helvetica-Bold", 6.9)
        c.drawCentredString(boxes[1][0] + box_w / 2, box_y - 12, f"Generator circuit: {generator_circuit_number(job)}")

        # The dashed NEC 110.26 working space in front of the panel and the transfer equipment.
        c.setStrokeColor(GREEN)
        c.setLineWidth(1.0)
        c.setDash(5, 3)
        for bx, _title, _lines in boxes[:2]:
            c.rect(bx, box_y - 42, box_w, 36, stroke=1, fill=0)
        c.setDash()
        c.setFillColor(GREEN)
        c.setFont("Helvetica", 6.6)
        c.drawString(24, box_y - 54, WORKING_SPACE_LABEL)


def generator_circuit_number(job) -> str:
    """The generator backfeed's circuit number: its row in the panel schedule, or none for a transfer switch."""
    if not job.spaces_needed:
        return "transfer switch, not a panel circuit"
    return str(len(job.existing_circuits) + 1)


def checklist_rows(packet: GeneratorPacket) -> list[tuple[str, str, str]]:
    job = packet.job
    plan = job.plan
    rows = []
    for req in job.jurisdiction.checklist_for("generator").items:
        sec = req.section
        if sec == "by_others":
            rows.append((req.item, f"By others: {req.who}", "By others"))
        elif sec == "application":
            missing = job.jurisdiction.needs_parcel_number and not (plan and plan.parcel_number)
            rows.append((req.item, "Page 2: add the parcel number" if missing else "Page 2: fields ready", "Open" if missing else "Ready"))
        elif sec == "site_plan":
            rows.append((req.item, f"Page 3: to scale, 1 in = {printed_scale(plan)} ft" if plan else "Page 3: schematic only", "Ready" if plan else "Open"))
        elif sec == "equipment":
            has_doc = bool(find_equipment(job.generator_model, "appliance") or job.data_sheet_attached)
            rows.append((req.item, "Page 7 + data sheet attached" if has_doc else "Page 7: attach interlock/generator cut sheet", "Ready" if has_doc else "Attach"))
        elif sec == "fuel":
            if job.fuel_type:
                rows.append((req.item, f"Page {SECTION_PAGES['one_line']}: fuel type on the one-line", "Ready"))
            else:
                rows.append((req.item, "Page 4: add the generator's fuel type", "Open"))
        elif sec == "equipment_layout":
            rows.append((req.item, f"Page {EQUIPMENT_LAYOUT_PAGE}: equipment layout and working space", "Ready"))
        else:
            shown = panel_row(job, sec, SECTION_PAGES["one_line"], burial=None)
            if shown:
                rows.append((req.item, *shown))
            elif sec in SECTION_PAGES:
                rows.append((req.item, f"Page {SECTION_PAGES[sec]}", "Ready"))
            else:
                rows.append((req.item, "Not in this packet: add it by hand", "Open"))  # never shown as done
    return rows + [(PANEL_SCHEDULE_ITEM, *panel_schedule_row(job, SECTION_PAGES["panel_schedule"]))]


def scope_of_work(packet: GeneratorPacket) -> str:
    job = packet.job
    model = f" ({job.generator_model})" if job.generator_model else ""
    fuel = f" Fuel type: {FUEL_LABELS[job.fuel_type].lower()}." if job.fuel_type else ""
    return (
        f"Install one {TRANSFER_LABELS[job.transfer_type]} rated {packet.breaker} A at 120/240 V "
        f"for a {display_number(job.generator_kw)} kW standby generator{model} at {LOCATION_LABELS[job.location]}.{fuel} "
        f"Run {job.run_ft} ft feeder, {_wire_text(packet)}, in {_conduit(packet)}, and install NEC 702.7 warning signage."
    )


def equipment_layout_page(packet: GeneratorPacket) -> list:
    """The equipment layout and NEC 110.26 working space, drawn from the packet's own one-line and schedule data."""
    return [
        _p(EQUIPMENT_LAYOUT_TITLE, H1),
        _p("Plan-view schematic of the main panel, transfer equipment and generator / inlet, with the "
           "feeder raceway, conductor sizes, circuit number and the NEC 110.26 working space.", SMALL),
        Spacer(1, 10),
        diagram(EquipmentLayout(packet), share=0.75),
    ]


def application_fields(packet: GeneratorPacket) -> list[tuple[str, str]]:
    job = packet.job
    return [
        ("Project address", job.address),
        ("Parcel number", job.plan.parcel_number if job.plan and job.plan.parcel_number else "Not on file"),
        ("Jurisdiction", job.jurisdiction.label),
        ("Property owner", job.customer),
        ("Permit type", f"Electrical, residential {TRANSFER_LABELS[job.transfer_type]}"),
        ("Generator / equipment", job.generator_model or f"{display_number(job.generator_kw)} kW standby generator"),
        ("Contractor", job.contractor),
        ("License number", job.license_number or "Owner-Builder"),
    ]


def render_generator_packet_pdf(packet: GeneratorPacket) -> bytes:
    job = packet.job
    jurisdiction = job.jurisdiction
    checklist_cell = (
        f"{jurisdiction.label}\n{jurisdiction.checklist_for('generator').source_label}"
        if jurisdiction.known_for("generator")
        else f"{jurisdiction.label}\nUsing the national NEC checklist. Confirm local amendments with {jurisdiction.name if jurisdiction.name != 'This area' else 'your city'}."
    )
    parcel = f"\nParcel {job.plan.parcel_number}" if job.plan and job.plan.parcel_number else ""
    cover = cover_page(
        title=f"{TRANSFER_TITLES[job.transfer_type]} Permit Packet",
        address=job.address,
        job_cell=f"{job.home.square_feet:,} sq ft home{parcel}\n{display_number(job.generator_kw)} kW generator, {packet.breaker} A\nCustomer: {job.customer}",
        contractor_cell=contractor_with_license(job.contractor, job.license_number),
        checklist_cell=checklist_cell,
        checklist_rows=checklist_rows(packet),
        checks=[(c.name, c.result, c.passed, c.neutral, c.assumed) for c in packet.checks],
        flags=packet.flags,
        stamp_box_in=jurisdiction.stamp_box_in,
    )
    app_sec = application_page(
        rows=application_fields(packet), scope=scope_of_work(packet),
        inspections=[("Rough", "Inlet box, feeder conduit and grounding before covering"), ("Final", "Interlock/transfer operation, neutral bonding and NEC 702.7 signage")],
    )
    if job.plan is None:
        site_sec = [_p("Site Plan", H1), _p("Shows main panel, generator / inlet box and feeder route.", SMALL), Spacer(1, 10), diagram(SitePlan(packet), share=0.8)]
    else:
        markers = [PlanMarker(job.plan.markers["panel"], INK, "P"), PlanMarker(job.plan.markers["inlet"], GREEN, "G")]
        site_sec = site_plan_page(
            address=job.address, plan=job.plan, markers=markers, underground=bool(job.trench_ft),
            legend=[f"P  Main panel, {job.service_amps} A", f"G  Generator / {packet.breaker} A inlet"],
            measures=[f"Feeder run: {job.run_ft} ft"], outline_over_aerial=jurisdiction.outline_over_aerial,
        )
    one_line_sec = fit_page([
        _p("Single-Line Diagram", H1),
        _p("Utility service, transfer/interlock equipment, generator feeder and inlet.", SMALL),
        Spacer(1, 10),
        diagram(OneLine(packet), legend=one_line_data(job)),
        Spacer(1, 8),
        _table([_heads("Segment", "Conductors", "Conduit", "Protection"),
                [_p("Generator feeder"), _p(_wire_text(packet)), _p(_conduit(packet)), _p(f"{packet.breaker} A, 2-pole")]],
               [1.4 * inch, 2.4 * inch, 1.3 * inch, content_w() - 5.1 * inch]),
    ] + heat_block(packet.branch.heat, jurisdiction))
    load_sec = load_page(
        packet.load,
        method=f"Optional dwelling method, {jurisdiction.code_name} 220.82 (NEC Article 702 standby load review).",
        service_rows=[("Existing service", f"{job.service_amps} A"), ("Generator capacity", f"{display_number(job.generator_kw)} kW ({display_number(job.generator_amps)} A)")],
    )
    rows = existing_rows(job.existing_circuits)
    if job.spaces_needed:
        rows.append(ScheduleRow(f"Generator interlock backfeed (this permit)", f"{packet.breaker} A", 2, "New"))
    sched_sec = panel_schedule_page(
        [(f"Main panel, {job.service_amps} A", rows)], entered=bool(job.existing_circuits),
        spaces_note=f"Open spaces: {job.open_breaker_spaces} before, {max(job.open_breaker_spaces - job.spaces_needed, 0)} after.",
        header=panel_header(job),
    )
    equip_rows = [
        ("Transfer equipment", TRANSFER_LABELS[job.transfer_type].capitalize(), "UL 1008 / UL 67 listed"),
        ("Generator / inlet", f"{display_number(job.generator_kw)} kW, {packet.breaker} A, 120/240 V", "NEC 702.5 / 702.7"),
        ("Feeder conductors", f"{_wire_text(packet)}, {_conduit(packet)}", f"{jurisdiction.code_name} 310.16"),
    ]
    equip_sec = [
        _p("Equipment Data", H1),
        _p("Attach manufacturer cut sheets for the interlock kit / transfer switch and generator inlet box.", SMALL),
        Spacer(1, 10),
        _table([_heads("Item", "Specification", "Listing")] + [[_p(a), _p(b), _p(c)] for a, b, c in equip_rows],
               [1.6 * inch, content_w() - 3.5 * inch, 1.9 * inch]),
    ]
    rev_sec = review_page([
        "Interlock kit or transfer switch UL-listed for the exact panel model (NEC 702.5)",
        "Generator neutral configuration verified (floating for 2-pole interlock; switched for 3-pole ATS)",
        "Permanent backup-power warning signage installed at service entrance (NEC 702.7)",
        "Exterior inlet box mounted away from windows, doors and air intakes",
    ])
    layout_sec = equipment_layout_page(packet)
    pdf = build_document(
        [cover, app_sec, site_sec, one_line_sec, load_sec, sched_sec, equip_sec, rev_sec, layout_sec],
        title=demo_title(f"{TRANSFER_TITLES[job.transfer_type]} Permit Packet"),
        block=title_block_for(job),
        sheet_titles=["Checklist and Checks", "Permit Application Data", "Site Plan", "Single-Line Diagram", "Load Calculation", "Panel Schedule", "Equipment Data", "Pre-Submittal Review", EQUIPMENT_LAYOUT_TITLE],
    )
    sheet = find_equipment(job.generator_model, "appliance")
    return attach_data_sheets(pdf, [sheet] if sheet else [], after_title="Equipment Data")
