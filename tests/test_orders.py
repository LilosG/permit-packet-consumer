"""Public preview, order creation, Whop unlock and the admin approve flow."""
import base64
import json
from pathlib import Path

import pytest
import pypdfium2
from fastapi.testclient import TestClient

from app import app
from permit_packets import orders
from tests.test_ev_golden import GOLDEN, to_current_request

SAMPLES = Path(__file__).parent / "samples"


@pytest.fixture(autouse=True)
def fresh_database(tmp_path, monkeypatch):
    monkeypatch.delenv("DATABASE_URL", raising=False)
    monkeypatch.delenv("DEV_AUTO_APPROVE", raising=False)
    monkeypatch.setattr(orders, "SQLITE_PATH", str(tmp_path / "orders.db"))
    monkeypatch.setenv("ADMIN_PASSWORD", "admin-pw")
    monkeypatch.setenv("WHOP_WEBHOOK_SECRET", "ws_test_secret")
    monkeypatch.setenv("WHOP_LINK_39", "https://whop.com/checkout/plan_39")
    monkeypatch.setenv("WHOP_LINK_89", "https://whop.com/checkout/plan_89")
    monkeypatch.setenv("WHOP_LINK_169", "https://whop.com/checkout/plan_169")


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


def test_an_order_is_saved_pending_with_its_whop_link(client):
    for tier, link in (("load_calc", "39"), ("instant_packet", "89"), ("city_checked_24h", "169")):
        order = place_order(client, tier)
        assert order["order_code"].startswith("PP-")
        assert order["order_url"] == f"/order/{order['access_token']}"
        assert order["whop_checkout_url"] == f"https://whop.com/checkout/plan_{link}?metadata[order_token]={order['access_token']}"
    view = client.get(f"/api/orders/{order['access_token']}").json()
    assert (view["status"], view["paid"], view["order_code"]) == ("pending_payment", False, order["order_code"])
    assert "pdf_url" not in view and view["whop_checkout_url"] == order["whop_checkout_url"]
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


# ---- Whop webhook ----

def _signed(body: dict, secret="ws_test_secret", timestamp=None):
    import hashlib, hmac, time
    raw = json.dumps(body).encode()
    stamp = str(int(timestamp if timestamp is not None else time.time()))
    signature = base64.b64encode(hmac.new(secret.encode(), f"msg_1.{stamp}.".encode() + raw, hashlib.sha256).digest()).decode()
    return raw, {"webhook-id": "msg_1", "webhook-timestamp": stamp, "webhook-signature": f"v1,{signature}",
                 "content-type": "application/json"}


def _event(token, kind="payment.succeeded"):
    return {"type": kind, "data": {"metadata": {"order_token": token}}}


def _status(client, order):
    return client.get(f"/api/orders/{order['access_token']}").json()["status"]


def test_a_signed_whop_payment_unlocks_the_order(client):
    order = place_order(client)
    raw, headers = _signed(_event(order["access_token"]))
    assert client.post("/api/webhooks/whop", content=raw, headers=headers).status_code == 200
    assert _status(client, order) == "paid"
    assert client.get(f"/api/orders/{order['access_token']}/pdf").status_code == 200


def test_the_webhook_refuses_unsigned_and_wrongly_signed_requests(client):
    order = place_order(client)
    raw = json.dumps(_event(order["access_token"])).encode()
    assert client.post("/api/webhooks/whop", content=raw).status_code == 401
    raw, headers = _signed(_event(order["access_token"]), secret="someone-else")
    assert client.post("/api/webhooks/whop", content=raw, headers=headers).status_code == 401
    raw, headers = _signed(_event(order["access_token"]), timestamp=1_000_000)
    assert client.post("/api/webhooks/whop", content=raw, headers=headers).status_code == 401
    assert _status(client, order) == "pending_payment"


def test_the_webhook_is_off_without_a_secret(client, monkeypatch):
    monkeypatch.delenv("WHOP_WEBHOOK_SECRET")
    assert client.post("/api/webhooks/whop", json={}).status_code == 503


def test_the_webhook_ignores_other_events_and_unknown_tokens(client):
    order = place_order(client)
    raw, headers = _signed(_event(order["access_token"], kind="payment.failed"))
    assert client.post("/api/webhooks/whop", content=raw, headers=headers).status_code == 200
    assert _status(client, order) == "pending_payment"
    raw, headers = _signed(_event("no-such-token"))
    assert client.post("/api/webhooks/whop", content=raw, headers=headers).status_code == 200
    raw, headers = _signed({"type": "payment.succeeded", "data": None})
    assert client.post("/api/webhooks/whop", content=raw, headers=headers).status_code == 200


def test_a_delivered_order_is_not_set_back_to_paid(client):
    order = place_order(client)
    raw, headers = _signed(_event(order["access_token"]))
    client.post("/api/webhooks/whop", content=raw, headers=headers)
    client.get(f"/api/orders/{order['access_token']}/pdf")
    assert _status(client, order) == "delivered"
    client.post("/api/webhooks/whop", content=raw, headers=headers)
    assert _status(client, order) == "delivered"
