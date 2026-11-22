"""Stage 8: Visual sharpness, header/footer layout, 4-card symmetrical grids, city chips & sheet badges."""
import re
import pytest
from fastapi.testclient import TestClient
import app as app_module


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def test_job_hubs_render_sheet_badges_city_chips_and_four_related_cards(client):
    html = client.get("/ev-charger-permit/").text
    assert '<span class="sheet-num">Sheet 01</span>' in html
    assert '<ul class="city-chips">' in html
    rel_section = html.split("<h2>Free tools and document guides</h2>", 1)[1].split("</ul>", 1)[0]
    assert len(re.findall(r"<li><a href=", rel_section)) == 4


def test_footer_has_by_state_subhead_and_preserves_all_links(client):
    footer = client.get("/").text.split("<footer", 1)[1]
    assert '<p class="foot-subhead">By state</p>' in footer
    assert 'href="/permits/ca/san-diego/"' in footer
    assert 'href="/permits/ca/"' in footer


def test_css_enforces_nowrap_header_and_custom_qa_accordions():
    css = (app_module.ASSETS / "css" / "app.css").read_text(encoding="utf-8")
    assert ".brand { display: inline-flex; align-items: center; gap: 10px; flex: none; white-space: nowrap;" in css
    assert ".city-chips {" in css
    assert ".qa summary::-webkit-details-marker { display: none; }" in css
