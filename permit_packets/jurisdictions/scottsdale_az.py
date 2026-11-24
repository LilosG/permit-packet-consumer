"""Scottsdale, AZ: City of Scottsdale Planning & Development Services"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Scottsdale enforces the 2024 International Codes and 2023 NEC with City of Scottsdale amendments."
SOURCE_LABEL = "From Scottsdale Planning & Development electrical permit rules"

SCOTTSDALE = Jurisdiction(
    key="scottsdale-az", name="Scottsdale", state="AZ", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Arizona ROC-licensed contractors or qualifying owner-builders occupying a single-family home.",
    owner_may_file=True,
    portal_url="https://www.scottsdaleaz.gov/planning-development/permits",
    fee_note="Electrical permit fees are calculated per the published Scottsdale development fee schedule.",
    sources=("https://www.scottsdaleaz.gov/planning-development/permits",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "A residential electrical permit is required for hardwired or plug-in Level 2 EVSE circuits.",
        SERVICE_UPGRADE: "Service entrance upgrades require utility coordination with APS or SRP.",
    },
    bbox=(-111.9613, 33.4585, -111.7875, 33.8602), center=(-111.9261, 33.4942),
    department="Scottsdale Planning & Development",
    phone="(480) 312-2500",
    email="permits@scottsdaleaz.gov",
    website="https://eservices.scottsdaleaz.gov/bldgresources",
    website_label="Scottsdale e-Services",
    submit_how="Submit applications and PDF plans online through Scottsdale e-Services.",
    needs_parcel_number=True,
    design_ambient_f=108,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722780",
    code_note=CODE_NOTE,
    utility="APS (Arizona Public Service) or SRP, by address",
    utility_short="APS/SRP",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.scottsdaleaz.gov/planning-development/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Scottsdale municipal amendments prior to installation."),
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
            source_url="https://www.scottsdaleaz.gov/planning-development/permits",
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
            source_url="https://www.scottsdaleaz.gov/planning-development/permits",
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
            source_url="https://www.scottsdaleaz.gov/planning-development/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
