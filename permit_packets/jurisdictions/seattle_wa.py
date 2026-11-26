"""Seattle, WA: Seattle Department of Construction & Inspections (SDCI)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Seattle enforces the 2023 NEC with Washington State rules and Seattle local amendments."
SOURCE_LABEL = "From SDCI electrical permit guidelines"

SEATTLE = Jurisdiction(
    key="seattle-wa", name="Seattle", state="WA", known=True,
    last_verified="2026-11-25",
    no_plan_jobs={'ev_charger': 'https://www.seattle.gov/DPD/Publications/CAM/cam132.pdf', 'service_upgrade': 'https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf', 'subpanel': 'https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf', 'appliance_circuit': 'https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf', 'generator': 'https://seattlegov.zendesk.com/hc/en-us/articles/115004979048-Which-Electrical-Permit-Should-I-Choose'},
    permit_rules_verified="2026-11-25",
    who_may_pull="Homeowner must perform their own work; if not doing the work, must hire an electrical contractor.",
    owner_may_file=True,
    portal_url="https://www.seattle.gov/sdci/permits/permits-we-issue-(a-z)/electrical-permit",
    fee_note="Fees are calculated per the SDCI fee ordinance based on circuit counts and service amps.",
    sources=("https://www.seattle.gov/sdci",),
    nec_edition="2023 NEC (Seattle amendments)",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "EV charger installations require an over-the-counter electrical permit.",
        SERVICE_UPGRADE: "Service upgrades over a certain capacity trigger plan review.",
    },
    bbox=(-122.4359, 47.4950, -122.2405, 47.7341), center=(-122.3321, 47.6062),
    department="Seattle SDCI",
    phone="(206) 684-8600",
    email="sci_microfilm@seattle.gov",
    website="https://cosaccela.seattle.gov/portal/",
    website_label="Seattle Services Portal",
    submit_how="Submit applications and PDF plans through the Seattle Services Portal.",
    needs_parcel_number=True,
    design_ambient_f=80,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Seattle City Light (SCL)",
    utility_short="SCL",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Apply online via Seattle Services Portal and print OTC permit the same day", "application",
                            "https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit"),
                Requirement("Plan review required if EV charger is fed by services or feeders rated 400 amps or more", "one_line",
                            "https://www.seattle.gov/DPD/Publications/CAM/cam132.pdf"),
            ),
            source_url="https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Seattle municipal amendments prior to installation."),
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
                Requirement("Apply online via Seattle Services Portal for OTC permit (single-family); submit plans electronically if plan review required", "application",
                            "https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit"),
                Requirement("Complete set of switchboard and panel schedules when plan review is required", "panel_schedule",
                            "https://www.seattle.gov/Documents/Departments/SDCI/Permits/SubmittalRequirementsforElectricalPlanReview.pdf"),
                Requirement("Fault current calculations and listed interrupting rating of all feeder and service equipment (when plan review required)", "load",
                            "https://www.seattle.gov/Documents/Departments/SDCI/Permits/SubmittalRequirementsforElectricalPlanReview.pdf"),
                Requirement("Service inspection required before energizing the electrical service", "utility",
                            "https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf"),
            ),
            source_url="https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check SCL approved meter-main combo lists before purchasing equipment."),
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
                Requirement("Apply online via Seattle Services Portal for OTC permit and schedule Feeder Inspection", "application",
                            "https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf"),
            ),
            source_url="https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf",
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
                Requirement("Heat Equipment Sizing Form required when applying for permits with an electrical heater as primary heat source", "load",
                            "https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit"),
            ),
            source_url="https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit",
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
                Requirement("Apply online via Seattle Services Portal for OTC permit (single-family); submit plans electronically if plan review required", "application",
                            "https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit"),
                Requirement("Complete set of switchboard and panel schedules when plan review is required", "panel_schedule",
                            "https://www.seattle.gov/Documents/Departments/SDCI/Permits/SubmittalRequirementsforElectricalPlanReview.pdf"),
                Requirement("Fault current calculations and listed interrupting rating of all feeder and service equipment (when plan review required)", "load",
                            "https://www.seattle.gov/Documents/Departments/SDCI/Permits/SubmittalRequirementsforElectricalPlanReview.pdf"),
                Requirement("Service inspection required before energizing the electrical service", "by_others",
                            "https://www.seattle.gov/documents/Departments/SDCI/Permits/ElectricalPermitQA.pdf",
                            who="Seattle City Light and the city inspector: schedule the inspection before energizing"),
            ),
            source_url="https://www.seattle.gov/construction-and-inspections/permits/permits-we-issue-(a-z)/electrical-permit",
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
                Requirement("SDCI electrical plan review required for all new installations of Energy Storage Systems (ESS)", "by_others",
                            "https://www.seattle.gov/documents/departments/sdci/codes/2023secquickreference.pdf",
                            who="SDCI: electrical plan review for the energy storage system"),
            ),
            source_url="https://www.seattle.gov/documents/departments/sdci/codes/2023secquickreference.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
