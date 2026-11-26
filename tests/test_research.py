"""tools/research.py: only quotes found word for word on the fetched page and confirmed by the check are kept."""
import importlib.util
from pathlib import Path

import yaml

SPEC = importlib.util.spec_from_file_location("research", Path(__file__).resolve().parent.parent / "tools" / "research.py")
rs = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rs)

PAGE = ("Electrical Permits. A homeowner may obtain an electrical permit for work on a single-family dwelling they own "
        "and occupy. An electrical permit is required to install an electric vehicle charging station. Plans are not "
        "required for residential electrical service upgrades up to 200 amps. The City enforces the 2023 National "
        "Electrical Code effective January 1, 2025.")
URL = "https://www.example-city.gov/electrical-permits"


def test_parse_json_accepts_fenced_and_plain_replies():
    assert rs.parse_json('```json\n{"a": 1}\n```') == {"a": 1}
    assert rs.parse_json('Sure: {"b": [2]} done') == {"b": [2]}
    assert rs.parse_json("no json here") == {}


def test_official_sources_are_decided_in_code():
    houston = frozenset({"houstonpermittingcenter.org"})
    assert rs.official("https://www.houstonpermittingcenter.org/hpwcode1056", houston)
    assert not rs.official("https://www.houstonpermittingcenter.org/hpwcode1056")  # not that city's domain
    assert rs.official("https://www.plano.gov/692/Building-Inspections")
    assert rs.official("https://codelibrary.amlegal.com/codes/ftworth/latest/overview")
    assert rs.official("https://library.municode.com/fl/tampa/codes/code_of_ordinances")
    assert not rs.official("https://www.nfpa.org/education-and-research/codes-adoption")
    assert not rs.official("https://permitmint.com/permits/texas/dallas/ev_charger/")
    assert not rs.official("https://www.google.com/search?q=permit")
    assert not rs.official("https://search.houstontx.gov/texis/search/x")


def test_gaps_lists_only_what_is_not_verified(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "VERIFIED", tmp_path)
    (tmp_path / "x-city.json").write_text(
        '{"who_may_file": {"ok": true, "owner_may_file": true}, "code_edition": {"ok": true},'
        ' "jobs": {"ev_charger": {"permit_required": {"ok": true, "value": "yes"},'
        ' "plans_required_single_family": {"ok": true, "value": "unknown"}}}}')
    missing = rs.gaps("x-city")
    assert "who_may_file" not in missing and "code_edition" not in missing
    assert "ev_charger.permit_required" not in missing and "ev_charger.plans_required" in missing
    assert "generator.permit_required" in missing
    assert len(rs.gaps("never-researched")) == 2 + 2 * len(rs.JOBS)


def test_evidence_file_matches_the_importer_schema():
    doc = rs.to_evidence("x-city", "X", "CA", [
        ("who_may_file", {"value": True, "conditions": "owner-occupied", "quote": "q1  text", "url": URL}),
        ("code_edition", {"value": "2023 NEC", "effective_date": "2025-01-01", "quote": "q2", "url": URL}),
        ("ev_charger.plans_required", {"value": "No", "conditions": "none", "quote": "q3", "url": URL}),
    ])
    assert doc["who_may_file"] == {"owner_may_file": True, "conditions": "owner-occupied", "quote": "q1 text", "url": URL}
    assert doc["code_edition"]["value"] == "2023 NEC"
    assert doc["jobs"]["ev_charger"]["plans_required_single_family"]["value"] == "no"


