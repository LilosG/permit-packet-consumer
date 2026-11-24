"""Payments behind one interface. PAYMENT_PROVIDER picks the module (default "square"); another provider is another module here
that offers create_checkout, signature_ok and completed_payment."""
from __future__ import annotations

import importlib
import json
import logging
import os
from typing import Any, Callable

from fastapi import HTTPException, status

from permit_packets.payments.square import PaymentError  # noqa: F401  (re-exported)

log = logging.getLogger("permit_packets")


def _provider():
    name = os.environ.get("PAYMENT_PROVIDER", "").strip().lower() or "square"
    return importlib.import_module(f"permit_packets.payments.{name}")


def create_checkout(
    kind: str, record: dict[str, Any], amount_cents: int, buyer_email: str, redirect_url: str, name: str,
) -> tuple[str, str]:
    """(checkout_url, provider_order_id) for an order or a credit pack. Raises PaymentError."""
    return _provider().create_checkout(kind, record, amount_cents, buyer_email, redirect_url, name)


def handle_webhook(
    raw_body: bytes, headers: Any, find_record: Callable[[str], tuple[str, dict[str, Any], int] | None],
    on_paid: Callable[[str, dict[str, Any]], None],
) -> dict[str, Any]:
    """Verify and act on a provider webhook. A bad or missing signature is a 401 and changes nothing.

    find_record(provider_order_id) -> (kind, record, amount_cents the checkout was made for) or None; on_paid(kind, record) unlocks it and must be idempotent.
    Any correctly signed event gets {"ok": True}, including ones that are ignored."""
    provider = _provider()
    if not provider.signature_ok(raw_body, headers.get(provider.SIGNATURE_HEADER)):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Bad signature")
    try:
        event = json.loads(raw_body)
    except ValueError:
        return {"ok": True}
    payment = provider.completed_payment(event) if isinstance(event, dict) else None
    if payment is None:
        return {"ok": True}
    found = find_record(str(payment.get("order_id") or ""))
    if found is None:
        return {"ok": True}
    kind, record, expected = found
    paid = (payment.get("total_money") or {}).get("amount")
    if paid != expected:
        log.error("Payment amount mismatch for %s %s: paid %s, expected %s; not unlocking",
                  kind, record.get("order_code") or record.get("id"), paid, expected)
        return {"ok": True}
    on_paid(kind, record)
    return {"ok": True}
