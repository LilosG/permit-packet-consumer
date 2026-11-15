import pytest


@pytest.fixture(autouse=True)
def _no_mapbox_token_unless_a_test_sets_one(monkeypatch):
    """A developer's own MAPBOX_TOKEN must not change which service a test talks to."""
    monkeypatch.delenv("MAPBOX_TOKEN", raising=False)
