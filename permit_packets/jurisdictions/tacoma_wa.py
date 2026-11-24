"""Tacoma, WA: City of Tacoma Planning and Development Services"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Tacoma enforces the 2023 NEC with Washington State (WAC 296-46B) and Tacoma amendments."
SOURCE_LABEL = "From City of Tacoma electrical permit guidelines"

TACOMA = Jurisdiction(
    key="tacoma-wa", name="Tacoma", state="WA", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Washington licensed electrical contractors or owner-occupants of single-family dwellings.",
    owner_may_file=True,
    portal_url="https://www.cityoftacoma.org/government/city_departments/planning_and_development_services",
    fee_note="Electrical permit fees are set by the City of Tacoma fee schedule.",
    sources=("https://www.cityoftacoma.org/government/city_departments/planning_and_development_services",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Residential EV charger installations require an electrical permit via Tacoma Permits.",
        SERVICE_UPGRADE: "Service upgrades require Tacoma Power coordination and NEC 230.85 outdoor disconnect.",
    },
    bbox=(-122.5625, 47.1684, -122.3452, 47.3212), center=(-122.4443, 47.2529),
    department="Tacoma Planning & Development",
    phone="(253) 591-5030",
    email="tacomapermits@cityoftacoma.org",
    website="https://aca-prod.accela.com/TACOMA/",
    website_label="Tacoma Permits Portal",
    submit_how="Apply online through Tacoma Permits (Accela) and upload PDF plans.",
    needs_parcel_number=True,
    design_ambient_f=82,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=727930",
    code_note=CODE_NOTE,
    utility="Tacoma Power",
    utility_short="Tacoma Power",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.cityoftacoma.org/government/city_departments/planning_and_development_services",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Tacoma municipal amendments prior to installation."),
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
            source_url="https://www.cityoftacoma.org/government/city_departments/planning_and_development_services",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check Tacoma Power approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.cityoftacoma.org/government/city_departments/planning_and_development_services",
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
            source_url="https://www.cityoftacoma.org/government/city_departments/planning_and_development_services",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
