"""Bellevue, WA, from the City of Bellevue's own electrical pages and forms, Washington's electrical rules and PSE.

Bellevue runs its own electrical permit and inspection program (not L&I). Applications go in through
MyBuildingPermit.com. Code (Bellevue Codes page; BCC 23.30.015, Ord. 6781, March 4, 2024): the 2023 NEC as
adopted and amended by Washington (chapter 296-46B WAC), plus the 2023 Washington Cities Electrical Code,
Parts 1 and 3 (Part 2, Administration, is excluded), effective April 1, 2024. Bellevue's only local
amendment (BCC 23.30.450.14) is about transformer disconnects and does not touch these four jobs.

What Bellevue publishes for these jobs: its electrical permits page (what needs a permit, when plan review
applies, the forms), the Electrical Plan Review Submittal Guide (August 17, 2021), the Load Calculation Forms
(Standard and Optional, July 2019; the packet's load calc is the Optional, NEC 220.82, method), the Panel
Schedules Form, the Fault Current Calculation Form, Handout B-4 for single-family EV chargers (November
2010), the Altered Electrical Service Inspection Process for single-family homes (December 7, 2023) and the
Electrical Grounding and Water Service Re-piping guide (March 4, 2020). Bellevue publishes no residential
checklist per job, so each checklist below is built from those documents and the WCEC/WAC text.

Utility: Puget Sound Energy (PSE), Electric Service Handbook, Single-Family Residential (March 2026).

Plan review: the Submittal Guide lists installations under 2,500 sq ft with a load increase of 100 A or more,
or an altered service, without a separate single-family rule. Bellevue's permit records show single-family
service changes issued the same day. The packet carries everything plan review asks for (riser, load calc,
panel schedule with A.I.C., fault current) so it covers either path.
"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

PERMITS_URL = (
    "https://bellevuewa.gov/city-government/departments/development/permits/"
    "electrical-mechanical-plumbing-permits/electrical-permits"
)
CODES_URL = (
    "https://bellevuewa.gov/city-government/departments/development/codes-and-guidelines/"
    "building-fire-codes-and-guidelines"
)
BCC_URL = "https://bellevue.municipal.codes/BCC/23.30.015"
SUBMITTAL_GUIDE_URL = "https://bellevuewa.gov/sites/default/files/media/file/2019-06/Electrical-Plan-Review-Submittal-Guide.pdf"
LOAD_FORM_URL = "https://bellevuewa.gov/sites/default/files/media/document/2019-07/Load%20Calculation%20Form%20-%20Optional.pdf"
PANEL_FORM_URL = "https://bellevuewa.gov/sites/default/files/media/pdf_document/forms_panel_schedules_f.pdf"
FAULT_FORM_URL = "https://bellevuewa.gov/sites/default/files/media/pdf_document/forms_fault_current_calc.pdf"
APPLICATION_URL = "https://bellevuewa.gov/sites/default/files/media/pdf_document/Electrical-Application.pdf"
EV_HANDOUT_URL = "https://bellevuewa.gov/sites/default/files/media/pdf_document/B-4_EVchargestation.pdf"
ALTERED_SERVICE_URL = (
    "https://bellevuewa.gov/sites/default/files/media/pdf_document/2023/"
    "Altered%20Electrical%20Service%20Inspection%20Process%20%28SF%20Residential%29.pdf"
)
GROUNDING_URL = (
    "https://bellevuewa.gov/sites/default/files/media/file/2020/"
    "Electrical%20Grounding%20and%20Water%20Service%20Repiping.pdf"
)
WCEC_URL = "https://MyBuildingpermit.com/sites/default/files/2023%20WCEC_4-1-24_0.pdf"
WAC_URL = (
    "https://lawfilesext.leg.wa.gov/Law/WACArchive/2024/pdf/WAC%20296%20-%2046B%20CHAPTER/"
    "WAC%20296%20-%2046B%20COMBINEDCHAPTER.pdf"
)
PSE_HANDBOOK_URL = (
    "https://www.pse.com/-/media/Feature/PSE/Construction-Service/Technical-Resource-Documents/"
    "Electric-Service-SingleFamily-Residential-Permanent-and-Temporary-Service/1218-Electric_Service_handbook.pdf"
)
PSE_SOCKETS_URL = (
    "https://www.pse.com/-/media/Feature/PSE/Construction-Service/Technical-Resource-Documents/"
    "Electric-Service-SingleFamily-Residential-Permanent-and-Temporary-Service/7517-Meter_Socket_Catalog.pdf"
)
PSE_EV_URL = "https://www.pse.com/en/pages/electric-cars/Home-charging/qualifying-income"
DESIGN_TEMP_URL = (
    "https://lawfilesext.leg.wa.gov/Law/WACArchive/2019/htm/WAC%20%2051%20%20TITLE/WAC%20%2051%20-%2011R%20CHAPTER/"
    "WAC%20%2051%20-%2011R-60100.htm"
)

CODE_NOTE = (
    "Bellevue enforces the 2023 NEC as adopted and amended by Washington (WAC 296-46B) and the 2023 Washington "
    "Cities Electrical Code, Parts 1 and 3 (BCC 23.30.015), effective April 1, 2024."
)
SOURCE_LABEL = "From Bellevue's electrical permit forms and guides, the 2023 WCEC and WAC 296-46B"

# Every job type
APPLICATION = Requirement(
    "MyBuildingPermit.com electrical application: address, parcel number, owner, contractor, scope and value",
    "application", APPLICATION_URL,
)
LOAD = Requirement(
    "Load calculation on Bellevue's Optional Format (NEC 220.82): first 10 kVA at 100%, rest at 40%",
    "load", LOAD_FORM_URL,
)
PANEL_SCHEDULE = Requirement(
    "Panel schedule: circuits, breakers and poles, with the new work marked", "panel_schedule", PANEL_FORM_URL,
)
FAULT_CURRENT = Requirement(
    "Available fault current and equipment A.I.C. rating (Bellevue Fault Current Calculation Form; NEC 110.9, 110.10)",
    "fault_current", FAULT_FORM_URL,
)
PANEL_DETAILS = Requirement(
    "Panel location, bus rating and main breaker or main lugs identified", "panel_details", PANEL_FORM_URL,
)
EGC_SIZE = Requirement(
    "Conductor, raceway and equipment grounding conductor sizes on the one-line (NEC 250.122)", "egc_size",
    SUBMITTAL_GUIDE_URL,
)
SITE_PLAN = "site_plan"

# Notes for every job type
PANEL_FORM_NOTE = Note(
    "always",
    "Bellevue's Panel Schedules Form also asks for each circuit's connected kVA and load type and the panel's "
    "A.I.C. rating. The A.I.C. rating and available fault current are on the one-line; if the job goes to plan "
    "review, copy the schedule onto Bellevue's form and add the kVA per circuit.",
    PANEL_FORM_URL,
)
PERMIT_AND_INSPECTION = Note(
    "always",
    "Bellevue: apply on MyBuildingPermit.com. Work that needs no plan review can be issued over the counter the "
    "same day. Inspection is still required before covering or energizing.",
    PERMITS_URL,
)
PLAN_REVIEW = Note(
    "always",
    "Bellevue's Electrical Plan Review Submittal Guide lists installations under 2,500 sq ft with a load increase "
    "of 100 A or more, or an altered service, for plan review. It does not separate single-family homes, and "
    "Bellevue's permit records show single-family service changes issued the same day. If MyBuildingPermit "
    "routes the job to plan review, this packet already has the riser, load calc, panel schedule with A.I.C. "
    "and fault current. Questions: MEP review, (425) 452-6873, MEPreview@bellevuewa.gov.",
    SUBMITTAL_GUIDE_URL,
)
OUTDOOR_HEIGHT = Note(
    "always",
    "WCEC 240.24(C) / WAC 296-46B-240: an outdoor enclosure holding a breaker sits with its bottom at least 24 in "
    "above finished grade, unless it is listed for pad or ground mounting or sits over paving extending 3 ft or "
    "more, or over a roof.",
    WCEC_URL,
)
NO_CLOSETS = Note(
    "always",
    "WCEC 230.70(A)(3), 225.31 / WAC 296-46B-408: service equipment, panelboards and subpanels are readily "
    "accessible and not in bathrooms, clothes closets, toilet rooms or shower rooms. Indoor panels have working "
    "space and lighting.",
    WCEC_URL,
)
EMT_WET = Note(
    "always",
    "WCEC 358.10(D), 358.12: EMT in a wet location carries a separate equipment grounding conductor sized per "
    "NEC 250.122, and EMT is not installed in the earth or in concrete on or below grade.",
    WCEC_URL,
)
NM_OUTDOORS = Note(
    "always",
    "WCEC 334.12: NM cable may run inside a short outdoor conduit used for protection only if the cable is "
    "unbroken from inside, the conduit is not flexible metal, not over 10 ft, not below grade, and sealed and "
    "drained.",
    WCEC_URL,
)
DIG = Note(
    "trench",
    "Call 811 (Washington 811) at least two business days before digging. WCEC Table 300.5 note 6: where "
    "practicable, raceways go beneath an interior slab.",
    WCEC_URL,
)

# EV charger (the PSE call is a note: the EV packet has no utility page)
EV_NOTES = (
    PERMIT_AND_INSPECTION,
    PANEL_FORM_NOTE,
    Note(
        "always",
        "Bellevue Handout B-4: an electrical permit and inspection are required for a home charger, and the "
        "inspector's final approval comes before the charger is energized. Only the property owner or a "
        "Washington-licensed electrical contractor can pull the permit.",
        EV_HANDOUT_URL,
    ),
    Note(
        "always",
        "PSE: you or the installer call Customer Construction Services at 1-888-321-7779 (7 a.m. to 5 p.m., "
        "Monday to Friday) to confirm the existing service can support the new charger.",
        PSE_EV_URL,
    ),
    OUTDOOR_HEIGHT, EMT_WET, NM_OUTDOORS, DIG,
)

# Service upgrade
EMERGENCY_DISCONNECT = Requirement(
    "Outdoor emergency disconnect when the service size changes or the meter, mast or riser moves "
    "(WCEC / WAC 296-46B-230(11), replacing NEC 230.85(C))",
    "emergency_disconnect", WCEC_URL,
)
SURGE = Requirement(
    "Surge protective device, Type 1 or Type 2, shown on the riser (NEC 230.67)", "surge", WCEC_URL,
)
GEC = Requirement(
    "Grounding electrode system and GEC sized (NEC 250.50, 250.66)",
    "gec", WCEC_URL,
)
RISER = Requirement(
    "Riser (one-line) diagram with service conductors, raceway sizes and types, grounding and bonding",
    "one_line", SUBMITTAL_GUIDE_URL,
)
PSE_SERVICE = Requirement(
    "PSE Customer Construction Services (1-888-321-7779): panel amperage change, disconnect and reconnect, "
    "5 to 10 working days' notice",
    "utility", PSE_HANDBOOK_URL,
)
SERVICE_NOTES = (
    PERMIT_AND_INSPECTION,
    PANEL_FORM_NOTE,
    PLAN_REVIEW,
    Note(
        "always",
        "WCEC 230.85 / WAC 296-46B-230(11): when service equipment for a one- or two-family dwelling is replaced, "
        "an emergency disconnecting means is required whenever the service ampacity is increased or decreased, or "
        "when the service disconnect, meter base, overhead mast or underground riser is relocated. An outdoor "
        "meter-main breaker can serve as it. WCEC 110.22(E): group it with any PV rapid-shutdown or other "
        "emergency disconnects, or put a red plate with white letters at each one naming the others.",
        WCEC_URL,
    ),
    Note(
        "always",
        "WCEC 230.70(A)(1): an outside service disconnect is installed on the building it serves. Inside, the "
        "service raceway runs no more than 15 ft into the building before the disconnect. Label the disconnect "
        "with a plate in 1/2 in letters naming the building served and its function as the main disconnect "
        "(WCEC 110.22(D)).",
        WCEC_URL,
    ),
    Note(
        "always",
        "WCEC 230.28: a service mast that supports the drop is at least 2 in rigid metal conduit, with approved "
        "flashing, bracing, no couplings above the support point, and guys if the drop attaches more than 24 in "
        "above the roof or runs over 100 ft.",
        WCEC_URL,
    ),
    Note(
        "always",
        "WCEC 250.104(A): bond the hot and cold water pipes together (a mixing valve counts if the inspector can "
        "confirm it). WCEC 250.104(B): the gas piping bond is at least #6 copper, on the load side of the gas meter, "
        "with a listed connector at an accessible point. Bellevue's grounding guide: where ground rods are used, two 5/8 in x 8 ft rods at least 6 ft "
        "apart; keep the water pipe electrode bonded around any dielectric union or PRV.",
        GROUNDING_URL,
    ),
    Note(
        "always",
        "PSE Handbook (March 2026): meter top 4 to 6 ft above grade, on the front third of the house; the "
        "disconnect within 5 ft of the meter; meter hot-sequenced, no disconnect ahead of it. Upgrades over "
        "200 A may need 3 in Schedule 40 gray PVC end to end. Sizes: 200 A up to 2,500 sq ft, 320/400 A from "
        "2,501 to 3,500 sq ft.",
        PSE_HANDBOOK_URL,
    ),
    Note(
        "always",
        "PSE: the meter socket is ring-type (screw-type stainless or aluminum ring), and PSE lists the sockets and "
        "meter-main combos it accepts on Form 7517 (May 16, 2024). The packet's checks fail a meter-main that is "
        "not on that list. A combo unit also needs the manufacturer's drawings sent to PSE for review.",
        PSE_SOCKETS_URL,
    ),
    Note(
        "always",
        "PSE: the service is disconnected for the cutover and is not re-energized until every new wire is landed "
        "with grounding and bonding in place. If the permit is posted and the work is finished but not yet "
        "inspected, PSE may re-energize when the work looks safe, and the inspection follows.",
        PSE_HANDBOOK_URL,
    ),
    Note(
        "always",
        "Bellevue Altered Service Inspection (December 7, 2023): give the inspector a contact phone; have the "
        "meter base, mast, grounding and bonding done and every termination torqued. The inspector calls before "
        "8 a.m. with a 2-hour window and may give a partial approval with a sticker on the meter base.",
        ALTERED_SERVICE_URL,
    ),
    OUTDOOR_HEIGHT, NO_CLOSETS,
)

# Subpanel
FEEDER_ONE_LINE = Requirement(
    "One-line diagram with the feeder breaker, feeder conductors, raceway and equipment grounding conductor",
    "one_line", SUBMITTAL_GUIDE_URL,
)
SUBPANEL_NOTES = (
    PERMIT_AND_INSPECTION,
    PANEL_FORM_NOTE,
    PLAN_REVIEW,
    NO_CLOSETS,
    Note(
        "always",
        "WCEC 225.36: a subpanel in a detached garage or ADU needs a building disconnect there; a generator "
        "disconnect installed per its subsection (2)(b) need not be rated as service equipment.",
        WCEC_URL,
    ),
    OUTDOOR_HEIGHT, EMT_WET, NM_OUTDOORS, DIG,
)

# 240 V circuit
APPLIANCE_ONE_LINE = Requirement(
    "One-line diagram with breaker, conductors, raceway and the appliance disconnect", "one_line", SUBMITTAL_GUIDE_URL,
)
APPLIANCE_NOTES = (
    PERMIT_AND_INSPECTION,
    PANEL_FORM_NOTE,
    Note(
        "always",
        "WCEC 680.15, 680.40: hot tub or spa equipment that is field installed sits at least 5 ft from the inside "
        "wall of the tub (by the shortest cord path) unless a permanent barrier separates them; a self-contained "
        "tub's equipment is within 5 ft and listed with the tub; a factory skid pack is at least 5 ft away.",
        WCEC_URL,
    ),
    Note(
        "always",
        "WCEC 422.10: a water heater rated over 3,500 W and under 4,900 W at 208 or 240 V gets branch conductors "
        "no smaller than #10 copper.",
        WCEC_URL,
    ),
    Note(
        "always",
        "WCEC 440.52(A)(5): a heat pump or air conditioner breaker does not exceed the maximum overcurrent "
        "protection on the nameplate.",
        WCEC_URL,
    ),
    OUTDOOR_HEIGHT, EMT_WET, NM_OUTDOORS,
)


BELLEVUE = Jurisdiction(
    key="bellevue-wa", name="Bellevue", state="WA", known=True,
    last_verified="2026-11-17",
    who_may_pull="Property owners or their state-licensed electrical contractors. Bellevue Handout B-4 says only property owners or their state-licensed electrical contractors can get an electrical permit and perform the electrical work, and the electrical permit application certifies the applicant is the owner (or owner's authorized agent) or an appropriately licensed contractor.",
    portal_url="https://mybuildingpermit.com/",
    fee_note="Bellevue's electrical permits page lists no dollar amounts and points to its Permit Fees and Payment page and Permit Fee Estimator. Handout B-4 describes a flat fee for a single-family EV charger permit and inspection; check the current amount with the city.",
    sources=(PERMITS_URL, EV_HANDOUT_URL, APPLICATION_URL, BCC_URL, CODES_URL),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True},
    permit_notes={
        EV_CHARGER: "Bellevue's electrical permits page lists installing an electric vehicle charging station as work that needs an electrical permit, and Handout B-4 says an electrical permit and an inspection are required.",
        SERVICE_UPGRADE: "Bellevue's electrical permits page says electrical permits are required for changes to the service panel. Plan review may apply to altered services rated 100 amps or more.",
        SUBPANEL: "Bellevue's electrical permits page lists adding a panel as work that needs an electrical permit.",
    },
    # Census TIGERweb incorporated place extent (west, south, east, north) and downtown (lon, lat).
    bbox=(-122.2228, 47.5350, -122.0793, 47.6608), center=(-122.2015, 47.6101),
    department="City of Bellevue Development Services, Permit Processing",
    phone="(425) 452-4898",
    email="permits@bellevuewa.gov",
    website="https://mybuildingpermit.com/",
    website_label="MyBuildingPermit.com (Bellevue electrical permits)",
    submit_how=(
        "Apply for the electrical permit on MyBuildingPermit.com and upload this packet. Work that needs no "
        "plan review is issued over the counter the same day. Request inspections on MyBuildingPermit.com or "
        "the inspection line, (425) 452-6875."
    ),
    needs_parcel_number=True,
    # Bellevue's guides state no sheet size, stamp box or single-PDF rule, so these stay at the defaults.
    # Washington State Energy Code Table RC-1 (WAC 51-11R-60100) outdoor design cooling temperature for
    # Bellevue: 83 F (28 C), which falls in the 26-30 C row of NEC 310.15(B)(1), factor 1.00 for 90 C wire.
    design_ambient_f=83,
    design_ambient_source=DESIGN_TEMP_URL,
    # Measured with tools/measure_alignment.py: FEMA/ORNL outlines sit (0, 0) ft from King County parcels over
    # 788 houses (spread 0.3 ft), and Bellevue's tree cover hides many roofs in summer aerials.
    outline_over_aerial=True,
    # PSE Form 7517 (May 16, 2024), residential single-phase 120/240 V meter combo units, every size, plus the
    # commercial-column 200 A combos PSE lists for the same service. Catalog numbers as PSE prints them.
    approved_meter_mains=(
        "U217MTBL", "U2M2R", "CMBEB200BTS", "CMBE88B200BTS", "CMBEB200BTF", "MBE4040B200BTS", "U4042MCC",
        "U40411230MCC", "U224MTB", "U214MTBL", "U214MTBPL", "U-3251-0-200-CB", "SC816D150C", "SC816D200C",
        "SC1624M100S", "SC2040M200C", "SC816F200PS", "SU816F200PS", "SU3040D400CB", "CU816D400CB",
        "MM0406L1200ESC", "MC0816B1200EST", "MM0404L1400SCS", "MC0816B1400SCS",
    ),
    approved_meter_mains_source=PSE_SOCKETS_URL,
    design_ambient_label="Washington State Energy Code outdoor design cooling temperature (Table RC-1)",
    code_note=CODE_NOTE,
    fallback_notes=(PERMIT_AND_INSPECTION, PLAN_REVIEW),
    utility="Puget Sound Energy (PSE)",
    utility_short="PSE",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                APPLICATION,
                LOAD,
                Requirement("One-line diagram: supply equipment level, breaker, conductor and conduit sizes, "
                            "disconnect if required", "one_line", SUBMITTAL_GUIDE_URL),
                Requirement("Site plan showing the panel, charger and route", SITE_PLAN, SUBMITTAL_GUIDE_URL),
                Requirement("Charger data sheet, ratings and NRTL listing (UL 2594 / UL 2202)", "equipment",
                            SUBMITTAL_GUIDE_URL),
                PANEL_SCHEDULE, FAULT_CURRENT, PANEL_DETAILS, EGC_SIZE,
            ),
            source_url=PERMITS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=EV_NOTES,
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                APPLICATION,
                LOAD,
                RISER,
                EMERGENCY_DISCONNECT,
                Requirement("Site plan showing the meter and main panel", SITE_PLAN, SUBMITTAL_GUIDE_URL),
                Requirement("Panel and meter base specifications and listing", "equipment", SUBMITTAL_GUIDE_URL),
                PANEL_SCHEDULE, FAULT_CURRENT, PANEL_DETAILS, GEC, SURGE,
                PSE_SERVICE,
            ),
            source_url=PERMITS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=SERVICE_NOTES,
        ),
        SUBPANEL: Checklist(
            items=(
                APPLICATION,
                LOAD,
                FEEDER_ONE_LINE,
                Requirement("Site plan showing the main panel, subpanel and feeder route", SITE_PLAN,
                            SUBMITTAL_GUIDE_URL),
                Requirement("Subpanel specifications and listing", "equipment", SUBMITTAL_GUIDE_URL),
                PANEL_SCHEDULE, FAULT_CURRENT, PANEL_DETAILS, EGC_SIZE,
                Requirement("Burial depth for underground runs (NEC 300.5)", "burial", WCEC_URL),
            ),
            source_url=PERMITS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=SUBPANEL_NOTES,
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                APPLICATION,
                LOAD,
                APPLIANCE_ONE_LINE,
                Requirement("Site plan showing the panel and the appliance", SITE_PLAN, SUBMITTAL_GUIDE_URL),
                Requirement("Appliance manufacturer specifications and listing", "equipment", SUBMITTAL_GUIDE_URL),
                PANEL_SCHEDULE, FAULT_CURRENT, PANEL_DETAILS, EGC_SIZE,
            ),
            source_url=PERMITS_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=APPLIANCE_NOTES,
        ),
    },
)
