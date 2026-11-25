"""Denver, CO: Denver Community Planning and Development"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Denver enforces the 2023 NEC with City and County of Denver amendments."
SOURCE_LABEL = "From Denver CPD electrical permit guidelines"

DENVER = Jurisdiction(
    key="denver-co", name="Denver", state="CO", known=True,
    permit_rules_verified="2026-11-21",
    who_may_pull="Homeowner (owner-occupier) must pass the Electrical exam (or hold a state electrical license) and submit Quick Permit applications by email to planreview@denvergov.org; homeowners are not eligible to apply for Quick Permits through E-permits.",
    owner_may_file=True,
    portal_url="https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Permits-and-Licenses",
    fee_note="Fees are calculated per the Denver CPD fee schedule.",
    sources=("https://www.denvergov.org/",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Electrical permits are required for all EV charging stations.",
        SERVICE_UPGRADE: "Service upgrades must meet Xcel Energy meter standards.",
    },
    bbox=(-105.1099, 39.6144, -104.7343, 39.9142), center=(-104.9903, 39.7392),
    department="Denver CPD",
    phone="(720) 865-2700",
    email="cpd.info@denvergov.org",
    website="https://www.denvergov.org/e-permits",
    website_label="Denver e-permits",
    submit_how="Submit electrical permits online through Denver's e-permits system.",
    needs_parcel_number=True,
    design_ambient_f=91,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Xcel Energy",
    utility_short="Xcel Energy",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
                Requirement("Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org", "application",
                            "https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf"),
                Requirement("Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation", "application",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/How-to-Apply/Homeowner-Permits"),
            ),
            source_url="https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Denver municipal amendments prior to installation."),
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
                Requirement("Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org", "application",
                            "https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf"),
                Requirement("Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation", "application",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/How-to-Apply/Homeowner-Permits"),
            ),
            source_url="https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check Xcel Energy approved meter-main combo lists before purchasing equipment."),
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
                Requirement("Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org", "application",
                            "https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf"),
                Requirement("Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation", "application",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/How-to-Apply/Homeowner-Permits"),
            ),
            source_url="https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf",
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
                Requirement("Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org", "application",
                            "https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf"),
                Requirement("Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation", "application",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/How-to-Apply/Homeowner-Permits"),
            ),
            source_url="https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf",
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
                Requirement("Zoning permit required if generator is located on the ground / exterior of the structure", "site_plan",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits"),
            ),
            source_url="https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits",
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
                Requirement("For SolarAPP+, upload unique SolarAPP+ ID number and approval documents under Quick Permits > Electrical Permit", "application",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits"),
                Requirement("Non-SolarAPP+ systems <10 kW require review of non-engineered electrical plans via Building Log", "one_line",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits"),
                Requirement("Non-SolarAPP+ systems >=10 kW require stamped and signed engineered electrical plans via Building Log", "one_line",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits"),
                Requirement("Zoning permit required if solar panels are installed on the ground", "site_plan",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits"),
            ),
            source_url="https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
