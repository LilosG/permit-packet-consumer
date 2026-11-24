"""Order emails through Resend's HTTP API. A failed or unconfigured send is logged and never raised."""
from __future__ import annotations

import base64
import hashlib
import hmac

import logging
import os
from html import escape
from typing import Any

import httpx

from permit_packets import seo

log = logging.getLogger("permit_packets")

RESEND_URL = "https://api.resend.com/emails"
DEFAULT_FROM = "Permit Packets <hello@myelectricalpermit.com>"
DEFAULT_SUPPORT = "hello@myelectricalpermit.com"


def support_email() -> str:
    return os.environ.get("SUPPORT_EMAIL", "").strip() or DEFAULT_SUPPORT


def send(to: str, subject: str, text: str, html: str, attachments: list[dict[str, str]] | None = None) -> bool:
    """Send one email. Returns False, and never raises, when it can't."""
    key = os.environ.get("RESEND_API_KEY", "").strip()
    if not key:
        log.warning("RESEND_API_KEY is not set, so the email %r was not sent", subject)
        return False
    body: dict[str, Any] = {"from": os.environ.get("EMAIL_FROM", "").strip() or DEFAULT_FROM, "to": [to], "subject": subject, "text": text, "html": html}
    if attachments:
        body["attachments"] = attachments
    try:
        response = httpx.post(RESEND_URL, timeout=12, headers={"Authorization": f"Bearer {key}"}, json=body)
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


def credit_line(price: float) -> str:
    """The Panel Capacity Report credit promise, with the price the buyer paid."""
    amount = f"{price:.2f}".removesuffix(".00")
    return f"Buy a full permit packet with this same email within 30 days and your ${amount} comes off automatically at checkout. No code needed."


def paid_ready(order: dict[str, Any], link: str) -> bool:
    what = "Your Panel Capacity Report is" if order["tier"] == "load_calc" else "Your packet is"
    paragraphs = [f"Thanks for your payment. {what} ready to download for {order['address']}."]
    if order["tier"] == "load_calc" and (order.get("amount_cents") or 0) > 0:
        paragraphs.append(credit_line(order["amount_cents"] / 100))
    return _send(order["customer_email"], "Your packet is ready to download", paragraphs, link, "Download from your order page")


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
    """Tell support a 24-Hour City-Checked order is paid and waiting in the review queue."""
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

def draft_saved(to_email: str, link: str, address: str, job: str, pdf_bytes: bytes | None = None, filename: str = "preview-packet.pdf", summary: str = "") -> bool:
    paras = [f"We saved your free watermarked preview for {address}."]
    if summary:
        paras.append(summary)
    paras.append("Your watermarked preview PDF is attached, and you can view all sheets or unlock the clean, unwatermarked packet anytime using the link below.")
    text, html = _compose(paras, link, "View saved preview & unlock clean PDF")
    atts = [{"filename": filename, "content": base64.b64encode(pdf_bytes).decode()}] if pdf_bytes else None
    return send(to_email, f"Your {job} permit packet preview: {address}", text, html, attachments=atts)


def pack_ready(to_email: str, credits: int, expires: str, link: str) -> bool:
    """Sent when a prepaid credit pack is paid. `expires` is a date such as "November 24, 2027"."""
    return _send(
        to_email, f"Your {credits} Permit Packets credits are ready",
        [f"Thanks for your payment. {credits} Instant Permit Packet credits are now on {to_email}.",
         "To use a credit: start a packet at the link below, choose \"I'm an electrician\" or \"I'm a contractor\", and at the package step choose "
         "\"Use a prepaid credit\". Enter this email address and we'll send you a confirmation link. Opening it spends one credit and unlocks your packet.",
         f"These credits expire on {expires}."],
        link, "Start a packet")


def credit_confirm(to_email: str, link: str) -> bool:
    return _send(
        to_email, "Confirm your prepaid credit",
        ["Use the link below to spend one prepaid credit and unlock your Instant Permit Packet.",
         "The link works once and expires in 30 minutes. If you didn't ask for it, you can ignore this email."],
        link, "Confirm and use one credit")


# ---- Follow-up and review emails ----

def business_postal_address() -> str:
    return os.environ.get("BUSINESS_POSTAL_ADDRESS", "").strip()


def _sign(data: str, secret: str) -> str:
    return hmac.new(secret.encode(), data.encode(), hashlib.sha256).hexdigest()


def unsubscribe_token(email: str) -> str:
    """A token that verifies with CREDITS_SECRET and still lets us recover the email when the link is opened."""
    secret = os.environ.get("CREDITS_SECRET", "").strip()
    encoded = base64.urlsafe_b64encode(email.strip().lower().encode()).rstrip(b"=").decode()
    return f"{encoded}.{_sign(encoded, secret)}"


def verify_unsubscribe_token(token: str) -> str | None:
    """The email a token was made for, or None if it doesn't verify against CREDITS_SECRET."""
    try:
        encoded, signature = token.rsplit(".", 1)
        email = base64.urlsafe_b64decode(encoded + "=" * (-len(encoded) % 4)).decode()
    except Exception:
        return None
    secret = os.environ.get("CREDITS_SECRET", "").strip()
    if not secret or not hmac.compare_digest(signature, _sign(encoded, secret)):
        return None
    return email


def unsubscribe_url(email: str) -> str:
    return f"{seo.public_base_url()}/email/unsubscribe?token={unsubscribe_token(email)}"


def send_followup(to: str, subject: str, paragraphs: list[str], link: str | None, link_label: str) -> bool:
    """A follow-up or review email: the message, an unsubscribe link and the business postal address footer."""
    postal = business_postal_address()
    support = support_email()
    unsubscribe = unsubscribe_url(to)
    text = "\n\n".join(paragraphs)
    if link:
        text += f"\n\n{link_label}: {link}"
    text += f"\n\nQuestions? Email {support}."
    text += f"\nUnsubscribe: {unsubscribe}"
    text += f"\n{postal}"
    body = "".join(f'<p style="margin:0 0 14px">{escape(p)}</p>' for p in paragraphs)
    button = ""
    if link:
        button = (
            f'<p style="margin:22px 0"><a href="{escape(link, quote=True)}" style="display:inline-block;padding:12px 22px;'
            f'border-radius:999px;background:#1d4ed8;color:#ffffff;text-decoration:none;font-weight:600">{escape(link_label)}</a></p>'
            f'<p style="margin:0 0 14px;color:#475569;font-size:14px">Or paste this link into your browser:<br>'
            f'<a href="{escape(link, quote=True)}" style="color:#1d4ed8;word-break:break-all">{escape(link)}</a></p>')
    footer = (
        f'<p style="margin:24px 0 0;color:#64748b;font-size:14px">Questions? Email '
        f'<a href="mailto:{escape(support)}" style="color:#1d4ed8">{escape(support)}</a>. '
        f'<a href="{escape(unsubscribe, quote=True)}" style="color:#64748b">Unsubscribe</a></p>'
        f'<p style="margin:12px 0 0;color:#64748b;font-size:13px">{escape(postal)}</p>')
    html = (
        '<div style="font-family:-apple-system,Segoe UI,Helvetica,Arial,sans-serif;font-size:16px;line-height:1.55;'
        'color:#0f172a;max-width:560px;margin:0 auto;padding:24px">'
        f'{body}{button}{footer}</div>')
    return send(to, subject, text, html)
