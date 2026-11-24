"""Scheduled follow-up and review emails, run by the cron endpoint.

Each run sends only what is due and records it, so nothing is sent twice. Marketing emails
(follow-ups and the review request) are gated on BUSINESS_POSTAL_ADDRESS: without it none of
them go out and one warning is logged per run. Order emails are unaffected.
"""
from __future__ import annotations

import datetime
import logging
import os

from permit_packets import content, emails, orders, pricing

log = logging.getLogger("permit_packets")

MAX_PER_RUN = 200
HOUR = datetime.timedelta(hours=1)
DAY = datetime.timedelta(days=1)
REVIEW_AFTER = datetime.timedelta(days=7)


def _clock() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc)


def _parse(iso: str) -> datetime.datetime:
    value = datetime.datetime.fromisoformat(iso)
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


def _base() -> str:
    return os.environ.get("PUBLIC_BASE_URL", "").strip().rstrip("/")


def _order_url(order: dict) -> str:
    return f"{_base()}/order/{order['access_token']}"


def _pay_url(order: dict) -> str:
    return f"{_base()}/api/orders/{order['access_token']}/pay"


def _guarantee_refund() -> str:
    return "Full refund if you ask before downloading your clean packet."


def _followup_copy(order: dict, kind: str, now: datetime.datetime) -> tuple[str, list[str], str, str]:
    """(subject, paragraphs, link, link_label) for one follow-up."""
    address = order["address"]
    if kind == "preview_1h":
        return ("Your permit packet preview is saved",
                [f"Your preview for {address} is saved. It's the real packet with a watermark. Unlock the clean files any time:",
                 "If your city rejects the packet because of an error in it, we re-draft it free."],
                _order_url(order), "Open your saved preview")
    if kind == "preview_24h":
        return ("What happens after you download",
                [content.POSITIONING, content.GUARANTEE, _guarantee_refund()],
                _order_url(order), "Open your order")
    if kind == "preview_72h":
        return ("Launch pricing ends Dec 31",
                [pricing.resolve("Complete permit packets are {price:instant_packet} (regularly {regular:instant_packet}) through Dec 31.", now)],
                _order_url(order), "Unlock your packet")
    if kind == "checkout_1h":
        return ("Your checkout is still open",
                [f"You started checking out for {address}. Your packet is ready to unlock:"],
                _pay_url(order), "Resume checkout")
    # checkout_24h
    return ("Your checkout is still open",
            [f"You started checking out for {address}. Your packet is ready to unlock:", _guarantee_refund()],
            _pay_url(order), "Resume checkout")


FOLLOWUPS: dict[str, tuple[tuple[datetime.timedelta, str], ...]] = {
    "preview_saved": ((HOUR, "preview_1h"), (24 * HOUR, "preview_24h"), (72 * HOUR, "preview_72h")),
    "checkout": ((HOUR, "checkout_1h"), (24 * HOUR, "checkout_24h")),
}


def _send(order: dict, kind: str, now: datetime.datetime) -> bool:
    subject, paragraphs, link, label = _followup_copy(order, kind, now)
    if emails.send_followup(order["customer_email"], subject, paragraphs, link, label):
        orders.record_email_event(order["id"], kind, now)
        return True
    return False


def _followup_for(order: dict, now: datetime.datetime, counts: dict[str, int], sent: list[int]) -> None:
    email = order["customer_email"]
    if orders.is_opted_out(email):
        return
    if orders.paid_since(email, _parse(order["created_at"])):
        return  # they paid for something with this email since; the sales nudge isn't for them
    age = now - _parse(order["created_at"])
    for delay, kind in FOLLOWUPS[order["source"]]:
        if age < delay:
            continue
        if kind == "preview_72h" and not pricing.launch_active(now):
            continue
        if orders.has_email_event(order["id"], kind):
            continue
        if sent[0] >= MAX_PER_RUN:
            return
        if _send(order, kind, now):
            counts[kind] = counts.get(kind, 0) + 1
            sent[0] += 1


def _review_for(order: dict, now: datetime.datetime, counts: dict[str, int], sent: list[int]) -> None:
    review_url = os.environ.get("REVIEW_URL", "").strip()
    if not review_url:
        return
    if orders.is_opted_out(order["customer_email"]):
        return
    if orders.has_email_event(order["id"], "review_7d"):
        return
    downloaded = order.get("downloaded_at")
    if not downloaded:
        return
    if now - _parse(downloaded) < REVIEW_AFTER:
        return
    if sent[0] >= MAX_PER_RUN:
        return
    subject = "How did your permit go?"
    paragraphs = [
        f"Did your packet help with {order['address']}? A short review helps other homeowners and electricians find us.",
        review_url,
        "If the city rejected it because of an error in the packet, reply with the plan-check comments and we'll re-draft it free.",
    ]
    if emails.send_followup(order["customer_email"], subject, paragraphs, None, ""):
        orders.record_email_event(order["id"], "review_7d", now)
        counts["review_7d"] = counts.get("review_7d", 0) + 1
        sent[0] += 1


def run(now: datetime.datetime | None = None) -> dict[str, int]:
    """Send every follow-up and review request that is due. Returns {kind: count}, at most MAX_PER_RUN emails in total."""
    now = (now or _clock())
    if now.tzinfo is None:
        now = now.replace(tzinfo=datetime.timezone.utc)
    counts: dict[str, int] = {}
    if not emails.business_postal_address():
        log.warning("BUSINESS_POSTAL_ADDRESS is not set, so no follow-up or review emails were sent")
        return counts
    sent: list[int] = [0]
    for order in orders.list_pending(MAX_PER_RUN):
        if sent[0] >= MAX_PER_RUN:
            break
        _followup_for(order, now, counts, sent)
    for order in orders.list_downloaded(MAX_PER_RUN):
        if sent[0] >= MAX_PER_RUN:
            break
        _review_for(order, now, counts, sent)
    return counts