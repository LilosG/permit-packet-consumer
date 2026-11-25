"""What each city asks for. Every entry comes from the city's own published checklist.

A city carries one checklist per job type it has been set up for. A new city is
a new module here, checked against its checklists and past approved packets.
Any other address, or a job type a city has no checklist for, gets the general
checklist and says so.
"""
from __future__ import annotations

from dataclasses import dataclass, field, replace

DEFAULT_CODE_NOTE = "Confirm the adopted code edition."


@dataclass(frozen=True)
class Requirement:
    item: str
    section: str
    source: str = ""  # URL of the page or form this item comes from
    who: str = ""  # for section "by_others": who supplies this item


# NEC 230.67 (2020 NEC and later, so every city here): a dwelling service that is replaced or upgraded gets a
# Type 1 or Type 2 surge protective device. A city's own checklist may carry a sourced copy of it instead.
SURGE_PROTECTION = Requirement(
    "Surge protective device, Type 1 or Type 2, shown on the riser (NEC 230.67)", "surge")


@dataclass(frozen=True)
class Note:
    when: str  # always, disconnect, trench, indoor or outdoor (EV charger location)
    text: str
    source: str = ""  # URL of the page or form this note comes from


@dataclass(frozen=True)
class Checklist:
    items: tuple[Requirement, ...]
    source_url: str = ""
    code_note: str = DEFAULT_CODE_NOTE
    notes: tuple[Note, ...] = ()
    source_label: str = "From the city's published checklist"


