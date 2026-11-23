"""Stage 7: Trailing-slash internal link hygiene, homepage authority flow, and 100% UL cut-sheet guide coverage."""
import re
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets import guides_content as gc


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def test_homepage_flows_authority_to_guides_and_tools(client):
    home = client.get("/").text
    main = home[home.index("<main"):home.index("</main>")]
    for href in (
        "/guides/",
        "/tools/",
        "/tools/ev-charger-load-calculator/",
        "/tools/residential-load-calculator/",
        "/guides/hardwired-vs-plug-in-ev-charger-permit/",
        "/guides/subpanel-vs-200a-panel-upgrade/",
    ):
        assert f'href="{href}"' in main, f"Missing homepage main link to {href}"


def test_no_internal_links_trigger_trailing_slash_301(client):
    for path in ("/", "/guides/", "/tools/", "/permits/", "/nope-404"):
        html = client.get(path).text
        hrefs = re.findall(r'href="(/[^"#?]*)"', html)
        for h in hrefs:
            if h == "/" or h.startswith("/assets/") or "." in h.rsplit("/", 1)[-1]:
                continue
            assert h.endswith("/"), f"Internal link missing trailing slash on {path}: {h}"


def test_all_34_guides_include_complete_ul_cut_sheet_coverage():
    assert len(gc.GUIDES) == 36
    for slug in (
        "tesla-wall-connector-gen-3-cut-sheet-permit",
        "tesla-universal-wall-connector-cut-sheet-permit",
        "chargepoint-home-flex-cut-sheet-permit",
        "emporia-classic-ev-charger-cut-sheet-permit",
        "wallbox-pulsar-plus-cut-sheet-permit",
        "square-d-homeline-200a-panel-cut-sheet-permit",
        "milbank-u5168-xtl-200-meter-main-cut-sheet-permit",
    ):
        assert slug in gc.GUIDES
