from permit_packets.jurisdictions import Checklist, Requirement
from dataclasses import replace
from permit_packets.jurisdictions.general import make_city
MIAMI = make_city(*('miami-fl', 'Miami', 'FL', 'NEC', 'Florida state-licensed electrical contractors (EC/ER) or qualifying owner-builders.', 'https://www.miamigov.com/Services/Permits-Construction/Electrical-Permits', 'Electrical permit fees are calculated per the City of Miami Building Department fee schedule.', '2020 NEC (Florida Building Code 8th Ed)', 'An electrical permit and load calculation are required for residential EV charger installations.', 'Panel and service upgrades require Florida Power & Light (FPL) coordination and grounding verification.', (-80.3198, 25.709, -80.1392, 25.8558), (-80.1918, 25.7617), 'City of Miami Building Department', '(305) 416-1100', 'building@miamigov.com', 'https://www.miamigov.com/Services/Permits-Construction', 'Miami iBuild Online Portal', 'Submit applications and PDF plans online through the City of Miami iBuild portal.', 91, 'https://ashrae-meteo.info/v3.0/index.php?wmo=722020', 'Florida Power & Light (FPL)', 'FPL', 'Miami enforces the 8th Edition Florida Building Code (2020 NEC base) with Miami-Dade high-velocity wind zone anchorage rules.'))

# Verified from evidence/verified/ by tools/import_evidence.py.
MIAMI = replace(
    MIAMI,
    permit_rules_verified="",
)

# Verified from evidence/verified/ by tools/import_evidence.py.
MIAMI = replace(
    MIAMI,
    owner_may_file=True,
    who_may_pull="Strictly limited to owner-occupied one- and two-family residential work; requires in-person interview, written test, proof of residency (ID + utility bill), and signed/notarized Owner-Builder disclosure statement at MRC 444 SW 2nd Ave",
    checklists={
        **MIAMI.checklists,
        "ev_charger": replace(
            MIAMI.checklists["ev_charger"],
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Online building/electrical permit application submitted through the iBuild portal", "application",
                            "https://www.miami.gov/Services/Guide-to-Getting-a-Permit"),
                Requirement("Documents and plans uploaded to ProjectDox (ePlan) if plan review is required", "application",
                            "https://www.miami.gov/Services/Guide-to-Getting-a-Permit"),
            ),
            source_url="https://www.miami.gov/Services/Guide-to-Getting-a-Permit",
            source_label="From the city's published pages"),
        "service_upgrade": replace(
            MIAMI.checklists["service_upgrade"],
            items=(
                Requirement("Permit application: address, scope and valuation", "application"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter base specifications and listing", "equipment"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("Utility service request", "utility"),
                Requirement("Surge protective device, Type 1 or 2 (NEC 230.67)", "surge"),
                Requirement("Easy Permit application in iBuild with property location, project cost, trade items, and contractor qualifier number (for eligible service repair)", "application",
                            "https://www.miami.gov/Permits-Construction/Get-an-Easy-Permit"),
                Requirement("Print and keep the emailed permit card on-site at all times", "application",
                            "https://www.miami.gov/Permits-Construction/Get-an-Easy-Permit"),
            ),
            source_url="https://www.miami.gov/Permits-Construction/Get-an-Easy-Permit",
            source_label="From the city's published pages"),
        "subpanel": replace(
            MIAMI.checklists["subpanel"],
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel specifications and listing", "equipment"),
                Requirement("Online building/electrical permit application submitted through the iBuild portal", "application",
                            "https://www.miami.gov/Services/Guide-to-Getting-a-Permit"),
                Requirement("Documents and plans uploaded to ProjectDox (ePlan) if plan review is required", "application",
                            "https://www.miami.gov/Services/Guide-to-Getting-a-Permit"),
            ),
            source_url="https://www.miami.gov/Services/Guide-to-Getting-a-Permit",
            source_label="From the city's published pages"),
        "appliance_circuit": replace(
            MIAMI.checklists["appliance_circuit"],
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the panel and the appliance", "site_plan"),
                Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Manufacturer specifications and listing", "equipment"),
                Requirement("Easy Permit application in iBuild with property location, project cost, trade items, and contractor qualifier number (for eligible service repair)", "application",
                            "https://www.miami.gov/Permits-Construction/Get-an-Easy-Permit"),
                Requirement("Print and keep the emailed permit card on-site at all times", "application",
                            "https://www.miami.gov/Permits-Construction/Get-an-Easy-Permit"),
            ),
            source_url="https://www.miami.gov/Permits-Construction/Get-an-Easy-Permit",
            source_label="From the city's published pages"),
        "generator": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, generator inlet and feeder route", "site_plan"),
                Requirement("One-line diagram showing interlock or transfer switch (NEC 702.5)", "one_line"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Interlock kit / transfer switch UL listing and cut sheets", "equipment"),
                Requirement("Online building/electrical permit application submitted through the iBuild portal", "application",
                            "https://www.miami.gov/Services/Guide-to-Getting-a-Permit"),
                Requirement("Documents and plans uploaded to ProjectDox (ePlan) if plan review is required", "application",
                            "https://www.miami.gov/Services/Guide-to-Getting-a-Permit"),
            ),
            source_url="https://www.miami.gov/Services/Guide-to-Getting-a-Permit",
            source_label="From the city's published pages",
            code_note=MIAMI.code_note),
        "solar_storage": Checklist(
            items=(
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, inverter/ESS and output route", "site_plan"),
                Requirement("One-line diagram with rapid shutdown (NEC 690.12) and ESS disconnect (NEC 706.15)", "one_line"),
                Requirement("Load calculation and NEC 705.12 120% busbar calculation", "load"),
                Requirement("Inverter UL 1741 and battery UL 9540 specification cut sheets", "equipment"),
                Requirement("Permit application signed by both owner and contractor and notarized for both signatures", "application",
                            "https://www.miami.gov/Permits-Construction/Permit-Catalog/Get-a-Permit-to-Install-Solar-Panels"),
                Requirement("Plans with riser diagram, OCP/equipment sizes, inverter/PV specs, NEC 705.12(D) (120%) compliance, labels, and mounting details", "one_line",
                            "https://www.miami.gov/Permits-Construction/Permit-Catalog/Get-a-Permit-to-Install-Solar-Panels"),
                Requirement("Two copies of a signed and sealed Florida P.E. structural letter for normal and hurricane FBC wind conditions", "by_others",
                            "https://www.miami.gov/Permits-Construction/Permit-Catalog/Get-a-Permit-to-Install-Solar-Panels",
                            who="A Florida-licensed professional engineer (signed and sealed structural letter, two copies)"),
                Requirement("Manufacturer equipment specs, battery size/type/location (if used), and manual/automatic transfer switch details", "equipment",
                            "https://www.miami.gov/Permits-Construction/Permit-Catalog/Get-a-Permit-to-Install-Solar-Panels"),
            ),
            source_url="https://www.miami.gov/Permits-Construction/Permit-Catalog/Get-a-Permit-to-Install-Solar-Panels",
            source_label="From the city's published pages",
            code_note=MIAMI.code_note),
    },
)
