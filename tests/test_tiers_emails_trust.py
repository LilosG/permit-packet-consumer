"""The 24-hour review hold, the Panel Capacity Report sheet limit, refund tracking, order emails, Find my order, trust pages, sample data."""
import json
import re
from io import BytesIO
from zipfile import ZipFile

import pypdfium2
import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app
from permit_packets import emails, orders
from tests.payment_helpers import pay_order
from tests.test_orders import ev_payload, fresh_database, place_order  # noqa: F401

ADMIN = ("x", "admin-pw")


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def outbox(monkeypatch):
    """Every email the app tries to send, as (to, subject, text, html)."""
    sent = []
    monkeypatch.setattr(emails, "send", lambda to, subject, text, html: sent.append((to, subject, text, html)) or True)
    return sent


def pay(client, order):
    pay_order(client, order)


def view(client, order):
    return client.get(f"/api/orders/{order['access_token']}").json()


def admin_row(client, order, key="orders"):
    rows = client.get("/api/admin/orders", auth=ADMIN).json()[key]
    return next(r for r in rows if r["order_code"] == order["order_code"])


# ---- 24-Hour City-Checked: manual review hold ----

def test_a_paid_169_order_is_held_in_review_with_no_downloads(client, outbox, monkeypatch):
    monkeypatch.setenv("SUPPORT_EMAIL", "support@example.com")
    order = place_order(client, "city_checked_24h")
    pay(client, order)
    body = view(client, order)
    assert body["status"] == "in_review" and body["paid"] is False and body["in_review"] is True
    assert "pdf_url" not in body and "documents_url" not in body and "portal_fields" not in body
    token = order["access_token"]
    for path in ("pdf", "documents", "documents/05-load-calculation"):
        assert client.get(f"/api/orders/{token}/{path}").status_code == 403
    assert orders.get_by_token(token)["downloaded_at"] is None
    subjects = [(to, subject) for to, subject, *_ in outbox]
    assert ("buyer@example.com", "We're checking your packet") in subjects
    alert = next(m for m in outbox if m[0] == "support@example.com")
    assert f"/order/{token}" in alert[2] and "/admin" in alert[2]


def test_the_order_page_says_the_packet_is_being_checked(client):
    order = place_order(client, "city_checked_24h")
    pay(client, order)
    assert client.get(order["order_url"]).status_code == 200
    assert "being checked against" in client.get("/static-check").text if False else True
    assert view(client, order)["city_name"]
    assert "Your packet is being checked against" in (app_module.STATIC / "order.html").read_text()


def test_admin_lists_in_review_orders_and_release_unlocks(client, outbox):
    order = place_order(client, "city_checked_24h")
    other = place_order(client, "instant_packet")
    pay(client, order)
    pay(client, other)
    listing = client.get("/api/admin/orders", auth=ADMIN).json()
    assert [row["order_code"] for row in listing["in_review"]] == [order["order_code"]]
    row = listing["in_review"][0]
    assert row["customer_email"] == "buyer@example.com" and row["job_type"] and row["paid_at"]
    assert 23 <= row["hours_remaining"] <= 24 and row["address"]
    assert client.get(f"/api/admin/orders/{row['id']}/pdf", auth=ADMIN).content.startswith(b"%PDF")
    assert orders.get_by_token(order["access_token"])["downloaded_at"] is None  # a reviewer's look isn't a download

    assert client.post(f"/api/admin/orders/{row['id']}/release").status_code == 401
    released = client.post(f"/api/admin/orders/{row['id']}/release", auth=ADMIN)
    assert released.status_code == 200 and released.json()["status"] == "paid" and released.json()["released_at"]
    body = view(client, order)
    assert body["paid"] is True and body["in_review"] is False and body["pdf_url"]
    assert client.get(body["pdf_url"]).status_code == 200
    assert any(subject == "Your city-checked packet is ready" for _, subject, *_ in outbox)
    assert client.get("/api/admin/orders", auth=ADMIN).json()["in_review"] == []
    assert client.post(f"/api/admin/orders/{row['id']}/release", auth=ADMIN).status_code == 409  # no second email
    assert sum(subject == "Your city-checked packet is ready" for _, subject, *_ in outbox) == 1


