"""San Diego, CA: City of San Diego Development Services"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "San Diego enforces the 2025 California Electrical Code (2023 NEC base), effective January 1, 2026."
SOURCE_LABEL = "From San Diego Development Services and the San Diego Municipal Code"

SAN_DIEGO = Jurisdiction(
    key="san-diego-ca", name="San Diego", state="CA", known=True,
    permit_rules_verified="2026-11-21",
    who_may_pull="Property owners of single-family dwellings or state-licensed electrical contractors (C-10) may pull permits.",
    owner_may_file=True,
    portal_url="https://www.sandiego.gov/development-services/permits/electrical-permit",
    fee_note="Fees are calculated based on the scope of work per the published Information Bulletin 501.",
    sources=("https://www.sandiego.gov/development-services", "https://sandiego.gov/development-services/forms-publications/information-bulletins/187"),
    no_plan_jobs={"ev_charger": "https://sandiego.gov/development-services/forms-publications/information-bulletins/187"},
    nec_edition="2023 NEC (2025 California Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "An electrical permit is required to install, alter, or replace EV charging equipment.",
        SERVICE_UPGRADE: "Service panel upgrades require a permit and SDG&E work order coordination.",
    },
    bbox=(-117.2532, 32.5348, -116.9283, 33.1142), center=(-117.1611, 32.7157),
    department="San Diego Development Services",
    phone="(619) 446-5000",
    email="dsdweb@sandiego.gov",
    website="https://www.sandiego.gov/development-services",
    website_label="San Diego Development Services",
    submit_how="Apply online through the OpenDSD portal and upload the required PDF plans.",
    needs_parcel_number=True,
    design_ambient_f=84,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="San Diego Gas & Electric (SDG&E)",
    utility_short="SDG&E",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.sandiego.gov/development-services/permits/electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local San Diego municipal amendments prior to installation."),
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
            source_url="https://www.sandiego.gov/development-services/permits/electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check SDG&E approved meter-main combo lists before purchasing equipment."),
                Note("always", "2023 NEC 230.85 requires an outdoor emergency disconnect for all replaced services."),
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
            source_url="https://www.sandiego.gov/development-services/permits/electrical-permit",
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
            source_url="https://www.sandiego.gov/development-services/permits/electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
