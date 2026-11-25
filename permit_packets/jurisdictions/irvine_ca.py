from dataclasses import replace
from permit_packets.jurisdictions import Checklist, Requirement, SURGE_PROTECTION
from permit_packets.jurisdictions.general import make_city
IRVINE = make_city(*('irvine-ca', 'Irvine', 'CA', 'CEC', 'California C-10 contractors or occupant owner-builders.', 'https://www.cityofirvine.org/community-development/building-safety', 'Fees based on the City of Irvine fee schedule.', '2025 CEC', 'EV chargers require a residential electrical permit.', 'Panel upgrades require SCE coordination and an exterior disconnect.', (-117.892, 33.6186, -117.7126, 33.7471), (-117.8265, 33.6846), 'Irvine Building & Safety', '(949) 724-6490', 'irvinepermits@cityofirvine.org', 'https://irvineca.gov/', 'IrvineReady! Portal', 'Submit plans online via the IrvineReady! permitting portal.', 85, 'https://ashrae-meteo.info/v3.0/index.php?wmo=722970', 'Southern California Edison (SCE)', 'SCE', 'Irvine enforces the 2025 California Electrical Code (2023 NEC base).'))

# Verified from evidence/verified/ by tools/import_evidence.py.
IRVINE = replace(
    IRVINE,
    owner_may_file=True,
    who_may_pull="Property owner must read, initial, sign, and return the Owner-Builder Acknowledgment and Information Verification Form (Form 66-18); same-day rooftop solar/battery permits via PermitsDIRECT! are restricted to licensed contractors",
    no_plan_jobs={'service_upgrade': 'https://permits.cityofirvine.org/irvinepermits/ApplyInstrutctions.htm', 'subpanel': 'https://permits.cityofirvine.org/irvinepermits/ApplyInstrutctions.htm'},
    permit_rules_verified="",
    last_verified="2026-11-24",
    checklists={
        **IRVINE.checklists,
        "ev_charger": replace(
            IRVINE.checklists["ev_charger"],
            items=(
                Requirement("Residential Electric Vehicle Charging Station Application Package", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
                Requirement("Electric Vehicle Charging Station (EVCS) Permit Worksheet (Form 66-114)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
                Requirement("Manufacturer's Specifications for the EVCS equipment", "equipment",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
                Requirement("Single Line Diagram", "one_line",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            IRVINE.checklists["service_upgrade"],
            items=(
                Requirement("Building Permit Application (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Residential Take-Off Sheet (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Electronic/Digital Signature Disclosure (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                SURGE_PROTECTION,
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including",
            source_label="From the city's published pages"),
        "subpanel": replace(
            IRVINE.checklists["subpanel"],
            items=(
                Requirement("Building Permit Application (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Residential Take-Off Sheet (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Electronic/Digital Signature Disclosure (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            IRVINE.checklists["appliance_circuit"],
            items=(
                Requirement("Building Permit Application, Residential Take-Off Sheet, and Electronic/Digital Signature Disclosure", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-or-modifying-residential-swimming-poolspa"),
                Requirement("Scaled Site Plan showing pool/spa mechanical equipment distance to property lines and height (for pools/spas)", "site_plan",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-or-modifying-residential-swimming-poolspa"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/adding-or-modifying-residential-swimming-poolspa",
            source_label="From the city's published pages"),
        "solar_storage": Checklist(
            items=(
                Requirement("Building Permit Application with kW (DC) size, panel count, and main panel upgrade/battery scope", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system"),
                Requirement("Roof Plan with module layout, setbacks, roof coverage percentage, fire sprinkler note, and roof access points", "site_plan",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system"),
                Requirement("Single Line Electrical Diagram and Signs and Labeling Sheet", "one_line",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system"),
                Requirement("Manufacturer specification sheets (UL 9540 for batteries) and anchorage details", "equipment",
                            "https://cityofirvine.gov/community-development/battery-storage-system"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system",
            source_label="From the city's published pages",
            code_note=IRVINE.code_note),
    },
)

# Verified from evidence/verified/ by tools/import_evidence.py.
IRVINE = replace(
    IRVINE,
    checklists={
        **IRVINE.checklists,
        "ev_charger": replace(
            IRVINE.checklists["ev_charger"],
            items=(
                Requirement("Residential Electric Vehicle Charging Station Application Package", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
                Requirement("Electric Vehicle Charging Station (EVCS) Permit Worksheet (Form 66-114)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
                Requirement("Manufacturer's Specifications for the EVCS equipment", "equipment",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
                Requirement("Single Line Diagram", "one_line",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/adding-electric-vehicle-charging-station-evcs-single-family",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            IRVINE.checklists["service_upgrade"],
            items=(
                Requirement("Building Permit Application (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Residential Take-Off Sheet (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Electronic/Digital Signature Disclosure (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                SURGE_PROTECTION,
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including",
            source_label="From the city's published pages"),
        "subpanel": replace(
            IRVINE.checklists["subpanel"],
            items=(
                Requirement("Building Permit Application (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Residential Take-Off Sheet (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
                Requirement("Electronic/Digital Signature Disclosure (when submitting via IrvineReady!)", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/minor-plumbing-or-electrical-work-or-combination-two-including",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            IRVINE.checklists["appliance_circuit"],
            items=(
                Requirement("Building Permit Application, Residential Take-Off Sheet, and Electronic/Digital Signature Disclosure", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-or-modifying-residential-swimming-poolspa"),
                Requirement("Scaled Site Plan showing pool/spa mechanical equipment distance to property lines and height (for pools/spas)", "site_plan",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-or-modifying-residential-swimming-poolspa"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/adding-or-modifying-residential-swimming-poolspa",
            source_label="From the city's published pages"),
        "solar_storage": replace(
            IRVINE.checklists["solar_storage"],
            items=(
                Requirement("Building Permit Application with kW (DC) size, panel count, and main panel upgrade/battery scope", "application",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system"),
                Requirement("Roof Plan with module layout, setbacks, roof coverage percentage, fire sprinkler note, and roof access points", "site_plan",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system"),
                Requirement("Single Line Electrical Diagram and Signs and Labeling Sheet", "one_line",
                            "https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system"),
                Requirement("Manufacturer specification sheets (UL 9540 for batteries) and anchorage details", "equipment",
                            "https://cityofirvine.gov/community-development/battery-storage-system"),
            ),
            source_url="https://cityofirvine.gov/building-permits-and-inspections/adding-rooftop-solar-energy-system",
            source_label="From the city's published pages"),
    },
)
