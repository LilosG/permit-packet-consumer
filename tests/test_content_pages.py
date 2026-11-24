"""Wave 1B: the content pages. Each is a 200 with one H1, a slash canonical, valid JSON-LD and a sitemap entry."""
import json
import re
from html.parser import HTMLParser

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import content, locations, pricing, seo

HUB_PATHS = ["/ev-charger-permit/", "/panel-upgrade-permit/", "/subpanel-permit/", "/hot-tub-240v-permit/", "/generator-permit/", "/solar-battery-permit/"]
AUDIENCE_PATHS = ["/for/diy-homeowners/", "/for/homeowners-hiring-an-electrician/", "/for/electricians/",
                  "/for/contractors/"]
OTHER_PATHS = ["/", "/sample-packet/", "/pricing/", "/faq/", "/about/"]
CONTENT_PATHS = HUB_PATHS + AUDIENCE_PATHS + OTHER_PATHS


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []

    def handle_starttag(self, tag, attrs):
        if tag == "a" and dict(attrs).get("href"):
            self.hrefs.append(dict(attrs)["href"])


def hrefs(html):
    parser = Links()
    parser.feed(html)
    return parser.hrefs


def words(html, tag="main"):
    body = re.search(rf"<{tag}.*?</{tag}>", html, re.S).group(0)
    return len(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", body)).split())


@pytest.mark.parametrize("path", CONTENT_PATHS)
def test_page_basics(client, path):
    page = client.get(path)
    assert page.status_code == 200
    assert len(re.findall(r"<h1[ >]", page.text)) == 1
    canonical = re.search(r'<link rel="canonical" href="([^"]+)"', page.text).group(1)
    assert canonical.endswith("/") and canonical.endswith(path)
    assert '<meta name="robots" content="index,follow">' in page.text
    blocks = re.findall(r'<script type="application/ld\+json">(.*?)</script>', page.text, re.S)
    assert blocks and all(isinstance(json.loads(block), dict) for block in blocks)
    title = re.search(r"<title>(.*?)</title>", page.text).group(1)
    assert len(title) <= 60
    description = re.search(r'<meta name="description" content="([^"]+)"', page.text).group(1)
    assert len(description) <= 155
    assert "Permit Packets by Lilos Growth" in page.text and "Last reviewed: November 16, 2026" in page.text


@pytest.mark.parametrize("path", CONTENT_PATHS)
def test_page_is_in_the_sitemap_and_registry(client, path):
    entry = seo.PAGES[path]
    assert entry.indexable and entry.lastmod == "2026-11-16"
    assert f"{path}</loc><lastmod>2026-11-16</lastmod>" in client.get("/sitemap-pages.xml").text


@pytest.mark.parametrize("path", HUB_PATHS + AUDIENCE_PATHS + ["/sample-packet/", "/pricing/", "/faq/", "/about/"])
def test_answer_block_is_40_to_60_words(client, path):
    answer = re.search(r'class="answer">(.*?)</p>', client.get(path).text, re.S).group(1)
    assert 40 <= len(re.sub(r"<[^>]+>", "", answer).split()) <= 60


@pytest.mark.parametrize("path", HUB_PATHS)
def test_hubs(client, path):
    html = client.get(path).text
    assert 900 <= words(html) <= 1450  # was 1400: the Panel Capacity Report description is longer
    links = hrefs(html)
    for audience in AUDIENCE_PATHS:
        assert audience in links
    assert "/sample-packet/" in links and "/pricing/" in links
    assert any(link.startswith("/start/?job=") for link in links)
    schema = [json.loads(b) for b in re.findall(r'ld\+json">(.*?)</script>', html, re.S)]
    kinds = {block["@type"] for block in schema}
    assert {"Product", "FAQPage", "BreadcrumbList"} <= kinds
    product = next(b for b in schema if b["@type"] == "Product")
    assert product["offers"]["offerCount"] == 3
    assert 5 <= len(next(b for b in schema if b["@type"] == "FAQPage")["mainEntity"]) <= 7


@pytest.mark.parametrize("path", AUDIENCE_PATHS)
def test_audience_pages(client, path):
    html = client.get(path).text
    assert 700 <= words(html) <= 1050  # was 1000: same
    for hub in HUB_PATHS:
        assert hub in hrefs(html)
    kinds = {json.loads(b)["@type"] for b in re.findall(r'ld\+json">(.*?)</script>', html, re.S)}
    assert {"FAQPage", "BreadcrumbList"} <= kinds
    assert 4 <= len(content.AUDIENCES[path.split("/")[-2]].faqs) <= 6


def test_audience_cta_params(client):
    assert "/start/?role=diy" in client.get("/for/diy-homeowners/").text
    assert "/start/?role=hiring&amp;tier=load_calc" in client.get("/for/homeowners-hiring-an-electrician/").text
    assert "/start/?role=electrician" in client.get("/for/electricians/").text
    assert "/start/?role=contractor" in client.get("/for/contractors/").text


def test_sample_packet_shows_each_sheet(client):
    html = client.get("/sample-packet/").text
    for stem in ("01-cover", "02-site-plan", "03-single-line", "04-load-calc", "05-spec-sheet"):
        assert f"/assets/samples/{stem}-1000.webp" in html and f"/assets/samples/{stem}-2000.webp" in html
    for title in ("Checklist and Checks", "Site Plan", "Single-Line Diagram", "Load Calculation"):
        assert title in html
    assert "Sample Homeowner" in html
    images = [b for b in (json.loads(x) for x in re.findall(r'ld\+json">(.*?)</script>', html, re.S))
              if b["@type"] == "ImageObject"]
    assert len(images) == 5


def test_pricing_page(client):
    html = client.get("/pricing/").text
    for text in (*(f"${pricing.price(tier)}" for tier in pricing.TIER_KEYS), "Payments processed securely by Square", "/refund/"):
        assert text in html


def test_faq_covers_every_homepage_question(client):
    from permit_packets import faq as faq_data
    html = client.get("/faq/").text
    for question, _answer in faq_data.FAQ:
        assert question.replace("'", "&#39;") in html or question in html
    for heading in ("General", "Pricing &amp; refunds", "By job", "By role"):
        assert f">{heading}</h2>" in html


def test_about_page(client):
    html = client.get("/about/").text
    assert "https://lilosgrowth.com" in html and "hello@myelectricalpermit.com" in html
    kinds = {json.loads(b)["@type"] for b in re.findall(r'ld\+json">(.*?)</script>', html, re.S)}
    assert "Organization" in kinds


def test_start_is_noindex_and_autolooks_up_an_address(client):
    html = client.get("/start/").text
    assert '<meta name="robots" content="noindex,follow">' in html
    assert 'data-autolookup=""' in html
    assert 'data-autolookup="1"' in client.get("/start/?address=1 Main St, El Cajon, CA").text


def test_privacy_has_analytics(client):
    html = client.get("/privacy/").text
    assert "<h2>Analytics</h2>" in html and "Google Analytics" in html and "sets cookies" in html


def test_footer_product_links_point_to_the_new_pages(client):
    links = hrefs(client.get("/").text)
    for path in ("/sample-packet/", "/pricing/", "/faq/"):
        assert path in links


def test_home_has_the_two_card_rows(client):
    html = client.get("/").text
    for path in AUDIENCE_PATHS + HUB_PATHS:
        assert path in hrefs(html)
    assert "Pull your own permit with the plans your city asks for" in html
    assert "Know your panel capacity before you get quotes" in html
    assert len(re.search(r'<meta name="description" content="([^"]+)"', html).group(1)) <= 150
    assert len(re.search(r"<title>(.*?)</title>", html).group(1)) <= 60


def test_no_indexable_page_links_to_a_noindex_page(client):
    utility = {"/start/", "/find-order/"}  # tools reached from a button, not content pages
    indexable = [path for path, entry in seo.PAGES.items() if entry.indexable]
    for path in indexable:
        for link in hrefs(client.get(path).text):
            target = link.split("#")[0].split("?")[0]
            if not target.startswith("/") or target in utility or "." in target.rsplit("/", 1)[-1]:
                continue
            entry = seo.PAGES.get(target)
            if target.startswith("/permits/"):
                continue  # navigation links every city and state hub; indexing is gated separately
            assert entry is None or entry.indexable, f"{path} links to the noindex page {link}"
            if entry is None:
                assert client.get(target).status_code == 200, f"{path} links to {link}"


def test_permits_link_is_always_present(client, monkeypatch):
    monkeypatch.setattr(locations, "permits_indexable", lambda: False)
    assert "/permits/" in hrefs(client.get("/for/diy-homeowners/").text)


def test_location_pages_stay_out_of_the_pages_sitemap(client):
    assert "/permits/" not in client.get("/sitemap-pages.xml").text
