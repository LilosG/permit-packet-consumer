"""Each client signs in with their own password and sees only their own cities, logo and job types."""
import json
import os

import pytest
from fastapi.testclient import TestClient

import app as app_module
from app import app
from permit_packets.clients import ALL_JOB_TYPES, CLIENTS, Client
from permit_packets.jurisdictions import KNOWN
from tests.packet_helpers import complete_inputs, page_texts

PASSWORDS = {key: f"pw-{key}-0123456789" for key in CLIENTS if key != "demo"}
CITIES = {"erke": "nashville-tn", "elc": "san-francisco-ca", "thee-electrician": "san-francisco-ca", "jbee": "mesa-az"}
LOGOS = {"erke": "erke.png", "elc": "elc.png", "thee-electrician": "thee.png", "jbee": "jbee.png"}
BY_KEY = {j.key: j for j in KNOWN.values()}
EXTRA_CITIES = {"jbee": ("chandler-az",)}
OTHER = {"erke": "mesa-az", "elc": "nashville-tn", "thee-electrician": "mesa-az", "jbee": "san-francisco-ca"}


@pytest.fixture(autouse=True)
def passwords(monkeypatch):
    monkeypatch.setenv("CLIENT_PASSWORDS", json.dumps(PASSWORDS))
    monkeypatch.setenv("DEMO_PASSWORD", "demo-password")


def sign_in(password: str) -> TestClient:
    session = TestClient(app)
    assert session.post("/api/signin", json={"password": password}).status_code == 200
    return session


def payload(city_key: str, job_type: str = "ev_charger") -> dict:
    return complete_inputs(job_type, BY_KEY[city_key])


def text_of(pdf_b64: str) -> str:
    import base64
    return "\n".join(page_texts(base64.b64decode(pdf_b64)))


def test_the_five_clients_are_set_up():
    assert set(CLIENTS) == {"demo", *PASSWORDS}
    for key, city in CITIES.items():
        client = CLIENTS[key]
        assert client.jurisdiction_keys[0] == city
        assert client.jurisdiction_keys == (city,) + EXTRA_CITIES.get(key, ())
        assert client.job_types == ALL_JOB_TYPES
        assert client.logo == LOGOS[key]
        assert client.company_name and client.website.startswith("https://")


def test_a_wrong_password_is_refused():
    assert TestClient(app).post("/api/signin", json={"password": "nope"}).status_code == 401


@pytest.mark.parametrize("key", CITIES)
def test_client_sees_only_their_cities_logo_and_all_job_types(key):
    session = sign_in(PASSWORDS[key])
    info = session.get("/api/client").json()
    assert info["key"] == key and info["demo"] is False
    assert [c["key"] for c in info["cities"]] == [CITIES[key], *EXTRA_CITIES.get(key, ())]
    assert info["company_name"] == CLIENTS[key].company_name
    assert info["logo"] == (f"/assets/logos/{LOGOS[key]}" if LOGOS[key] else "")
    types = [t["key"] for t in session.get("/api/job-types").json()["job_types"]]
    assert types == list(ALL_JOB_TYPES)


@pytest.mark.parametrize("key", CITIES)
def test_client_gets_403_for_another_city(key):
    session = sign_in(PASSWORDS[key])
    other = payload(OTHER[key])
    assert session.post("/api/jobs/ev-charger/packet", json=other).status_code == 403
    assert session.post("/api/jobs/ev-charger/documents", json=other).status_code == 403
    unknown = {**payload(CITIES[key]), "jurisdiction_key": "general", "city": "Nowhere", "state": "ZZ"}
    assert session.post("/api/jobs/ev-charger/packet", json=unknown).status_code == 403


@pytest.mark.parametrize("key", CITIES)
def test_client_packet_has_no_demo_marks_and_names_the_company(key):
    session = sign_in(PASSWORDS[key])
    response = session.post("/api/jobs/ev-charger/packet", json=payload(CITIES[key]))
    assert response.status_code == 200
    text = text_of(response.json()["pdf"])
    assert "DEMO" not in text
    assert "NOT FOR SUBMISSION" not in text


def test_demo_login_keeps_its_demo_marks_and_every_city():
    session = sign_in("demo-password")
    info = session.get("/api/client").json()
    assert info["demo"] is True
    assert {c["key"] for c in info["cities"]} == set(BY_KEY)
    response = session.post("/api/jobs/ev-charger/packet", json=payload("oro-valley-az"))
    assert response.status_code == 200
    assert "DEMO PACKET: NOT FOR SUBMISSION" in text_of(response.json()["pdf"])


