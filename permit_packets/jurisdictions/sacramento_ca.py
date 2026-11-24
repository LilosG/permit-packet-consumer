"""Sacramento, CA: City of Sacramento Community Development Department"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Sacramento enforces the 2025 California Electrical Code (2023 NEC base), effective January 1, 2026."
SOURCE_LABEL = "From Sacramento Community Development electrical permit guidelines"

SACRAMENTO = Jurisdiction(
    key="sacramento-ca", name="Sacramento", state="CA", known=True,
    code_name="CEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="California C-10 licensed contractors or owner-builders of single-family dwellings.",
    owner_may_file=True,
    portal_url="https://www.cityofsacramento.gov/community-development/building",
    fee_note="Permit fees are set by the City of Sacramento Community Development fee schedule.",
    sources=("https://www.cityofsacramento.gov/community-development/building",),
    nec_edition="2023 NEC (2025 California Electrical Code base)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Streamlined residential EV charger permits are issued online via the Citizen Portal.",
        SERVICE_UPGRADE: "Service panel upgrades require SMUD service coordination and green-tag release.",
    },
    bbox=(-121.5601, 38.4376, -121.3627, 38.6856), center=(-121.4944, 38.5816),
    department="Sacramento Building Division",
    phone="(916) 264-5011",
    email="ezpermit@cityofsacramento.org",
    website="https://aca-prod.accela.com/SACRAMENTO/",
    website_label="Sacramento Citizen Portal",
    submit_how="Apply online through the Sacramento Citizen Portal and upload PDF plans.",
    needs_parcel_number=True,
    design_ambient_f=98,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=724830",
    code_note=CODE_NOTE,
    utility="Sacramento Municipal Utility District (SMUD)",
    utility_short="SMUD",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://www.cityofsacramento.gov/community-development/building",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Sacramento municipal amendments prior to installation."),
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
            source_url="https://www.cityofsacramento.gov/community-development/building",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check SMUD approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://www.cityofsacramento.gov/community-development/building",
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
            source_url="https://www.cityofsacramento.gov/community-development/building",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
