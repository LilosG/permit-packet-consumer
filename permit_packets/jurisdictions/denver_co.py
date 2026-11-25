"""Denver, CO: Denver Community Planning and Development"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Denver enforces the 2023 NEC with City and County of Denver amendments."
SOURCE_LABEL = "From Denver CPD electrical permit guidelines"

DENVER = Jurisdiction(
    key="denver-co", name="Denver", state="CO", known=True,
    last_verified="2026-11-24",
    permit_rules_verified="",
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
                Requirement("Contractors apply electronically through E-permits under Quick Permits; homeowners email Quick Permit application to planreview@denvergov.org", "application",
                            "https://denvergov.org/files/assets/public/v/6/community-planning-and-development/documents/ds/building-codes/policies/admin-131a.pdf"),
                Requirement("Homeowner (owner-occupier) must pass the Electrical exam (or hold a state license) and submit passing documentation", "application",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/How-to-Apply/Homeowner-Permits"),
                SURGE_PROTECTION,
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
                Requirement("Zoning permit required if generator is located on the ground / exterior of the structure", "site_plan",
                            "https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits"),
            ),
            source_url="https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Community-Planning-and-Development/Plan-Review-Permits-and-Inspections/Single-Family-and-Duplex-Projects/Solar-Permits",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
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
