"""Launch pricing display, the banner, the re-draft guarantee, the positioning line and the trimmed header."""
import datetime
import html as htmllib
import re

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import content, pricing

LA = pricing.TZ
DEC_15 = datetime.datetime(2026, 12, 15, 12, 0, tzinfo=LA)
NOV_28 = datetime.datetime(2026, 11, 28, 12, 0, tzinfo=LA)
DEC_31 = datetime.datetime(2026, 12, 31, 20, 0, tzinfo=LA)
JAN_1 = datetime.datetime(2027, 1, 1, 0, 0, 1, tzinfo=LA)

STRIKE = re.compile(r"<s[ >]")


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


@pytest.fixture
def at(monkeypatch):
    def pin(moment):
        monkeypatch.setattr(pricing, "_clock", lambda: moment)
    return pin


def text_of(response):
    return htmllib.unescape(response.text)


def test_banner_shows_before_dec_31(client, at):
    at(DEC_15)
    page = text_of(client.get("/pricing/"))
    assert 'id="launch-banner"' in page and 'href="/pricing/"' in page
    assert "Launch pricing: complete permit packets $59 (regularly $89) through Dec 31." in page
    assert "Black Friday–Cyber Monday" not in page
    at(DEC_31)
    assert 'id="launch-banner"' in client.get("/").text


def test_banner_gone_on_jan_1_2027(client, at):
    at(JAN_1)
    for path in ("/", "/pricing/", "/start/", "/faq/"):
        page = client.get(path).text
        assert "launch-banner" not in page.replace(".launch-banner", "") or 'id="launch-banner"' not in page
        assert 'id="launch-banner"' not in page and "Launch pricing:" not in page


def test_banner_mentions_the_bonus_only_in_the_bonus_window(client, at):
    at(NOV_28)
    page = text_of(client.get("/"))
    assert ("through Dec 31. Black Friday–Cyber Monday: bonus credits on Pro packs.") in page


def test_banner_dismissal_is_stored_inside_try_catch():
    js = (app_module.ASSETS / "js" / "site.js").read_text(encoding="utf-8")
    assert re.search(r"try \{[^}]*localStorage\.getItem", js) and re.search(r"try \{[^}]*localStorage\.setItem", js)


def test_strikethrough_only_while_on_sale(client, at):
    at(DEC_15)
    for path in ("/pricing/", "/"):
        page = text_of(client.get(path))
        assert STRIKE.search(page), path
        assert "Launch price through Dec 31" in page
        assert '<b class="price-now">$59</b><s class="price-was"><span class="vh">regularly </span>$89</s>' in page
    start = text_of(client.get("/start/"))
    assert '<span class="price-now">$29</span><s class="price-was"><span class="vh">regularly </span>$39</s>' in start
    at(JAN_1)
    for path in ("/pricing/", "/", "/start/"):
        page = text_of(client.get(path))
        assert not STRIKE.search(page), path
        assert "Launch price through" not in page
    assert "$89" in text_of(client.get("/pricing/")) and "$59" not in text_of(client.get("/pricing/"))


def test_prices_come_from_pricing_everywhere(client, at):
    at(DEC_15)
    assert '"price": 59' in client.get("/start/").text
    assert pricing.prices_json(DEC_15)["tiers"]["instant_packet"]["price"] == 59
    ld = text_of(client.get("/pricing/"))
    assert '"lowPrice": "29"' in ld and '"highPrice": "109"' in ld
    at(JAN_1)
    ld = text_of(client.get("/pricing/"))
    assert '"lowPrice": "39"' in ld and '"highPrice": "149"' in ld
    assert "priceValidUntil" not in ld


def test_panel_capacity_report_name_and_description(client):
    assert pricing.TIER_NAMES["load_calc"] == "Panel Capacity Report"
    for path in ("/pricing/", "/", "/start/", "/terms/"):
        page = text_of(client.get(path))
        assert "Panel Capacity Report" in page
        assert "Load Calc & Panel Audit" not in page
    assert pricing.PANEL_REPORT_DESCRIPTION == (
        "A submittal-ready NEC 220 load calculation and panel schedule for your address, so you know your panel's "
        "capacity before you get quotes.")
    assert pricing.PANEL_REPORT_DESCRIPTION in text_of(client.get("/pricing/"))
    for path in ("/", "/pricing/", "/start/", "/terms/", "/llms-full.txt"):
        page = text_of(client.get(path))
        assert "plain-English capacity verdict" not in page and "credited toward" not in page


