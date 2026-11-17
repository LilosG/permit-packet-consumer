"""Which /permits/ pages may be indexed. One rule set, used by the routes, the sitemap, llms.txt and every link.

A city x job page is indexable only when the city module has: last_verified, permit-required confirmed for the
job, 3 or more checklist items, a code edition, who_may_pull and 1 or more official source. A city hub is
indexable when 2 or more of its jobs are; a state hub when 1 or more of its cities are; /permits/ when any city
is. Every other page answers noindex,follow and is left out of the sitemap and out of internal links.
"""
from __future__ import annotations

from permit_packets import sitedata
from permit_packets.jurisdictions import Jurisdiction

MIN_CHECKLIST_ITEMS = 3
MIN_JOBS_FOR_CITY_HUB = 2
MIN_CITIES_FOR_STATE_HUB = 1


def missing_fields(city: Jurisdiction, job_slug: str) -> list[str]:
    """What keeps this city x job page out of the index. Empty: the page is indexable."""
    job = sitedata.JOBS[job_slug]
    missing = []
    if not city.last_verified:
        missing.append("last_verified")
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
    return city.known and bool(city.state) and not missing_fields(city, job_slug)


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
    return [(city.label, sitedata.city_path(city)) for city in indexable_cities()[:limit]]


def city_job_links(job_slug: str) -> list[tuple[str, str]]:
    """(label, url) for every city whose page for this job is indexable."""
    return [(city.label, job_path(city, job_slug)) for city in sitedata.known_cities() if job_indexable(city, job_slug)]


def location_paths() -> list[tuple[str, str]]:
    """(path, lastmod) of every indexable /permits/ page. lastmod is the city module's last_verified."""
    paths: list[tuple[str, str]] = []
    if not permits_indexable():
        return paths
    paths.append(("/permits/", max(c.last_verified for c in indexable_cities())))
    for state in indexable_states():
        cities = indexable_cities(state)
        paths.append((f"/permits/{state}/", max(c.last_verified for c in cities)))
        for city in cities:
            paths.append((sitedata.city_path(city), city.last_verified))
            paths.extend((job_path(city, slug), city.last_verified) for slug in indexable_jobs(city))
    return paths


def path_indexable(path: str) -> bool:
    return any(path == p for p, _ in location_paths())
