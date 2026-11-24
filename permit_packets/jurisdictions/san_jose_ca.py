"""San Jose, CA: City of San Jose Permit Center"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "San Jose enforces the 2025 California Electrical Code (2023 NEC base), effective January 1, 2026."
SOURCE_LABEL = "From San Jose Building Division guidelines"

SAN_JOSE = Jurisdiction(
    key="san-jose-ca", name="San Jose", state="CA", known=True,
    permit_rules_verified="2026-11-21",
    who_may_pull="Licensed contractors (C-10) and qualifying owner-builders.",
    owner_may_file=True,
    portal_url="https://www.sanjoseca.gov/your-government/departments-offices/planning-building-code-enforcement",
    fee_note="Electrical permit fees are based on the city's adopted master fee schedule.",
    sources=("https://www.sanjoseca.gov/",),
    nec_edition="2023 NEC (2025 California Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "San Jose offers a streamlined residential EV charger permitting process.",
        SERVICE_UPGRADE: "Panel upgrades must coordinate with PG&E Greenbook standards.",
    },
    bbox=(-122.0456, 37.1245, -121.7295, 37.4692), center=(-121.8863, 37.3382),
    department="San Jose Building Division",
    phone="(408) 535-3555",
    email="BuildingPermits@sanjoseca.gov",
    website="https://www.sanjoseca.gov/",
    website_label="San Jose SJPermits",
    submit_how="Apply online at SJPermits.org.",
    needs_parcel_number=True,
    design_ambient_f=85,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Pacific Gas and Electric (PG&E)",
    utility_short="PG&E",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.sanjoseca.gov/your-government/departments-offices/planning-building-code-enforcement",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local San Jose municipal amendments prior to installation."),
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
            source_url="https://www.sanjoseca.gov/your-government/departments-offices/planning-building-code-enforcement",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check PG&E approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.sanjoseca.gov/your-government/departments-offices/planning-building-code-enforcement",
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
            source_url="https://www.sanjoseca.gov/your-government/departments-offices/planning-building-code-enforcement",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
