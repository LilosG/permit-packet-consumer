"""Who may file in each city, the no-plan Simple Permit, job-label grammar and the Panel Capacity Summary page."""
import re
from dataclasses import replace
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import app
from permit_packets import emails, locations, sitedata
from permit_packets.jurisdictions import KNOWN, filing_line, job_phrase, jurisdiction_json, no_plan_line
from permit_packets.jurisdictions.chicago_il import CHICAGO
from permit_packets.jurisdictions.new_york_ny import NEW_YORK
from permit_packets.jurisdictions.san_diego_ca import SAN_DIEGO
from tests.payment_helpers import pay_order
from tests.test_orders import client as order_client  # noqa: F401
from tests.test_orders import ev_payload, fresh_database, pdf_text, place_order  # noqa: F401

APP_JS = Path(__file__).parent.parent / "permit_packets" / "static" / "assets" / "js" / "app.js"


@pytest.fixture
def web():
    return TestClient(app)


def test_filing_line_for_true_false_and_none():
    assert filing_line(replace(SAN_DIEGO, owner_may_file=True)) == (
        "San Diego: owners may file for work they do themselves on their own home. If you hire an electrician, they file it.")
    assert filing_line(replace(SAN_DIEGO, owner_may_file=False)) == (
        "San Diego: a licensed electrician must do and file all electrical work. Hand them this packet.")
    assert filing_line(replace(SAN_DIEGO, owner_may_file=None)) == (
        "Check with San Diego whether you can file yourself or need a licensed electrician.")


def test_new_york_and_chicago_say_electrician_only_and_the_rest_are_not_guessed():
    assert NEW_YORK.owner_may_file is False and CHICAGO.owner_may_file is False
    assert any("nyc.gov/site/buildings/property-or-business-owner" in s for s in NEW_YORK.sources)
    assert any("chicago.gov/city/en/depts/bldgs/supp_info/electrical_inspections" in s for s in CHICAGO.sources)
    for city in KNOWN.values():
        if city.owner_may_file is True:  # only where the city's own who_may_pull text names owners
            assert re.search(r"owner|homeowner|homestead", city.who_may_pull, re.I), city.key
        if city.key not in ("new-york-ny", "chicago-il") and not re.search(r"owner|homeowner|homestead", city.who_may_pull, re.I):
            assert city.owner_may_file is None, city.key


def test_the_wizard_json_carries_the_filing_values():
    ny = jurisdiction_json(NEW_YORK, "ev_charger")
    assert ny["owner_may_file"] is False and ny["filing_line"].startswith("New York: a licensed electrician")
    chicago = jurisdiction_json(CHICAGO, "ev_charger")
    assert chicago["owner_may_file"] is False
    sd = jurisdiction_json(SAN_DIEGO, "ev_charger")
    assert sd["owner_may_file"] is True and sd["no_plan"]["ev_charger"]["url"].endswith("/information-bulletins/187")
    assert "service_upgrade" not in sd["no_plan"]


def test_the_wizard_hides_the_diy_role_where_only_an_electrician_may_file():
    js = APP_JS.read_text()
    assert "owner_may_file === false" in js and "diy.closest('label').hidden" in js
    assert "'input[name=\"who\"][value=\"hiring\"]').checked = true" in js
    assert "no_plan[current.key]" in js and "'load_calc'" in js


def test_san_diego_ev_page_leads_with_the_simple_permit_not_plans(web):
    html = web.get("/permits/ca/san-diego/ev-charger/").text
    flat = re.sub(r"<[^>]+>", "", html)
    assert "Single-family EV charger installs qualify for a no-plan Simple Permit in San Diego." in flat
    heading = flat.index("If your job needs plans (for example multi-family or larger installs)")
    assert flat.index("Simple Permit") < heading
    assert "upload the required PDF plans" not in flat[:heading]
    assert "owners may file for work they do themselves" in flat
    assert 'href="https://sandiego.gov/development-services/forms-publications/information-bulletins/187"' in html
    # a job without a no-plan source keeps the ordinary wording
    other = re.sub(r"<[^>]+>", "", web.get("/permits/ca/san-diego/panel-upgrade/").text)
    assert "no-plan Simple Permit" not in other


def test_job_phrase_article_and_ev_capitalisation():
    assert job_phrase("ev_charger", article=True) == "an EV charger"
    assert job_phrase("service_upgrade", article=True) == "a panel upgrade"
    assert job_phrase("subpanel", article=True) == "a subpanel"
    assert job_phrase("appliance_circuit", article=True) == "a hot tub or 240V circuit"
    assert "Simple Permit" in no_plan_line(SAN_DIEGO, "ev_charger")


