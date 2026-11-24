"""Credit packs, prepaid credit redemption, the Panel Capacity Report credit, /pro-credits/ and the no-Whop check."""
import datetime
import re
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from app import app
from permit_packets import emails, orders, pricing
from tests.payment_helpers import CALLS, event, post_event
from tests.test_orders import ev_payload, fresh_database, place_order  # noqa: F401

ROOT = Path(__file__).resolve().parent.parent
ADMIN = ("x", "admin-pw")
UTC = datetime.timezone.utc
IN_WINDOW = datetime.datetime(2026, 11, 28, 12, 0, tzinfo=pricing.TZ)
AFTER_WINDOW = datetime.datetime(2026, 12, 10, 12, 0, tzinfo=pricing.TZ)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(emails, "send", lambda to, subject, text, html: sent.append((to, subject, text)) or True)
    return sent


def freeze(monkeypatch, when):
    monkeypatch.setattr(pricing, "_clock", lambda: when)


def buy_pack(client, pack="pack_5", email="pro@example.com"):
    response = client.post("/api/public/packs", json={"pack": pack, "email": email})
    assert response.status_code == 200, response.text
    return orders.get_pack_order_by_provider_order_id(f"sq_order_{len(CALLS)}")


def pay_pack(client, record):
    assert post_event(client, event(record["provider_order_id"], record["amount_cents"])).status_code == 200


def lots(email="pro@example.com"):
    return [lot for lot in orders.list_lots() if lot["customer_email"] == email]


# ---- Packs ----

def test_a_paid_pack_inside_the_bonus_window_gets_the_bonus_count(client, monkeypatch, outbox):
    freeze(monkeypatch, IN_WINDOW)
    record = buy_pack(client, "pack_5")
    assert record["credits"] == pricing.BONUS_CREDITS["pack_5"] == 6
    assert record["amount_cents"] == pricing.pack_price("pack_5") * 100
    # the bonus is honored even if the buyer pays after the window closes
    freeze(monkeypatch, AFTER_WINDOW)
    pay_pack(client, record)
    (lot,) = lots()
    assert (lot["credits_total"], lot["credits_used"]) == (6, 0)
    expires = datetime.datetime.fromisoformat(lot["expires_at"])
    paid = datetime.datetime.fromisoformat(orders.get_pack_order(record["id"])["paid_at"])
    assert expires - paid == datetime.timedelta(days=365)
    (to, subject, text) = outbox[-1]
    assert to == "pro@example.com" and subject == "Your 6 Permit Packets credits are ready"
    assert expires.strftime("%B %-d, %Y") in text


def test_a_pack_outside_the_window_gets_the_base_count(client, monkeypatch):
    freeze(monkeypatch, AFTER_WINDOW)
    record = buy_pack(client, "pack_10")
    pay_pack(client, record)
    assert lots()[0]["credits_total"] == pricing.PACKS["pack_10"] == 10


def test_a_pack_paid_twice_credits_once(client, monkeypatch, outbox):
    freeze(monkeypatch, AFTER_WINDOW)
    record = buy_pack(client)
    for _ in range(3):
        pay_pack(client, record)
    assert len(lots()) == 1
    assert sum(1 for _, subject, _ in outbox if "credits are ready" in subject) == 1


def test_a_pack_with_the_wrong_amount_adds_nothing(client, monkeypatch):
    freeze(monkeypatch, AFTER_WINDOW)
    record = buy_pack(client)
    assert post_event(client, event(record["provider_order_id"], record["amount_cents"] - 1)).status_code == 200
    assert lots() == []


def test_the_pack_api_refuses_bad_input(client):
    assert client.post("/api/public/packs", json={"pack": "pack_99", "email": "a@b.co"}).status_code == 422
    assert client.post("/api/public/packs", json={"pack": "pack_5", "email": "nope"}).status_code == 422


# ---- Redeeming credits ----

def grant(email, credits, days=365, now=None):
    lot = orders.grant_credits(email, credits, "test", now=now)
    if days != 365:
        orders._run("UPDATE credit_lots SET expires_at = ? WHERE id = ?",
                    ((datetime.datetime.now(UTC) + datetime.timedelta(days=days)).isoformat(), lot["id"]))
    return lot


