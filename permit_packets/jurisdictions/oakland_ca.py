"""Oakland, CA: City of Oakland Planning & Building Department"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Oakland enforces the 2025 California Electrical Code (2023 NEC base) with Oakland amendments."
SOURCE_LABEL = "From Oakland Planning & Building electrical permit rules"

OAKLAND = Jurisdiction(
    key="oakland-ca", name="Oakland", state="CA", known=True,
    code_name="CEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="California C-10 licensed electrical contractors or qualifying owner-builders.",
    owner_may_file=True,
    portal_url="https://www.oaklandca.gov/services/apply-for-an-electrical-permit",
    fee_note="Fees are assessed according to the City of Oakland Master Fee Schedule.",
    sources=("https://www.oaklandca.gov/services/apply-for-an-electrical-permit",),
    nec_edition="2023 NEC (2025 California Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Dedicated EV charger circuits require an electrical permit via the Online Permit Center.",
        SERVICE_UPGRADE: "Main service upgrades require PG&E EUSERC-approved meter-main equipment.",
    },
    bbox=(-122.3422, 37.6974, -122.1147, 37.8854), center=(-122.2712, 37.8044),
    department="Oakland Planning & Building",
    phone="(510) 238-3891",
    email="permitquestions@oaklandca.gov",
    website="https://aca-prod.accela.com/OAKLAND/",
    website_label="Oakland Online Permit Center",
    submit_how="Submit applications and PDF drawings online via Oakland Accela Citizen Access.",
    needs_parcel_number=True,
    design_ambient_f=81,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=724930",
    code_note=CODE_NOTE,
    utility="Pacific Gas and Electric (PG&E)",
    utility_short="PG&E",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.oaklandca.gov/services/apply-for-an-electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Oakland municipal amendments prior to installation."),
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
            ),
            source_url="https://www.oaklandca.gov/services/apply-for-an-electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check PG&E approved meter-main combo lists before purchasing equipment."),
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
            ),
            source_url="https://www.oaklandca.gov/services/apply-for-an-electrical-permit",
            source_label=SOURCE_LABEL,
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
            ),
            source_url="https://www.oaklandca.gov/services/apply-for-an-electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
