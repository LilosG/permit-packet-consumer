"""Phoenix, AZ: City of Phoenix Planning & Development Department"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Phoenix enforces the 2024 Phoenix Building Construction Code and 2023 NEC with local amendments."
SOURCE_LABEL = "From City of Phoenix Planning & Development electrical guidelines"

PHOENIX = Jurisdiction(
    key="phoenix-az", name="Phoenix", state="AZ", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Arizona ROC-licensed electrical contractors or qualifying owner-occupants of single-family homes.",
    owner_may_file=True,
    portal_url="https://www.phoenix.gov/pdd/permits",
    fee_note="Permit and plan review fees are assessed by valuation and circuit count under the Phoenix fee schedule.",
    sources=("https://www.phoenix.gov/pdd/permits",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Residential EV charger installations require an electrical permit through SHAPE PHX.",
        SERVICE_UPGRADE: "Service upgrades require a permit and utility clearance from APS or SRP.",
    },
    bbox=(-112.3240, 33.2903, -111.9255, 33.9206), center=(-112.0740, 33.4484),
    department="Phoenix Planning & Development",
    phone="(602) 262-7811",
    email="pdd.customerservice@phoenix.gov",
    website="https://shapephoenix.phoenix.gov/",
    website_label="SHAPE PHX Portal",
    submit_how="Apply online through SHAPE PHX and upload your combined PDF plan set.",
    needs_parcel_number=True,
    design_ambient_f=109,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722780",
    code_note=CODE_NOTE,
    utility="APS (Arizona Public Service) or SRP, by address",
    utility_short="APS/SRP",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.phoenix.gov/pdd/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Phoenix municipal amendments prior to installation."),
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
            source_url="https://www.phoenix.gov/pdd/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check APS/SRP approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.phoenix.gov/pdd/permits",
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
            source_url="https://www.phoenix.gov/pdd/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
