"""Houston, TX: Houston Permitting Center (Department of Public Works)"""
from __future__ import annotations

from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement

EV_CHARGER = "ev_charger"
SERVICE_UPGRADE = "service_upgrade"
SUBPANEL = "subpanel"
APPLIANCE_CIRCUIT = "appliance_circuit"

CODE_NOTE = "Houston enforces the 2023 NEC with City of Houston Electrical Code local amendments."
SOURCE_LABEL = "From Houston Permitting Center electrical code guidelines"

HOUSTON = Jurisdiction(
    key="houston-tx", name="Houston", state="TX", known=True,
    code_name="NEC",
    permit_rules_verified="2026-11-25",
    who_may_pull="Electrical permits are issued only to registered master electricians; a homeowner cannot pull one.",
    owner_may_file=False,
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
                Requirement("Permit application: address, owner, contractor and valuation", "application"),
                Requirement("Site plan showing the charger, panel and trench route", "site_plan"),
                Requirement("Load calculation with the charger at its full nameplate rating (NEC 220), and its branch circuit and breaker sized at 125% of the charger's continuous load (NEC 625)", "load"),
                Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"),
                Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"),
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
                Requirement("Permit application: address, scope and valuation", "application"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
                Requirement("Panel and meter base specifications and listing", "equipment"),
                Requirement("Site plan showing the meter and main panel", "site_plan"),
                Requirement("Utility service request", "utility"),
                Requirement("Surge protective device, Type 1 or 2 (NEC 230.67)", "surge"),
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
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
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
                Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Panel specifications and listing", "equipment"),
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
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the panel and the appliance", "site_plan"),
                Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
                Requirement("Load calculation", "load"),
                Requirement("Manufacturer specifications and listing", "equipment"),
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
                Requirement("Permit application", "application"),
                Requirement("Site plan showing the main panel, generator inlet and feeder route", "site_plan"),
                Requirement("One-line diagram showing interlock or transfer switch (NEC 702.5)", "one_line"),
                Requirement("Load calculation (NEC 220)", "load"),
                Requirement("Interlock kit / transfer switch UL listing and cut sheets", "equipment"),
                Requirement("Log in or register for an iPermits account and complete an electrical permit application", "application",
                            "https://www.houstonpermittingcenter.org/hpwcode1050"),
            ),
            source_url="https://www.houstonpermittingcenter.org/hpwcode1050",
            source_label="From the city's published pages",
            code_note=CODE_NOTE,
        ),
    },
)
