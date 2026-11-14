"""Nashville, TN (Metro Nashville-Davidson County), audited against Metro Codes' published pages.

What Metro publishes: the adopted-codes list (the 2023 NEC with local amendments), the ePermits user
guide, and a solar PV permit page (an electrical diagram, spec sheets, a to-scale site plan, a Tennessee
license and Metro registration). Metro publishes no residential EV charger, service upgrade, subpanel or
240 V circuit checklist, and no residential sheet size, stamp box or single-PDF rule: its ePlans system
(GeoCivix, from September 8, 2025) is described only for commercial permits. So every job type uses the
general NEC checklist, with the Metro items below that Metro does publish, and the packet says so.
Electric utility is Nashville Electric Service (NES), which approves service work separately.

Not found published, so not in the packet: the exact text of Metro's local NEC amendments (Metro Code
Chapter 16.20 on Municode, which blocked direct download) and the Tennessee statewide NEC edition.
"""
from __future__ import annotations

from permit_packets.jurisdictions import SURGE_PROTECTION, Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"

ADOPTED_CODES_URL = "https://www.nashville.gov/departments/codes/codes-administration/adopted-codes-list"
EPERMITS_GUIDE_URL = "https://filetransfer.nashville.gov/Portals/0/SiteContent/Codes/docs/ePermitsUserGuide.pdf"
PV_URL = "https://www.nashville.gov/departments/codes/construction-and-permits/trades-permits/solar-panel-photovoltaic-permits"
MUNICODE_URL = (
    "https://library.municode.com/tn/metro_government_of_nashville_and_davidson_county/codes/code_of_ordinances"
    "?nodeId=CD_TIT16BUCO_CH16.20ELCO_ARTIVIN"
)
NES_RULES_URL = "https://www.nespower.com/-/media/project/nes/common/pdfs/schedule-of-rules--regulations-10012023-lt.pdf"
NES_GUIDELINES_URL = (
    "https://www.nespower.com/-/media/project/nes/common/pdfs/builders-and-developers/electric-service-guidelines-v21.pdf"
)
CODE_NOTE = (
    "Metro Nashville lists the 2023 NEC as adopted with local amendments (Metro Code Chapter 16.20). "
    "Confirm the amendments with Metro Codes."
)
SOURCE_LABEL = "General NEC checklist plus what Metro Codes publishes (Metro has no residential checklist for this job)"

NO_PUBLISHED_CHECKLIST = Note(
    "always",
    "Metro Codes publishes no residential {job} checklist, so this is the general NEC checklist with the 2023 NEC "
    "Metro has adopted. Keep this packet in the job file and attach it in ePermits if the reviewer asks.",
    ADOPTED_CODES_URL,
)
NEC_AMENDMENTS = Note(
    "always",
    "Metro Code Chapter 16.20 adopts the 2023 NEC with local amendments, including 230.1 (the meter location "
    "provision), 210.70(C), 334.15(C) and 680.14. Read the chapter for the exact wording before design.",
    MUNICODE_URL,
)
NES_RELEASE = Note(
    "always",
    "NES requires an inspection and release of the electrical installation by the State Fire Marshal's Office or "
    "Metro Codes before it provides service.",
    NES_RULES_URL,
)

APPLICATION = Requirement(
    "ePermits electrical application: address/parcel, scope, contract value and quantities", "application",
    EPERMITS_GUIDE_URL,
)
LICENSE = Requirement(
    "Tennessee contractor license (licensed and bonded) and Metro Codes registration", "application", PV_URL,
)


def _note(job: str) -> Note:
    return Note(NO_PUBLISHED_CHECKLIST.when, NO_PUBLISHED_CHECKLIST.text.format(job=job), NO_PUBLISHED_CHECKLIST.source)


NASHVILLE = Jurisdiction(
    key="nashville-tn", name="Nashville", state="TN", known=True,
    department="Metro Codes and Building Safety, Permit Issuance",
    phone="(615) 862-6517",
    email="permitissuance@nashville.gov",
    website="https://epermits.nashville.gov",
    website_label="Metro Nashville ePermits",
    submit_how=(
        "Apply in ePermits with the contractor's Metro-registered account. Metro's ePlans system "
        "(GeoCivix) is described only for commercial permits, so upload this packet in ePermits."
    ),
    needs_parcel_number=True,
    # No residential sheet size, stamp box or single-PDF rule is published, so these stay at the defaults.
    # ASHRAE 2% annual cooling dry-bulb design temperature, Nashville International (WMO 723270). Every
    # ambient from 87 to 95 F (31 to 35 C) falls in the same NEC 310.15(B)(1) row, so 90 C conductors
    # get a factor of 0.96. CONFIRM the exact 2% figure on the station page below.
    design_ambient_f=92,
    design_ambient_source=(
        "https://ashrae-meteo.info/v3.0/index.php?lat=36.12&lng=-86.69&place=%27%27&wmo=723270&ashrae_version=2017"
    ),
    code_note=CODE_NOTE,
    fallback_notes=(NEC_AMENDMENTS, NES_RELEASE),
    utility="Nashville Electric Service (NES)",
    utility_short="NES",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                APPLICATION,
                LICENSE,
                Requirement("Load calculation with the charger at 100% of its rating (NEC 220, 625.42)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect (if required)", "one_line"),
                Requirement("Charger data sheet and NRTL listing (UL 2594 / UL 2202)", "equipment"),
                Requirement("Site plan to scale showing the panel, charger and route", "site_plan", PV_URL),
            ),
            source_url=EPERMITS_GUIDE_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(_note("EV charger"), NEC_AMENDMENTS),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                APPLICATION,
                LICENSE,
                Requirement("Load calculation", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter base specifications and listing", "equipment"),
                Requirement("Site plan to scale showing the meter and main panel", "site_plan", PV_URL),
                Requirement("Nashville Electric Service (NES) service request and disconnect/reconnect scheduling", "utility",
                            NES_RULES_URL),
                SURGE_PROTECTION,
            ),
            source_url=EPERMITS_GUIDE_URL,
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                _note("service upgrade"),
                NEC_AMENDMENTS,
                NES_RELEASE,
                Note("always", "Build the meter base and service to the NES Electric Service Guidelines (current "
                     "version) and confirm with NES.", NES_GUIDELINES_URL),
            ),
        ),
    },
)
