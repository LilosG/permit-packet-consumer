"""Tampa, FL: City of Tampa Construction Services Division"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Tampa enforces the 8th Edition Florida Building Code (2020 NEC base) with local amendments."
SOURCE_LABEL = "From City of Tampa Construction Services electrical permit rules"

TAMPA = Jurisdiction(
    key="tampa-fl", name="Tampa", state="FL", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="Florida licensed electrical contractors or qualifying owner-builders of single-family homes.",
    portal_url="https://www.tampa.gov/construction-services",
    fee_note="Electrical permit fees are set by the City of Tampa Construction Services fee schedule.",
    sources=("https://www.tampa.gov/construction-services",),
    nec_edition="2020 NEC (Florida Building Code 8th Edition)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Installing a 240V EV charger circuit requires a residential electrical permit.",
        SERVICE_UPGRADE: "Service upgrades require Tampa Electric (TECO) work-order scheduling and surge protection.",
    },
    bbox=(-82.6488, 27.8214, -82.2539, 28.1714), center=(-82.4572, 27.9506),
    department="Tampa Construction Services",
    phone="(813) 274-3100",
    email="csdp@tampagov.net",
    website="https://aca-prod.accela.com/TAMPA/",
    website_label="Tampa Accela Portal",
    submit_how="Apply online through Tampa Accela Citizen Access and upload PDF documents.",
    needs_parcel_number=True,
    design_ambient_f=92,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722110",
    code_note=CODE_NOTE,
    utility="Tampa Electric (TECO)",
    utility_short="TECO",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.tampa.gov/construction-services",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Tampa municipal amendments prior to installation."),
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
            source_url="https://www.tampa.gov/construction-services",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check TECO approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.tampa.gov/construction-services",
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
            source_url="https://www.tampa.gov/construction-services",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