def test_a_city_run_keeps_only_verified_and_supported_quotes(tmp_path, monkeypatch):
    monkeypatch.setattr(rs, "EVIDENCE", tmp_path)
    monkeypatch.setattr(rs, "ROOT", tmp_path)
    monkeypatch.setattr(rs, "gaps", lambda key: ["who_may_file", "code_edition", "ev_charger.permit_required",
                                                  "service_upgrade.plans_required", "generator.plans_required"])
    monkeypatch.setattr(rs, "find_pages", lambda *a, **k: [URL])
    monkeypatch.setattr(rs, "fetch", lambda url: PAGE)
    monkeypatch.setattr(rs, "fetch_in_browser", lambda urls: {})
    monkeypatch.setattr(rs, "crawl_links", lambda url, domains, limit=15: [])
    monkeypatch.setattr(rs, "extract", lambda *a, **k: {"facts": [
        {"fact": "who_may_file", "value": True, "conditions": "owner-occupied",
         "quote": "A homeowner may obtain an electrical permit for work on a single-family dwelling they own and occupy.",
         "url": URL},
        {"fact": "ev_charger.permit_required", "value": "yes",
         "quote": "An electrical permit is required to install an electric vehicle charging station.", "url": URL},
        {"fact": "service_upgrade.plans_required", "value": "no",
         "quote": "Plans are not required for residential electrical service upgrades up to 200 amps.", "url": URL},
        {"fact": "generator.plans_required", "value": "yes",            # invented: not on the page
         "quote": "Plans are required for all standby generators in the city.", "url": URL},
        {"fact": "code_edition", "value": "2023 NEC",                    # on the page, but the check rejects it
         "quote": "The City enforces the 2023 National Electrical Code effective January 1, 2025.", "url": URL},
    ]})
    seen_context = []
    monkeypatch.setattr(rs, "judge", lambda model, city, fact, item, context="":
                        (seen_context.append(context) or fact != "code_edition", "test"))

    result = rs.research_city("san-diego-ca", "m", "j")

    found = {f for f, _, _ in result["accepted"]}
    assert found == {"who_may_file", "ev_charger.permit_required", "service_upgrade.plans_required"}
    reasons = dict(result["rejected"])
    assert "word for word" in reasons["generator.plans_required"]
    assert "check failed" in reasons["code_edition"]
    written = yaml.safe_load((tmp_path / result["file"]).read_text())
    assert written["jurisdiction_key"] == "san-diego-ca"
    assert written["who_may_file"]["owner_may_file"] is True
    assert "generator" not in written["jobs"]
    assert all("Electrical Permits" in c for c in seen_context)  # the check sees the page around the quote


def test_context_around_finds_the_quote_in_the_page():
    quote = "Plans are not required for residential electrical service upgrades up to 200 amps."
    around = rs.context_around(PAGE, quote, chars=40)
    assert quote in around and len(around) < len(PAGE)
    assert rs.context_around(PAGE, "words that are not on the page at all") == ""


def test_pages_are_ranked_per_group():
    pages = {"https://a.gov/solar": "solar photovoltaic battery storage permit " * 5,
             "https://a.gov/owner": "homeowner affidavit owner occupied " * 5}
    assert list(rs.rank_pages(pages, rs.GROUP_WORDS["generator_and_solar"]))[0] == "https://a.gov/solar"
    assert list(rs.rank_pages(pages, rs.GROUP_WORDS["filing_and_code"]))[0] == "https://a.gov/owner"


def test_every_fact_is_in_exactly_one_group():
    grouped = [f for facts in rs.GROUPS.values() for f in facts]
    assert sorted(grouped) == sorted(rs.gaps("never-researched")) and len(grouped) == len(set(grouped))


def test_the_importer_verifies_what_the_research_tool_writes():
    spec = importlib.util.spec_from_file_location("ie", Path(__file__).resolve().parent.parent / "tools" / "import_evidence.py")
    ie = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ie)
    doc = rs.to_evidence("x-city", "X", "CA", [
        ("who_may_file", {"value": True, "conditions": "none", "url": URL,
                          "quote": "A homeowner may obtain an electrical permit for work on a single-family dwelling"}),
        ("service_upgrade.plans_required", {"value": "no", "conditions": "up to 200 A", "url": URL,
                                            "quote": "Plans are not required for residential electrical service upgrades"}),
    ])
    doc["jobs"] = ie.resolve_same_as(doc["jobs"])
    stats = {"seen": set(), "good": set(), "rewrites": set()}
    ie.verify_file(doc, [URL], {URL: {"text": ie.normalize(PAGE), "error": ""}}, stats)
    assert doc["who_may_file"]["ok"] is True
    assert doc["jobs"]["service_upgrade"]["plans_required_single_family"]["ok"] is True
    assert ie.known_value(doc["jobs"]["service_upgrade"]["plans_required_single_family"])