def test_trust_cards_and_who_submits(client):
    home = text_of(client.get("/"))
    grid = home[home.index('class="trust-grid"'):]
    grid = grid[:grid.index("</section>")]
    assert grid.count('class="trust-card"') == 6 and "Secure Checkout via Whop" not in grid
    assert ("Drafts are not PE-stamped and are not legal or engineering advice. You, or your licensed electrician "
            "if your city requires one, sign and submit it.") in grid
    answer = ("You do, or your licensed electrician if your city requires one. Your order page lists the city's "
              "submission steps and the copy-paste fields for its portal. The packet is not PE-stamped, and approval "
              "is not guaranteed.")
    assert answer in home and answer in text_of(client.get("/faq/"))


def test_home_hero_and_metric_copy(client, at):
    at(DEC_15)
    page = text_of(client.get("/"))
    assert ("Electricians charge customers $300–$450 to prepare permit paperwork like this. Build yours from one "
            "address in minutes: site plan, single-line diagram, load calc, panel schedule and UL cut sheets.") in page
    assert "Any US address · Complete packet $59 (reg. $89) · Preview free" in page
    assert "$59 vs $300–$450" in page and "What electricians charge customers for permit paperwork" in page
    assert "Starting at $39" not in page
    at(JAN_1)
    page = text_of(client.get("/"))
    assert "Any US address · Complete packet $89 · Preview free" in page


def test_positioning_line_on_home_pricing_and_first_faq(client):
    for path in ("/", "/pricing/"):
        assert content.POSITIONING in text_of(client.get(path))
    first_question, first_answer = __import__("permit_packets.faq", fromlist=["FAQ"]).FAQ[0]
    assert first_question == "Do I need an electrician?"
    assert first_answer.startswith(content.POSITIONING)
    assert "Who can file depends on your city. Many let homeowners file for work they do themselves on their own home; some require a licensed electrician for all electrical work." in first_answer
    assert 'href="/permits/"' in first_answer
    assert content.POSITIONING in text_of(client.get("/faq/"))


@pytest.mark.parametrize("path", ["/refund/", "/terms/", "/faq/"])
def test_guarantee_text_is_verbatim(client, path):
    page = text_of(client.get(path))
    assert content.GUARANTEE in page
    assert content.GUARANTEE_NOT_COVERED in page
    assert content.GUARANTEE_HOW in page
    assert content.GUARANTEE == (
        "If your city rejects the packet because of an error in it, like a wrong calculation, a drawing mistake, "
        "or an item from the city's checklist we missed, send us the plan-check comments within 60 days and we'll "
        "re-draft it free.")


def test_guarantee_on_home_and_pricing_and_city_changes_answer(client):
    home = text_of(client.get("/"))
    assert "Free Re-draft If We Made an Error" in home and "Full Refund Before Download" in home
    assert content.GUARANTEE in home
    assert content.GUARANTEE in text_of(client.get("/pricing/"))
    assert content.CITY_CHANGES_ANSWER in home


def test_checkout_acknowledgement(client):
    assert "I'm responsible for confirming who can sign and submit in my city." in text_of(client.get("/start/"))


def test_header_no_longer_links_tools_guides_or_documents(client):
    page = client.get("/pricing/").text
    header = page[page.index('<header class="site-header">'):page.index("</header>")]
    for path in ("/tools/", "/guides/", "/permit-documents/", "/faq/"):
        assert f'href="{path}"' not in header
    for path in ("/sample-packet/", "/pricing/", "/start/"):
        assert f'href="{path}"' in header
    assert "Who it's for" in header and "Permits" in header
    footer = page[page.index("<footer"):]
    for path in ("/tools/", "/guides/", "/permit-documents/", "/faq/"):
        assert f'href="{path}"' in footer


def test_no_hardcoded_old_prices_in_the_source():
    import pathlib
    root = pathlib.Path(app_module.__file__).parent
    bad = []
    for path in [root / "app.py", *(root / "permit_packets").rglob("*")]:
        if path.suffix not in (".py", ".html", ".js") or path.name == "pricing.py" or "job_types" in path.parts:
            continue
        for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
            if re.search(r"\$(39|89|169)\b", line):
                bad.append(f"{path.relative_to(root)}:{number}")
    assert bad == ["permit_packets/templates/home.html:154"], bad  # a competitor's price, not ours
