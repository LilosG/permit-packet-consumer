# Evidence import, 2026-11-24

| City | Quotes verified/total | Fields set unknown | URL rewrites | Blocked hosts | permit_rules_verified |
|---|---|---|---|---|---|
| atlanta-ga | 5/15 | 25 | 0 | www.atlantaga.gov (HTTP 403) | False |
| austin-tx | 27/28 | 6 | 0 | none | True |
| dallas-tx | 23/25 | 13 | 0 | none | False |
| denver-co | 19/20 | 7 | 0 | none | False |
| el-cajon-ca | 5/11 | 25 | 0 | www.elcajon.gov (HTTP 403) | False |
| fresno-ca | 23/26 | 12 | 0 | documents.fresno.gov (ReadError) | False |
| henderson-nv | 4/15 | 26 | 0 | www.cityofhenderson.com (HTTP 403) | False |
| houston-tx | 10/15 | 19 | 1 | none | False |
| irvine-ca | 36/37 | 7 | 0 | none | False |
| los-angeles-ca | 18/18 | 11 | 1 | dbs.lacity.gov (HTTP 404) | False |
| miami-fl | 5/27 | 26 | 0 | www.miami.gov (HTTP 403) | False |
| oakland-ca | 1/42 | 26 | 0 | www.oaklandca.gov (HTTP 403) | False |
| phoenix-az | 32/35 | 5 | 0 | none | False |
| portland-or | 32/33 | 6 | 0 | none | True |
| sacramento-ca | 37/37 | 6 | 0 | none | False |
| san-antonio-tx | 20/23 | 7 | 0 | www.sa.gov (HTTP 403) | False |
| san-diego-ca | 58/61 | 3 | 1 | none | False |
| san-francisco-ca | 36/37 | 6 | 0 | none | False |
| san-jose-ca | 3/36 | 26 | 0 | www.sanjoseca.gov (HTTP 403) | False |
| seattle-wa | 29/30 | 8 | 0 | none | False |

## atlanta-ga

Fields set unknown: who_may_file, ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.plans_required_single_family, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- none

Replaced module values:
- `permit_rules_verified`: '2026-11-21' -> ''

## austin-tx