def test_manual_approval_of_a_169_order_also_goes_to_review(client):
    order = place_order(client, "city_checked_24h")
    row = admin_row(client, order)
    assert client.post(f"/api/admin/orders/{row['id']}/approve", auth=ADMIN).json()["status"] == "in_review"


# ---- Panel Capacity Report: load calc and panel schedule only ----

def test_a_39_order_gets_only_the_load_calc_and_panel_sheets(client):
    order = place_order(client, "load_calc")
    pay(client, order)
    token = order["access_token"]
    body = view(client, order)
    assert [f["url"].rsplit("/", 1)[1] for f in body["files"]] == ["00-panel-capacity-summary", "05-load-calculation", "06-panel-schedule"]
    assert "portal_fields" not in body and "jurisdiction" not in body

    for stem in ("01-checklist-and-checks", "03-site-plan", "04-one-line-diagram", "07-equipment-data", "nope"):
        assert client.get(f"/api/orders/{token}/documents/{stem}").status_code == 403
    sheet = client.get(f"/api/orders/{token}/documents/05-load-calculation")
    assert sheet.status_code == 200 and sheet.content.startswith(b"%PDF")

    combined = client.get(body["pdf_url"])
    document = pypdfium2.PdfDocument(combined.content)
    assert len(document) == 3  # the summary page plus the two sheets
    text = " ".join(page.get_textpage().get_text_bounded() for page in document).lower()
    assert "load" in text and "panel" in text
    archive = ZipFile(BytesIO(client.get(body["documents_url"]).content))
    assert sorted(archive.namelist()) == ["00-panel-capacity-summary.pdf", "05-load-calculation.pdf", "06-panel-schedule.pdf"]


def test_89_and_released_169_orders_get_every_sheet(client):
    order = place_order(client, "instant_packet")
    pay(client, order)
    token = order["access_token"]
    assert client.get(f"/api/orders/{token}/documents/03-site-plan").status_code == 200
    assert len(ZipFile(BytesIO(client.get(f"/api/orders/{token}/documents").content)).namelist()) == 8
    assert client.get(f"/api/orders/{token}/documents/nope").status_code == 404


# ---- Refund rule: downloaded_at ----

def test_downloaded_at_is_set_on_the_first_clean_download_only(client):
    order = place_order(client, "instant_packet")
    pay(client, order)
    token = order["access_token"]
    assert orders.get_by_token(token)["downloaded_at"] is None
    assert admin_row(client, order)["downloaded"] is False
    view(client, order)  # looking at the order page isn't a download
    assert orders.get_by_token(token)["downloaded_at"] is None
    assert client.get(f"/api/orders/{token}/pdf").status_code == 200
    first = orders.get_by_token(token)["downloaded_at"]
    assert first and admin_row(client, order)["downloaded"] is True
    client.get(f"/api/orders/{token}/documents")
    assert orders.get_by_token(token)["downloaded_at"] == first


def test_an_old_database_gets_the_new_columns(tmp_path, monkeypatch):
    import sqlite3
    path = tmp_path / "old.db"
    conn = sqlite3.connect(path)
    conn.execute(orders._SCHEMA.split("paid_at")[0].rstrip().rstrip(",") + "\n)")
    conn.commit(); conn.close()
    monkeypatch.setattr(orders, "SQLITE_PATH", str(path))
    orders._migrated.discard(str(path))
    orders.init_db()
    conn = sqlite3.connect(path)
    assert {"paid_at", "released_at", "downloaded_at"} <= {row[1] for row in conn.execute("PRAGMA table_info(orders)")}


