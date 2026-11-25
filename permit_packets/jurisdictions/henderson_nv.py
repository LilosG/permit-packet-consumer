from permit_packets.jurisdictions import Checklist, Requirement
from dataclasses import replace
from permit_packets.jurisdictions.general import make_city
HENDERSON = make_city(*('henderson-nv', 'Henderson', 'NV', 'NEC', 'NV licensed electrical contractors or homeowner-occupants.', 'https://www.cityofhenderson.com/government/departments/building-and-fire-safety', 'Fees based on the City of Henderson fee schedule.', '2017 NEC', 'EV charger circuits require a residential electrical permit.', 'Service upgrades require NV Energy coordination.', (-115.1762, 35.9189, -114.9325, 36.0792), (-114.9817, 36.0395), 'Henderson Building and Fire Safety', '(702) 267-3600', 'dschelp@cityofhenderson.com', 'https://dsconline.cityofhenderson.com/', 'Henderson DSC Online', 'Apply and upload plans online via Henderson DSC Online.', 108, 'https://ashrae-meteo.info/v3.0/index.php?wmo=723860', 'NV Energy', 'NV Energy', 'Henderson enforces the 2017 National Electrical Code with Southern Nevada amendments.'))

# Verified from evidence/verified/ by tools/import_evidence.py.
HENDERSON = replace(
    HENDERSON,
    permit_rules_verified="",
)

# Verified from evidence/verified/ by tools/import_evidence.py.
HENDERSON = replace(
    HENDERSON,
    owner_may_file=True,
    who_may_pull="Owner building or improving a residential structure on their primary Nevada residence for their own occupancy (not intended for sale or lease) must submit the Nevada State Contractors Board Owner Builder Affidavit of Exemption per NRS 624.031 and sign each page of homeowner-drawn plans.",
    permit_rules_verified="2026-11-25",
    last_verified="2026-11-25",
    checklists={
        **HENDERSON.checklists,
        "ev_charger": replace(
            HENDERSON.checklists["ev_charger"],
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Apply online via DSC Online and schedule a Virtual Counter appointment if eligible for over-the-counter review", "application",
                            "https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter"),
                Requirement("Single family residential load calculation worksheet (COHBFS)", "load",
                            "https://www.cityofhenderson.com/government/departments/building-and-fire-safety/standard-designs/electrical-information"),
            ),
            source_url="https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            HENDERSON.checklists["service_upgrade"],
            items=(
                Requirement("Permit application: address, scope and valuation", "application"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter base specifications and listing", "equipment"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("Utility service request", "utility"),
                Requirement("Surge protective device, Type 1 or 2 (NEC 230.67)", "surge"),
                Requirement("Apply online via DSC Online and schedule a Virtual Counter appointment if eligible for over-the-counter review", "application",
                            "https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter"),
                Requirement("Single family residential load calculation worksheet (COHBFS)", "load",
                            "https://www.cityofhenderson.com/government/departments/building-and-fire-safety/standard-designs/electrical-information"),
            ),
            source_url="https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter",
            source_label="From the city's published pages"),
        "subpanel": replace(
            HENDERSON.checklists["subpanel"],
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel specifications and listing", "equipment"),
                Requirement("Apply online via DSC Online and schedule a Virtual Counter appointment if eligible for over-the-counter review", "application",
                            "https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter"),
                Requirement("Single family residential load calculation worksheet (COHBFS)", "load",
                            "https://www.cityofhenderson.com/government/departments/building-and-fire-safety/standard-designs/electrical-information"),
            ),
            source_url="https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            HENDERSON.checklists["appliance_circuit"],
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the panel and the appliance", "site_plan"),
                Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Manufacturer specifications and listing", "equipment"),
                Requirement("Apply online via DSC Online and schedule a Virtual Counter appointment if eligible for over-the-counter review", "application",
                            "https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter"),
                Requirement("Single family residential load calculation worksheet (COHBFS)", "load",
                            "https://www.cityofhenderson.com/government/departments/building-and-fire-safety/standard-designs/electrical-information"),
            ),
            source_url="https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter",
            source_label="From the city's published pages"),
        "generator": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, generator inlet and feeder route", "site_plan"),
                Requirement("One-line diagram showing interlock or transfer switch (NEC 702.5)", "one_line"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Interlock kit / transfer switch UL listing and cut sheets", "equipment"),
                Requirement("Apply online via DSC Online and schedule a Virtual Counter appointment if eligible for over-the-counter review", "application",
                            "https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter"),
                Requirement("Single family residential load calculation worksheet (COHBFS)", "load",
                            "https://www.cityofhenderson.com/government/departments/building-and-fire-safety/standard-designs/electrical-information"),
            ),
            source_url="https://www.cityofhenderson.com/government/departments/development-services-center/virtualcounter",
            source_label="From the city's published pages",
            code_note=HENDERSON.code_note),
        "solar_storage": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, inverter/ESS and output route", "site_plan"),
                Requirement("One-line diagram with rapid shutdown (NEC 690.12) and ESS disconnect (NEC 706.15)", "one_line"),
                Requirement("Load calculation and NEC 705.12 120% busbar calculation", "load"),
                Requirement("Inverter UL 1741 and battery UL 9540 specification cut sheets", "equipment"),
                Requirement("Submit Residential Photovoltaic (Solar) plans and checklist items via DSC Online", "site_plan",
                            "https://www.cityofhenderson.com/business/development-services-center/submittal-checklist"),
            ),
            source_url="https://www.cityofhenderson.com/business/development-services-center/submittal-checklist",
            source_label="From the city's published pages",
            code_note=HENDERSON.code_note),
    },
)
