"""Square checkout (payment links) and webhook verification, over httpx."""
from __future__ import annotations

import base64
import hashlib
import hmac
import os
import uuid
from typing import Any

import httpx

# Square-Version header. Latest entry ("Latest") on Square's API changelog, https://developer.squareup.com/docs/changelog/connect,
# which matches the "API version" shown on the Create Payment Link reference page.
SQUARE_VERSION = "2026-11-18"
PRODUCTION_URL = "https://connect.squareup.com"
SANDBOX_URL = "https://connect.squareupsandbox.com"
SIGNATURE_HEADER = "x-square-hmacsha256-signature"


class PaymentError(Exception):
    """A checkout could not be created."""


def base_url() -> str:
    return PRODUCTION_URL if os.environ.get("SQUARE_ENVIRONMENT", "").strip().lower() == "production" else SANDBOX_URL


def _headers() -> dict[str, str]:
    return {
        "Authorization": f"Bearer {os.environ.get('SQUARE_ACCESS_TOKEN', '').strip()}",
        "Content-Type": "application/json",
        "Square-Version": SQUARE_VERSION,
    }


def create_checkout(
    kind: str, record: dict[str, Any], amount_cents: int, buyer_email: str, redirect_url: str, name: str,
) -> tuple[str, str]:
    """Create a Square payment link. Returns (checkout_url, provider_order_id). `kind` is "order" or "pack"; the record's code is the payment note."""
    body = {
        "idempotency_key": str(uuid.uuid4()),
        "quick_pay": {
            "name": name,
            "price_money": {"amount": int(amount_cents), "currency": "USD"},
            "location_id": os.environ.get("SQUARE_LOCATION_ID", "").strip(),
        },
        "checkout_options": {"redirect_url": redirect_url},
        "pre_populated_data": {"buyer_email": buyer_email},
        "payment_note": str(record.get("order_code") or record.get("id") or ""),
    }
    try:
        response = httpx.post(f"{base_url()}/v2/online-checkout/payment-links", headers=_headers(), json=body, timeout=15)
        response.raise_for_status()
        link = response.json()["payment_link"]
        url, order_id = link["url"], link["order_id"]
    except (httpx.HTTPError, ValueError, KeyError, TypeError) as error:
        raise PaymentError(f"Square checkout failed: {error}") from error
    if not (isinstance(url, str) and url and isinstance(order_id, str) and order_id):
        raise PaymentError("Square checkout came back without a url or order id")
    return url, order_id


def signature_ok(raw_body: bytes, header: str | None) -> bool:
    """base64(HMAC-SHA256(key=SQUARE_WEBHOOK_SIGNATURE_KEY, msg=SQUARE_WEBHOOK_URL + raw body)) must equal the header."""
    if not header:
        return False
    key = os.environ.get("SQUARE_WEBHOOK_SIGNATURE_KEY", "").strip().encode()
    url = os.environ.get("SQUARE_WEBHOOK_URL", "").strip().encode()
    if not key or not url:  # unconfigured: never accept a signature made with an empty key
        return False
    expected = base64.b64encode(hmac.new(key, url + raw_body, hashlib.sha256).digest()).decode()
    return hmac.compare_digest(expected.encode(), header.strip().encode())


def completed_payment(event: dict[str, Any]) -> dict[str, Any] | None:
    """The payment object of a payment.created / payment.updated event whose status is COMPLETED, else None."""
    if event.get("type") not in ("payment.created", "payment.updated"):
        return None
    data = event.get("data")
    obj = data.get("object") if isinstance(data, dict) else None
    payment = obj.get("payment") if isinstance(obj, dict) else None
    if isinstance(payment, dict) and payment.get("status") == "COMPLETED":
        return payment
    return None