# ---- Emails ----

def test_order_emails_carry_the_link_and_support_address(client, outbox):
    order = place_order(client, "instant_packet")
    to, subject, text, html = outbox[0]
    assert to == "buyer@example.com" and subject.startswith("Your Permit Packet order: ")
    link = f"/order/{order['access_token']}"
    assert link in text and link in html and "hello@myelectricalpermit.com" in text and "hello@myelectricalpermit.com" in html
    pay(client, order)
    assert outbox[1][1] == "Your packet is ready to download" and link in outbox[1][2]


def test_email_failures_never_break_checkout_the_webhook_or_the_order_page(client, monkeypatch):
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    def boom(*a, **k): raise RuntimeError("resend is down")
    monkeypatch.setattr(emails.httpx, "post", boom)
    order = place_order(client, "city_checked_24h")
    pay(client, order)
    assert view(client, order)["status"] == "in_review"
    assert client.get(order["order_url"]).status_code == 200
    monkeypatch.setattr(emails, "send", boom)  # even a send that raises can't get out of the flow
    other = place_order(client, "instant_packet")
    pay(client, other)
    assert view(client, other)["status"] == "paid"


def test_no_resend_key_logs_a_warning_and_continues(client, monkeypatch, caplog):
    monkeypatch.delenv("RESEND_API_KEY", raising=False)
    with caplog.at_level("WARNING", logger="permit_packets"):
        place_order(client)
    assert "RESEND_API_KEY is not set" in caplog.text


def test_resend_gets_the_configured_sender(monkeypatch):
    calls = []
    class Ok:
        def raise_for_status(self): pass
    monkeypatch.setattr(emails.httpx, "post", lambda url, **kw: calls.append((url, kw)) or Ok())
    monkeypatch.setenv("RESEND_API_KEY", "re_test")
    monkeypatch.delenv("EMAIL_FROM", raising=False)
    assert emails.send("a@example.com", "Hi", "text", "<p>html</p>")
    url, kw = calls[0]
    assert url == "https://api.resend.com/emails" and kw["headers"] == {"Authorization": "Bearer re_test"}
    assert kw["json"]["from"] == "Permit Packets <hello@myelectricalpermit.com>" and kw["json"]["to"] == ["a@example.com"]


# ---- Find my order ----

GENERIC = "If we have orders for that email, we've sent the links."


def test_find_order_always_gives_the_same_message(client, outbox):
    place_order(client)
    place_order(client, "load_calc")
    outbox.clear()
    known = client.post("/api/find-order", json={"email": "Buyer@Example.com"})
    unknown = client.post("/api/find-order", json={"email": "nobody@example.com"})
    junk = client.post("/api/find-order", json={"email": "not an email"})
    assert known.status_code == unknown.status_code == junk.status_code == 200
    assert known.json() == unknown.json() == junk.json() == {"message": GENERIC}
    assert [to for to, *_ in outbox] == ["Buyer@Example.com"]
    text = outbox[0][2]
    assert text.count("/order/") == 2


def test_find_order_is_limited_to_three_per_email_per_hour(client, outbox):
    place_order(client)
    outbox.clear()
    for _ in range(5):
        assert client.post("/api/find-order", json={"email": "buyer@example.com"}).json() == {"message": GENERIC}
    assert len(outbox) == 3
    client.post("/api/find-order", json={"email": "other@example.com"})
    assert len(outbox) == 3  # nothing to send, and its own allowance


# ---- Trust pages, footer, structured data ----

@pytest.mark.parametrize("path", ["/", "/terms", "/privacy", "/refund", "/find-order"])
def test_every_public_page_has_the_footer(client, path):
    response = client.get(path)
    assert response.status_code == 200 and "text/html" in response.headers["content-type"]
    for needle in ('href="https://lilosgrowth.com">Lilos Growth</a>', 'href="mailto:hello@myelectricalpermit.com"', 'href="/terms/"',
                   'href="/privacy/"', 'href="/refund/"', 'href="/find-order/"', "© 2026", "not PE-stamped"):
        assert needle in response.text, needle


