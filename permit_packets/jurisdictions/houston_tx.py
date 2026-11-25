"""Houston, TX: Houston Permitting Center (Department of Public Works)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement, SURGE_PROTECTION

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Houston enforces the 2023 NEC with City of Houston Electrical Code local amendments."
SOURCE_LABEL = "From Houston Permitting Center electrical code guidelines"

HOUSTON = Jurisdiction(
    key="houston-tx", name="Houston", state="TX", known=True,
    last_verified="2026-11-24",
    code_name="NEC",
    permit_rules_verified="",
    who_may_pull="State law exempts homeowners who own and reside in a dwelling from state electrician licensing (Tex. Occ. Code 1305.003(a)(6)), unless regulated by city ordinance; Houston Permitting Center electrical permit pages state 'Registered electrical contractors' must apply.",
    owner_may_file=None,
    portal_url="https://www.houstonpermittingcenter.org/",
    fee_note="Permit fees are calculated per the Houston Permitting Center fee schedule.",
    sources=("https://www.houstonpermittingcenter.org/",),
    nec_edition="2023 NEC",
    permit_required={EV_CHARGER: True, SERVICE_UPGRADE: True, SUBPANEL: True, APPLIANCE_CIRCUIT: True},
    permit_notes={
        EV_CHARGER: "Residential EV charger installations require an electrical permit through iPermits.",
        SERVICE_UPGRADE: "Service upgrades require CenterPoint Energy meter release and grounding verification.",
    },
    bbox=(-95.7881, 29.5236, -95.0145, 30.1107), center=(-95.3698, 29.7604),
    department="Houston Permitting Center",
    phone="(832) 394-8800",
    email="hpc.customerservice@houstontx.gov",
    website="https://www.houstonpermittingcenter.org/",
    website_label="Houston iPermits",
    submit_how="Apply online through Houston iPermits and upload plans for review if required.",
    needs_parcel_number=True,
    design_ambient_f=95,
    design_ambient_source="https://ashrae-meteo.info/v3.0/index.php?wmo=722430",
    code_note=CODE_NOTE,
    utility="CenterPoint Energy",
    utility_short="CenterPoint",
    checklists={
        EV_CHARGER: Checklist(
            items=(
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
            ),
            source_url="https://www.houstonpermittingcenter.org/hpwcode1050",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Review all local Houston municipal amendments prior to installation."),
            ),
        ),
        SERVICE_UPGRADE: Checklist(
            items=(
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
                SURGE_PROTECTION,
            ),
            source_url="https://www.houstonpermittingcenter.org/hpwcode1050",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Check CenterPoint approved meter-main combo lists before purchasing equipment."),
                Note("always", "NEC 230.85 requires an outdoor emergency disconnect for all replaced dwelling services."),
            ),
        ),
        SUBPANEL: Checklist(
            items=(
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
            ),
            source_url="https://www.houstonpermittingcenter.org/hpwcode1050",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),
            ),
        ),
        APPLIANCE_CIRCUIT: Checklist(
            items=(
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
            ),
            source_url="https://www.houstonpermittingcenter.org/hpwcode1050",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
            notes=(
                Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),
            ),
        ),
        "generator": Checklist(
            items=(
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
            ),
            source_url="https://www.houstonpermittingcenter.org/hpwcode1050",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
