"""Mesa, AZ: City of Mesa Development Services issues residential electrical permits through DIMES.

Code: the 2024 I-Codes and the 2023 NEC with Mesa amendments (the "Mesa Electrical Code"),
for applications submitted on or after January 8, 2026. Mesa's amendments go past the base
NEC in three places that touch these jobs: EMT needs an additional equipment grounding
conductor (250.118(A)(4)), service disconnect labels must be engraved or raised and fastened
with screws or rivets (230.70(B)), and an EVSE over 60 A or 150 V to ground needs a lockable
disconnect 15 to 50 ft away with a plaque showing where it is (625.43).
Utility: SRP serves most of Mesa; downtown is Mesa Electric and parts of the city are APS.
"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

DIMES_URL = "https://aca-prod.accela.com/MESA/Default.aspx"
NEC_AMENDMENTS_URL = (
    "https://www.mesaaz.gov/files/assets/public/v/3/business-development/devsvcs/codeamendments/"
    "2023-nec-amendment.pdf"
)
CHECKLIST_URL = (
    "https://www.mesaaz.gov/files/assets/public/v/3/business-development/devsvcs/checklists/"
    "ned-checklist-electric-code.pdf"
)
FORMAT_URL = "https://mesaaz.gov/home/showpublisheddocument/22231/637570186539370000"
CODE_NOTE = (
    "Mesa enforces the 2024 International Codes and the 2023 NEC with Mesa amendments "
    "(the Mesa Electrical Code), for applications submitted on or after January 8, 2026."
)
SOURCE_LABEL = "From City of Mesa Development Services and the Mesa Electrical Code"


def _checklist_note(text: str, when: str = "always") -> Note:
    return Note(when, "Mesa electrical plan checklist: " + text, CHECKLIST_URL)


# Items from Mesa's Electrical Plan Submittal Checklist (2023 NEC, with Mesa amendments) that apply to
# these residential jobs. The checklist is one document for all occupancies, so only the items that touch
# a residential service, feeder or branch circuit are carried over.
CL_CLEARANCES = _checklist_note("show working clearances around all electrical equipment (NEC 110.26) and the "
                                "dedicated equipment space with dimensions (NEC 110.26(E)).")
CL_LABEL = _checklist_note("label every piece of equipment on the one-line as new, existing or relocated (NEC 110.22(A)).")
CL_AFCI = _checklist_note("provide arc-fault circuit interrupter protection where required (NEC 210.12).")
CL_SPD = _checklist_note("provide surge protection (NEC 215.18, 230.67).")

# The same checklist's items that the packet draws, so they are Requirements it shows as Ready.
# The checklist's panel item also asks for voltage, phase and new/existing/relocated, which the packet does
# not show as such, so the panel Requirement covers only location, bus rating and main.
FAULT_CURRENT = Requirement("Fault current identified and equipment AIC ratings verified (NEC 110.9, 110.10)",
                            "fault_current", CHECKLIST_URL)
EGC_SIZE = Requirement("Equipment grounding conductor size identified (NEC 250.122)", "egc_size", CHECKLIST_URL)
PANEL_DETAILS = Requirement("Panel location, bus rating and main breaker or main lugs identified "
                            "(NEC 408.4(A), 408.36, 240.4)", "panel_details", CHECKLIST_URL)
BURIAL = Requirement("Burial depth identified for underground runs (NEC 300.5)", "burial", CHECKLIST_URL)
GEC = Requirement("Grounding electrode conductor sized (NEC 250.50, 250.66)", "gec", CHECKLIST_URL)
SURGE = Requirement("Surge protective device, Type 1 or Type 2, shown on the riser (NEC 230.67)", "surge",
                    CHECKLIST_URL)

UTILITY_CHECK = Note(
    "always",
    "SRP serves most of Mesa. Downtown Mesa is served by Mesa Electric and some areas by APS: "
    "confirm the utility on the customer's bill.",
)
EMT_EGC = Note("always", "Mesa Electrical Code 250.118(A)(4): EMT counts as the equipment grounding "
               "path only with an additional equipment grounding conductor pulled in it.", NEC_AMENDMENTS_URL)
APPLICATION = Requirement("DIMES residential electrical permit: address/APN, scope and valuation", "application")
LICENSE = Requirement("Contractor Licensure Verification Form and Arizona ROC electrical license", "application")
AZ_811 = Note(
    "trench",
    "Contact Arizona 811 at least two full working days before digging (811 or (602) 263-1100 in "
    "Maricopa County).",
)

MESA = Jurisdiction(
    key="mesa-az", name="Mesa", state="AZ", known=True,
    last_verified="2026-11-17",
    who_may_pull="",
    portal_url=DIMES_URL,
    fee_note="Mesa publishes a citywide Fees and Charges schedule; its Development Services pages list no electrical permit amounts.",
    sources=("https://www.mesaaz.gov/Business-Development/Development-Services", "https://www.mesaaz.gov/Business-Development/Development-Services/Building-Permit-Plan-Review", NEC_AMENDMENTS_URL, CHECKLIST_URL),
    nec_edition="2023 NEC",
    permit_required={},
    permit_notes={},
    bbox=(-111.8945, 33.2774, -111.5633, 33.5698), center=(-111.8315, 33.4152),  # Mapbox place bounds (west, south, east, north) and (lon, lat)
    department="City of Mesa Development Services, Building Safety",
    phone="(480) 644-4273",
    email="PermitServices@mesaaz.gov",
    website=DIMES_URL,
    website_label="DIMES (Mesa online permits)",
    submit_how=(
        "Apply in DIMES and upload every document as a PDF labeled Construction Documents, with the "
        "Contractor Licensure Verification Form. Pay fees, request inspections and print the approved "
        "set for the job site from the same DIMES record."
    ),
    needs_parcel_number=True,
    # Mesa, "Submission and Formatting Requirements for Electronic Plans" (FORMAT_URL): a 4-inch by 4-inch
    # empty box on the cover sheet for City stamps; plan sheets are not submitted as separate PDFs; each
    # sheet is electronically sealed and signed by the designer of record. The same document says a wrong
    # sheet size, scale, margins or orientation is not accepted, but the size itself is not in the text
    # we could read, so sheet_size stays at the default until Mesa's number is confirmed.
    stamp_box_in=4.0,
    single_pdf_only=True,
    # ASHRAE 2% annual cooling dry-bulb design temperature, Phoenix Sky Harbor (WMO 722780), the
    # reporting station nearest Mesa. 109 F lies between the 1% (110.2 F) and 2.5% (108.1 F) values
    # published for that station, and every ambient from 106 to 113 F falls in the same NEC
    # 310.15(B)(1) row (41-45 C, factor 0.87). CONFIRM the exact 2% figure on the station page below.
    design_ambient_f=109,
    design_ambient_source=(
        "https://ashrae-meteo.info/v3.0/index.php?lat=33.44&lng=-111.99&place=%27%27&wmo=722780&ashrae_version=2017"
    ),
    code_note=CODE_NOTE,
    utility="SRP (Salt River Project)",
    utility_short="SRP",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("DIMES residential electrical permit: address/APN, scope and valuation", "application"),
                Requirement("Contractor Licensure Verification Form and Arizona ROC electrical license", "application"),
                Requirement("Load calculation with the charger at 100% of its rating (NEC 220, 625.42)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit and a separate EGC in EMT "
                            "(Mesa 250.118(A)(4))", "one_line"),
                Requirement("Charger data sheet and NRTL listing (UL 2594 / UL 2202)", "equipment"),
                Requirement("Site plan showing the panel, charger and route", "site_plan"),
                FAULT_CURRENT, EGC_SIZE, PANEL_DETAILS, BURIAL,
            ),
            source_url=NEC_AMENDMENTS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Mesa Electrical Code 250.118(A)(4): EMT counts as the equipment grounding "
                     "path only with an additional equipment grounding conductor pulled in it."),
                Note("disconnect", "Mesa Electrical Code 625.43: over 60 A or 150 V to ground, the EVSE "
                     "disconnect must be lockable open, 15 to 50 ft from the equipment, with a plaque on "
                     "the equipment showing where it is."),
                UTILITY_CHECK,
                AZ_811,
                CL_CLEARANCES, CL_LABEL, CL_AFCI,
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("DIMES residential electrical permit: address/APN, scope, new service size and valuation", "application"),
                Requirement("Contractor Licensure Verification Form and Arizona ROC electrical license", "application"),
                Requirement("Load calculation", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter socket listing; meter socket per SRP Electric Service Specifications", "equipment"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("SRP service request; SRP reconnects after Mesa sends its clearance", "utility"),
                FAULT_CURRENT, PANEL_DETAILS, GEC, SURGE,
            ),
            source_url=NEC_AMENDMENTS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Mesa Electrical Code 230.70(B): service disconnect labels need engraved or "
                     "raised letters fastened with screws or rivets. Plastic tape labels are not accepted."),
                Note("always", "2023 NEC 230.85: one- and two-family dwellings need an outdoor emergency "
                     "disconnect, readily accessible and marked."),
                Note("always", "SRP reconnects after Mesa passes the service inspection and sends its clearance "
                     "(allow three to four days). Downtown Mesa is Mesa Electric and some areas APS: confirm the "
                     "utility on the bill."),
                Note("always", "Mesa's Residential Utility Repair permit in DIMES lists installing a residential "
                     "200 A panel with no plan upload. Confirm with Permit Services that the scope fits it."),
                CL_CLEARANCES, CL_LABEL,
                _checklist_note("show the service disconnect location, rating and grouping (NEC 230.70, 230.71) "
                                "and the grounding electrode system (NEC 250.50)."),
                _checklist_note("provide emergency disconnects for dwelling units (the checklist cites NEC 225.41)."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                APPLICATION,
                LICENSE,
                Requirement("Load calculation for the feeder and subpanel (NEC 220)", "load"),
                Requirement("One-line diagram with the feeder breaker, 4-wire feeder and a separate EGC in EMT "
                            "(Mesa 250.118(A)(4))", "one_line"),
                Requirement("Subpanel specifications and listing", "equipment"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                FAULT_CURRENT, EGC_SIZE, PANEL_DETAILS, BURIAL,
            ),
            source_url=NEC_AMENDMENTS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Subpanel: keep the neutral and ground bars separate and remove the bonding screw or "
                     "strap. The neutral is bonded only at the service disconnect (NEC 250.24(A)(5), 250.142(B))."),
                Note("always", "Subpanel in a detached building: add a grounding electrode there (NEC 250.32) and a "
                     "disconnect at the building (NEC 225.31)."),
                EMT_EGC,
                AZ_811,
                CL_CLEARANCES, CL_LABEL, CL_AFCI, CL_SPD,
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                APPLICATION,
                LICENSE,
                Requirement("Load calculation with the new appliance (NEC 220)", "load"),
                Requirement("One-line diagram with breaker, conductors, disconnect and a separate EGC in EMT "
                            "(Mesa 250.118(A)(4))", "one_line"),
                Requirement("Appliance data sheet with nameplate rating and listing", "equipment"),
                Requirement("Site plan showing the panel, the appliance and the route", "site_plan"),
                FAULT_CURRENT, EGC_SIZE, PANEL_DETAILS,
            ),
            source_url=NEC_AMENDMENTS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Air conditioners, heat pumps and motor-driven appliances need a disconnect within "
                     "sight of the unit (NEC 440.14, 422.31)."),
                EMT_EGC,
                AZ_811,
                CL_CLEARANCES, CL_LABEL, CL_AFCI,
                _checklist_note("identify burial depths (the checklist cites NEC Table 300.7(A)).", "trench"),
            ),
        ),
    },
)