def test_a_session_cannot_be_moved_to_another_client():
    session = sign_in(PASSWORDS["erke"])
    cookie = session.cookies.get("permit_demo_session")
    expires, _, rest = cookie.partition(".")
    forged = f"{expires}.demo.{rest.partition('.')[2]}"
    other = TestClient(app)
    other.cookies.set("permit_demo_session", forged)
    assert other.get("/api/job-types").status_code == 401


def test_overrides_beat_the_city_default():
    sf = BY_KEY["san-francisco-ca"]
    plain = Client("x", "X", ())
    assert plain.sheet_size_for(sf) == sf.sheet_size and plain.single_pdf_only_for(sf) == sf.single_pdf_only
    assert Client("x", "X", (), sheet_size="tabloid").sheet_size_for(sf) == "tabloid"
    assert Client("x", "X", (), single_pdf_only=not sf.single_pdf_only).single_pdf_only_for(sf) is (not sf.single_pdf_only)


def test_bad_client_passwords_json_is_a_503(monkeypatch):
    monkeypatch.setenv("CLIENT_PASSWORDS", "not json")
    assert TestClient(app).post("/api/signin", json={"password": "x"}).status_code == 503


def _title(pdf_b64: str) -> str:
    import base64
    import pypdfium2
    document = pypdfium2.PdfDocument(base64.b64decode(pdf_b64))
    try:
        return document.get_metadata_dict().get("Title", "")
    finally:
        document.close()


@pytest.mark.parametrize("job_type,slug", [
    ("ev_charger", "ev-charger"), ("service_upgrade", "service-upgrade"),
    ("subpanel", "subpanel"), ("appliance_circuit", "appliance-circuit"),
])
def test_demo_in_titles_and_zip_names_is_for_the_demo_login_only(job_type, slug):
    client_session, demo_session = sign_in(PASSWORDS["erke"]), sign_in("demo-password")
    mine = client_session.post(f"/api/jobs/{slug}/packet", json=payload("nashville-tn", job_type)).json()
    demo = demo_session.post(f"/api/jobs/{slug}/packet", json=payload("nashville-tn", job_type)).json()
    assert "demo" not in _title(mine["pdf"]).lower()
    assert _title(demo["pdf"]).endswith("(demo)")
    mine_zip = client_session.post(f"/api/jobs/{slug}/documents", json=payload("nashville-tn", job_type))
    demo_zip = demo_session.post(f"/api/jobs/{slug}/documents", json=payload("nashville-tn", job_type))
    assert "demo" not in mine_zip.headers["content-disposition"]
    assert mine_zip.headers["content-disposition"].endswith('-documents.zip"')
    assert "-demo.zip" in demo_zip.headers["content-disposition"]


def _sheet_size(response) -> str:
    return response.json()["sheet_size"]


def test_request_sheet_size_overrides_client_and_city_for_client_logins(monkeypatch):
    session = sign_in(PASSWORDS["elc"])  # San Francisco's default is its own sheet size
    city_default = BY_KEY["san-francisco-ca"].sheet_size
    other = "letter" if city_default == "tabloid" else "tabloid"
    base = payload("san-francisco-ca")
    base.pop("sheet_size", None)
    assert _sheet_size(session.post("/api/jobs/ev-charger/packet", json=base)) == city_default
    assert _sheet_size(session.post("/api/jobs/ev-charger/packet", json={**base, "sheet_size": other})) == other
    # A client override beats the city default, and the request still beats the client override.
    monkeypatch.setitem(CLIENTS, "elc", Client(**{**CLIENTS["elc"].__dict__, "sheet_size": other}))
    assert _sheet_size(session.post("/api/jobs/ev-charger/packet", json=base)) == other
    assert _sheet_size(session.post("/api/jobs/ev-charger/packet", json={**base, "sheet_size": city_default})) == city_default


def test_address_suggestions_are_limited_to_the_signed_in_clients_cities_and_the_demo_gets_all(monkeypatch):
    asked = []
    monkeypatch.setattr(app_module, "suggest_addresses", lambda text, client=None, areas=None: asked.append(
        [area.key for area in areas]) or ["suggested"])
    body = {"text": "710 Steiner"}
    assert sign_in(PASSWORDS["elc"]).post("/api/property/suggest", json=body).json() == {"suggestions": ["suggested"]}
    sign_in(PASSWORDS["jbee"]).post("/api/property/suggest", json=body)
    sign_in("demo-password").post("/api/property/suggest", json=body)
    assert asked[0] == ["san-francisco-ca"]
    assert asked[1] == ["mesa-az", "chandler-az"]
    assert asked[2] == [j.key for j in KNOWN.values()]
    assert all(j.bbox and j.center for j in KNOWN.values())
