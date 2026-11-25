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
    no_plan_jobs={'ev_charger': 'https://www.portland.gov/ppd/documents/electrical-plan-review-program-guide/download', 'service_upgrade': 'https://www.portland.gov/ppd/documents/electrical-plan-review-program-guide/download', 'subpanel': 'https://www.portland.gov/ppd/documents/electrical-plan-review-program-guide/download', 'appliance_circuit': 'https://www.portland.gov/ppd/documents/electrical-plan-review-program-guide/download', 'generator': 'https://www.portland.gov/ppd/documents/electrical-plan-review-program-guide/download'},
    last_verified="2026-11-25",
    permit_rules_verified="2026-11-25",
    who_may_pull="Recorded property owner (not an LLC) who owns and lives in the single-family home or duplex side as their primary residence, not intended for sale, lease, or rent; work done by homeowner or immediate family member only",
    owner_may_file=True,
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
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov)", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits"),
                Requirement("Homeowners applying for their own electrical work must print, sign, scan, and email the PDF application", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection"),
            ),
            source_url="https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits",
            source_label="From the city's published pages",
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
                Requirement("Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov)", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits"),
                Requirement("Panel amperage when upgrading service or changing a fuse box to breakers", "equipment",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits"),
                Requirement("Additional branch circuits purchased on the permit for any new, altered, moved, or extended circuits", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection"),
            ),
            source_url="https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits",
            source_label="From the city's published pages",
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
                Requirement("Additional service/feeder line item for any new or moved/altered subpanel and its feeder wires", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection"),
                Requirement("Additional branch circuits purchased on the permit for any new or extended circuits", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection"),
            ),
            source_url="https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection",
            source_label="From the city's published pages",
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
                Requirement("Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov)", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits"),
                Requirement("Homeowners applying for their own electrical work must print, sign, scan, and email the PDF application", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection"),
            ),
            source_url="https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "generator": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, generator inlet and feeder route", "site_plan"),
                Requirement("One-line diagram showing interlock or transfer switch (NEC 702.5)", "one_line"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Interlock kit / transfer switch UL listing and cut sheets", "equipment"),
                Requirement("Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov)", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits"),
                Requirement("Homeowners applying for their own electrical work must print, sign, scan, and email the PDF application", "application",
                            "https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits/lights-outlets-switches-reconnection"),
            ),
            source_url="https://www.portland.gov/ppd/residential-permitting/residential-electrical-permits",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, inverter/ESS and output route", "site_plan"),
                Requirement("One-line diagram with rapid shutdown (NEC 690.12) and ESS disconnect (NEC 706.15)", "one_line"),
                Requirement("Load calculation and NEC 705.12 120% busbar calculation", "load"),
                Requirement("Inverter UL 1741 and battery UL 9540 specification cut sheets", "equipment"),
                Requirement("Solar Permit Request submitted online via DevHub with scaled PDF plan set (max 100MB; no sketches)", "application",
                            "https://www.portland.gov/ppd/solar-permit-app-guide"),
                Requirement("Structural Design Criteria on sheet 1 stamped by an Oregon Registered Design Professional (min 20 psf snow, 98 mph wind, dead load)", "by_others",
                            "https://www.portland.gov/ppd/solar-development/solar-permits",
                            who="An Oregon registered design professional (stamped structural criteria)"),
                Requirement("Solar Worksheet for Prescriptive Path Eligibility (for Prescriptive Path projects)", "application",
                            "https://www.portland.gov/ppd/solar-permit-app-guide"),
                Requirement("Email address and phone number for the property owner and designer or technical lead", "application",
                            "https://www.portland.gov/ppd/solar-development/solar-permits"),
            ),
            source_url="https://www.portland.gov/ppd/solar-permit-app-guide",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
