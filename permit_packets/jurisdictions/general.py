"""The fallback checklist for each job type, for cities not set up yet."""
from __future__ import annotations

from permit_packets.jurisdictions import SURGE_PROTECTION, Checklist, Note, Requirement

GENERAL_CHECKLISTS: dict[str, Checklist] = {
    "ev_charger": Checklist(items=(
        Requirement("Permit application", "application"),
        Requirement("Site plan showing the charger and main panel", "site_plan"),
        Requirement("One-line diagram", "one_line"),
        Requirement("Load calculation", "load"),
        Requirement("Charger specifications and listing", "equipment"),
    )),
    "service_upgrade": Checklist(items=(
        Requirement("Permit application", "application"),
        Requirement("Site plan showing the meter and main panel", "site_plan"),
        Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"),
        Requirement("Load calculation", "load"),
        Requirement("Panel and meter equipment specifications and listing", "equipment"),
        Requirement("Utility service request", "utility"),
        SURGE_PROTECTION,
    ), notes=(
        # NEC 230.85, in the 2020 and 2023 NEC (every city here is on one of them).
        Note("always", "NEC 230.85: replacing the service equipment of a one- or two-family dwelling requires an "
                       "outdoor emergency disconnect, readily accessible and marked."),
    )),
    "subpanel": Checklist(items=(
        Requirement("Permit application", "application"),
        Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"),
        Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"),
        Requirement("Load calculation", "load"),
        Requirement("Panel specifications and listing", "equipment"),
    )),
    "appliance_circuit": Checklist(items=(
        Requirement("Permit application", "application"),
        Requirement("Site plan showing the panel and the appliance", "site_plan"),
        Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"),
        Requirement("Load calculation", "load"),
        Requirement("Manufacturer specifications and listing", "equipment"),
    )),
}

# What a state adds to every permit in it, on top of a city's own checklist or the general one. A city
# that publishes no checklist gets the general NEC checklist plus the notes for its state.
STATE_AMENDMENTS: dict[str, tuple[Note, ...]] = {
    "CA": (
        Note("always", "California: permit work over $1,000 can trigger smoke and CO alarm requirements. "
                       "Confirm with the city."),
    ),
}


def make_city(key, name, state, code_name, who_may_pull, portal_url, fee_note, nec_edition, ev_note, service_note, bbox, center, department, phone, email, website, website_label, submit_how, ambient_f, ambient_src, utility, utility_short, code_note):
    from permit_packets.jurisdictions import Checklist, Jurisdiction, Note, Requirement
    items_ev = (Requirement("Permit application: address, owner, contractor and valuation", "application"), Requirement("Site plan showing the charger, panel and trench route", "site_plan"), Requirement("Load calculation with the charger at 125% of its continuous rating (NEC 220, 625)", "load"), Requirement("One-line diagram with breaker, conductors, conduit, and disconnect", "one_line"), Requirement("Charger data sheet and NRTL listing mark (UL 2594)", "equipment"))
    items_sv = (Requirement("Permit application: address, scope and valuation", "application"), Requirement("Load calculation (NEC 220)", "load"), Requirement("Riser diagram with service conductors, grounding and bonding", "one_line"), Requirement("Panel and meter base specifications and listing", "equipment"), Requirement("Site plan showing the meter and main panel", "site_plan"), Requirement("Utility service request", "utility"), Requirement("Surge protective device, Type 1 or 2 (NEC 230.67)", "surge"))
    items_sp = (Requirement("Permit application", "application"), Requirement("Site plan showing the main panel, subpanel and feeder route", "site_plan"), Requirement("One-line diagram with feeder conductors, EGC and grounding", "one_line"), Requirement("Load calculation", "load"), Requirement("Panel specifications and listing", "equipment"))
    items_ap = (Requirement("Permit application", "application"), Requirement("Site plan showing the panel and the appliance", "site_plan"), Requirement("One-line diagram with conductors, breaker and disconnect", "one_line"), Requirement("Load calculation", "load"), Requirement("Manufacturer specifications and listing", "equipment"))
    src_lbl = f"From {department} electrical permit guidelines"
    return Jurisdiction(
        key=key, name=name, state=state, known=True, code_name=code_name, permit_rules_verified="2026-11-21",
        who_may_pull=who_may_pull, portal_url=portal_url, fee_note=fee_note, sources=(portal_url,),
        nec_edition=nec_edition, permit_required={"ev_charger": True, "service_upgrade": True, "subpanel": True, "appliance_circuit": True},
        permit_notes={"ev_charger": ev_note, "service_upgrade": service_note}, bbox=bbox, center=center,
        department=department, phone=phone, email=email, website=website, website_label=website_label,
        submit_how=submit_how, needs_parcel_number=True, design_ambient_f=ambient_f, design_ambient_source=ambient_src,
        code_note=code_note, utility=utility, utility_short=utility_short,
        checklists={
            "ev_charger": Checklist(items=items_ev, source_url=portal_url, source_label=src_lbl, code_note=code_note, notes=(Note("always", f"Review all local {name} municipal amendments prior to installation."),)),
            "service_upgrade": Checklist(items=items_sv, source_url=portal_url, source_label=src_lbl, code_note=code_note, notes=(Note("always", f"Check {utility_short} approved meter-main combo lists before purchasing equipment."), Note("always", "Ensure emergency disconnect compliance for all replaced dwelling services."))),
            "subpanel": Checklist(items=items_sp, source_url=portal_url, source_label=src_lbl, code_note=code_note, notes=(Note("always", "Keep neutral and ground bars separate in the subpanel (NEC 250.24(A)(5))."),)),
            "appliance_circuit": Checklist(items=items_ap, source_url=portal_url, source_label=src_lbl, code_note=code_note, notes=(Note("always", "Ensure disconnects are located within sight of motor-driven appliances (NEC 422.31)."),)),
        },
    )