def test_no_job_page_says_a_ev_or_a_lowercase_ev_charger(web):
    checked = 0
    for city in KNOWN.values():
        for slug in sitedata.JOBS:
            if not locations.job_indexable(city, slug):
                continue
            html = web.get(locations.job_path(city, slug)).text
            checked += 1
            assert not re.search(r"\ba ev\b", html, re.I) and " ev charger" not in html, (city.key, slug)
    assert checked > 0


def test_city_pages_show_the_filing_line(web):
    assert "Chicago: a licensed electrician must do and file all electrical work" in web.get(sitedata.city_path(CHICAGO)).text
    html = web.get(sitedata.city_path(SAN_DIEGO)).text
    assert "San Diego: owners may file" in html
    assert "Supporting plans" in html and "no-plan Simple Permit" in html


def first_page_text(pdf: bytes) -> str:
    import pypdfium2
    document = pypdfium2.PdfDocument(pdf)
    return document[0].get_textpage().get_text_bounded()


def test_the_summary_page_is_first_in_load_calc_pdfs_and_absent_from_instant_packets(order_client):
    load = place_order(order_client, tier="load_calc")
    preview = order_client.get(f"/api/orders/{load['access_token']}/preview-pdf").content
    assert "Panel Capacity Summary" in first_page_text(preview)
    pay_order(order_client, load)
    paid = order_client.get(f"/api/orders/{load['access_token']}/pdf")
    text = first_page_text(paid.content)
    assert "Panel Capacity Summary" in text and "PREVIEW" not in text
    assert "Your panel can take this job" in text or "does not have room for this job as entered" in text
    for label in ("Address", "Service rating", "Calculated load", "Spare amps", "Open breaker spaces"):
        assert label in text
    files = order_client.get(f"/api/orders/{load['access_token']}").json()["files"]
    assert files[0]["title"] == "Panel Capacity Summary"
    assert order_client.get(files[0]["url"]).content.startswith(b"%PDF")
    zipped = order_client.get(f"/api/orders/{load['access_token']}/documents")
    assert b"00-panel-capacity-summary.pdf" in zipped.content

    instant = place_order(order_client, tier="instant_packet")
    pay_order(order_client, instant)
    full = order_client.get(f"/api/orders/{instant['access_token']}/pdf").content
    assert "Panel Capacity Summary" not in pdf_text(full)
    assert "Panel Capacity Summary" not in pdf_text(order_client.get(f"/api/orders/{instant['access_token']}/preview-pdf").content)


def test_the_summary_lists_options_when_the_panel_does_not_have_room(order_client):
    payload = ev_payload() | {"service_amps": 60, "open_breaker_spaces": 0}
    order = place_order(order_client, tier="load_calc", payload=payload)
    text = pdf_text(order_client.get(f"/api/orders/{order['access_token']}/preview-pdf").content)
    assert "does not have room for this job as entered" in text
    assert "NEC 220.87 measured-demand method" in text and "A load management device" in text
    assert "A service upgrade (our panel upgrade packet covers it)" in text


def test_the_public_preview_adds_the_summary_only_for_the_load_calc_package(order_client):
    plain = order_client.post("/api/public/preview/ev-charger", json=ev_payload()).json()["packet_page_images"]
    report = order_client.post("/api/public/preview/ev-charger", json=ev_payload() | {"tier": "load_calc"}).json()["packet_page_images"]
    assert len(report) == len(plain) + 1


def test_the_credit_line_uses_the_price_paid(order_client, monkeypatch):
    assert emails.credit_line(29) == "Buy a full permit packet with this same email within 30 days and your $29 comes off automatically at checkout. No code needed."
    assert emails.credit_line(39.5).startswith("Buy a full permit packet with this same email within 30 days and your $39.50 ")
    sent = []
    monkeypatch.setattr(emails, "_send", lambda to, subject, paragraphs, link, label: sent.append(paragraphs) or True)
    emails.paid_ready({"customer_email": "a@b.co", "tier": "load_calc", "address": "1 Main", "amount_cents": 2900}, "https://x")
    emails.paid_ready({"customer_email": "a@b.co", "tier": "instant_packet", "address": "1 Main", "amount_cents": 8900}, "https://x")
    assert any("your $29 comes off automatically" in p for p in sent[0]) and not any("credited" in p for p in sent[1])
    page = Path(__file__).parent.parent / "permit_packets" / "static" / "order.html"
    assert "comes off automatically at checkout. No code needed." in page.read_text()


def test_the_calculator_result_offers_the_panel_capacity_report(web):
    html = web.get("/tools/ev-charger-load-calculator/?service_amps=100").text
    assert "Need it on paper for your electrician or the city?" in html
    assert "/start/?tier=39&amp;role=hiring&amp;job=ev-charger" in html
    assert "credited toward your full packet" in html
    js = (Path(__file__).parent.parent / "permit_packets" / "static" / "assets" / "js" / "calculator.js").read_text()
    assert "calculator_cta_clicked" in js and "calculatorUsed" in js
