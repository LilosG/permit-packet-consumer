"""Site-wide facts shared by the page routes, the header and footer, the wizard and the sitemaps."""
from __future__ import annotations

from dataclasses import dataclass

from permit_packets.jurisdictions import KNOWN, Jurisdiction


@dataclass(frozen=True)
class Job:
    slug: str  # in URLs: /permits/{st}/{city}/{slug}/ and ?job={slug}
    label: str
    url: str  # the job's own page
    type_key: str  # the job type in the packet builder
    api_slug: str  # the job type's slug in /api/jobs/{slug}


JOBS: dict[str, Job] = {job.slug: job for job in (
    Job("ev-charger", "EV Charger", "/ev-charger-permit/", "ev_charger", "ev-charger"),
    Job("panel-upgrade", "Panel Upgrade", "/panel-upgrade-permit/", "service_upgrade", "service-upgrade"),
    Job("subpanel", "Subpanel", "/subpanel-permit/", "subpanel", "subpanel"),
    Job("hot-tub-240v", "Hot Tub / 240V", "/hot-tub-240v-permit/", "appliance_circuit", "appliance-circuit"),
)}


def job_for_api_slug(api_slug: str) -> str:
    """The URL job slug (ev-charger, panel-upgrade, ...) for a job type's API slug."""
    return next((job.slug for job in JOBS.values() if job.api_slug == api_slug), "")


# Who the packet is for. diy and hiring print the Owner-Builder title block; electrician and contractor print
# the contractor and license title block.
ROLES = {
    "diy": "I'm a homeowner doing the work myself",
    "hiring": "I'm a homeowner hiring an electrician",
    "electrician": "I'm an electrician",
    "contractor": "I'm a contractor or handyman working with a licensed electrician",
}
OWNER_ROLES = ("diy", "hiring")
DEFAULT_ROLE = "diy"

TIER_PARAMS = {"39": "load_calc", "89": "instant_packet", "169": "city_checked_24h"}


def recommended_tier(role: str, tier_param: str = "") -> str:
    """The tier to preselect: an explicit ?tier=, else $39 for a homeowner hiring an electrician, else $89."""
    if tier_param in TIER_PARAMS:
        return TIER_PARAMS[tier_param]
    return "load_calc" if role == "hiring" else "instant_packet"


# ---- Cities, from the jurisdiction modules ----

def city_slug(city: Jurisdiction) -> str:
    """el-cajon-ca -> el-cajon."""
    suffix = f"-{city.state.lower()}"
    return city.key[:-len(suffix)] if city.key.endswith(suffix) else city.key


STATE_NAMES = {"az": "Arizona", "ca": "California", "nc": "North Carolina", "tn": "Tennessee", "wa": "Washington"}


def known_cities() -> list[Jurisdiction]:
    return sorted((city for city in KNOWN.values() if city.known and city.state), key=lambda c: (c.state, c.name))


def cities_by_state() -> dict[str, list[Jurisdiction]]:
    grouped: dict[str, list[Jurisdiction]] = {}
    for city in known_cities():
        grouped.setdefault(city.state.lower(), []).append(city)
    return grouped


def find_city(state: str, slug: str) -> Jurisdiction | None:
    return next((city for city in cities_by_state().get(state, []) if city_slug(city) == slug), None)


def city_by_key(key: str) -> Jurisdiction | None:
    return next((city for city in known_cities() if city.key == key), None)


def city_path(city: Jurisdiction) -> str:
    return f"/permits/{city.state.lower()}/{city_slug(city)}/"


def popular_cities(limit: int = 8) -> list[tuple[str, str]]:
    """(label, url) for the footer, straight from the jurisdiction modules."""
    return [(city.label, city_path(city)) for city in known_cities()[:limit]]


# ---- Header navigation ----

NAV_WHO = [
    ("DIY Homeowners", "/for/diy-homeowners/"),
    ("Hiring an Electrician", "/for/homeowners-hiring-an-electrician/"),
    ("Electricians", "/for/electricians/"),
    ("Contractors", "/for/contractors/"),
]
NAV_PERMITS = [
    ("EV Charger", "/ev-charger-permit/"),
    ("Panel Upgrade", "/panel-upgrade-permit/"),
    ("Subpanel", "/subpanel-permit/"),
    ("Hot Tub / 240V", "/hot-tub-240v-permit/"),
    ("All cities", "/permits/"),
]
NAV_LINKS = [("Tools", "/tools/"), ("Guides", "/guides/"), ("Permit Documents", "/permit-documents/"), ("Sample Packet", "/sample-packet/"), ("Pricing", "/pricing/"), ("FAQ", "/faq/")]
