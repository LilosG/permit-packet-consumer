"""Dallas, TX: City of Dallas Development Services"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Dallas enforces the 2023 NEC with local Dallas amendments."
SOURCE_LABEL = "From Dallas Development Services electrical rules"

DALLAS = Jurisdiction(
    key="dallas-tx", name="Dallas", state="TX", known=True,
    last_verified="2026-11-24",
    permit_rules_verified="",
    who_may_pull="Residential homesteaded property only; homeowner must reside in the property, perform all work without hired assistance, pass a homeowner's exam, and have the district electrical inspector witness the exemption form at the field office",
    owner_may_file=True,
    portal_url="https://dallascityhall.com/departments/sustainabledevelopment/buildinginspection",
    fee_note="Permit fees are assessed based on the Dallas building fee schedule.",
    sources=("https://dallascityhall.com/",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Permits are required for all new EV branch circuits.",
        SERVICE_UPGRADE: "Service upgrades require a permit and Oncor meter coordination.",
    },
    bbox=(-96.9993, 32.6163, -96.5556, 33.0238), center=(-96.7970, 32.7767),
    department="Dallas Development Services",
    phone="(214) 948-4480",
    email="bipn@dallascityhall.com",
    website="https://dallascityhall.com/",
    website_label="Dallas online portal",
    submit_how="Apply online through the Dallas building inspection portal.",
    needs_parcel_number=True,
    design_ambient_f=101,
    design_ambient_source="ASHRAE 2% annual cooling dry-bulb",
    code_note=CODE_NOTE,
    utility="Oncor",
    utility_short="Oncor",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout", "one_line",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf"),
            ),
            source_url="https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Dallas municipal amendments prior to installation."),
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout", "one_line",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf"),
                SURGE_PROTECTION,
            ),
            source_url="https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check Oncor approved meter-main combo lists before purchasing equipment."),
                Note("always", "2023 NEC 230.85 requires an outdoor emergency disconnect for all replaced services."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                Requirement("If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout", "one_line",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf"),
            ),
            source_url="https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                Requirement("If electrical plans are submitted, include service diagram, conductor/pipe sizes, grounding electrode diagram, overcurrent protection, and power layout", "one_line",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf"),
            ),
            source_url="https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/pdf/building/ElectricalPermit.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "generator": Checklist(
            items=(
                Requirement("Scaled and dimensioned site plan showing property lines, buildings, and easements (or floor plan if interior)", "site_plan",
                            "https://dallascityhall.com/departments/sustainabledevelopment/buildinginspection/DCH%20documents/pdf/BI_Backup%20Generator%20Permit_Rev%2009-11-2018.pdf"),
                Requirement("One-line electrical drawings and electrical load analysis", "one_line",
                            "https://dallascityhall.com/departments/sustainabledevelopment/buildinginspection/DCH%20documents/pdf/BI_Backup%20Generator%20Permit_Rev%2009-11-2018.pdf"),
                Requirement("Generator, transfer equipment, and fuel tank component specifications", "equipment",
                            "https://dallascityhall.com/departments/sustainabledevelopment/buildinginspection/DCH%20documents/pdf/BI_Backup%20Generator%20Permit_Rev%2009-11-2018.pdf"),
                Requirement("Fuel type listed on plans (separate plumbing permit for natural gas; flammable liquid permit for propane)", "other",
                            "https://dallascityhall.com/departments/sustainabledevelopment/buildinginspection/DCH%20documents/pdf/BI_Backup%20Generator%20Permit_Rev%2009-11-2018.pdf"),
            ),
            source_url="https://dallascityhall.com/departments/sustainabledevelopment/buildinginspection/DCH%20documents/pdf/BI_Backup%20Generator%20Permit_Rev%2009-11-2018.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Three-line electrical diagram complete with conductor calculations (including correction, adjustment, and duty factors)", "one_line",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/SOLARPANELWATERHEATEROROTHERSYSTEM.pdf"),
                Requirement("Roof plan showing existing condition and proposed equipment location, plus building elevations", "site_plan",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/SOLARPANELWATERHEATEROROTHERSYSTEM.pdf"),
                Requirement("Engineered construction documents sealed by a licensed PE for structural connection and framing", "other",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/SOLARPANELWATERHEATEROROTHERSYSTEM.pdf"),
                Requirement("Equipment manufacturer installation instructions, listing/labeling specs, and total kWh if battery/ESS is included", "equipment",
                            "https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/SOLARPANELWATERHEATEROROTHERSYSTEM.pdf"),
            ),
            source_url="https://dallascityhall.com/departments/sustainabledevelopment/DCH%20documents/SOLARPANELWATERHEATEROROTHERSYSTEM.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
