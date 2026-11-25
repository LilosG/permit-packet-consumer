"""San Antonio, TX: City of San Antonio Development Services (DSD)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "San Antonio enforces the 2023 NEC with City Code Chapter 10 local amendments."
SOURCE_LABEL = "From San Antonio DSD electrical permitting guidelines"

SAN_ANTONIO = Jurisdiction(
    key="san-antonio-tx", name="San Antonio", state="TX", known=True,
    no_plan_jobs={'ev_charger': 'https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf', 'service_upgrade': 'https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf', 'subpanel': 'https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf', 'appliance_circuit': 'https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf', 'generator': 'https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf'},
    last_verified="2026-11-24",
    code_name="NEC",
    permit_rules_verified="",
    who_may_pull="Texas licensed electrical contractors or verified homestead owners occupying the property.",
    owner_may_file=None,
    portal_url="https://www.sanantonio.gov/DSD",
    fee_note="Electrical permit fees are based on the adopted San Antonio DSD fee schedule.",
    sources=("https://www.sanantonio.gov/DSD",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "A residential electrical permit is required for Level 2 EV charger circuits.",
        SERVICE_UPGRADE: "Service panel upgrades require CPS Energy coordination and green-tag inspection.",
    },
    bbox=(-98.8054, 29.2143, -98.2216, 29.6989), center=(-98.4936, 29.4241),
    department="San Antonio DSD",
    phone="(210) 207-1111",
    email="dsdcustomerservice@sanantonio.gov",
    website="https://aca-prod.accela.com/COSA/",
    website_label="San Antonio BuildSA",
    submit_how="Submit applications and plans online via the BuildSA portal.",
    needs_parcel_number=True,
    design_ambient_f=98,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722530",
    code_note=CODE_NOTE,
    utility="CPS Energy",
    utility_short="CPS Energy",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary", "application",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation", "equipment",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Indication of whether work with CPS Energy is required", "utility",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
            ),
            source_url="https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local San Antonio municipal amendments prior to installation."),
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary", "application",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation", "equipment",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Indication of whether work with CPS Energy is required", "utility",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                SURGE_PROTECTION,
            ),
            source_url="https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check CPS Energy approved meter-main combo lists before purchasing equipment."),
                Note("always", "NEC 230.85 requires an outdoor emergency disconnect for all replaced dwelling services."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                Requirement("Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary", "application",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation", "equipment",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Indication of whether work with CPS Energy is required", "utility",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
            ),
            source_url="https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                Requirement("Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary", "application",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation", "equipment",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Indication of whether work with CPS Energy is required", "utility",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
            ),
            source_url="https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "generator": Checklist(
            items=(
                Requirement("Electrical Permit Application submitted via BuildSA portal (or in person) with contractor license, address, and work summary", "application",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Itemized quantities of electrical equipment/circuits to be installed, repaired, or modified for fee calculation", "equipment",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
                Requirement("Indication of whether work with CPS Energy is required", "utility",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf"),
            ),
            source_url="https://docsonline.sanantonio.gov/FileUploads/dsd/DSD_Electrical_Application.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
        "solar_storage": Checklist(
            items=(
                Requirement("Online DSD Photovoltaic permit application submitted by a Master Electrician via BuildSA building module", "application",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/IB153.pdf"),
                Requirement("Site Plan showing existing/proposed structures, setbacks to property/lot lines, and main electrical service wall layout", "site_plan",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/IB153.pdf"),
                Requirement("Texas-licensed PE structural calculations if roof array >6 lbs/sq ft on <4:12 pitch, >=2 roof coverings, or new support structure", "other",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/IB153.pdf"),
                Requirement("CPS Energy preconstruction package: One-Line Diagram, Site Layout/Plan, Photos, Equipment Specs, and DER Application", "utility",
                            "https://docsonline.sanantonio.gov/FileUploads/dsd/IB153.pdf"),
            ),
            source_url="https://docsonline.sanantonio.gov/FileUploads/dsd/IB153.pdf",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
