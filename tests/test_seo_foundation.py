"""Wave 1A: templates, routes, trailing slashes, the wizard at /start/, sitemaps, robots, llms.txt, tracking."""
import json
import re

import pytest
from fastapi.testclient import TestClient

import app as app_module
from permit_packets import seo

PLACEHOLDERS = [  # gated city x job pages (hubs render in full, noindex)
    "/permits/az/chandler/ev-charger/", "/permits/ca/el-cajon/ev-charger/", "/permits/wa/bellevue/hot-tub-240v/",
]


@pytest.fixture
def client():
    return TestClient(app_module.app)


@pytest.mark.parametrize("path", ["/terms", "/pricing", "/start", "/permits/ca/el-cajon", "/find-order"])
def test_a_missing_trailing_slash_is_a_301(client, path):
    response = client.get(path + "?x=1", follow_redirects=False)
    assert response.status_code == 301 and response.headers["location"] == path + "/?x=1"


@pytest.mark.parametrize("path", ["/robots.txt", "/sitemap.xml", "/sitemap-pages.xml", "/llms.txt", "/favicon.ico",
                                  "/api/job-types", "/admin"])
def test_files_api_and_admin_are_not_redirected(client, path):
    assert client.get(path, follow_redirects=False).status_code != 301


def test_unknown_state_city_and_job_are_the_html_404(client):
    for path in ("/permits/zz/", "/permits/ca/nowhere/", "/permits/ca/nowhere/ev-charger/",
                 "/permits/ca/el-cajon/windmill/", "/permits/az/el-cajon/"):
        response = client.get(path)
        assert response.status_code == 404 and "We can't find that page" in response.text


@pytest.mark.parametrize("path", PLACEHOLDERS)
def test_placeholders_are_noindex_and_in_no_sitemap(client, path):
    page = client.get(path)
    assert page.status_code == 200 and "Coming soon" in page.text and "<h1>" in page.text
    assert '<meta name="robots" content="noindex,follow">' in page.text
    for sitemap in ("/sitemap-pages.xml", "/sitemap-locations.xml", "/sitemap-guides.xml"):
        assert path not in client.get(sitemap).text
    assert path not in client.get("/llms.txt").text


def test_sitemap_index_lists_only_children_with_urls(client):
    body = client.get("/sitemap.xml").text
    assert "<sitemapindex" in body and "<urlset" not in body
    assert "/sitemap-pages.xml</loc>" in body and "/sitemap-locations.xml</loc>" in body
    assert "sitemap-guides" not in body  # empty: not listed
    pages = client.get("/sitemap-pages.xml").text
    assert "<lastmod>" in pages and "/terms/</loc>" in pages


def test_sitemap_index_drops_a_child_when_it_empties(client, monkeypatch):
    from permit_packets import locations
    monkeypatch.setattr(locations, "location_paths", lambda: [])
    body = client.get("/sitemap.xml").text
    assert "sitemap-locations" not in body and "sitemap-guides" not in body and "sitemap-pages.xml" in body
    monkeypatch.setitem(seo.PAGES, "/guide-x/", seo.PageEntry("/guide-x/", "G", True, "2026-01-02", "guides"))
    assert "sitemap-guides.xml</loc>" in client.get("/sitemap.xml").text


def test_robots_and_llms(client):
    robots = client.get("/robots.txt").text
    assert "Disallow: /start/?" in robots and "Sitemap: " in robots and "Disallow: /admin" in robots
    llms = client.get("/llms.txt").text
    assert seo.HOME_DESCRIPTION in llms and "/terms/" in llms


def test_start_prefills_and_recommends_39_for_hiring(client):
    html = client.get("/start/?job=ev-charger&role=hiring&address=1 Main St&city=el-cajon-ca").text
    assert re.search(r'name="who" value="hiring" checked', html)
    assert re.search(r'name="tier" value="load_calc" checked', html)
    assert 'data-job="ev_charger"' in html and 'value="1 Main St"' in html and "El Cajon, CA" in html


def test_start_defaults_to_89_and_tier_param_wins(client):
    assert re.search(r'name="tier" value="instant_packet" checked', client.get("/start/?role=electrician").text)
    assert re.search(r'name="tier" value="city_checked_24h" checked', client.get("/start/?role=hiring&tier=169").text)
    junk = client.get("/start/?job=x&role=y&tier=7&city=nope").text
    assert re.search(r'name="who" value="diy" checked', junk) and 'data-job=""' in junk


