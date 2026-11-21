"""Order emails through Resend's HTTP API. A failed or unconfigured send is logged and never raised."""
from __future__ import annotations

import logging
import os
from html import escape
from typing import Any

import httpx

log = logging.getLogger("permit_packets")

RESEND_URL = "https://api.resend.com/emails"
DEFAULT_FROM = "Permit Packets <hello@myelectricalpermit.com>"
DEFAULT_SUPPORT = "hello@myelectricalpermit.com"


def support_email() -> str:
    return os.environ.get("SUPPORT_EMAIL", "").strip() or DEFAULT_SUPPORT


def send(to: str, subject: str, text: str, html: str) -> bool:
    """Send one email. Returns False, and never raises, when it can't."""
    key = os.environ.get("RESEND_API_KEY", "").strip()
    if not key:
        log.warning("RESEND_API_KEY is not set, so the email %r was not sent", subject)
        return False
    try:
        response = httpx.post(
            RESEND_URL, timeout=8,
            headers={"Authorization": f"Bearer {key}"},
            json={"from": os.environ.get("EMAIL_FROM", "").strip() or DEFAULT_FROM, "to": [to],
                  "subject": subject, "text": text, "html": html},
        )
        response.raise_for_status()
        return True
    except Exception as error:  # any failure: the order flow must go on
        log.error("Could not send the email %r: %s", subject, error)
        return False


def _html(paragraphs: list[str], link: str | None, link_label: str, support: str) -> str:
    body = "".join(f'<p style="margin:0 0 14px">{paragraph}</p>' for paragraph in paragraphs)
    button = (
        f'<p style="margin:22px 0"><a href="{escape(link, quote=True)}" style="display:inline-block;padding:12px 22px;'
        f'border-radius:999px;background:#1d4ed8;color:#ffffff;text-decoration:none;font-weight:600">{escape(link_label)}</a></p>'
        f'<p style="margin:0 0 14px;color:#475569;font-size:14px">Or paste this link into your browser:<br>'
        f'<a href="{escape(link, quote=True)}" style="color:#1d4ed8;word-break:break-all">{escape(link)}</a></p>'
    ) if link else ""
    return (
        '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.55;'
        'color:#0f172a;max-width:560px;margin:0 auto;padding:24px">'
        f'{body}{button}'
        f'<p style="margin:24px 0 0;color:#64748b;font-size:14px">Questions? Email '
        f'<a href="mailto:{escape(support)}" style="color:#1d4ed8">{escape(support)}</a>.</p></div>'
    )


def _compose(paragraphs: list[str], link: str | None, link_label: str) -> tuple[str, str]:
    """(text, html) for a message of plain paragraphs with an optional link and the support address."""
    support = support_email()
    text = "\n\n".join(paragraphs)
    if link:
        text += f"\n\n{link_label}: {link}"
    text += f"\n\nQuestions? Email {support}."
    return text, _html([escape(p) for p in paragraphs], link, link_label, support)


def _send(to: str, subject: str, paragraphs: list[str], link: str | None, link_label: str) -> bool:
    text, html = _compose(paragraphs, link, link_label)
    return send(to, subject, text, html)


def order_created(order: dict[str, Any], link: str) -> bool:
    return _send(
        order["customer_email"], f"Your Permit Packet order: {order['address']}",
        [f"We've saved your order {order['order_code']} for {order['address']}.",
         "Use this link to pay and to come back to your order any time."],
        link, "Your order page")


def paid_ready(order: dict[str, Any], link: str) -> bool:
    what = "Your load calculation and panel audit are" if order["tier"] == "load_calc" else "Your packet is"
    return _send(
        order["customer_email"], "Your packet is ready to download",
        [f"Thanks for your payment. {what} ready to download for {order['address']}."],
        link, "Download from your order page")


def in_review(order: dict[str, Any], link: str, city: str) -> bool:
    return _send(
        order["customer_email"], "We're checking your packet",
        [f"Thanks for your payment. We're checking your packet for {order['address']} against {city}'s requirements.",
         "It will be released within 24 hours, and we'll email you as soon as it is."],
        link, "Your order page")


def released(order: dict[str, Any], link: str) -> bool:
    return _send(
        order["customer_email"], "Your city-checked packet is ready",
        [f"Your city-checked packet for {order['address']} has been released and is ready to download."],
        link, "Download from your order page")


def review_alert(order: dict[str, Any], order_link: str, admin_link: str) -> bool:
    """Tell support a $169 order is paid and waiting in the review queue."""
    paragraphs = [
        f"A 24-Hour City-Checked order was paid and is waiting for review: {order['order_code']}, {order['address']}.",
        f"Buyer: {order['customer_email']}",
        f"Order page: {order_link}",
    ]
    text, html = _compose(paragraphs, admin_link, "Admin (In review list)")
    return send(support_email(), f"Review needed: {order['order_code']} {order['address']}", text, html)


def find_order(email: str, found: list[tuple[dict[str, Any], str]]) -> bool:
    """One email listing every order link for the address. found is [(order, link)]."""
    lines = [f"{order['order_code']}, {order['address']}: {link}" for order, link in found]
    paragraphs = ["Here are the order links for this email address:"]
    text = "\n\n".join(paragraphs) + "\n\n" + "\n".join(lines) + f"\n\nQuestions? Email {support_email()}."
    items = "".join(
        f'<li style="margin-bottom:10px">{escape(order["order_code"])}, {escape(order["address"])}<br>'
        f'<a href="{escape(link, quote=True)}" style="color:#1d4ed8;word-break:break-all">{escape(link)}</a></li>'
        for order, link in found)
    html = (
        '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.55;'
        'color:#0f172a;max-width:560px;margin:0 auto;padding:24px">'
        f'<p style="margin:0 0 14px">{escape(paragraphs[0])}</p><ul style="padding-left:20px">{items}</ul>'
        f'<p style="margin:24px 0 0;color:#64748b;font-size:14px">Questions? Email '
        f'<a href="mailto:{escape(support_email())}" style="color:#1d4ed8">{escape(support_email())}</a>.</p></div>')
    return send(email, "Your Permit Packet order links", text, html)

def draft_saved(to_email: str, link: str, address: str, job: str) -> bool:
    return _send(to_email, f"Your {job} permit packet preview: {address}", [f"We saved your free watermarked preview for {address}.", "Use the link below to return to your packet anytime and unlock the clean PDF."], link, "Open your saved preview")