Fields set unknown: ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'Registered electrical contractors (Master Electricians) and homestead owners.' -> 'Homeowner must have a homestead exemption filed with county tax appraisal district, own/occupy property as of Jan 1, apply in person with affidavit and photo ID, not pull another homestead permit within 12 months, and work cannot include the main electric service.'
- `permit_rules_verified`: '2026-11-21' -> '2026-11-24'
- `checklists[ev_charger]` (5 items -> 1 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Registered licensed electrical contractor applies via AB+C Portal (or qualifying homeowner via Homestead Permit)
- `checklists[service_upgrade]` (7 items -> 2 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Registered licensed electrical contractor applies for Stand-Alone Electrical Upgrade permit via AB+C Portal; Submit Electric Service Planning Application (ESPA) to Austin Energy for service upgrade
- `checklists[subpanel]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Registered licensed electrical contractor applies via AB+C Portal (or qualifying homeowner via Homestead Permit)
- `checklists[appliance_circuit]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Registered licensed electrical contractor applies via AB+C Portal (or qualifying homeowner via Homestead Permit)
- `checklists[generator]`: general NEC checklist -> 3 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## dallas-tx

Fields set unknown: ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.sheet_requirements, generator.sheet_requirements

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'Registered electrical contractors (Master Electricians) or verified homestead owners.' -> "Residential homesteaded property only; homeowner must reside in the property, perform all work without hired assistance, pass a homeowner's exam, and have the district electrical inspector witness the exemption form at the field office"
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 1 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout
- `checklists[service_upgrade]` (7 items -> 1 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout
- `checklists[subpanel]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout
- `checklists[appliance_circuit]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout
- `checklists[generator]`: general NEC checklist -> 4 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## denver-co

Fields set unknown: ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.plans_required_single_family, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'Licensed electrical contractors and qualifying owner-occupants of single-family homes.' -> 'Homeowner (owner-occupier) must pass the Electrical exam (or hold a state electrical license) and submit Quick Permit applications by email to planreview@denvergov.org; homeowners are not eligible to apply for Quick Permits through E-permits.'
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 2 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org; Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation
- `checklists[service_upgrade]` (7 items -> 2 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org; Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation
- `checklists[subpanel]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org; Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation
- `checklists[appliance_circuit]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org; Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation
- `checklists[generator]`: general NEC checklist -> 1 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## el-cajon-ca

Fields set unknown: who_may_file, ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.plans_required_single_family, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- none

Replaced module values:
- none

## fresno-ca

Fields set unknown: code_edition, who_may_file, ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.permit_required, subpanel.load_calculation, appliance_circuit.permit_required, appliance_circuit.load_calculation, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 2 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information; Electric Vehicle Charging Submittal Checklist (Planning Division)
- `checklists[service_upgrade]` (7 items -> 2 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information; Payment of all applicable permit fees prior to permit issuance
- `checklists[subpanel]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information; Payment of all applicable permit fees prior to permit issuance
- `checklists[appliance_circuit]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Permit application via ACA or Permit Affidavit Form with itemized fixture and equipment information; Payment of all applicable permit fees prior to permit issuance
- `checklists[generator]`: general NEC checklist -> 2 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## henderson-nv

Fields set unknown: code_edition, who_may_file, ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.plans_required_single_family, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- none

Replaced module values:
- `permit_rules_verified`: '2026-11-21' -> ''

## houston-tx

Fields set unknown: code_edition, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- https://search.houstontx.gov/texis/search/mlt.html?query=gov&pr=all&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cmd=mlt&id=6af2cf49191&m=0&p=5 -> https://www.houstonpermittingcenter.org/hpwcode1050

Rejected search URLs:
- https://search.houstontx.gov/texis/search/mlt.html?query=code&pr=all&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cmd=mlt&id=6afead02108&m=0&p=5
- https://search.houstontx.gov/texis/search/mlt.html?query=gov&pr=all&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cmd=mlt&id=6af2cf49191&m=0&p=5
- https://search.houstontx.gov/texis/search/mlt.html?query=plan&pr=all&prox=page&rorder=500&rprox=500&rdfreq=500&rwfreq=500&rlead=500&rdepth=0&sufs=0&order=r&cmd=mlt&id=6af2cf6916&m=0&p=5

Replaced module values:
- `owner_may_file`: True -> None
- `who_may_pull`: 'Texas licensed Master Electricians registered with the City of Houston or qualifying homestead owners.' -> "State law exempts homeowners who own and reside in a dwelling from state electrician licensing (Tex. Occ. Code 1305.003(a)(6)), unless regulated by city ordinance; Houston Permitting Center electrical permit pages state 'Registered electrical contractors' must apply."
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 1 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Log in or register for an iPermits account and complete an electrical permit application
- `checklists[service_upgrade]` (7 items -> 1 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Log in or register for an iPermits account and complete an electrical permit application
- `checklists[subpanel]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Log in or register for an iPermits account and complete an electrical permit application
- `checklists[appliance_circuit]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Log in or register for an iPermits account and complete an electrical permit application
- `checklists[generator]`: general NEC checklist -> 1 verified city items

## irvine-ca

Fields set unknown: ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.permit_required, generator.plans_required_single_family, generator.load_calculation

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'California C-10 contractors or occupant owner-builders.' -> 'Property owner must read, initial, sign, and return the Owner-Builder Acknowledgment and Information Verification Form (Form 66-18); same-day rooftop solar/battery permits via PermitsDIRECT! are restricted to licensed contractors'
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 4 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Residential Electric Vehicle Charging Station Application Package; Electric Vehicle Charging Station (EVCS) Permit Worksheet (Form 66-114); Manufacturer's Specifications for the EVCS equipment; Single Line Diagram
- `checklists[service_upgrade]` (7 items -> 3 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Building Permit Application (when submitting via IrvineReady!); Residential Take-Off Sheet (when submitting via IrvineReady!); Electronic/Digital Signature Disclosure (when submitting via IrvineReady!)
- `checklists[subpanel]` (5 items -> 3 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Building Permit Application (when submitting via IrvineReady!); Residential Take-Off Sheet (when submitting via IrvineReady!); Electronic/Digital Signature Disclosure (when submitting via IrvineReady!)
- `checklists[appliance_circuit]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Building Permit Application, Residential Take-Off Sheet, and Electronic/Digital Signature Disclosure; Scaled Site Plan showing pool/spa mechanical equipment distance to property lines and height (for pools/spas)
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## los-angeles-ca

Fields set unknown: service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/Permitting%20Checklist%20for%20Electric%20Vehicle%20Charging%20Applications.pdf -> https://dbs.lacity.gov/sites/default/files/efs/pdf/publications/Permitting%20Checklist%20for%20Electric%20Vehicle%20Charging%20Station%20Applications.pdf

Replaced module values:
- `who_may_pull`: 'State-licensed electrical contractors (C-10) or owner-builders of single-family homes may apply.' -> 'Perform the work prior to sale of the dwelling. Be a homeowner that has resided in the residence for at least 12 months prior to the completion of the work.'
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 2 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Electrical plans and calculations signed and stamped by registered Electrical Engineer when required; Site plan and floor plan if inside a building for plan check submittals
- `checklists[solar_storage]`: general NEC checklist -> 2 verified city items

## miami-fl

Fields set unknown: code_edition, who_may_file, ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.plans_required_single_family, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- none

Replaced module values:
- `permit_rules_verified`: '2026-11-21' -> ''

## oakland-ca

Fields set unknown: code_edition, who_may_file, ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.plans_required_single_family, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- none

Replaced module values:
- `owner_may_file`: True -> None
- `permit_rules_verified`: '2026-11-21' -> ''

## phoenix-az

Fields set unknown: ev_charger.plans_required_single_family, service_upgrade.plans_required_single_family, subpanel.plans_required_single_family, appliance_circuit.plans_required_single_family, generator.plans_required_single_family

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'Arizona ROC-licensed electrical contractors or qualifying owner-occupants of single-family homes.' -> 'Owner must occupy the building and act as general contractor; per A.R.S. 32-1121.A(5), property may not be for sale or rent within one year after Certificate of Occupancy.'
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 4 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Submit plans electronically via SHAPE PHX Customer Portal or in person by appointment; Load calculations for upstream distribution equipment affected by added load when plans are required; Identify serving electrical utility company (APS or SRP) on electrical plans; Show size, length, and location of branch circuits over 20 amps on electrical plans
- `checklists[service_upgrade]` (7 items -> 4 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Complete site plan showing transformer and service equipment locations; Service equipment and panelboard schedules showing volt-ampere or ampere ratings of feeders and branch circuits; Grounding and bonding details and sizes for services and equipment grounding conductors; Identify serving electrical utility company (APS or SRP)
- `checklists[subpanel]` (5 items -> 4 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Complete site plan showing transformer and service equipment locations; Service equipment and panelboard schedules showing volt-ampere or ampere ratings of feeders and branch circuits; Grounding and bonding details and sizes for services and equipment grounding conductors; Identify serving electrical utility company (APS or SRP)
- `checklists[appliance_circuit]` (5 items -> 3 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Pool/Spa Residential Permit Application and plot plan emailed to plotplan.submittals@phoenix.gov for pool/spa projects; Volt-ampere, horsepower, or nameplate data and motor disconnecting device ratings on electrical plans; Grounding and bonding details for pools on electrical plans
- `checklists[generator]`: general NEC checklist -> 3 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## portland-or

Fields set unknown: ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'Oregon licensed electrical contractors and qualifying resident homeowners.' -> 'Recorded property owner (not an LLC) who owns and lives in the single-family home or duplex side as their primary residence, not intended for sale, lease, or rent; work done by homeowner or immediate family member only'
- `permit_rules_verified`: '2026-11-21' -> '2026-11-24'
- `checklists[ev_charger]` (5 items -> 2 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov); Homeowners applying for their own electrical work must print, sign, scan, and email the PDF application
- `checklists[service_upgrade]` (7 items -> 3 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov); Panel amperage when upgrading service or changing a fuse box to breakers; Additional branch circuits purchased on the permit for any new, altered, moved, or extended circuits
- `checklists[subpanel]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Additional service/feeder line item for any new or moved/altered subpanel and its feeder wires; Additional branch circuits purchased on the permit for any new or extended circuits
- `checklists[appliance_circuit]` (5 items -> 2 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Online residential electrical permit application via DevHub (or PDF emailed to PPDTradePermits@portlandoregon.gov); Homeowners applying for their own electrical work must print, sign, scan, and email the PDF application
- `checklists[generator]`: general NEC checklist -> 2 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## sacramento-ca

Fields set unknown: subpanel.permit_required, subpanel.plans_required_single_family, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `who_may_pull`: 'California C-10 licensed contractors or owner-builders of single-family dwellings.' -> "Owner must personally perform work or assume contractor responsibility, complete Owner-Builder Acknowledgment and Information Verification Form (CDD-0220), and verify signature with driver's license or notarization."
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 4 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Completed Building Permit Application form CDD-0200 as PDF#1; Site plan showing house on lot, service, and EVSE; One-line diagram showing service size, EV breaker, conductors, and EVSE; Load calculation worksheet CDD-0213 and manufacturer cut sheets for hardwired chargers
- `checklists[service_upgrade]` (7 items -> 4 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Complete set of Electrical Plans and Building Permit Application CDD-0200; Single-line drawings showing main service size, conductors, OCPDs, AIC, and grounding; Complete CEC load calculations and complete panel schedules; Commitment letter from SMUD for new or upgraded services
- `checklists[subpanel]` (5 items -> 4 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Complete set of Electrical Plans and Building Permit Application CDD-0200; Single-line drawings showing main service size, conductors, OCPDs, AIC, and grounding; Complete CEC load calculations and complete panel schedules; Commitment letter from SMUD for new or upgraded services
- `checklists[appliance_circuit]` (5 items -> 3 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Completed Building Permit Application CDD-0200 and Owner-Builder form CDD-0220 if applicable; Completed Electrical Load Calculation Worksheet CDD-0213; Scaled site plan showing equipment location and electrical features
- `checklists[solar_storage]`: general NEC checklist -> 3 verified city items

## san-antonio-tx

Fields set unknown: who_may_file, ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `owner_may_file`: True -> None
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 3 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary; Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation; Indication of whether work with CPS Energy is required
- `checklists[service_upgrade]` (7 items -> 3 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary; Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation; Indication of whether work with CPS Energy is required
- `checklists[subpanel]` (5 items -> 3 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary; Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation; Indication of whether work with CPS Energy is required
- `checklists[appliance_circuit]` (5 items -> 3 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary; Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation; Indication of whether work with CPS Energy is required
- `checklists[generator]`: general NEC checklist -> 3 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## san-diego-ca

Fields set unknown: generator.plans_required_single_family, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- https://www.sandiego.gov/sites/default/files/2025-04/ib-187-how-to-obtain-a-permit-for-electric-vehicle-charging-systems-city-www.sandiego.gov_.pdf -> https://www.sandiego.gov/development-services/forms-publications/information-bulletins/187

Overrides:
- service_upgrade and subpanel sheet_size forced to not_stated

Replaced module values:
- `who_may_pull`: 'Property owners of single-family dwellings or state-licensed electrical contractors (C-10) may pull permits.' -> 'Property owner or lessee may be issued an electrical permit; property owner doing the work or hiring different contractors must sign and upload Owner-Builder Verification Form (DS-3042) before permit issuance.'
- `no_plan_jobs`: {'ev_charger': 'https://sandiego.gov/development-services/forms-publications/information-bulletins/187'} -> {'ev_charger': 'https://www.sandiego.gov/development-services/forms-publications/information-bulletins/187'}
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 4 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Completed Circuit Card (DS-1779A) with load calculations provided on site for inspection; EVCS manufacturer's installation instructions provided on site for inspection; EVSE listed and labeled by a Nationally Recognized Testing Laboratory; Owner-Builder Verification Form (DS-3042) uploaded if property owner pulls the permit
- `checklists[service_upgrade]` (7 items -> 4 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Completed Electrical Circuit Card (DS-1779) available on the job site for rough inspection; Service bond/ground wire size, type, and clamp locations documented on Circuit Card (DS-1779); Branch-circuit, feeder, and service load calculations on Supplemental Circuit Card (DS-1779A); Stamped and signed electrical plan and calculations when plans are required
- `checklists[subpanel]` (5 items -> 4 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Completed Electrical Circuit Card (DS-1779) available on the job site for rough inspection; Service bond/ground wire size, type, and clamp locations documented on Circuit Card (DS-1779); Branch-circuit, feeder, and service load calculations on Supplemental Circuit Card (DS-1779A); Stamped and signed electrical plan and calculations when plans are required
- `checklists[appliance_circuit]` (5 items -> 4 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Completed Electrical Circuit Card (DS-1779) available on the job site for rough inspection; Service bond/ground wire size, type, and clamp locations documented on Circuit Card (DS-1779); Branch-circuit, feeder, and service load calculations on Supplemental Circuit Card (DS-1779A); Stamped and signed electrical plan and calculations when plans are required
- `checklists[generator]`: general NEC checklist -> 4 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## san-francisco-ca

Fields set unknown: who_may_file, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.load_calculation, solar_storage.load_calculation

URL rewrites:
- none

Replaced module values:
- `owner_may_file`: True -> None
- `permit_rules_verified`: '2026-11-17' -> ''
- `checklists[ev_charger]` (9 items -> 4 verified)
  - old: Application: address, block/lot, owner, contractor, license number and phone; Existing load, electrical service and equipment documented; Load calculation (CEC 220), unless the registered contractor verifies one charger fits the panel; One-line diagram: charger, panel, raceway, wire types and sizes, main breaker and service voltage; Site plan, approximately to scale: panel, meter and charger; Charger manufacturer specifications and installation guidelines; NRTL listing mark on all equipment (UL 2594 / UL 2202); Mechanical ventilation, only if the manufacturer requires it; Panel schedule (CEC 220)
  - new: Project address, parcel number, owner/contractor contact details, and valid contractor license; EVSE manufacturer specifications and installation guidelines; Electrical load calculation and panel schedule per CEC Article 220; Details documenting existing load, electrical service, and equipment
- `checklists[service_upgrade]`: general NEC checklist -> 4 verified city items
- `checklists[subpanel]`: general NEC checklist -> 4 verified city items
- `checklists[appliance_circuit]`: general NEC checklist -> 3 verified city items
- `checklists[generator]`: general NEC checklist -> 4 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 4 verified city items

## san-jose-ca

Fields set unknown: code_edition, who_may_file, ev_charger.permit_required, ev_charger.plans_required_single_family, ev_charger.load_calculation, ev_charger.sheet_requirements, service_upgrade.permit_required, service_upgrade.plans_required_single_family, service_upgrade.load_calculation, service_upgrade.sheet_requirements, subpanel.permit_required, subpanel.plans_required_single_family, subpanel.load_calculation, subpanel.sheet_requirements, appliance_circuit.permit_required, appliance_circuit.plans_required_single_family, appliance_circuit.load_calculation, appliance_circuit.sheet_requirements, generator.permit_required, generator.plans_required_single_family, generator.load_calculation, generator.sheet_requirements, solar_storage.permit_required, solar_storage.plans_required_single_family, solar_storage.load_calculation, solar_storage.sheet_requirements

URL rewrites:
- none

Overrides:
- subpanel plans_required_single_family forced to unknown

Replaced module values:
- `owner_may_file`: True -> None
- `permit_rules_verified`: '2026-11-21' -> ''

## seattle-wa

Fields set unknown: ev_charger.load_calculation, service_upgrade.load_calculation, subpanel.load_calculation, appliance_circuit.load_calculation, generator.plans_required_single_family, generator.load_calculation, solar_storage.plans_required_single_family, solar_storage.load_calculation

URL rewrites:
- none

Overrides:
- dropped 2 solar requirements stating 12 kW
- solar plans_required_single_family stated 12 kW: set unknown

Replaced module values:
- `who_may_pull`: 'Washington licensed electrical contractors and qualifying owner-occupiers.' -> 'Homeowner must perform their own work; if not doing the work, must hire an electrical contractor.'
- `permit_rules_verified`: '2026-11-21' -> ''
- `checklists[ev_charger]` (5 items -> 2 verified)
  - old: Permit application: address, owner, contractor and valuation; Site plan showing the charger, panel and trench route; Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625); One-line diagram with breaker, conductors, conduit, and disconnect; Charger data sheet and NRTL listing mark (UL 2594)
  - new: Apply online via Seattle Services Portal and print OTC permit the same day; Plan review required if EV charger is fed by services or feeders rated 400 amps or more
- `checklists[service_upgrade]` (7 items -> 4 verified)
  - old: Permit application: address, scope and valuation; Load calculation (NEC 220); Riser diagram with service conductors, grounding and bonding; Panel and meter base specifications and listing; Site plan showing the meter and main panel; Utility service request; Surge protective device, Type 1 or 2 (NEC 230.67)
  - new: Apply online via Seattle Services Portal for OTC permit (single-family); submit plans electronically if plan review required; Complete set of switchboard and panel schedules when plan review is required; Fault current calculations and listed interrupting rating of all feeder and service equipment (when plan review required); Service inspection required before energizing the electrical service
- `checklists[subpanel]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the main panel, subpanel and feeder route; One-line diagram with feeder conductors, EGC and grounding; Load calculation; Panel specifications and listing
  - new: Apply online via Seattle Services Portal for OTC permit and schedule Feeder Inspection
- `checklists[appliance_circuit]` (5 items -> 1 verified)
  - old: Permit application; Site plan showing the panel and the appliance; One-line diagram with conductors, breaker and disconnect; Load calculation; Manufacturer specifications and listing
  - new: Heat Equipment Sizing Form required when applying for permits with an electrical heater as primary heat source
- `checklists[generator]`: general NEC checklist -> 4 verified city items
- `checklists[solar_storage]`: general NEC checklist -> 1 verified city items
