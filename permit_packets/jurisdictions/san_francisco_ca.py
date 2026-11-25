"""San Francisco, CA: from DBI Information Sheet E-02 (Electric Vehicle Charging Station Checklist).

Code: the 2025 San Francisco Electrical Code, which is the 2025 California Electrical Code
(the 2023 NEC with California amendments) plus San Francisco amendments, operative
January 1, 2026. Registered contractors apply online through PermitSF; DBI issues an
electrical trade permit for an EV charger instantly. Utility is PG&E.
"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"

# DBI Information Sheet E-02 (December 21, 2020), hosted by SFMTA. It still cites the 2019 codes.
E02_URL = "https://sfmta.com/media/36888/download"
# DBI Information Sheet E-01 (2019), page 2: electrical plans for DBI electrical review are scaled at no
# smaller than 1/8 in = 1 ft, on sheets no smaller than 11 x 17 in, with text at least 1/8 in tall, stamped
# and signed by an electrical engineer, a California architect or a C-10 contractor.
E01_URL = "https://SF.gov/sites/default/files/2022-08/IS%20E-01.pdf"
WORKSHEET_URL = "https://media.api.sf.gov/documents/DBI_Worksheet_for_Electrical_Permits.pdf"
DBI_URL = "https://www.sf.gov/departments--department-building-inspection"
PDF_RULES_URL = "https://www.sf.gov/information--how-create-pdfs-your-plans-or-addenda"
PLANS_URL = "https://www.sf.gov/reports--october-2023--prepare-your-plans-your-site-permit-application"
# San Francisco Building Code 106A.1.16 and 106A.1.16.1 (EVSE permits and general requirements), as printed in
# Ordinance 12-26 (File No. 251024, passed February 3, 2026), which carries the current section text.
SFBC_EVSE_URL = "https://www.sfbos.org/sites/default/files/o0012-26.pdf"
# DBI's stand-alone list of the 2025 San Francisco Electrical Code amendments (Ordinance 228-25, operative
# January 1, 2026): 230.43 (service-entrance wiring methods, 1-1/4 in minimum raceway), 352.10 (PVC only in
# concrete, underground, cinder fill or corrosive locations), 340.10 (UF only at 50 V or less), 300.4(I) and
# 330.12 (wiring under 8 ft is subject to damage; no MC there).
SFEC_URL = "https://media.api.sf.gov/documents/2025_SF_Electrical_Code.pdf"
PERMIT_PAGE_URL = "https://sf.gov/apply-electrical-permit"
CODE_NOTE = (
    "San Francisco enforces the 2025 San Francisco Electrical Code: the 2025 California "
    "Electrical Code (2023 NEC base) with local amendments, operative January 1, 2026. DBI: filings on or "
    "after January 1, 2026 use the 2025 California Codes and the 2025 San Francisco amendments."
)

SAN_FRANCISCO = Jurisdiction(
    key="san-francisco-ca", name="San Francisco", state="CA", known=True,
    no_plan_jobs={'service_upgrade': 'https://www.sf.gov/apply-electrical-permit', 'subpanel': 'https://www.sf.gov/apply-electrical-permit', 'appliance_circuit': 'https://www.sf.gov/apply-electrical-permit', 'generator': 'https://www.sf.gov/apply-electrical-permit'},
    permit_rules_verified="2026-11-17",
    who_may_pull="Contractors must hold a B, C7, C10, C45, C46, C61 or D34 license (a C7 covers only low-voltage work). Only owners of a stand-alone single-family dwelling (R-3 occupancy) may apply to do the work themselves; staff may direct an owner to hire a licensed contractor.",
    owner_may_file=None,
    portal_url="https://sf.gov/apply-electrical-permit",
    fee_note="San Francisco permit fees depend on the scope of work. DBI publishes a fee schedule (Table 1A-E, 2026) that the permit page links.",
    sources=(PERMIT_PAGE_URL, E02_URL, SFBC_EVSE_URL, SFEC_URL),
    nec_edition="2023 NEC (2025 California Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True},
    permit_notes={
        EV_CHARGER: "DBI Information Sheet E-02: installing or modifying electrical equipment needed for the charger takes an electrical permit. No permit is required to plug a charger into a previously approved receptacle and circuit that already meets the charger maker's specifications.",
        SERVICE_UPGRADE: "San Francisco's permit page lists services as Category 3 work on the electrical permit application.",
        SUBPANEL: "San Francisco's permit page lists subpanels as Category 3 work on the electrical permit application.",
    },
    bbox=(-122.5446, 37.6011, -122.3011, 37.8665), center=(-122.4194, 37.7792),  # Mapbox place bounds (west, south, east, north) and (lon, lat)
    code_name="CEC",
    department="Department of Building Inspection (DBI), Permit Center",
    phone="(628) 652-4900",  # Permit Center help desk, on the DBI electrical permit page (PERMIT_PAGE_URL)
    email="permitsf@sfgov.org",
    website="https://sf.gov/apply-electrical-permit",
    website_label="DBI electrical permits (PermitSF)",
    submit_how=(
        "A DBI-registered contractor applies online through PermitSF. DBI issues an electrical trade "
        "permit for an EV charger instantly. Have the work inspected before covering wiring."
    ),
    needs_parcel_number=True,
    # DBI, "How to create PDFs of your plans or addenda" (PDF_RULES_URL) and "Prepare your plans" (PLANS_URL):
    # drawings go in as a single PDF; every sheet carries the preparer's scanned signature and PDF stamp;
    # each title block reserves a stamp area at least 2 in wide by 2 in tall in the same place on every
    # sheet; the title sheet carries a blank 8.5 x 11 in area for agency stamps. stamp_box_in is the 2 in
    # title-block stamp area and title_sheet_blank_area_in the 8.5 x 11 in area. DBI's PDF page accepts
    # drawing sheets "larger than 22 x 34 in" (11 x 17 in for signs only) and E-01 sets an 11 x 17 in minimum
    # for electrical plans, so the drawing sheets go out as a 22 x 34 in set: each sheet printed at 2.5x
    # (text at least 1/8 in tall, a 1 in = 20 ft site plan at exactly 1/8 in = 1 ft), the 8.5 x 11 in area on
    # the cover at true size, and a 2 x 2 in stamp area in the same spot on every sheet. Forms, data sheets
    # and the review page are supplemental documents and stay 8.5 x 11 in (PDF_RULES_URL).
    sheet_size="ansi_d",
    # SF's "Protocol for PV Plans" wants PV plans on 11 x 17 in sheets with notes no smaller than 10 pt.
    sheet_size_by_job={"solar_storage": "tabloid"},
    max_plan_scale_ft_per_in=20,  # E-01: no smaller than 1/8 in = 1 ft; 1 in = 20 ft prints at 1 in = 8 ft
    stamp_box_in=2.0,
    title_sheet_blank_area_in=(8.5, 11.0),
    # ASHRAE 2% annual cooling dry-bulb design temperature, San Francisco International (WMO 724940).
    # Every ambient from 78 to 86 F (26 to 30 C) falls in the same NEC 310.15(B)(1) row, so 90 C conductors
    # get a factor of 1.00; 77 F and below would get 1.04. CONFIRM the exact 2% figure on the station page below.
    design_ambient_f=78,
    design_ambient_source=(
        "https://ashrae-meteo.info/v3.0/index.php?lat=37.62&lng=-122.37&place=%27%27&wmo=724940&ashrae_version=2017"
    ),
    single_pdf_only=True,
    code_note=CODE_NOTE,
    service_raceways=("RMC", "IMC"),  # SFEC 230.43(A): RMC, IMC, PVC, MI, busway, gutter, HDPE, NUCC, RTRC; PVC per 352.10
    min_service_raceway='1-1/4"',  # SFEC 230.43(B)(1)
    pvc_underground_only=True,  # SFEC 352.10: (A) concealed and the exposed uses are Reserved
    cable_outdoors=False,  # SFEC 340.10: UF only at 50 V or less; NM is not for wet locations (334.12(B))
    wiring_source=SFEC_URL,
    fallback_notes=(
        Note("always", "DBI Information Sheet E-01 (2019) routes electrical systems alterations, such as electric "
             "service upgrades, to DBI's electrical plan review with Title 24 compliance certificates on the plans, "
             "and DBI's electrical permit worksheet asks for the service, feeder and panelboard numbers and sizes. "
             "Confirm with DBI whether the job needs plan review.", E01_URL),
        Note("always", "DBI's electrical permit worksheet requires a valid California contractor license and a "
             "valid San Francisco business tax registration.", WORKSHEET_URL),
    ),
    utility="Pacific Gas and Electric (PG&E)",
    utility_short="PG&E",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Application: address, block/lot, owner, contractor, license number and phone", "application",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Existing load, electrical service and equipment documented", "load",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Load calculation (CEC 220), unless the registered contractor verifies one charger fits the panel", "load",
                            "https://sfmta.com/media/36888/download"),
                Requirement("One-line diagram: charger, panel, raceway, wire types and sizes, main breaker and service voltage", "one_line",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Site plan, approximately to scale: panel, meter and charger", "site_plan",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Charger manufacturer specifications and installation guidelines", "equipment",
                            "https://sfmta.com/media/36888/download"),
                Requirement("NRTL listing mark on all equipment (UL 2594 / UL 2202)", "equipment",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Mechanical ventilation, only if the manufacturer requires it", "ventilation",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Panel schedule (CEC 220)", "panel_schedule",
                            "https://sfmta.com/media/36888/download"),
                Requirement("Project address, parcel number, owner/contractor contact details, and valid contractor license", "application",
                            "https://media.api.sf.gov/documents/IS_E-02.EV.Charging_Final_Signed.pdf"),
                Requirement("EVSE manufacturer specifications and installation guidelines", "equipment",
                            "https://media.api.sf.gov/documents/IS_E-02.EV.Charging_Final_Signed.pdf"),
                Requirement("Electrical load calculation and panel schedule per CEC Article 220", "load",
                            "https://media.api.sf.gov/documents/IS_E-02.EV.Charging_Final_Signed.pdf"),
                Requirement("Details documenting existing load, electrical service, and equipment", "panel_schedule",
                            "https://media.api.sf.gov/documents/IS_E-02.EV.Charging_Final_Signed.pdf"),
            ),
            source_url="https://sfmta.com/media/36888/download",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "DBI's plan-prep pages ask for an empty 8.5 x 11 in area on the title sheet for agency "
                     "stamps and a 2 x 2 in stamp area in the same place on every sheet. Both are on the 22 x 34 in "
                     "drawing sheets at true size. Sign and stamp every sheet.", PLANS_URL),
                Note("indoor", "San Francisco Building Code 106A.1.16.1: store the charger's coupling means (the "
                     "connector) not less than 18 in and not more than 48 in above the finished floor.", SFBC_EVSE_URL),
                Note("outdoor", "San Francisco Building Code 106A.1.16.1: outdoors, store the charger's coupling means "
                     "(the connector) at least 24 in above grade (CEC 625.50).", SFBC_EVSE_URL),
                Note("always", "San Francisco Building Code 106A.1.16.1: fasten the Level 2 charger in place per the "
                     "manufacturer's instructions and CEC 625.44.", SFBC_EVSE_URL),
                Note("always", "DBI E-02: the electrical plan and calculations are signed and stamped by a California "
                     "registered electrical engineer or by the licensed electrical contractor responsible for the "
                     "design and installation.", E02_URL),
                Note("disconnect", "CEC 625.43: a charger rated over 60 A or over 150 V to ground gets a disconnecting "
                     "means in a readily accessible location, lockable open (110.25). If it is remote from the "
                     "charger, put a plaque on the charger that says where the disconnect is."),
                Note("trench", "DBI E-02: when trenching is required, all work complies with CEC 225 and CEC 300.",
                     E02_URL),
            ),
        ),
        "service_upgrade": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel and meter equipment specifications and listing", "equipment"),
                Requirement("Utility service request", "utility"),
                SURGE_PROTECTION,
                Requirement("Building occupancy type and floor where electrical work is performed", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Category 3 electrical work declaration for services or distribution equipment", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Service size in amps of any service distribution and utilization equipment", "equipment",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Estimated valuation of electrical work including all materials and labor", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
            ),
            source_url="https://www.sf.gov/apply-electrical-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "subpanel": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel specifications and listing", "equipment"),
                Requirement("Building occupancy type and floor where electrical work is performed", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Category 3 electrical work declaration for services or distribution equipment", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Service size in amps of any service distribution and utilization equipment", "equipment",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Estimated valuation of electrical work including all materials and labor", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
            ),
            source_url="https://www.sf.gov/apply-electrical-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "appliance_circuit": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the panel and the appliance", "site_plan"),
                Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Manufacturer specifications and listing", "equipment"),
                Requirement("Number of devices or outlets being installed", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Building occupancy type and floor where electrical work is performed", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Estimated valuation of electrical work including all materials and labor", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
            ),
            source_url="https://www.sf.gov/apply-electrical-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "generator": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, generator inlet and feeder route", "site_plan"),
                Requirement("One-line diagram showing interlock or transfer switch (NEC 702.5)", "one_line"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Interlock kit / transfer switch UL listing and cut sheets", "equipment"),
                Requirement("Building occupancy type and floor where electrical work is performed", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Category 3 electrical work declaration for services or distribution equipment", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Service size in amps of any service distribution and utilization equipment", "equipment",
                            "https://www.sf.gov/apply-electrical-permit"),
                Requirement("Estimated valuation of electrical work including all materials and labor", "application",
                            "https://www.sf.gov/apply-electrical-permit"),
            ),
            source_url="https://www.sf.gov/apply-electrical-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, inverter/ESS and output route", "site_plan"),
                Requirement("One-line diagram with rapid shutdown (NEC 690.12) and ESS disconnect (NEC 706.15)", "one_line"),
                Requirement("Load calculation and NEC 705.12 120% busbar calculation", "load"),
                Requirement("Inverter UL 1741 and battery UL 9540 specification cut sheets", "equipment"),
                Requirement("Roof plan showing modules, conduit routing, disconnects, inverters, service, and subpanels", "site_plan",
                            "https://www.sf.gov/information--prepare-plans-your-solar-panel-or-photovoltaic-pv-system"),
                Requirement("Single-line or multi-line wiring diagram with wire/conduit sizes and ampacity calculations", "one_line",
                            "https://www.sf.gov/information--prepare-plans-your-solar-panel-or-photovoltaic-pv-system"),
                Requirement("Current PDF manufacturer data sheets for all major system components", "equipment",
                            "https://www.sf.gov/information--prepare-plans-your-solar-panel-or-photovoltaic-pv-system"),
                Requirement("Warning label and signage sheets for service personnel and emergency responders", "labels",
                            "https://www.sf.gov/information--prepare-plans-your-solar-panel-or-photovoltaic-pv-system"),
            ),
            source_url="https://www.sf.gov/information--prepare-plans-your-solar-panel-or-photovoltaic-pv-system",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
