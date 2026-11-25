from dataclasses import replace
from permit_packets.jurisdictions import Checklist, Requirement, SURGE_PROTECTION
from permit_packets.jurisdictions.general import make_city
FRESNO = make_city(*('fresno-ca', 'Fresno', 'CA', 'CEC', 'California C-10 contractors or occupant owner-builders.', 'https://www.fresno.gov/darm/building-safety/', 'Fees based on the City of Fresno fee schedule.', '2025 CEC', 'EV chargers require an electrical permit and load calc.', 'Panel upgrades require PG&E coordination and EUSERC compliance.', (-119.9328, 36.6534, -119.6738, 36.8837), (-119.7871, 36.7378), 'Fresno Building & Safety', '(559) 621-8003', 'buildinganddevelopment@fresno.gov', 'https://fresno.gov/', 'Fresno FAASTER Portal', 'Submit PDF plans via the Fresno FAASTER online permitting portal.', 103, 'https://ashrae-meteo.info/v3.0/index.php?wmo=723890', 'Pacific Gas and Electric (PG&E)', 'PG&E', 'Fresno enforces the 2025 California Electrical Code (2023 NEC base).'))

# Verified from evidence/verified/ by tools/import_evidence.py.
FRESNO = replace(
    FRESNO,
    no_plan_jobs={'service_upgrade': 'https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf', 'subpanel': 'https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf', 'appliance_circuit': 'https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf'},
    permit_rules_verified="",
    last_verified="2026-11-24",
    checklists={
        **FRESNO.checklists,
        "ev_charger": replace(
            FRESNO.checklists["ev_charger"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Electric Vehicle Charging Submittal Checklist (Planning Division)", "application",
                            "https://www.fresno.gov/planning/applications-forms-fees/"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            FRESNO.checklists["service_upgrade"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
                SURGE_PROTECTION,
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "subpanel": replace(
            FRESNO.checklists["subpanel"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            FRESNO.checklists["appliance_circuit"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "generator": Checklist(
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages",
            code_note=FRESNO.code_note),
        "solar_storage": Checklist(
            items=(
                Requirement("Complete scaled plan set with preparer name, signature, address, phone, and license stamp/number on each sheet", "application",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
                Requirement("Site plan showing building footprint, lot dimensions, setbacks, PV panel locations, and point of service connections", "site_plan",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
                Requirement("Complete set of manufacturer product cut-sheets for all equipment used in the installation", "equipment",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
                Requirement("Structural calculations for ground-mount and reverse-tilt installations over 24 inches at tall side", "other",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
            ),
            source_url="https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf",
            source_label="From the city's published pages",
            code_note=FRESNO.code_note),
    },
)

# Verified from evidence/verified/ by tools/import_evidence.py.
FRESNO = replace(
    FRESNO,
    checklists={
        **FRESNO.checklists,
        "ev_charger": replace(
            FRESNO.checklists["ev_charger"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Electric Vehicle Charging Submittal Checklist (Planning Division)", "application",
                            "https://www.fresno.gov/planning/applications-forms-fees/"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            FRESNO.checklists["service_upgrade"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
                SURGE_PROTECTION,
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "subpanel": replace(
            FRESNO.checklists["subpanel"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            FRESNO.checklists["appliance_circuit"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "generator": replace(
            FRESNO.checklists["generator"],
            items=(
                Requirement("Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information", "application",
                            "https://www.fresno.gov/planning/building-and-safety/building-permit-center/"),
                Requirement("Payment of all applicable permit fees prior to permit issuance", "application",
                            "https://www.fresno.gov/wp-content/uploads/2024/01/2023.10.02-Building-Safety-Booklet1.pdf"),
            ),
            source_url="https://www.fresno.gov/planning/building-and-safety/building-permit-center/",
            source_label="From the city's published pages"),
        "solar_storage": replace(
            FRESNO.checklists["solar_storage"],
            items=(
                Requirement("Complete scaled plan set with preparer name, signature, address, phone, and license stamp/number on each sheet", "application",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
                Requirement("Site plan showing building footprint, lot dimensions, setbacks, PV panel locations, and point of service connections", "site_plan",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
                Requirement("Complete set of manufacturer product cut-sheets for all equipment used in the installation", "equipment",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf"),
                Requirement("Structural calculations for ground-mount and reverse-tilt installations over 24 inches at tall side", "by_others",
                            "https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf",
                            who="A licensed engineer, only for ground-mount or reverse-tilt arrays over 24 inches at the tall side"),
            ),
            source_url="https://www.fresno.gov/wp-content/uploads/2023/07/New-Residential-Solar-Plan-Check-Submittal.pdf",
            source_label="From the city's published pages"),
    },
)
