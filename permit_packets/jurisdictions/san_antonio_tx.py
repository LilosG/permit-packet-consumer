"""San Antonio, TX: City of San Antonio Development Services (DSD)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "San Antonio enforces the 2023 NEC with City Code Chapter 10 local amendments."
SOURCE_LABEL = "From San Antonio DSD electrical permitting guidelines"

SAN_ANTONIO = Jurisdiction(
    key="san-antonio-tx", name="San Antonio", state="TX", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Texas licensed electrical contractors or verified homestead owners occupying the property.",
    owner_may_file=True,
    portal_url="https://www.sanantonio.gov/DSD",
    fee_note="Electrical permit fees are based on the adopted San Antonio DSD fee schedule.",
    sources=("https://www.sanantonio.gov/DSD",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "A residential electrical permit is required for Level 2 EV charger circuits.",
        SERVICE_UPGRADE: "Service panel upgrades require CPS Energy coordination and green-tag inspection.",
    },
    bbox=(-98.8054, 29.2143, -98.2216, 29.6989), center=(-98.4936, 29.4241),
    department="San Antonio DSD",
    phone="(210) 207-1111",
    email="dsdcustomerservice@sanantonio.gov",
    website="https://aca-prod.accela.com/COSA/",
    website_label="San Antonio BuildSA",
    submit_how="Submit applications and plans online via the BuildSA portal.",
    needs_parcel_number=True,
    design_ambient_f=98,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722530",
    code_note=CODE_NOTE,
    utility="CPS Energy",
    utility_short="CPS Energy",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.sanantonio.gov/DSD",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local San Antonio municipal amendments prior to installation."),
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
            source_url="https://www.sanantonio.gov/DSD",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check CPS Energy approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.sanantonio.gov/DSD",
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
            source_url="https://www.sanantonio.gov/DSD",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
