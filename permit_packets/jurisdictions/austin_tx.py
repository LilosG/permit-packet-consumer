"""Austin, TX: Austin Development Services Department (DSD)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Austin enforces the 2023 NEC with City of Austin local amendments."
SOURCE_LABEL = "From Austin DSD electrical permitting guidelines"

AUSTIN = Jurisdiction(
    key="austin-tx", name="Austin", state="TX", known=True,
    no_plan_jobs={'ev_charger': 'https://www.austintexas.gov/development-services/types-permits', 'service_upgrade': 'https://www.austintexas.gov/development-services/types-permits', 'subpanel': 'https://www.austintexas.gov/development-services/types-permits', 'appliance_circuit': 'https://www.austintexas.gov/development-services/types-permits'},
    last_verified="2026-11-24",
    permit_rules_verified="2026-11-24",
    who_may_pull="Homeowner must have a homestead exemption filed with county tax appraisal district, own/occupy property as of Jan 1, apply in person with affidavit and photo ID, not pull another homestead permit within 12 months, and work cannot include the main electric service.",
    owner_may_file=True,
    portal_url="https://www.austintexas.gov/department/development-services",
    fee_note="Electrical permit fees are based on the city's adopted fee schedule.",
    sources=("https://www.austintexas.gov/department/development-services",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "A residential electrical permit is required for Level 2 EV charging equipment.",
        SERVICE_UPGRADE: "Panel upgrades require coordination with Austin Energy.",
    },
    bbox=(-97.9384, 30.0986, -97.5615, 30.5169), center=(-97.7431, 30.2672),
    department="Austin DSD",
    phone="(512) 978-4000",
    email="dsdhelp@austintexas.gov",
    website="https://www.austintexas.gov/department/development-services",
    website_label="Austin Build + Connect (AB+C)",
    submit_how="Submit permits via the Austin Build + Connect (AB+C) portal.",
    needs_parcel_number=True,
    design_ambient_f=100,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Austin Energy",
    utility_short="Austin Energy",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Registered licensed electrical contractor applies via AB+C Portal (or qualifying homeowner via Homestead Permit)", "application",
                            "https://www.austintexas.gov/development-services/apply-standalone-permit"),
            ),
            source_url="https://www.austintexas.gov/development-services/apply-standalone-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Austin municipal amendments prior to installation."),
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("Registered licensed electrical contractor applies for Stand-Alone Electrical Upgrade permit via AB+C Portal", "application",
                            "https://www.austintexas.gov/development-services/types-permits"),
                Requirement("Submit Electric Service Planning Application (ESPA) to Austin Energy for service upgrade", "utility",
                            "https://austinenergy.com/contractors/Construction-Renovation/Electric-Service-Planning-Application"),
                SURGE_PROTECTION,
            ),
            source_url="https://www.austintexas.gov/development-services/types-permits",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check Austin Energy approved meter-main combo lists before purchasing equipment."),
                Note("always", "2023 NEC 230.85 requires an outdoor emergency disconnect for all replaced services."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                Requirement("Registered licensed electrical contractor applies via AB+C Portal (or qualifying homeowner via Homestead Permit)", "application",
                            "https://www.austintexas.gov/development-services/apply-standalone-permit"),
            ),
            source_url="https://www.austintexas.gov/development-services/apply-standalone-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                Requirement("Registered licensed electrical contractor applies via AB+C Portal (or qualifying homeowner via Homestead Permit)", "application",
                            "https://www.austintexas.gov/development-services/apply-standalone-permit"),
            ),
            source_url="https://www.austintexas.gov/development-services/apply-standalone-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "generator": Checklist(
            items=(
                Requirement("Apply for Repair Stand-Alone Permit in AB+C Portal with description 'SB 1202 Home Back Up Installation - Generator'", "application",
                            "https://www.austintexas.gov/development-services/apply-standalone-permit"),
                Requirement("Upload Third-Party Review Compliance Letter signed by licensed engineer, master electrician, or certified inspector under SB 1202", "other",
                            "https://www.austintexas.gov/development-services/apply-standalone-permit"),
                Requirement("Interconnected spinning generators require an Auxiliary Power Electrical Permit and Austin Energy DGPA/Transformer Capacity Review", "utility",
                            "https://austinenergy.com/-/media/project/websites/austinenergy/green-power/solar/austinenergy_solarpermittingmanual.pdf?rev=9ce6cd025f3d4b138da6473b34e7a3c4&sc_lang=en&hash=8F0D5D3B092A56C67FE98BD7F6DBDF97"),
            ),
            source_url="https://www.austintexas.gov/development-services/apply-standalone-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Distributed Generation Planning Application (DGPA), Wire Diagram, and Equipment Spec Sheets attached in AB+C Portal", "one_line",
                            "https://austinenergy.com/-/media/project/websites/austinenergy/green-power/solar/austinenergy_solarpermittingmanual.pdf?rev=9ce6cd025f3d4b138da6473b34e7a3c4&sc_lang=en&hash=8F0D5D3B092A56C67FE98BD7F6DBDF97"),
                Requirement("Signed Residential Interconnection Agreement reviewed and approved by Austin Energy prior to permit activation", "utility",
                            "https://austinenergy.com/-/media/project/websites/austinenergy/green-power/solar/austinenergy_solarpermittingmanual.pdf?rev=9ce6cd025f3d4b138da6473b34e7a3c4&sc_lang=en&hash=8F0D5D3B092A56C67FE98BD7F6DBDF97"),
                Requirement("Residential Plan Review with Building Permit required for residential solar shingles or ground-mounted systems", "other",
                            "https://austinenergy.com/-/media/project/websites/austinenergy/green-power/solar/austinenergy_solarpermittingmanual.pdf?rev=9ce6cd025f3d4b138da6473b34e7a3c4&sc_lang=en&hash=8F0D5D3B092A56C67FE98BD7F6DBDF97"),
                Requirement("All associated permitted work must be in 'Final' status before scheduling Final Solar Inspection", "other",
                            "https://austinenergy.com/-/media/project/websites/austinenergy/green-power/solar/austinenergy_solarpermittingmanual.pdf?rev=9ce6cd025f3d4b138da6473b34e7a3c4&sc_lang=en&hash=8F0D5D3B092A56C67FE98BD7F6DBDF97"),
            ),
            source_url="https://austinenergy.com/-/media/project/websites/austinenergy/green-power/solar/austinenergy_solarpermittingmanual.pdf?rev=9ce6cd025f3d4b138da6473b34e7a3c4&sc_lang=en&hash=8F0D5D3B092A56C67FE98BD7F6DBDF97",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
