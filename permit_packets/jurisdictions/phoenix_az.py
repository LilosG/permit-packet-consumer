"""Phoenix, AZ: City of Phoenix Planning & Development Department"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Phoenix enforces the 2024 Phoenix Building Construction Code and 2023 NEC with local amendments."
SOURCE_LABEL = "From City of Phoenix Planning & Development electrical guidelines"

PHOENIX = Jurisdiction(
    key="phoenix-az", name="Phoenix", state="AZ", known=True,
    last_verified="2026-11-24",
    code_name="NEC",
    permit_rules_verified="",
    who_may_pull="Owner must occupy the building and act as general contractor; per A.R.S. 32-1121.A(5), property may not be for sale or rent within one year after Certificate of Occupancy.",
    owner_may_file=True,
    portal_url="https://www.phoenix.gov/pdd/permits",
    fee_note="Permit and plan review fees are assessed by valuation and circuit count under the Phoenix fee schedule.",
    sources=("https://www.phoenix.gov/pdd/permits",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Residential EV charger installations require an electrical permit through SHAPE PHX.",
        SERVICE_UPGRADE: "Service upgrades require a permit and utility clearance from APS or SRP.",
    },
    bbox=(-112.3240, 33.2903, -111.9255, 33.9206), center=(-112.0740, 33.4484),
    department="Phoenix Planning & Development",
    phone="(602) 262-7811",
    email="pdd.customerservice@phoenix.gov",
    website="https://shapephoenix.phoenix.gov/",
    website_label="SHAPE PHX Portal",
    submit_how="Apply online through SHAPE PHX and upload your combined PDF plan set.",
    needs_parcel_number=True,
    design_ambient_f=109,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722780",
    code_note=CODE_NOTE,
    utility="APS (Arizona Public Service) or SRP, by address",
    utility_short="APS/SRP",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Submit plans electronically via SHAPE PHX Customer Portal or in person by appointment", "application",
                            "https://www.phoenix.gov/pddsite/Documents/TRT/dsd_trt_pdf_00311.pdf"),
                Requirement("Load calculations for upstream distribution equipment affected by added load when plans are required", "load",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Identify serving electrical utility company (APS or SRP) on electrical plans", "utility_id",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Show size, length, and location of branch circuits over 20 amps on electrical plans", "one_line",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
            ),
            source_url="https://www.phoenix.gov/pddsite/Documents/TRT/dsd_trt_pdf_00311.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Phoenix municipal amendments prior to installation."),
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("Complete site plan showing transformer and service equipment locations", "site_plan",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Service equipment and panelboard schedules showing volt-ampere or ampere ratings of feeders and branch circuits", "panel_schedule",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Grounding and bonding details and sizes for services and equipment grounding conductors", "gec",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Identify serving electrical utility company (APS or SRP)", "utility",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                SURGE_PROTECTION,
            ),
            source_url="https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check APS/SRP approved meter-main combo lists before purchasing equipment."),
                Note("always", "NEC 230.85 requires an outdoor emergency disconnect for all replaced dwelling services."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                Requirement("Complete site plan showing transformer and service equipment locations", "site_plan",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Service equipment and panelboard schedules showing volt-ampere or ampere ratings of feeders and branch circuits", "panel_schedule",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Grounding and bonding details and sizes for services and equipment grounding conductors", "egc_size",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Identify serving electrical utility company (APS or SRP)", "utility_id",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
            ),
            source_url="https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                Requirement("Pool/Spa Residential Permit Application and plot plan emailed to plotplan.submittals@phoenix.gov for pool/spa projects", "application",
                            "https://www.phoenix.gov/administration/departments/pdd/residential-building/resident-plan-reviews/pool-spa-permits.html"),
                Requirement("Volt-ampere, horsepower, or nameplate data and motor disconnecting device ratings on electrical plans", "equipment",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Grounding and bonding details for pools on electrical plans", "packet_gap",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
            ),
            source_url="https://www.phoenix.gov/administration/departments/pdd/residential-building/resident-plan-reviews/pool-spa-permits.html",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "generator": Checklist(
            items=(
                Requirement("Grounding and bonding details and sizes for generators and equipment grounding conductors", "egc_size",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Complete floor plan showing equipment layout, working space, wire and conduit sizes, and circuit numbers", "packet_gap",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Identify serving electrical utility company (APS or SRP)", "utility_id",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
            ),
            source_url="https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Three-line diagram and equipment cut sheets for all solar PV equipment", "one_line",
                            "https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf"),
                Requirement("Email SolarAPP+ approved documents, manufacturer spec sheets, three-line diagram, and plot plan to pdd.records@phoenix.gov", "application",
                            "https://www.phoenix.gov/administration/departments/pdd/residential-building/resident-plan-reviews/solarapp-photovoltaic.html"),
                Requirement("Separate Phoenix Fire Department permit required for photovoltaic and battery energy storage systems", "by_others",
                            "https://www.phoenix.gov/administration/departments/pdd/residential-building/resident-plan-reviews/solarapp-photovoltaic.html",
                            who="Phoenix Fire Department: separate permit for PV and battery storage"),
                Requirement("Utility interconnection application via PowerClerk (APS or SRP) with battery spec sheets if applicable", "by_others",
                            "https://www.aps.com/-/media/APS/APSCOM-PDFs/Residential/Service-Plans/Understanding-Solar/InterconnectionApplicationProcessGuide.pdf?sc_lang=en",
                            who="APS or SRP: interconnection application through PowerClerk"),
            ),
            source_url="https://www.phoenix.gov/content/dam/phoenix/pddsite/documents/trt/external/dsd_trt_pdf_00574.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
