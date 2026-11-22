"""Stage 4: WebApplication free Offer schema, 7th NEC conduit-fill calculator, and 4 new commercial/DIY guides."""
import json
import re
import pytest
from fastapi.testclient import TestClient
import app as app_module
from permit_packets import calculators as calc


@pytest.fixture(scope="module")
def client():
    return TestClient(app_module.app)


def test_webapp_schema_includes_free_offer(client):
    html = client.get("/tools/conduit-fill-trench-depth-calculator/").text
    blocks = [json.loads(b) for b in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
    app_schema = next(b for b in blocks if b["@type"] == "WebApplication")
    assert app_schema["offers"]["price"] == "0"
    assert app_schema["offers"]["priceCurrency"] == "USD"


def test_conduit_fill_calculator_math():
    res = calc.conduit_fill_trench({"wire_size": 6, "conductor_count": 2, "ground_size": 10, "conduit_type": 0, "underground": 1})
    assert res["status"] == "ok"
    assert res["conduit"] == '3/4"'
    assert "18 inches" in res["rows"][3][1]
