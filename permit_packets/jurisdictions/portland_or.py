"""Portland, OR: Portland Bureau of Development Services (BDS)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Portland enforces the 2023 Oregon Electrical Specialty Code (based on the 2023 NEC)."
SOURCE_LABEL = "From Portland BDS residential electrical guidelines"

PORTLAND = Jurisdiction(
    key="portland-or", name="Portland", state="OR", known=True,
    permit_rules_verified="2026-11-21",
    who_may_pull="Oregon licensed electrical contractors and qualifying resident homeowners.",
    portal_url="https://www.portland.gov/bds/residential-permitting/residential-electrical-permits",
    fee_note="Electrical fees are set by the BDS fee schedule.",
    sources=("https://www.portland.gov/bds",),
    nec_edition="2023 NEC (2023 OESC)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Electrical permits are required for all hardwired EV chargers and new 240V outlets.",
        SERVICE_UPGRADE: "Service upgrades require coordination with Portland General Electric or Pacific Power.",
    },
    bbox=(-122.8367, 45.4325, -122.4720, 45.6528), center=(-122.6765, 45.5231),
    department="Portland BDS",
    phone="(503) 823-7300",
    email="bds@portlandoregon.gov",
    website="https://www.portland.gov/bds",
    website_label="Portland DevelopmentHub",
    submit_how="Apply online through DevelopmentHub PDX.",
    needs_parcel_number=True,
    design_ambient_f=88,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Portland General Electric (PGE) or Pacific Power",
    utility_short="PGE / Pacific Power",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.portland.gov/bds/residential-permitting/residential-electrical-permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Portland municipal amendments prior to installation."),
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
            source_url="https://www.portland.gov/bds/residential-permitting/residential-electrical-permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check PGE / Pacific Power approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.portland.gov/bds/residential-permitting/residential-electrical-permits",
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
            source_url="https://www.portland.gov/bds/residential-permitting/residential-electrical-permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
