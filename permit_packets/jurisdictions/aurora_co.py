"""Aurora, CO: City of Aurora Building Division"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Aurora enforces the 2023 NEC with City of Aurora municipal amendments."
SOURCE_LABEL = "From City of Aurora Building Division electrical guidelines"

AURORA = Jurisdiction(
    key="aurora-co", name="Aurora", state="CO", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Colorado licensed electrical contractors or owner-occupants of single-family residences.",
    owner_may_file=True,
    portal_url="https://www.auroragov.org/business_services/building_division",
    fee_note="Electrical permit fees are calculated based on project valuation per the Aurora fee schedule.",
    sources=("https://www.auroragov.org/business_services/building_division",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Residential Level 2 EV charger circuits require an electrical permit through Aurora4Biz.",
        SERVICE_UPGRADE: "Panel upgrades require Xcel Energy meter coordination and NEC 230.85 outdoor disconnect.",
    },
    bbox=(-104.8856, 39.5892, -104.5997, 39.8012), center=(-104.8319, 39.7294),
    department="Aurora Building Division",
    phone="(303) 739-7420",
    email="permitcounter@auroragov.org",
    website="https://aurora4biz.auroragov.org/",
    website_label="Aurora4Biz Portal",
    submit_how="Apply online through Aurora4Biz and upload plans as a combined PDF.",
    needs_parcel_number=True,
    design_ambient_f=91,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=725650",
    code_note=CODE_NOTE,
    utility="Xcel Energy",
    utility_short="Xcel Energy",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.auroragov.org/business_services/building_division",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Aurora municipal amendments prior to installation."),
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
            source_url="https://www.auroragov.org/business_services/building_division",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check Xcel Energy approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.auroragov.org/business_services/building_division",
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
            source_url="https://www.auroragov.org/business_services/building_division",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
