"""Sacramento, CA: City of Sacramento Community Development Department"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Sacramento enforces the 2025 California Electrical Code (2023 NEC base), effective January 1, 2026."
SOURCE_LABEL = "From Sacramento Community Development electrical permit guidelines"

SACRAMENTO = Jurisdiction(
    key="sacramento-ca", name="Sacramento", state="CA", known=True,
    no_plan_jobs={'service_upgrade': 'https://www.cityofsacramento.gov/community-development/building/permit-services/electronic-plan-check', 'subpanel': 'https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Sacramento-Streamline/Citizen-Portal-Public-User-Registration-Guide.pdf'},
    code_name="CEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Owner must personally perform work or assume contractor responsibility, complete Owner-Builder Acknowledgment and Information Verification Form (CDD-0220), and verify signature with driver's license or notarization.",
    owner_may_file=True,
    portal_url="https://www.cityofsacramento.gov/community-development/building",
    fee_note="Permit fees are set by the City of Sacramento Community Development fee schedule.",
    sources=("https://www.cityofsacramento.gov/community-development/building",),
    nec_edition="2023 NEC (2025 California Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Streamlined residential EV charger permits are issued online via the Citizen Portal.",
        SERVICE_UPGRADE: "Service panel upgrades require SMUD service coordination and green-tag release.",
    },
    bbox=(-121.5601, 38.4376, -121.3627, 38.6856), center=(-121.4944, 38.5816),
    department="Sacramento Building Division",
    phone="(916) 264-5011",
    email="ezpermit@cityofsacramento.org",
    website="https://aca-prod.accela.com/SACRAMENTO/",
    website_label="Sacramento Citizen Portal",
    submit_how="Apply online through the Sacramento Citizen Portal and upload PDF plans.",
    needs_parcel_number=True,
    design_ambient_f=98,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=724830",
    code_note=CODE_NOTE,
    utility="Sacramento Municipal Utility District (SMUD)",
    utility_short="SMUD",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Completed Building Permit Application form CDD-0200 as PDF#1", "application",
                            "https://cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0154_EVSE-Installations-Submission-Checklist.pdf"),
                Requirement("Site plan showing house on lot, service, and EVSE", "site_plan",
                            "https://cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0154_EVSE-Installations-Submission-Checklist.pdf"),
                Requirement("One-line diagram showing service size, EV breaker, conductors, and EVSE", "one_line",
                            "https://cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0154_EVSE-Installations-Submission-Checklist.pdf"),
                Requirement("Load calculation worksheet CDD-0213 and manufacturer cut sheets for hardwired chargers", "load",
                            "https://cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0154_EVSE-Installations-Submission-Checklist.pdf"),
            ),
            source_url="https://cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0154_EVSE-Installations-Submission-Checklist.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Sacramento municipal amendments prior to installation."),
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("Permit application: address, scope and valuation", "application"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter base specifications and listing", "equipment"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("Utility service request", "utility"),
                Requirement("Surge protective device, Type 1 or 2 (NEC 230.67)", "surge"),
                Requirement("Complete set of Electrical Plans and Building Permit Application CDD-0200", "application",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
                Requirement("Single-line drawings showing main service size, conductors, OCPDs, AIC, and grounding", "one_line",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
                Requirement("Complete CEC load calculations and complete panel schedules", "load",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
                Requirement("Commitment letter from SMUD for new or upgraded services", "utility",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
            ),
            source_url="https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check SMUD approved meter-main combo lists before purchasing equipment."),
                Note("always", "NEC 230.85 requires an outdoor emergency disconnect for all replaced dwelling services."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel specifications and listing", "equipment"),
                Requirement("Complete set of Electrical Plans and Building Permit Application CDD-0200", "application",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
                Requirement("Single-line drawings showing main service size, conductors, OCPDs, AIC, and grounding", "one_line",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
                Requirement("Complete CEC load calculations and complete panel schedules", "load",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf"),
                Requirement("Commitment letter from SMUD for new or upgraded services", "by_others",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf",
                            who="SMUD, only for a new or upgraded service: request the commitment letter from SMUD"),
            ),
            source_url="https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0212_Electrical-Plancheck-Requirements.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the panel and the appliance", "site_plan"),
                Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Manufacturer specifications and listing", "equipment"),
                Requirement("Completed Building Permit Application CDD-0200 and Owner-Builder form CDD-0220 if applicable", "application",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0282_Swimming-Pool-Plan-Review-Guidelines-Residential.pdf"),
                Requirement("Completed Electrical Load Calculation Worksheet CDD-0213", "load",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0282_Swimming-Pool-Plan-Review-Guidelines-Residential.pdf"),
                Requirement("Scaled site plan showing equipment location and electrical features", "site_plan",
                            "https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0282_Swimming-Pool-Plan-Review-Guidelines-Residential.pdf"),
            ),
            source_url="https://www.cityofsacramento.gov/content/dam/portal/cdd/Building/Forms/CDD-0282_Swimming-Pool-Plan-Review-Guidelines-Residential.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, inverter/ESS and output route", "site_plan"),
                Requirement("One-line diagram with rapid shutdown (NEC 690.12) and ESS disconnect (NEC 706.15)", "one_line"),
                Requirement("Load calculation and NEC 705.12 120% busbar calculation", "load"),
                Requirement("Inverter UL 1741 and battery UL 9540 specification cut sheets", "equipment"),
                Requirement("Submit eligible residential solar applications online through SolarAPP+", "application",
                            "https://www.cityofsacramento.gov/content/dam/portal/it/digitalstrategy/Residential%20SolarApp.pdf"),
                Requirement("Submit SMUD interconnection application via PowerClerk with one-time fee", "by_others",
                            "https://www.smud.org/Business-Solutions-and-Rebates/Interconnection-Information",
                            who="SMUD: interconnection application through PowerClerk"),
                Requirement("Interconnected energy storage must follow SMUD Rule 21 interconnection requirements", "by_others",
                            "https://www.smud.org/Business-Solutions-and-Rebates/Interconnection-Information",
                            who="SMUD: Rule 21 interconnection review for the battery"),
            ),
            source_url="https://www.cityofsacramento.gov/content/dam/portal/it/digitalstrategy/Residential%20SolarApp.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
