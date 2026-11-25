from permit_packets.jurisdictions import Checklist, Requirement
from dataclasses import replace
from permit_packets.jurisdictions.general import make_city
ATLANTA = make_city(*('atlanta-ga', 'Atlanta', 'GA', 'NEC', 'Georgia licensed electrical contractors.', 'https://www.atlantaga.gov/government/departments/city-planning', 'Electrical permit fees are based on the Atlanta building fee schedule.', '2020 NEC (Georgia Standard)', 'Electrical permits are required for all EV charging stations.', 'Panel upgrades require Georgia Power meter release and grounding verification.', (-84.551, 33.6478, -84.2896, 33.8868), (-84.388, 33.749), 'Atlanta City Planning', '(404) 330-6145', 'dpcd@atlantaga.gov', 'https://aca3.accela.com/ATLANTA_GA/', 'Atlanta Accela Citizen Access', 'Submit online via Atlanta Accela Citizen Access.', 93, 'https://ashrae-meteo.info/v3.0/index.php?wmo=722190', 'Georgia Power', 'Georgia Power', 'Atlanta enforces the 2020 NEC (Georgia State Minimum Standard Code).'))

# Verified from evidence/verified/ by tools/import_evidence.py.
ATLANTA = replace(
    ATLANTA,
    permit_rules_verified="",
)

# Verified from evidence/verified/ by tools/import_evidence.py.
ATLANTA = replace(
    ATLANTA,
    who_may_pull="Contractors Exception and Contractors Affidavit forms are listed on the Applications, Forms, and Checklists page, but the PDFs could not be opened directly to verify homeowner electrical permit eligibility",
    no_plan_jobs={'ev_charger': 'https://www.atlantaga.gov/residents/city-hall/online-services/apply-for-a-technical-permit', 'service_upgrade': 'https://www.atlantaga.gov/residents/city-hall/online-services/apply-for-a-technical-permit', 'subpanel': 'https://www.atlantaga.gov/residents/city-hall/online-services/apply-for-a-technical-permit', 'appliance_circuit': 'https://www.atlantaga.gov/residents/city-hall/online-services/apply-for-a-technical-permit', 'generator': 'https://www.atlantaga.gov/residents/city-hall/online-services/apply-for-a-technical-permit'},
    checklists={
        **ATLANTA.checklists,
        "ev_charger": replace(
            ATLANTA.checklists["ev_charger"],
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Online Residential Trades (Electrical) application via Accela Citizen Access (ACA) portal", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
                Requirement("EV Charger Affidavit Form", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/applications-forms-and-checklists"),
                Requirement("Documents uploaded using DCP naming convention and document details", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
            ),
            source_url="https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            ATLANTA.checklists["service_upgrade"],
            items=(
                Requirement("Permit application: address, scope and valuation", "application"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter base specifications and listing", "equipment"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("Utility service request", "utility"),
                Requirement("Surge protective device, Type 1 or 2 (NEC 230.67)", "surge"),
                Requirement("Online Residential Trades (Electrical) application via Accela Citizen Access (ACA) portal", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
                Requirement("Electrical Permit Application", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/applications-forms-and-checklists"),
            ),
            source_url="https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting",
            source_label="From the city's published pages"),
        "subpanel": replace(
            ATLANTA.checklists["subpanel"],
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel specifications and listing", "equipment"),
                Requirement("Online Residential Trades (Electrical) application via Accela Citizen Access (ACA) portal", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
                Requirement("Electrical Permit Application", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/applications-forms-and-checklists"),
            ),
            source_url="https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            ATLANTA.checklists["appliance_circuit"],
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the panel and the appliance", "site_plan"),
                Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Manufacturer specifications and listing", "equipment"),
                Requirement("Online Residential Trades (Electrical) application via Accela Citizen Access (ACA) portal", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
                Requirement("Electrical Permit Application", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/applications-forms-and-checklists"),
            ),
            source_url="https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting",
            source_label="From the city's published pages"),
        "generator": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, generator inlet and feeder route", "site_plan"),
                Requirement("One-line diagram showing interlock or transfer switch (NEC 702.5)", "one_line"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Interlock kit / transfer switch UL listing and cut sheets", "equipment"),
                Requirement("Online Residential Trades (Electrical) application via Accela Citizen Access (ACA) portal", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
                Requirement("Electrical Permit Application", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/applications-forms-and-checklists"),
            ),
            source_url="https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting",
            source_label="From the city's published pages",
            code_note=ATLANTA.code_note),
        "solar_storage": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, inverter/ESS and output route", "site_plan"),
                Requirement("One-line diagram with rapid shutdown (NEC 690.12) and ESS disconnect (NEC 706.15)", "one_line"),
                Requirement("Load calculation and NEC 705.12 120% busbar calculation", "load"),
                Requirement("Inverter UL 1741 and battery UL 9540 specification cut sheets", "equipment"),
                Requirement("Single and Two-Family Solar PV online application via Accela Citizen Access (ACA) portal", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting"),
                Requirement("Submittal Info-Solar Roof Install - Res (or Express) packet and PV - Inspection Checklist", "application",
                            "https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/applications-forms-and-checklists"),
            ),
            source_url="https://www.atlantaga.gov/government/departments/city-planning/zoning-development-permitting-services/online-permitting",
            source_label="From the city's published pages",
            code_note=ATLANTA.code_note),
    },
)
