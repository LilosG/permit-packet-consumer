"""The importer's generated block is replaced, not appended again."""
import importlib.util
from pathlib import Path

from permit_packets.jurisdictions import KNOWN


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "permit_packets" / "jurisdictions" / "atlanta_ga.py"


def _load_importer():
    spec = importlib.util.spec_from_file_location("import_evidence_under_test", ROOT / "tools" / "import_evidence.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


IMPORTER = _load_importer()


def _atlanta_inputs():
    atlanta = next(j for j in KNOWN.values() if j.key == "atlanta-ga")
    fields = {"who_may_pull": atlanta.who_may_pull}
    checklists = {"ev_charger": list(atlanta.checklists["ev_charger"].items)}
    return atlanta, fields, checklists


def _without_block(source: str) -> str:
    marker = IMPORTER.VERIFIED_MARKER
    if marker not in source:
        return source.rstrip()
    return source[:source.index(marker)].rstrip()


def test_rewrite_factory_is_idempotent():
    atlanta, fields, checklists = _atlanta_inputs()
    first = IMPORTER.rewrite_factory(MODULE_PATH.read_text(), "ATLANTA", atlanta, fields, checklists)
    second = IMPORTER.rewrite_factory(first, "ATLANTA", atlanta, fields, checklists)
    assert first == second
    assert first.count(IMPORTER.VERIFIED_MARKER) == 1


def test_rewrite_factory_on_a_module_without_a_block():
    atlanta, fields, checklists = _atlanta_inputs()
    source = _without_block(MODULE_PATH.read_text())
    assert IMPORTER.VERIFIED_MARKER not in source
    first = IMPORTER.rewrite_factory(source, "ATLANTA", atlanta, fields, checklists)
    second = IMPORTER.rewrite_factory(first, "ATLANTA", atlanta, fields, checklists)
    assert first == second
    assert first.count(IMPORTER.VERIFIED_MARKER) == 1