def credit_order(client, email="pro@example.com", role="electrician"):
    response = client.post("/api/public/orders/credit", json={
        "job_slug": "ev-charger", "customer_email": email, "payload": ev_payload(), "role": role})
    assert response.status_code == 200, response.text
    return response.json()


def redeem(client, email="pro@example.com"):
    order = credit_order(client, email)
    order_id = orders.get_by_token(order["order_url"].rsplit("/", 1)[1])["id"]
    return orders.redeem_confirm_token(orders.create_confirm_token(email, order_id))[0]


def test_credits_are_spent_soonest_expiring_first_and_expired_lots_are_skipped(client, outbox):
    expired = grant("pro@example.com", 3, days=-1)
    late = grant("pro@example.com", 2, days=300)
    soon = grant("pro@example.com", 1, days=30)
    used = lambda lot: orders.get_lot(lot["id"])["credits_used"]  # noqa: E731
    assert redeem(client) == "ok"
    assert (used(soon), used(late), used(expired)) == (1, 0, 0)  # the soonest-expiring lot goes first
    assert redeem(client) == "ok" and redeem(client) == "ok"
    assert (used(soon), used(late), used(expired)) == (1, 2, 0)
    assert redeem(client) == "no_credit"  # the expired lot still has credits but is skipped
    assert used(expired) == 0
    assert len(orders._query("SELECT id FROM credit_redemptions")) == 3


def test_opening_the_confirm_link_never_spends_a_credit_only_the_button_does(client, outbox):
    grant("pro@example.com", 2)
    answer = credit_order(client)
    assert answer["message"] == "If this email has credits, we've sent a confirmation link."
    link = next(text for to, subject, text in outbox if subject == "Confirm your prepaid credit")
    url = re.search(r"https://permits\.example\.com(/credits/confirm\?token=[\w-]+)", link).group(1)
    token = url.split("token=")[1]
    row = orders.get_by_token(answer["order_url"].rsplit("/", 1)[1])
    assert (row["source"], row["tier"], row["status"]) == ("credit", "instant_packet", "pending_payment")
    assert len(token) >= 43  # 32 random bytes
    for _ in range(3):  # any number of opens, GET or HEAD, changes nothing
        page = client.get(url)
        assert page.status_code == 200 and f"Use 1 credit for {row['address']}?" in page.text
        assert 'method="post"' in page.text and f'name="token" value="{token}"' in page.text and "noindex" in page.headers["x-robots-tag"]
        assert client.head(url).status_code == 200
    assert lots()[0]["credits_used"] == 0 and orders.get_by_token(row["access_token"])["status"] == "pending_payment"
    first = client.post("/credits/confirm", data={"token": token}, follow_redirects=False)
    assert first.status_code == 303 and first.headers["location"] == answer["order_url"]
    view = client.get(f"/api/orders/{row['access_token']}").json()
    assert view["paid"] and view["price"] == 0 and view["source"] == "credit"
    assert lots()[0]["credits_used"] == 1
    assert client.post("/credits/confirm", data={"token": token}, follow_redirects=False).status_code == 410
    assert client.get(url).status_code == 410 and lots()[0]["credits_used"] == 1


def test_only_the_hash_of_the_token_is_stored(client, outbox):
    grant("pro@example.com", 1)
    credit_order(client)
    link = next(text for to, subject, text in outbox if subject == "Confirm your prepaid credit")
    token = re.search(r"token=([\w-]+)", link).group(1)
    stored = [row[0] for row in orders._query("SELECT token_hash FROM credit_confirm_tokens")]
    assert token not in stored and len(stored[0]) == 64


def test_a_token_expires_after_30_minutes(client, outbox):
    grant("pro@example.com", 1)
    answer = credit_order(client)
    order_id = orders.get_by_token(answer["order_url"].rsplit("/", 1)[1])["id"]
    now = datetime.datetime.now(UTC)
    token = orders.create_confirm_token("pro@example.com", order_id, now=now - datetime.timedelta(minutes=31))
    assert orders.redeem_confirm_token(token) == ("invalid", None)
    fresh = orders.create_confirm_token("pro@example.com", order_id, now=now - datetime.timedelta(minutes=29))
    assert orders.redeem_confirm_token(fresh) == ("ok", order_id)
    assert orders.redeem_confirm_token(fresh) == ("invalid", None)