@dataclass(frozen=True)
class Jurisdiction:
    key: str
    name: str
    state: str
    known: bool
    # City limits box (west, south, east, north) and center (lon, lat), used to keep address suggestions in the city.
    bbox: tuple[float, float, float, float] | None = None
    center: tuple[float, float] | None = None
    # True where the permit area is not the city's name: addresses count when the Census places their coordinates
    # in this jurisdiction (Nashville: all of Davidson County except the satellite cities with their own offices).
    permit_area_by_location: bool = False
    code_name: str = "NEC"
    # ISO date this city's checklist and code edition were last checked against its official sources. Empty: not checked.
    last_verified: str = ""
    # ISO date this city's permit rules (permit required, who may pull, code edition, portal) were checked. The full
    # checklist may not have been: the packet cover prints only last_verified.
    permit_rules_verified: str = ""
    # Location-page facts, each from an official source and left empty where none confirms it (an empty field
    # keeps the city's pages out of the index: see permit_packets/locations.py).
    who_may_pull: str = ""  # who may apply for the electrical permit: homeowner and/or licensed contractor
    portal_url: str = ""  # where the permit application is filed
    fee_note: str = ""  # text only: how the city sets its fee. Never a dollar amount that is not published
    sources: tuple[str, ...] = ()  # official pages and documents behind the fields above
    # True: owners may pull the permit for electrical work they do themselves on their own home. False: a licensed
    # electrician must do and file all electrical work. None: not verified (never guess).
    owner_may_file: bool | None = None
    # Job type -> the official URL saying single-family installs of that job need no plans (a no-plan Simple Permit).
    no_plan_jobs: dict[str, str] = field(default_factory=dict)
    nec_edition: str = ""  # the NEC edition the city enforces, e.g. "2023 NEC"
    # Job type -> True where an official source confirms the permit is required. A missing job is unconfirmed.
    permit_required: dict[str, bool] = field(default_factory=dict)
    # Job type -> the condition or wording the official source gives with it.
    permit_notes: dict[str, str] = field(default_factory=dict)
    department: str = ""
    phone: str = ""
    email: str = ""
    website: str = ""
    website_label: str = ""
    submit_how: str = "Confirm how this city takes submittals."
    sets_required: int = 1
    needs_parcel_number: bool = False
    utility: str = ""
    utility_short: str = ""
    sheet_size: str = "letter"  # "tabloid" for 11" x 17" sheets; "ansi_d" for a 22" x 34" drawing set
    # Job type -> a sheet size for that job alone, over the city's sheet_size (e.g. SF PV plans on 11 x 17).
    sheet_size_by_job: dict[str, str] = field(default_factory=dict)
    # City-published general notes printed on solar packets (e.g. San Diego's PV plan template notes).
    solar_general_notes: tuple[str, ...] = ()
    # The largest site plan scale the city accepts, in feet per inch as drawn on letter. None: any.
    max_plan_scale_ft_per_in: int | None = None
    # Side, in inches, of the empty square the city reserves for its stamp on the cover sheet.
    stamp_box_in: float | None = None
    # (width, height) in inches of the empty area the city reserves on the title sheet for agency stamps.
    # Drawn beside the stamp box on the cover when it fits, else on a blank sheet at the end of the packet.
    title_sheet_blank_area_in: tuple[float, float] | None = None
    # True where the city takes one combined PDF and refuses plan sheets uploaded as separate files.
    single_pdf_only: bool = False
    # ASHRAE 2% annual cooling dry-bulb design temperature (F) for the station nearest the city. Outdoor
    # and sun-exposed conductors are corrected for it (NEC 310.15(B)(1)). None: not set up for this city.
    design_ambient_f: int | None = None
    design_ambient_source: str = ""  # where that figure comes from, a URL
    # What that figure is, as printed on the packet after "Design ambient NN F (NN C):".
    design_ambient_label: str = "ASHRAE 2% annual cooling dry-bulb"
    # True where the house outline is drawn over the aerial: only where outlines were measured to sit on the
    # county parcels (tools/measure_alignment.py) and tree cover hides roofs in the photo.
    outline_over_aerial: bool = False
    # Where the utility publishes the meter sockets and meter-main combos it accepts: their catalog numbers and
    # the list's URL. A service upgrade with a meter-main then has to name one of them. None: not checked.
    approved_meter_mains: tuple[str, ...] | None = None
    approved_meter_mains_source: str = ""
    # What this city enforces, for job types it publishes no checklist for (they use the general one).
    code_note: str = ""
    # Local amendments to the NEC wiring methods. Empty or False: the NEC as published.
    service_raceways: tuple[str, ...] = ()  # raceways allowed above ground for service-entrance conductors
    min_service_raceway: str = ""  # smallest raceway for service-entrance conductors, e.g. '1-1/4"'
    pvc_underground_only: bool = False  # PVC only underground or in concrete; metal raceway above ground
    cable_outdoors: bool = True  # False where no cable type is allowed for a 240 V circuit outdoors
    wiring_source: str = ""  # URL of the amendments behind the four fields above
    # Local service rules. None or empty: the NEC as published.
    max_meter_to_main_ft: int | None = None  # main disconnect within this distance of where conductors enter
    concrete_encased_note: str = ""  # shown when a service upgrade has no concrete-encased electrode
    afci_note: str = ""  # replaces the general AFCI flag on a service upgrade
    fallback_notes: tuple[Note, ...] = ()
    checklists: dict[str, Checklist] = field(default_factory=dict)

    @property
    def rules_date(self) -> str:
        """Date shown and used for page gating/lastmod: permit_rules_verified, else last_verified."""
        return self.permit_rules_verified or self.last_verified

    @property
    def label(self) -> str:
        return f"{self.name}, {self.state}" if self.state else self.name

    def checklist_for(self, job_type: str) -> Checklist:
        """This city's checklist for the job type, else the general NEC one, plus the state's amendments."""
        base = self.checklists.get(job_type)
        if base is None:
            base = GENERAL_CHECKLISTS[job_type]
            if self.known and (self.code_note or self.fallback_notes):
                base = replace(
                    base,
                    source_label="General NEC checklist (the city publishes none for this job)",
                    code_note=self.code_note or base.code_note,
                    notes=base.notes + (Note(
                        "always",
                        f"{self.name} publishes no {job_type.replace('_', ' ')} checklist. This is the general NEC "
                        "checklist."  # the code note is its own flag (checklist.code_note), so it is not repeated here
                    ),) + self.fallback_notes,
                )
        added = tuple(note for note in STATE_AMENDMENTS.get(self.state, ()) if note not in base.notes)
        return replace(base, notes=base.notes + added) if added else base

    def known_for(self, job_type: str) -> bool:
        """True only when this city's own checklist covers the job type."""
        return self.known and job_type in self.checklists


# The city modules import the classes above, so they come after them.
from permit_packets.jurisdictions.bellevue_wa import BELLEVUE  # noqa: E402
from permit_packets.jurisdictions.chandler_az import CHANDLER  # noqa: E402
from permit_packets.jurisdictions.charlotte_nc import CHARLOTTE  # noqa: E402
from permit_packets.jurisdictions.el_cajon_ca import EL_CAJON  # noqa: E402
from permit_packets.jurisdictions.general import GENERAL_CHECKLISTS, STATE_AMENDMENTS  # noqa: E402
from permit_packets.jurisdictions.mesa_az import MESA  # noqa: E402
from permit_packets.jurisdictions.nashville_tn import NASHVILLE  # noqa: E402
from permit_packets.jurisdictions.oro_valley_az import ORO_VALLEY  # noqa: E402
from permit_packets.jurisdictions.san_francisco_ca import SAN_FRANCISCO  # noqa: E402

