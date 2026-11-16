import pytest


@pytest.fixture(autouse=True)
def _no_mapbox_token_unless_a_test_sets_one(monkeypatch):
    """A developer's own MAPBOX_TOKEN must not change which service a test talks to."""
    monkeypatch.delenv("MAPBOX_TOKEN", raising=False)


@pytest.fixture(autouse=True)
def _no_rate_limits_unless_a_test_sets_them(monkeypatch):
    """The suite makes far more calls than one visitor would; test_rate_limit.py turns the limits back on."""
    for bucket in ("SUGGEST", "PROPERTY", "PREVIEW"):
        monkeypatch.setenv(f"RATE_LIMIT_{bucket}", "0")