def test_no_credit_says_so_and_keeps_the_link_usable(client, outbox):
    order = place_order(client)
    row = orders.get_by_token(order["access_token"])
    token = orders.create_confirm_token("pro@example.com", row["id"])
    page = client.post("/credits/confirm", data={"token": token})
    assert page.status_code == 200 and "No credits available" in page.text and "/pro-credits/" in page.text
    assert "noindex" in page.headers["x-robots-tag"]
    grant("pro@example.com", 1)
    assert client.post("/credits/confirm", data={"token": token}, follow_redirects=False).status_code == 303


def test_the_credit_answer_never_reveals_whether_the_email_has_credits(client, outbox):
    grant("has@example.com", 1)
    with_credits = credit_order(client, "has@example.com")
    without = credit_order(client, "none@example.com")
    assert with_credits["message"] == without["message"]
    assert [to for to, subject, _ in outbox if "Confirm" in subject] == ["has@example.com"]


def test_credits_are_for_electricians_and_contractors_only(client):
    response = client.post("/api/public/orders/credit", json={
        "job_slug": "ev-charger", "customer_email": "a@b.co", "payload": ev_payload(), "role": "diy"})
    assert response.status_code == 422


# ---- Panel Capacity Report credit ----

def paid_load_calc(client, email="buyer@example.com"):
    from tests.payment_helpers import pay_order
    order = client.post("/api/public/orders", json={
        "job_slug": "ev-charger", "customer_email": email, "tier": "load_calc", "payload": ev_payload()}).json()
    pay_order(client, order)
    return orders.get_by_token(order["access_token"])


def packet_order(client, tier="instant_packet", email="buyer@example.com"):
    order = client.post("/api/public/orders", json={
        "job_slug": "ev-charger", "customer_email": email, "tier": tier, "payload": ev_payload()}).json()
    return orders.get_by_token(order["access_token"])


def test_the_panel_report_credit_is_claimed_when_the_order_is_paid_not_at_checkout(client):
    from tests.payment_helpers import pay_order
    report = paid_load_calc(client)
    first = packet_order(client)
    assert first["credit_applied_cents"] == report["amount_cents"] and first["credit_source_order_id"] == report["id"]
    assert first["amount_cents"] == pricing.price("instant_packet") * 100 - report["amount_cents"]
    assert CALLS[-1][1]["json"]["quick_pay"]["price_money"]["amount"] == first["amount_cents"]
    assert orders.get_by_id(report["id"])["load_calc_credit_used_at"] is None  # starting checkout claims nothing
    abandoned_again = packet_order(client)  # the first was abandoned: the credit is still offered
    assert abandoned_again["credit_applied_cents"] == report["amount_cents"]
    pay_order(client, {"access_token": first["access_token"]})
    assert orders.get_by_id(report["id"])["load_calc_credit_used_at"]  # claimed on payment
    assert packet_order(client)["credit_applied_cents"] == 0 and orders.get_by_token(first["access_token"])["status"] == "paid"


def test_a_credit_already_claimed_by_another_paid_order_still_unlocks_with_a_warning(client, caplog):
    from tests.payment_helpers import pay_order
    paid_load_calc(client)
    one, two = packet_order(client), packet_order(client)
    pay_order(client, {"access_token": one["access_token"]})
    with caplog.at_level("WARNING"):
        pay_order(client, {"access_token": two["access_token"]})
    assert orders.get_by_token(two["access_token"])["status"] == "paid" and "already used" in caplog.text


def test_the_credit_applies_to_the_city_checked_packet_too_but_not_to_a_report(client):
    paid_load_calc(client)
    assert packet_order(client, "load_calc")["credit_applied_cents"] == 0
    assert packet_order(client, "city_checked_24h")["credit_applied_cents"] > 0


