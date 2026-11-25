from dataclasses import replace
from permit_packets.jurisdictions.general import make_city
MIAMI = make_city(*('miami-fl', 'Miami', 'FL', 'NEC', 'Florida state-licensed electrical contractors (EC/ER) or qualifying owner-builders.', 'https://www.miamigov.com/Services/Permits-Construction/Electrical-Permits', 'Electrical permit fees are calculated per the City of Miami Building Department fee schedule.', '2020 NEC (Florida Building Code 8th Ed)', 'An electrical permit and load calculation are required for residential EV charger installations.', 'Panel and service upgrades require Florida Power & Light (FPL) coordination and grounding verification.', (-80.3198, 25.709, -80.1392, 25.8558), (-80.1918, 25.7617), 'City of Miami Building Department', '(305) 416-1100', 'building@miamigov.com', 'https://www.miamigov.com/Services/Permits-Construction', 'Miami iBuild Online Portal', 'Submit applications and PDF plans online through the City of Miami iBuild portal.', 91, 'https://ashrae-meteo.info/v3.0/index.php?wmo=722020', 'Florida Power & Light (FPL)', 'FPL', 'Miami enforces the 8th Edition Florida Building Code (2020 NEC base) with Miami-Dade high-velocity wind zone anchorage rules.'))

# Verified from evidence/verified/ by tools/import_evidence.py.
MIAMI = replace(
    MIAMI,
    permit_rules_verified="",
)
