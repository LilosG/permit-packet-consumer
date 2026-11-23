"""Residential grid-tied Solar PV and Battery Energy Storage System (ESS) permits (NEC 690, 705, 706)."""
from __future__ import annotations

from permit_packets.job_types import JobType, Marker
from permit_packets.job_types.solar_storage.api import DOCUMENTS, FEATURE_PAGE, build_response
from permit_packets.job_types.solar_storage.schema import SolarStorageRequest

JOB_TYPE = JobType(
    key="solar_storage",
    slug="solar-battery",
    label="Solar PV & battery",
    short_label="Solar & ESS",
    blurb="Grid-tied solar PV & battery storage with NEC 705.12 120% busbar check, single-line & site plan",
    icon="solar",
    markers=(
        Marker("panel", "Main panel", "P", "#15212c", "Tap the main panel"),
        Marker("inverter", "Inverter / ESS", "S", "#1f7a58", "Tap the solar inverter or battery"),
    ),
    route_between=("panel", "inverter"),
    uses_home_loads=True,
    documents=DOCUMENTS,
    feature_page=FEATURE_PAGE,
    request_model=SolarStorageRequest,
    build_response=build_response,
    zip_name="solar-battery-permit-documents-demo.zip",
)
