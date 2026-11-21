"""Which /permits/ pages are indexed. One rule set, used by the routes, the sitemap, llms.txt and every link.

Every known city with a state is indexable: its hub, its state hub and all of its city x job pages. missing_fields()
is kept for reporting only (what data a city module still lacks); it does not gate indexing.
"""
from __future__ import annotations

from permit_packets import sitedata
from permit_packets.jurisdictions import Jurisdiction

MIN_CHECKLIST_ITEMS = 3
MIN_JOBS_FOR_CITY_HUB = 1
MIN_CITIES_FOR_STATE_HUB = 1


def missing_fields(city: Jurisdiction, job_slug: str) -> list[str]:
    """What keeps this city x job page out of the index. Empty: the page is indexable."""
    job = sitedata.JOBS[job_slug]
    missing = []
    if not city.rules_date:
        missing.append("permit_rules_verified")
    if not city.permit_required.get(job.type_key):
        missing.append("permit_required")
    if len(city.checklist_for(job.type_key).items) < MIN_CHECKLIST_ITEMS:
        missing.append("checklist")
    if not city.nec_edition:
        missing.append("nec_edition")
    if not city.who_may_pull:
        missing.append("who_may_pull")
    if not any(url.startswith("http") for url in city.sources):
        missing.append("sources")
    return missing


def job_indexable(city: Jurisdiction, job_slug: str) -> bool:
    return city.known and bool(city.state)


def indexable_jobs(city: Jurisdiction) -> list[str]:
    return [slug for slug in sitedata.JOBS if job_indexable(city, slug)]


def city_indexable(city: Jurisdiction) -> bool:
    return len(indexable_jobs(city)) >= MIN_JOBS_FOR_CITY_HUB


def indexable_cities(state: str | None = None) -> list[Jurisdiction]:
    return [city for city in sitedata.known_cities()
            if city_indexable(city) and (state is None or city.state.lower() == state)]


def state_indexable(state: str) -> bool:
    return len(indexable_cities(state)) >= MIN_CITIES_FOR_STATE_HUB


def indexable_states() -> list[str]:
    return [state for state in sitedata.cities_by_state() if state_indexable(state)]


def permits_indexable() -> bool:
    return bool(indexable_states())


def job_path(city: Jurisdiction, job_slug: str) -> str:
    return f"{sitedata.city_path(city)}{job_slug}/"


def popular_cities(limit: int = 8) -> list[tuple[str, str]]:
    """Flagship city hubs for navigation. Indexing is gated separately (sitemap, robots)."""
    return sitedata.popular_cities(limit)


def state_links() -> list[tuple[str, str]]:
    return [(sitedata.STATE_NAMES.get(st, st.upper()), f"/permits/{st}/") for st in sitedata.cities_by_state()]


def city_job_links(job_slug: str) -> list[tuple[str, str]]:
    """(label, url) for every city: its job page when that is indexable, else its city hub."""
    return [(city.label, job_path(city, job_slug) if job_indexable(city, job_slug) else sitedata.city_path(city))
            for city in sitedata.known_cities()]


def location_paths() -> list[tuple[str, str]]:
    """(path, lastmod) of every indexable /permits/ page. lastmod is the city module's permit_rules_verified or last_verified."""
    paths: list[tuple[str, str]] = []
    if not permits_indexable():
        return paths
    paths.append(("/permits/", max((c.rules_date for c in indexable_cities()), default="")))
    for state in indexable_states():
        cities = indexable_cities(state)
        paths.append((f"/permits/{state}/", max((c.rules_date for c in cities), default="")))
        for city in cities:
            paths.append((sitedata.city_path(city), city.rules_date))
            paths.extend((job_path(city, slug), city.rules_date) for slug in indexable_jobs(city))
    return paths


def path_indexable(path: str) -> bool:
    return any(path == p for p, _ in location_paths())
