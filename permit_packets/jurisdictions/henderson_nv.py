from dataclasses import replace
from permit_packets.jurisdictions.general import make_city
HENDERSON = make_city(*('henderson-nv', 'Henderson', 'NV', 'NEC', 'NV licensed electrical contractors or homeowner-occupants.', 'https://www.cityofhenderson.com/government/departments/building-and-fire-safety', 'Fees based on the City of Henderson fee schedule.', '2017 NEC', 'EV charger circuits require a residential electrical permit.', 'Service upgrades require NV Energy coordination.', (-115.1762, 35.9189, -114.9325, 36.0792), (-114.9817, 36.0395), 'Henderson Building and Fire Safety', '(702) 267-3600', 'dschelp@cityofhenderson.com', 'https://dsconline.cityofhenderson.com/', 'Henderson DSC Online', 'Apply and upload plans online via Henderson DSC Online.', 108, 'https://ashrae-meteo.info/v3.0/index.php?wmo=723860', 'NV Energy', 'NV Energy', 'Henderson enforces the 2017 National Electrical Code with Southern Nevada amendments.'))

# Verified from evidence/verified/ by tools/import_evidence.py.
HENDERSON = replace(
    HENDERSON,
    permit_rules_verified="",
)