from permit_packets.jurisdictions.san_diego_ca import SAN_DIEGO  # noqa: E402
from permit_packets.jurisdictions.los_angeles_ca import LOS_ANGELES  # noqa: E402
from permit_packets.jurisdictions.san_jose_ca import SAN_JOSE  # noqa: E402
from permit_packets.jurisdictions.seattle_wa import SEATTLE  # noqa: E402
from permit_packets.jurisdictions.portland_or import PORTLAND  # noqa: E402
from permit_packets.jurisdictions.austin_tx import AUSTIN  # noqa: E402
from permit_packets.jurisdictions.dallas_tx import DALLAS  # noqa: E402
from permit_packets.jurisdictions.denver_co import DENVER  # noqa: E402

from permit_packets.jurisdictions.phoenix_az import PHOENIX  # noqa: E402
from permit_packets.jurisdictions.scottsdale_az import SCOTTSDALE  # noqa: E402
from permit_packets.jurisdictions.sacramento_ca import SACRAMENTO  # noqa: E402
from permit_packets.jurisdictions.oakland_ca import OAKLAND  # noqa: E402
from permit_packets.jurisdictions.aurora_co import AURORA  # noqa: E402
from permit_packets.jurisdictions.tampa_fl import TAMPA  # noqa: E402
from permit_packets.jurisdictions.raleigh_nc import RALEIGH  # noqa: E402
from permit_packets.jurisdictions.houston_tx import HOUSTON  # noqa: E402
from permit_packets.jurisdictions.san_antonio_tx import SAN_ANTONIO  # noqa: E402
from permit_packets.jurisdictions.tacoma_wa import TACOMA  # noqa: E402

from permit_packets.jurisdictions.boston_ma import BOSTON  # noqa: E402
from permit_packets.jurisdictions.cambridge_ma import CAMBRIDGE  # noqa: E402
from permit_packets.jurisdictions.newark_nj import NEWARK  # noqa: E402
from permit_packets.jurisdictions.jersey_city_nj import JERSEY_CITY  # noqa: E402
from permit_packets.jurisdictions.new_york_ny import NEW_YORK  # noqa: E402
from permit_packets.jurisdictions.buffalo_ny import BUFFALO  # noqa: E402
from permit_packets.jurisdictions.chicago_il import CHICAGO  # noqa: E402
from permit_packets.jurisdictions.naperville_il import NAPERVILLE  # noqa: E402
from permit_packets.jurisdictions.atlanta_ga import ATLANTA  # noqa: E402
from permit_packets.jurisdictions.savannah_ga import SAVANNAH  # noqa: E402

from permit_packets.jurisdictions.miami_fl import MIAMI  # noqa: E402
from permit_packets.jurisdictions.minneapolis_mn import MINNEAPOLIS  # noqa: E402
from permit_packets.jurisdictions.columbus_oh import COLUMBUS  # noqa: E402
from permit_packets.jurisdictions.salt_lake_city_ut import SALT_LAKE_CITY  # noqa: E402

from permit_packets.jurisdictions.fort_worth_tx import FORT_WORTH  # noqa: E402
from permit_packets.jurisdictions.plano_tx import PLANO  # noqa: E402
from permit_packets.jurisdictions.frisco_tx import FRISCO  # noqa: E402
from permit_packets.jurisdictions.orlando_fl import ORLANDO  # noqa: E402
from permit_packets.jurisdictions.jacksonville_fl import JACKSONVILLE  # noqa: E402
from permit_packets.jurisdictions.irvine_ca import IRVINE  # noqa: E402
from permit_packets.jurisdictions.fresno_ca import FRESNO  # noqa: E402
from permit_packets.jurisdictions.durham_nc import DURHAM  # noqa: E402
from permit_packets.jurisdictions.henderson_nv import HENDERSON  # noqa: E402
from permit_packets.jurisdictions.colorado_springs_co import COLORADO_SPRINGS  # noqa: E402

