"""Follow-up and review emails: the cron endpoint, scheduling, opt-outs, marketing gating, and unsubscribe."""
import datetime

import pytest
from fastapi.testclient import TestClient

from app import app
from permit_packets import emails, followups, orders
from tests.test_orders import fresh_database  # noqa: F401


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def env(monkeypatch):
    monkeypatch.setenv("BUSINESS_POSTAL_ADDRESS", "Permit Packets, 123 Main St, El Cajon, CA 92020")
    monkeypatch.setenv("CREDITS_SECRET", "test-credits-secret")
    monkeypatch.setenv("REVIEW_URL", "https://reviews.example.com/permit")
    monkeypatch.setenv("PUBLIC_BASE_URL", "https://permits.example.com")
    monkeypatch.delenv("CRON_SECRET", raising=False)


@pytest.fixture
def outbox(monkeypatch):
    sent = []
    monkeypatch.setattr(emails, "send", lambda to, subject, text, html: sent.append((to, subject, text, html)) or True)
    return sent


def _parse(iso: str) -> datetime.datetime:
    value = datetime.datetime.fromisoformat(iso)
    if value.tzinfo is None:
        value = value.replace(tzinfo=datetime.timezone.utc)
    return value.astimezone(datetime.timezone.utc)


def make_order(source: str = "checkout", email: str = "buyer@example.com") -> dict:
    return orders.create_order(
        customer_email=email, tier="instant_packet", job_slug="ev-charger",
        address="123 Main St, El Cajon, CA 92020", jurisdiction_key="el-cajon-ca",
        payload={"city": "El Cajon", "state": "CA"}, source=source)


def at(order: dict, **kw) -> datetime.datetime:
    return _parse(order["created_at"]) + datetime.timedelta(**kw)


def subjects(outbox) -> list[str]:
    return [subject for _, subject, *_ in outbox]


def test_preview_followups_fire_once_at_the_right_age(outbox, env):
    order = make_order(source="preview_saved")
    assert followups.run(now=at(order, hours=1, seconds=1)) == {"preview_1h": 1}
    assert subjects(outbox) == ["Your permit packet preview is saved"]
    followups.run(now=at(order, hours=1, seconds=5))  # not again at the same age
    assert len(outbox) == 1
    assert followups.run(now=at(order, hours=24, seconds=1)) == {"preview_24h": 1}
    assert "What happens after you download" in subjects(outbox)
    assert followups.run(now=at(order, hours=72, seconds=1)) == {"preview_72h": 1}
    assert "Launch pricing ends Dec 31" in subjects(outbox)
    assert len(outbox) == 3


def test_checkout_followups_and_the_pay_link(outbox, env):
    order = make_order(source="checkout")
    assert followups.run(now=at(order, hours=1, seconds=1)) == {"checkout_1h": 1}
    to, subject, text, html = outbox[0]
    assert subject == "Your checkout is still open"
    assert f"/api/orders/{order['access_token']}/pay" in text
    assert followups.run(now=at(order, hours=24, seconds=1)) == {"checkout_24h": 1}
    assert "Full refund if you ask before downloading your clean packet." in outbox[1][2]


def test_followups_stop_after_the_email_pays(outbox, env):
    unpaid = make_order(source="preview_saved")
    paid = make_order(source="checkout")
    orders.set_status(paid["id"], "paid")  # this email has paid since the preview order was saved
    followups.run(now=at(unpaid, hours=72, seconds=1))
    assert outbox == []


def test_opted_out_emails_are_skipped(outbox, env):
    order = make_order(source="preview_saved")
    orders.add_optout(order["customer_email"])
    followups.run(now=at(order, hours=72, seconds=1))
    assert outbox == []


def test_no_marketing_goes_out_without_business_postal_address(outbox, env, monkeypatch, caplog):
    monkeypatch.delenv("BUSINESS_POSTAL_ADDRESS", raising=False)
    order = make_order(source="preview_saved")
    with caplog.at_level("WARNING", logger="permit_packets"):
        result = followups.run(now=at(order, hours=72, seconds=1))
    assert result == {} and outbox == []
    assert "BUSINESS_POSTAL_ADDRESS" in caplog.text


def test_72h_email_stops_after_dec_31_2026(outbox, env):
    order = make_order(source="preview_saved")
    orders.record_email_event(order["id"], "preview_1h", at(order, hours=1))
    orders.record_email_event(order["id"], "preview_24h", at(order, hours=24))
    after = datetime.datetime(2027, 1, 2, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert followups.run(now=after) == {} and outbox == []
    before = datetime.datetime(2026, 12, 30, 0, 0, 0, tzinfo=datetime.timezone.utc)
    assert followups.run(now=before) == {"preview_72h": 1}


def test_review_fires_after_seven_days(outbox, env):
    order = make_order(source="checkout", email="reviewer@example.com")
    orders.set_status(order["id"], "paid")
    orders.mark_downloaded(order["id"])
    downloaded = orders.get_by_id(order["id"])["downloaded_at"]
    result = followups.run(now=_parse(downloaded) + datetime.timedelta(days=7, seconds=1))
    assert result == {"review_7d": 1}
    assert "How did your permit go?" in subjects(outbox)
    followups.run(now=_parse(downloaded) + datetime.timedelta(days=10))  # recorded, not sent twice
    assert len(outbox) == 1


def test_review_is_skipped_without_review_url(outbox, env, monkeypatch):
    monkeypatch.delenv("REVIEW_URL", raising=False)
    order = make_order(source="checkout")
    orders.set_status(order["id"], "paid")
    orders.mark_downloaded(order["id"])
    downloaded = orders.get_by_id(order["id"])["downloaded_at"]
    assert followups.run(now=_parse(downloaded) + datetime.timedelta(days=8)) == {}
    assert outbox == []


def test_followups_carry_the_unsubscribe_link_and_postal_address(outbox, env):
    order = make_order(source="checkout")
    followups.run(now=at(order, hours=1, seconds=1))
    _, _, text, html = outbox[0]
    assert "email/unsubscribe?token=" in text and "email/unsubscribe?token=" in html
    assert "123 Main St, El Cajon, CA 92020" in text


def test_cron_requires_the_secret(client, env, monkeypatch):
    monkeypatch.setenv("CRON_SECRET", "the-secret")
    assert client.post("/api/cron/emails").status_code == 401
    assert client.post("/api/cron/emails", headers={"X-Cron-Secret": "wrong"}).status_code == 401
    assert client.post("/api/cron/emails", headers={"X-Cron-Secret": "the-secret"}).status_code == 200
    monkeypatch.delenv("CRON_SECRET")
    assert client.post("/api/cron/emails", headers={"X-Cron-Secret": "the-secret"}).status_code == 401


def test_unsubscribe_page_adds_an_optout(client, env):
    token = emails.unsubscribe_token("Buyer@Example.com")
    response = client.get(f"/email/unsubscribe?token={token}")
    assert response.status_code == 200 and "noindex" in response.text
    assert orders.is_opted_out("buyer@example.com")
    bad = client.get("/email/unsubscribe?token=nope")
    assert bad.status_code == 200 and not orders.is_opted_out("nope@example.com")