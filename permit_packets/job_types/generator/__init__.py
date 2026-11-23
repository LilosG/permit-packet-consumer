"""Residential standby generator interlock and transfer switch permits (NEC Article 702)."""
from __future__ import annotations

from permit_packets.job_types import JobType, Marker
from permit_packets.job_types.generator.api import DOCUMENTS, FEATURE_PAGE, build_response
from permit_packets.job_types.generator.schema import GeneratorRequest

JOB_TYPE = JobType(
    key="generator",
    slug="generator",
    label="Generator / transfer switch",
    short_label="Generator",
    blurb="Generator interlock or transfer switch with inlet box, single-line diagram and site plan",
    icon="generator",
    markers=(
        Marker("panel", "Main panel", "P", "#15212c", "Tap the main panel"),
        Marker("inlet", "Generator / inlet", "G", "#1f7a58", "Tap the generator or inlet box"),
    ),
    route_between=("panel", "inlet"),
    uses_home_loads=True,
    documents=DOCUMENTS,
    feature_page=FEATURE_PAGE,
    request_model=GeneratorRequest,
    build_response=build_response,
    zip_name="generator-permit-documents-demo.zip",
)