KNOWN = {(j.name.lower(), j.state): j for j in (FORT_WORTH, PLANO, FRISCO, ORLANDO, JACKSONVILLE, IRVINE, FRESNO, DURHAM, HENDERSON, COLORADO_SPRINGS, MIAMI, MINNEAPOLIS, COLUMBUS, SALT_LAKE_CITY, ORO_VALLEY, EL_CAJON, NASHVILLE, SAN_FRANCISCO, CHARLOTTE, MESA, CHANDLER, BELLEVUE, SAN_DIEGO, LOS_ANGELES, SAN_JOSE, SEATTLE, PORTLAND, AUSTIN, DALLAS, DENVER, PHOENIX, SCOTTSDALE, SACRAMENTO, OAKLAND, AURORA, TAMPA, RALEIGH, HOUSTON, SAN_ANTONIO, TACOMA, BOSTON, CAMBRIDGE, NEWARK, JERSEY_CITY, NEW_YORK, BUFFALO, CHICAGO, NAPERVILLE, ATLANTA, SAVANNAH)}


def jurisdiction_for(city: str | None, state: str | None) -> Jurisdiction:
    name = (city or "").strip()
    state = (state or "").strip().upper()
    known = KNOWN.get((name.lower(), state))
    if known:
        return known
    return Jurisdiction(key="general", name=name or "This area", state=state, known=False)


def jurisdiction_by_key(key: str | None, city: str | None = None, state: str | None = None) -> Jurisdiction:
    for jurisdiction in KNOWN.values():
        if jurisdiction.key == key:
            return jurisdiction
    return jurisdiction_for(city, state)


# How each job reads in a sentence, without its article. EV stays capitalised.
JOB_PHRASES = {
    "ev_charger": "EV charger", "service_upgrade": "panel upgrade", "subpanel": "subpanel",
    "appliance_circuit": "hot tub or 240V circuit", "generator": "generator", "solar_storage": "solar and battery system",
}


def job_phrase(job_type: str, article: bool = False) -> str:
    """'EV charger' or, with article, 'an EV charger' / 'a panel upgrade'."""
    phrase = JOB_PHRASES.get(job_type, job_type.replace("_", " "))
    if not article:
        return phrase
    return ("an " if phrase[:1].lower() in "aeiou" or phrase.startswith("EV") else "a ") + phrase


def filing_line(jurisdiction: Jurisdiction) -> str:
    """One line on who may file the electrical permit here, from owner_may_file (None: not verified)."""
    city = jurisdiction.name if jurisdiction.known else "your city"
    if jurisdiction.owner_may_file is True:
        return f"{city}: owners may file for work they do themselves on their own home. If you hire an electrician, they file it."
    if jurisdiction.owner_may_file is False:
        return f"{city}: a licensed electrician must do and file all electrical work. Hand them this packet."
    return f"Check with {city} whether you can file yourself or need a licensed electrician."


def no_plan_line(jurisdiction: Jurisdiction, job_type: str, link: bool = False) -> str:
    """The Simple Permit sentence for a job the city's source says needs no plans for single-family installs."""
    url = jurisdiction.no_plan_jobs.get(job_type)
    if not url:
        return ""
    permit = f'<a href="{url}" rel="noopener">Simple Permit</a>' if link else "Simple Permit"
    return (f"{jurisdiction.name} lets single-family {job_phrase(job_type)} permits go through a no-plan {permit}, "
            "so you may not need a full packet. The Panel Capacity Report confirms your panel can take it.")


def jurisdiction_json(jurisdiction: Jurisdiction, job_type: str) -> dict:
    """What the page needs to know about a city, for one job type."""
    checklist = jurisdiction.checklist_for(job_type)
    return {
        "key": jurisdiction.key,
        "name": jurisdiction.name,
        "state": jurisdiction.state,
        "known": jurisdiction.known_for(job_type),
        "code_name": jurisdiction.code_name,
        "code_note": checklist.code_note,
        "department": jurisdiction.department,
        "phone": jurisdiction.phone,
        "email": jurisdiction.email,
        "website": jurisdiction.website,
        "website_label": jurisdiction.website_label,
        "submit_how": jurisdiction.submit_how,
        "source_url": checklist.source_url,
        "sets_required": jurisdiction.sets_required,
        "needs_parcel_number": jurisdiction.needs_parcel_number,
        "single_pdf_only": jurisdiction.single_pdf_only,
        "sheet_size": jurisdiction.sheet_size,
        "label": jurisdiction.label,
        "owner_may_file": jurisdiction.owner_may_file,
        "filing_line": filing_line(jurisdiction),
        # Every no-plan job, so the wizard can follow the job the buyer picks after the address is found.
        "no_plan": {key: {"url": url, "before": no_plan_line(jurisdiction, key).split("Simple Permit")[0],
                          "after": no_plan_line(jurisdiction, key).split("Simple Permit")[1]}
                    for key, url in jurisdiction.no_plan_jobs.items()},
        "checklist": [requirement.item for requirement in checklist.items],
    }
