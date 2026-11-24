"""Raleigh, NC: City of Raleigh Development Services"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Raleigh enforces the 2023 North Carolina Electrical Code (2023 NEC with NC amendments)."
SOURCE_LABEL = "From City of Raleigh Development Services permitting guidelines"

RALEIGH = Jurisdiction(
    key="raleigh-nc", name="Raleigh", state="NC", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-21",
    who_may_pull="North Carolina licensed electrical contractors or owner-occupants of single-family dwellings.",
    owner_may_file=True,
    portal_url="https://raleighnc.gov/permits",
    fee_note="Trade permit fees are assessed per the City of Raleigh Development Fee Guide.",
    sources=("https://raleighnc.gov/permits",),
    nec_edition="2023 NEC (2023 North Carolina Electrical Code)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "A residential trade permit is required for dedicated EV charger branch circuits.",
        SERVICE_UPGRADE: "Service upgrades require Duke Energy Progress coordination and NEC 230.67 surge protection.",
    },
    bbox=(-78.8185, 35.6492, -78.4713, 35.9718), center=(-78.6382, 35.7796),
    department="Raleigh Development Services",
    phone="(919) 996-2500",
    email="ds.help@raleighnc.gov",
    website="https://permitportal.raleighnc.gov/",
    website_label="Raleigh Permit Portal",
    submit_how="Apply online through the Raleigh Permit and Development Portal.",
    needs_parcel_number=True,
    design_ambient_f=92,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=723060",
    code_note=CODE_NOTE,
    utility="Duke Energy Progress",
    utility_short="Duke Energy",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
            ),
            source_url="https://raleighnc.gov/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Raleigh municipal amendments prior to installation."),
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
            source_url="https://raleighnc.gov/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check Duke Energy approved meter-main combo lists before purchasing equipment."),
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
            source_url="https://raleighnc.gov/permits",
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
            source_url="https://raleighnc.gov/permits",
            source_label=SOURCE_LABEL,
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
    },
)