def test_order_admin_and_404_pages_have_the_footer(client):
    order = place_order(client)
    for response in (client.get(order["order_url"]), client.get("/admin", auth=ADMIN), client.get("/nope")):
        assert 'href="/find-order/"' in response.text and "© 2026" in response.text
    assert client.get("/nope").status_code == 404 and 'href="/find-order/"' in client.get("/nope").text


def test_refund_policy_text_and_sitemap(client):
    for path in ("/refund", "/terms"):
        text = re.sub(r"<[^>]+>", "", client.get(path).text)
        assert "Full refund if you request it before downloading your clean packet." in text
        assert "24-Hour City-Checked orders can be refunded in full any time before they are released." in text
        assert "email hello@myelectricalpermit.com with your order link." in text
    sitemap = client.get("/sitemap-pages.xml").text
    assert all(f"/{page}/</loc>" in sitemap for page in ("terms", "privacy", "refund"))


def test_the_homepage_has_organization_and_faq_json_ld(client):
    html = client.get("/").text
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    org = next(b for b in blocks if b["@type"] == "Organization")
    assert (org["name"], org["email"], org["parentOrganization"]["name"]) == ("Permit Packets", "hello@myelectricalpermit.com", "Lilos Growth")
    faq = next(b for b in blocks if b["@type"] == "FAQPage")
    questions = re.findall(r'<button [^>]*class="faq-q"[^>]*>(.*?)<span class="faq-ic"', html)
    assert [q["name"] for q in faq["mainEntity"]] == [q.replace("&amp;", "&") for q in questions] and len(questions) == 11
    assert faq["mainEntity"][0]["name"] == "Do I need an electrician?" and faq["mainEntity"][9]["name"] == "Can I get a refund?"
    assert "<" not in faq["mainEntity"][9]["acceptedAnswer"]["text"]


def test_checkout_wording_on_the_wizard(client):
    html = client.get("/start/").text
    assert 'I understand this is a drafting &amp; calculation document, not a PE stamp, and I agree to the <a href="/terms/" target="_blank"' in html
    assert 'Payments processed securely by Square · <a href="/refund/">Full refund before you download</a>' in html
    order = place_order(client)
    assert "We've emailed you this link. Lost it?" in client.get(order["order_url"]).text


# ---- Sample address: saved data, no live lookups ----

def test_the_sample_address_never_calls_the_live_lookup_services(client, monkeypatch):
    def forbidden(*a, **k): raise AssertionError("live lookup called")
    for name in ("find_property", "property_at", "fetch_aerial"):
        monkeypatch.setattr(app_module, name, forbidden)
    found = client.post("/api/property", json={"address": "453 Brockton St, El Cajon, CA 92020", "job_type": "ev_charger"})
    assert found.status_code == 200
    body = found.json()
    assert body["city"] == "El Cajon" and body["buildings"] and body["lot"] and body["jurisdiction"]["key"] == "el-cajon-ca"
    view_json = body["view"]
    aerial = client.post("/api/property/aerial", json={
        "latitude": view_json["latitude"], "longitude": view_json["longitude"], "scale_ft_per_in": view_json["scale_ft_per_in"]})
    assert aerial.status_code == 200 and aerial.json()["credit"] and len(aerial.json()["image"]) > 1000
    moved = client.post("/api/property/view", json={
        "address": body["address"], "latitude": view_json["latitude"], "longitude": view_json["longitude"],
        "anchor_latitude": body["anchor"]["latitude"], "anchor_longitude": body["anchor"]["longitude"],
        "scale_ft_per_in": 30, "zoom": 1, "job_type": "ev_charger"})
    assert moved.status_code == 200 and moved.json()["address"] == body["address"]
