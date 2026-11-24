"""Los Angeles, CA: Los Angeles Department of Building and Safety (LADBS)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Los Angeles enforces the 2026 City of Los Angeles Electrical Code (based on the 2025 CEC and 2023 NEC)."
SOURCE_LABEL = "From LADBS Information Bulletins and the Los Angeles Electrical Code"

LOS_ANGELES = Jurisdiction(
    key="los-angeles-ca", name="Los Angeles", state="CA", known=True,
    permit_rules_verified="2026-11-21",
    who_may_pull="State-licensed electrical contractors (C-10) or owner-builders of single-family homes may apply.",
    owner_may_file=True,
    portal_url="https://www.ladbs.org/services/core-services/plan-check-permit/electrical-permit",
    fee_note="Permit fees are based on the number of items and valuation per the LADBS fee schedule.",
    sources=("https://www.ladbs.org/",),
    nec_edition="2023 NEC (2026 LA Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "LADBS offers express permits for simple residential EV chargers.",
        SERVICE_UPGRADE: "Service upgrades require LADWP clearance and an electrical permit.",
    },
    bbox=(-118.6682, 33.7037, -118.1553, 34.3373), center=(-118.2437, 34.0522),
    department="LADBS",
    phone="(888) 524-2845",
    email="ladbs.org@lacity.org",
    website="https://www.ladbs.org/",
    website_label="LADBS ePlanLA",
    submit_how="Submit applications and plans online through ePlanLA.",
    needs_parcel_number=True,
    design_ambient_f=87,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Los Angeles Department of Water and Power (LADWP)",
    utility_short="LADWP",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.ladbs.org/services/core-services/plan-check-permit/electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Los Angeles municipal amendments prior to installation."),
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
            source_url="https://www.ladbs.org/services/core-services/plan-check-permit/electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check LADWP approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.ladbs.org/services/core-services/plan-check-permit/electrical-permit",
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
            source_url="https://www.ladbs.org/services/core-services/plan-check-permit/electrical-permit",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
