"""Square test doubles: a fake for httpx.post (no network) and signed webhook events."""
import base64
import hashlib
import hmac
import json
from types import SimpleNamespace

import httpx

from permit_packets import orders
from permit_packets.payments import square

WEBHOOK_URL = "https://permits.example.com/api/webhooks/square"
SIGNATURE_KEY = "sq_test_key"
CALLS: list[tuple[str, dict]] = []


class Reply:
    def __init__(self, body, status_code=200):
        self._body, self.status_code = body, status_code

    def json(self):
        return self._body

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("bad", request=httpx.Request("POST", "http://x"), response=httpx.Response(self.status_code))


def install(monkeypatch, fail=False):
    """Square env vars plus a fake httpx inside the Square module. Each checkout gets order id sq_order_<n>."""
    CALLS.clear()
    monkeypatch.setenv("SQUARE_ACCESS_TOKEN", "tok_test")
    monkeypatch.setenv("SQUARE_LOCATION_ID", "LOC1")
    monkeypatch.setenv("SQUARE_WEBHOOK_SIGNATURE_KEY", SIGNATURE_KEY)
    monkeypatch.setenv("SQUARE_WEBHOOK_URL", WEBHOOK_URL)
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://permits.example.com")
    monkeypatch.delenv("SQUARE_ENVIRONMENT", raising=False)
    monkeypatch.delenv("PAYMENT_PROVIDER", raising=False)

    def fake_post(url, **kwargs):
        CALLS.append((url, kwargs))
        if fail:
            return Reply({}, 500)
        n = len(CALLS)
        return Reply({"payment_link": {"url": f"https://square.link/u/{n}", "order_id": f"sq_order_{n}"}})

    monkeypatch.setattr(square, "httpx", SimpleNamespace(post=fake_post, HTTPError=httpx.HTTPError))


def sign(raw: bytes, key: str = SIGNATURE_KEY) -> dict:
    digest = hmac.new(key.encode(), WEBHOOK_URL.encode() + raw, hashlib.sha256).digest()
    return {"x-square-hmacsha256-signature": base64.b64encode(digest).decode(), "content-type": "application/json"}


def event(provider_order_id: str, amount_cents: int, status: str = "COMPLETED", kind: str = "payment.updated") -> dict:
    return {"type": kind, "data": {"object": {"payment": {
        "status": status, "order_id": provider_order_id, "total_money": {"amount": amount_cents, "currency": "USD"}}}}}


def post_event(client, body: dict, key: str = SIGNATURE_KEY):
    raw = json.dumps(body).encode()
    return client.post("/api/webhooks/square", content=raw, headers=sign(raw, key))


def pay_order(client, order: dict, **overrides):
    """Report a COMPLETED Square payment for an order made through the API."""
    row = orders.get_by_token(order["access_token"])
    amount = overrides.get("amount_cents", row["amount_cents"])
    response = post_event(client, event(row["provider_order_id"], amount, kind=overrides.get("kind", "payment.updated")))
    assert response.status_code == 200, response.text
    return response
