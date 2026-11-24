"""Public preview, order creation, Square unlock and the admin approve flow."""
import base64
import json
from pathlib import Path

import pytest
import pypdfium2
from fastapi.testclient import TestClient

from app import app
from permit_packets import emails, orders, pricing
from permit_packets.payments import square
from tests import payment_helpers
from tests.payment_helpers import CALLS, Reply, event, pay_order, post_event, sign
from tests.test_ev_golden import GOLDEN, to_current_request

SAMPLES = Path(__file__).parent / "samples"


@pytest.fixture(autouse=True)
def fresh_database(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DEV_AUTO_APPROVE", raising=False)
    monkeypatch.setattr(orders, "SQLITE_PATH", str(tmp_path / "orders.db"))
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-pw")
    payment_helpers.install(monkeypatch)


@pytest.fixture
def client():
    return TestClient(app)


def ev_payload() -> dict:
    return to_current_request(json.loads((GOLDEN / "cases" / "oro_valley_attached_no_plan.json").read_text()))


def place_order(client, tier="instant_packet", payload=None, slug="ev-charger") -> dict:
    response = client.post("/api/public/orders", json={
        "job_slug": slug, "customer_email": "buyer@example.com", "tier": tier, "payload": payload or ev_payload()})
    assert response.status_code == 200, response.text
    return response.json()


def pdf_text(content: bytes) -> str:
    document = pypdfium2.PdfDocument(content)
    return " ".join(page.get_textpage().get_text_bounded() for page in document)


def test_public_preview_is_watermarked_and_withholds_the_paid_extras(client):
    response = client.post("/api/public/preview/ev-charger", json=ev_payload())
    assert response.status_code == 200
    body = response.json()
    assert body["checks"] and body["summary"]
    assert len(body["packet_page_images"]) == 8
    assert base64.b64decode(body["packet_page_images"][0]).startswith(b"\xff\xd8")
    assert "fields" not in body and "submission_email" not in body


def test_preview_pdf_says_preview_and_has_no_lilos_text(client):
    text = pdf_text(client.post("/api/jobs/ev-charger/pdf", json=ev_payload()).content)
    assert "PREVIEW PACKET" in text and "UNLOCK CLEAN PDF" in text
    assert "Lilos" not in text and "DEMO" not in text


def test_an_order_is_saved_pending_with_its_square_link(client):
    for number, tier in enumerate(("load_calc", "instant_packet", "city_checked_24h"), start=1):
        order = place_order(client, tier)
        assert order["order_code"].startswith("PP-")
        assert order["order_url"] == f"/order/{order['access_token']}"
        assert order["checkout_url"] == f"https://square.link/u/{number}"
    view = client.get(f"/api/orders/{order['access_token']}").json()
    assert (view["status"], view["paid"], view["order_code"]) == ("pending_payment", False, order["order_code"])
    assert "pdf_url" not in view and view["checkout_url"] == f"/api/orders/{order['access_token']}/pay"
    assert client.get(order["order_url"]).status_code == 200


def test_order_codes_and_tokens_are_unique(client):
    first, second = place_order(client), place_order(client)
    assert first["order_code"] != second["order_code"] and first["access_token"] != second["access_token"]


def test_a_bad_order_is_refused(client):
    base = {"job_slug": "ev-charger", "customer_email": "buyer@example.com", "tier": "instant_packet", "payload": ev_payload()}
    assert client.post("/api/public/orders", json={**base, "customer_email": "nope"}).status_code == 422
    assert client.post("/api/public/orders", json={**base, "tier": "free"}).status_code == 422
    assert client.post("/api/public/orders", json={**base, "payload": {}}).status_code == 422
    assert client.post("/api/public/orders", json={**base, "job_slug": "nope"}).status_code == 404


def test_downloads_are_locked_until_paid(client):
    token = place_order(client)["access_token"]
    assert client.get(f"/api/orders/{token}/pdf").status_code == 402
    assert client.get(f"/api/orders/{token}/documents").status_code == 402
    assert client.get("/api/orders/not-a-token").status_code == 404


def test_admin_needs_the_password(client, monkeypatch):
    assert client.get("/admin").status_code == 401
    assert client.get("/api/admin/orders", auth=("x", "wrong")).status_code == 401
    assert client.get("/admin", auth=("x", "admin-pw")).status_code == 200
    monkeypatch.delenv("ADMIN_PASSWORD")
    assert client.get("/admin", auth=("x", "")).status_code == 503


def test_admin_approval_unlocks_a_clean_pdf_and_zip(client):
    order = place_order(client)
    token = order["access_token"]
    rows = client.get("/api/admin/orders", auth=("x", "admin-pw")).json()["orders"]
    row = next(r for r in rows if r["order_code"] == order["order_code"])
    assert row["status"] == "pending_payment" and row["customer_email"] == "buyer@example.com"
    assert client.post(f"/api/admin/orders/{row['id']}/approve").status_code == 401

    approved = client.post(f"/api/admin/orders/{row['id']}/approve", auth=("x", "admin-pw"))
    assert approved.status_code == 200 and approved.json()["status"] == "paid"

    view = client.get(f"/api/orders/{token}").json()
    assert view["paid"] and view["documents_url"] and view["portal_fields"] and view["submission_email"]
    pdf = client.get(view["pdf_url"])
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    text = pdf_text(pdf.content)
    assert "PREVIEW" not in text and "DEMO" not in text and "Lilos" not in text
    archive = client.get(view["documents_url"])
    assert archive.status_code == 200 and archive.content.startswith(b"PK")
    assert "-demo" not in archive.headers["content-disposition"]
    assert client.get(f"/api/orders/{token}").json()["status"] == "delivered"


def test_single_pdf_cities_get_no_zip(client):
    payload = {**ev_payload(), "jurisdiction_key": "san-francisco-ca", "city": "San Francisco", "state": "CA"}
    token = place_order(client, payload=payload)["access_token"]
    order = orders.get_by_token(token)
    orders.set_status(order["id"], "paid")
    view = client.get(f"/api/orders/{token}").json()
    assert view["documents_url"] is None and view["pdf_url"]
    assert client.get(f"/api/orders/{token}/documents").status_code == 409


def test_dev_auto_approve_unlocks_at_once(client, monkeypatch):
    monkeypatch.setenv("DEV_AUTO_APPROVE", "true")
    token = place_order(client)["access_token"]
    assert client.get(f"/api/orders/{token}").json()["paid"] is True


def test_owner_builder_prints_no_license(client):
    payload = {**ev_payload(), "contractor": "Pat Homeowner", "license_number": "Owner-Builder"}
    text = pdf_text(client.post("/api/jobs/ev-charger/pdf", json=payload).content)
    assert "Pat Homeowner" in text and "License Owner-Builder" not in text
    blank = {**payload, "license_number": ""}
    assert client.post("/api/jobs/ev-charger/pdf", json=blank).status_code == 200


def test_public_lookup_routes_need_no_login(client):
    assert client.post("/api/property", json={"address": "10 Main", "job_type": "nope"}).status_code == 422
    assert client.get("/api/job-types").status_code == 200
    assert client.get("/dashboard").status_code == 404
    assert client.post("/api/signin", json={"password": "x"}).status_code in (404, 405)


# ---- Square webhook ----

def _status(client, order):
    return client.get(f"/api/orders/{order['access_token']}").json()["status"]


def test_a_completed_square_payment_unlocks_the_order(client):
    order = place_order(client)
    pay_order(client, order)
    assert _status(client, order) == "paid"
    assert client.get(f"/api/orders/{order['access_token']}/pdf").status_code == 200


def test_the_signature_is_checked_good_bad_and_missing(client):
    order = place_order(client)
    row = orders.get_by_token(order["access_token"])
    body = event(row["provider_order_id"], row["amount_cents"])
    raw = json.dumps(body).encode()
    assert client.post("/api/webhooks/square", content=raw).status_code == 401  # missing
    assert post_event(client, body, key="someone-else").status_code == 401  # bad
    assert client.post("/api/webhooks/square", content=raw, headers={"x-square-hmacsha256-signature": ""}).status_code == 401
    assert _status(client, order) == "pending_payment"  # none of them changed anything
    assert post_event(client, body).status_code == 200  # good


def test_an_unconfigured_key_never_verifies(client, monkeypatch):
    order = place_order(client)
    monkeypatch.delenv("SQUARE_WEBHOOK_SIGNATURE_KEY")
    row = orders.get_by_token(order["access_token"])
    raw = json.dumps(event(row["provider_order_id"], row["amount_cents"])).encode()
    assert client.post("/api/webhooks/square", content=raw, headers=sign(raw, key="")).status_code == 401
    assert _status(client, order) == "pending_payment"


def test_the_webhook_ignores_other_events_and_unknown_orders(client):
    order = place_order(client)
    row = orders.get_by_token(order["access_token"])
    assert post_event(client, event(row["provider_order_id"], row["amount_cents"], status="APPROVED")).status_code == 200
    assert post_event(client, event(row["provider_order_id"], row["amount_cents"], kind="refund.created")).status_code == 200
    assert post_event(client, event("sq_unknown", 5900)).status_code == 200
    assert post_event(client, {"type": "payment.updated", "data": None}).status_code == 200
    assert _status(client, order) == "pending_payment"


def test_a_wrong_amount_does_not_unlock(client, caplog):
    order = place_order(client)
    row = orders.get_by_token(order["access_token"])
    with caplog.at_level("ERROR"):
        assert post_event(client, event(row["provider_order_id"], row["amount_cents"] - 100)).status_code == 200
    assert _status(client, order) == "pending_payment"
    assert "amount mismatch" in caplog.text


def test_duplicate_events_do_not_unlock_twice(client, monkeypatch):
    sent = []
    monkeypatch.setattr(emails, "send", lambda to, subject, text, html: sent.append(subject) or True)
    order = place_order(client)
    for kind in ("payment.created", "payment.updated", "payment.updated"):
        pay_order(client, order, kind=kind)
    assert _status(client, order) == "paid"
    assert sent.count("Your packet is ready to download") == 1


def test_every_checkout_link_counts_and_the_order_unlocks_once(client, monkeypatch):
    sent = []
    monkeypatch.setattr(emails, "send", lambda to, subject, text, html: sent.append(subject) or True)
    order = place_order(client)  # checkout 1 (sq_order_1)
    assert client.get(f"/api/orders/{order['access_token']}/pay", follow_redirects=False).status_code == 303  # checkout 2
    row = orders.get_by_token(order["access_token"])
    assert row["provider_order_id"] == "sq_order_2"  # display only: the latest
    assert orders.get_checkout_link("sq_order_1")["amount_cents"] == row["amount_cents"]
    assert post_event(client, event("sq_order_1", row["amount_cents"])).status_code == 200  # pay the FIRST link
    assert _status(client, order) == "paid"
    assert post_event(client, event("sq_order_2", row["amount_cents"])).status_code == 200  # the other link does nothing
    assert post_event(client, event("sq_order_1", row["amount_cents"])).status_code == 200
    assert _status(client, order) == "paid" and sent.count("Your packet is ready to download") == 1


def test_a_delivered_order_is_not_set_back_to_paid(client):
    order = place_order(client)
    pay_order(client, order)
    client.get(f"/api/orders/{order['access_token']}/pdf")
    assert _status(client, order) == "delivered"
    pay_order(client, order)
    assert _status(client, order) == "delivered"


# ---- Square checkout ----

def test_a_checkout_posts_the_payment_link_request(client):
    order = place_order(client, "instant_packet")
    assert order["checkout_url"] == "https://square.link/u/1"
    url, call = CALLS[0]
    assert url == "https://connect.squareupsandbox.com/v2/online-checkout/payment-links"
    assert call["headers"] == {"Authorization": "Bearer tok_test", "Content-Type": "application/json", "Square-Version": square.SQUARE_VERSION}
    body = call["json"]
    assert body["quick_pay"] == {"name": pricing.TIER_NAMES["instant_packet"],
                                 "price_money": {"amount": pricing.price("instant_packet") * 100, "currency": "USD"}, "location_id": "LOC1"}
    assert body["checkout_options"] == {"redirect_url": f"https://permits.example.com/order/{order['access_token']}"}
    assert body["pre_populated_data"] == {"buyer_email": "buyer@example.com"}
    assert body["payment_note"] == order["order_code"]
    assert len(body["idempotency_key"]) == 36
    row = orders.get_by_token(order["access_token"])
    assert (row["provider_order_id"], row["source"]) == ("sq_order_1", "checkout")


def test_production_uses_the_live_host(client, monkeypatch):
    monkeypatch.setenv("SQUARE_ENVIRONMENT", "production")
    place_order(client)
    assert CALLS[0][0].startswith("https://connect.squareup.com/")


def test_a_failed_checkout_gives_no_link(client):
    square.httpx.post = lambda *a, **k: Reply({}, 500)
    assert place_order(client)["checkout_url"] == ""


def test_the_buyer_sees_the_price_they_paid_not_todays(client, monkeypatch):
    order = place_order(client, "instant_packet")
    paid = pricing.price("instant_packet")
    monkeypatch.setattr(pricing, "launch_active", lambda now=None: False)
    assert pricing.price("instant_packet") != paid
    assert client.get(f"/api/orders/{order['access_token']}").json()["price"] == paid


def test_the_order_page_checkout_makes_one_link_per_click_not_per_poll(client):
    order = place_order(client, "instant_packet")
    for _ in range(3):
        client.get(f"/api/orders/{order['access_token']}")
    assert len(CALLS) == 1
    response = client.get(f"/api/orders/{order['access_token']}/pay", follow_redirects=False)
    assert response.status_code == 303 and response.headers["location"] == "https://square.link/u/2"
    assert CALLS[1][1]["json"]["quick_pay"]["price_money"]["amount"] == orders.get_by_token(order["access_token"])["amount_cents"]
    pay_order(client, order)
    paid = client.get(f"/api/orders/{order['access_token']}/pay", follow_redirects=False)
    assert paid.headers["location"] == f"/order/{order['access_token']}" and len(CALLS) == 2
    assert client.get("/api/orders/nope/pay", follow_redirects=False).status_code == 404


def test_the_role_is_stored_on_the_order_and_reported_for_analytics(client):
    response = client.post("/api/public/orders", json={
        "job_slug": "ev-charger", "customer_email": "buyer@example.com", "tier": "load_calc",
        "payload": ev_payload(), "role": "hiring"})
    assert response.status_code == 200
    view = client.get(f"/api/orders/{response.json()['access_token']}").json()
    assert (view["role"], view["job"], view["price"]) == ("hiring", "ev-charger", pricing.price("load_calc"))
    bogus = client.post("/api/public/orders", json={
        "job_slug": "ev-charger", "customer_email": "buyer@example.com", "tier": "instant_packet",
        "payload": ev_payload(), "role": "wizard"}).json()
    assert client.get(f"/api/orders/{bogus['access_token']}").json()["role"] == ""


def test_the_order_page_has_the_send_to_electrician_button(client):
    page = client.get(place_order(client)["order_url"]).text
    assert 'id="send-electrician" hidden' in page and "mailto:?subject=" in page