def test_the_credit_expires_after_30_days(client):
    report = paid_load_calc(client)
    old = (datetime.datetime.now(UTC) - datetime.timedelta(days=31)).isoformat()
    orders._run("UPDATE orders SET paid_at = ? WHERE id = ?", (old, report["id"]))
    assert packet_order(client)["credit_applied_cents"] == 0
    recent = (datetime.datetime.now(UTC) - datetime.timedelta(days=29)).isoformat()
    orders._run("UPDATE orders SET paid_at = ? WHERE id = ?", (recent, report["id"]))
    assert packet_order(client)["credit_applied_cents"] == report["amount_cents"]


def test_an_unpaid_report_earns_no_credit_and_the_quote_matches(client):
    client.post("/api/public/orders", json={"job_slug": "ev-charger", "customer_email": "buyer@example.com", "tier": "load_calc", "payload": ev_payload()})
    quote = lambda: client.post("/api/public/credit-quote", json={"email": "buyer@example.com", "tier": "instant_packet"}).json()["credit"]  # noqa: E731
    assert quote() == 0
    report = paid_load_calc(client, "other@example.com")
    assert client.post("/api/public/credit-quote", json={"email": "OTHER@example.com", "tier": "instant_packet"}).json()["credit"] == report["amount_cents"] / 100
    assert packet_order(client, email="other@example.com")["credit_applied_cents"] == report["amount_cents"]


# ---- Pages, admin, wording ----

def test_the_pro_credits_page(client):
    html = client.get("/pro-credits/").text
    assert "<title>Prepaid Permit Packet Credits for Electricians &amp; Contractors</title>" in html
    assert 'content="index,follow"' in html
    assert "Credits are good for 12 months. One credit = one Instant Permit Packet, any job type, any city." in html
    assert html.count('class="pack-form"') == 3 and "<s class=\"price-was\">" in html
    assert "/pro-credits/" in client.get("/sitemap-pages.xml").text
    for path in ("/pricing/", "/for/electricians/", "/for/contractors/", "/faq/"):
        assert 'href="/pro-credits/"' in client.get(path).text
    assert "Disallow: /credits/confirm" in client.get("/robots.txt").text


def test_the_bonus_shows_only_while_it_is_active(client, monkeypatch):
    freeze(monkeypatch, IN_WINDOW)
    assert "+1 bonus" in client.get("/pro-credits/").text
    freeze(monkeypatch, AFTER_WINDOW)
    assert "bonus</i>" not in client.get("/pro-credits/").text


def test_the_wizard_offers_the_credit_option_markup(client):
    html = client.get("/start/").text
    assert "Use a prepaid credit" in html and "Email the credits were bought with" in html


def test_admin_lists_and_grants_credits(client):
    assert client.get("/api/admin/credits").status_code == 401
    assert client.post("/api/admin/credits/grant", json={"email": "a@b.co", "credits": 3, "reason": "x"}).status_code == 401
    assert client.post("/api/admin/credits/grant", auth=ADMIN, json={"email": "bad", "credits": 3}).status_code == 422
    assert client.post("/api/admin/credits/grant", auth=ADMIN, json={"email": "A@b.co", "credits": 3, "reason": "make good"}).status_code == 200
    (row,) = client.get("/api/admin/credits", auth=ADMIN).json()["lots"]
    assert (row["email"], row["total"], row["used"], row["remaining"]) == ("a@b.co", 3, 0, 3)
    days = (datetime.datetime.fromisoformat(row["expires_at"]) - datetime.datetime.now(UTC)).days
    assert days in (364, 365)
    assert "Grant credits" in client.get("/admin", auth=ADMIN).text


def test_no_whop_remains_in_templates_static_files_or_app():
    paths = [ROOT / "app.py", *(ROOT / "permit_packets").rglob("*.py"),
             *(ROOT / "permit_packets" / "templates").rglob("*"), *(ROOT / "permit_packets" / "static").rglob("*")]
    hits = [str(path) for path in paths if path.is_file() and path.suffix in (".py", ".html", ".js", ".css", ".txt", ".json", ".svg")
            and "whop" in path.read_text(errors="ignore").lower()]
    assert hits == []