def test_start_canonical_is_always_bare(client):
    html = client.get("/start/?x=1").text
    assert f'<link rel="canonical" href="{seo.public_base_url()}/start/">' in html


def test_the_wizard_is_off_the_homepage_and_the_hero_submits_to_start(client):
    home = client.get("/").text
    assert 'id="workspace"' not in home and "studio-mode" not in home
    assert '<form id="hero-form" class="hero-form" action="/start/" method="get">' in home
    assert 'href="/start/?tier=39"' in home and 'href="/start/?tier=169"' in home


def test_header_and_footer_links(client):
    html = client.get("/pricing/").text
    for href in ("/for/diy-homeowners/", "/for/homeowners-hiring-an-electrician/", "/for/electricians/",
                 "/for/contractors/", "/ev-charger-permit/", "/panel-upgrade-permit/", "/subpanel-permit/",
                 "/hot-tub-240v-permit/", "/sample-packet/", "/pricing/", "/faq/", "/start/"):
        assert f'href="{href}"' in html, href
    assert 'href="/permits/"' in html and ">All cities<" in html
    footer = html[html.index("<footer"):]
    assert "Permits by job" in footer and "Popular cities" in footer
    assert 'href="/permits/wa/bellevue/"' in footer and 'href="/permits/ca/san-francisco/"' in footer


def test_breadcrumbs_render_html_and_json_ld(client):
    html = client.get("/permits/wa/bellevue/ev-charger/").text
    assert '<nav class="crumbs"' in html
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    crumbs = next(b for b in blocks if b["@type"] == "BreadcrumbList")
    assert [i["name"] for i in crumbs["itemListElement"]][:2] == ["Home", "Permits"]
    assert crumbs["itemListElement"][-1]["item"].endswith("/permits/wa/bellevue/ev-charger/")


def test_json_ld_builders():
    assert seo.service("S", "Area", [])["areaServed"]["name"] == "Area"
    assert seo.article("H", "2026-01-01", "2026-01-02")["author"]["name"] == "Permit Packets by Lilos Growth"
    assert seo.webapp("W", "/start/")["url"].endswith("/start/")
    assert seo.product_offers()["offers"]["lowPrice"] == "39"
    assert "<" not in seo.jsonld_script({"a": "</script>"}).split(">", 1)[1].rsplit("</script", 1)[0]


def test_page_meta_warns_on_long_text(caplog):
    with caplog.at_level("WARNING", logger="permit_packets"):
        seo.page_meta("t" * 61, "d" * 156, "/x")
    assert len(caplog.records) == 2


def test_verification_tags_only_when_set(client, monkeypatch):
    assert "google-site-verification" not in client.get("/").text
    monkeypatch.setenv("GOOGLE_SITE_VERIFICATION", "abc")
    monkeypatch.setenv("BING_SITE_VERIFICATION", "def")
    home = client.get("/").text
    assert '<meta name="google-site-verification" content="abc">' in home and '<meta name="msvalidate.01" content="def">' in home
    assert "google-site-verification" not in client.get("/pricing/").text


def test_gtag_loads_only_when_configured_and_never_on_admin(client, monkeypatch):
    assert "googletagmanager" not in client.get("/").text
    monkeypatch.setenv("GA4_MEASUREMENT_ID", "G-TEST1234")
    for path in ("/", "/start/", "/pricing/", "/nope/"):
        assert "gtag/js?id=G-TEST1234" in client.get(path).text, path
    monkeypatch.setenv("ADMIN_PASSWORD", "x")
    assert "googletagmanager" not in app_module.STATIC.joinpath("admin.html").read_text()


def test_google_search_console_verification_file(client):
    response = client.get("/google405b3c22f036058e.html", follow_redirects=False)
    assert response.status_code == 200 and response.headers["content-type"].startswith("text/html")
    assert response.text == "google-site-verification: google405b3c22f036058e.html"
    for path in ("/sitemap-pages.xml", "/sitemap-locations.xml", "/sitemap-guides.xml", "/llms.txt"):
        assert "google405b3c22f036058e" not in client.get(path).text
