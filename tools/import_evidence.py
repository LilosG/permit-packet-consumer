"""Verify evidence/*.yaml against the cited pages, then update the city modules.

    python tools/import_evidence.py

Writes evidence/verified/<key>.json and evidence/verified/REPORT.md. A quote counts only when it appears,
letters and digits only, in the text of a fetched page. Needs pyyaml, httpx and pdftotext.
"""
from __future__ import annotations

import argparse
import ast
import copy
import datetime
import hashlib
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from urllib.parse import urlsplit

import httpx
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/ (browser_fetch)

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
OUT = EVIDENCE / "verified"
CACHE = ROOT / ".cache" / "evidence_fetch"
OCR_SNAPSHOTS = EVIDENCE / "ocr"  # committed OCR text of scanned PDFs, named <sha256 of url>.txt
MODULES = ROOT / "permit_packets" / "jurisdictions"
TODAY = datetime.date.today().isoformat()
VERIFIED_MARKER = "# Verified from evidence/verified/ by tools/import_evidence.py."
JOBS = ("ev_charger", "service_upgrade", "subpanel", "appliance_circuit", "generator", "solar_storage")
BLOCKS = ("permit_required", "plans_required_single_family", "load_calculation", "sheet_requirements")
LISTS = ("requirements", "local_rules")
COMMON_SECTIONS = {"fault_current", "panel_details", "egc_size", "burial", "by_others", "utility_id", "packet_gap"}
ALLOWED_SECTIONS = {
    "ev_charger": COMMON_SECTIONS | {"application", "equipment", "load", "one_line", "panel_schedule", "review",
                                     "site_plan", "hoa", "ventilation"},
    "service_upgrade": COMMON_SECTIONS | {"application", "equipment", "load", "one_line", "panel_schedule", "review",
                                          "site_plan", "utility", "gec", "surge", "emergency_disconnect"},
    "subpanel": COMMON_SECTIONS | {"application", "equipment", "load", "one_line", "panel_schedule", "review",
                                   "site_plan", "feeder"},
    "appliance_circuit": COMMON_SECTIONS | {"application", "equipment", "load", "one_line", "panel_schedule", "review",
                                            "site_plan", "pool_bonding"},
    "generator": COMMON_SECTIONS | {"application", "equipment", "load", "one_line", "panel_schedule", "review",
                                    "site_plan", "fuel", "equipment_layout"},
    "solar_storage": COMMON_SECTIONS | {"application", "equipment", "load", "one_line", "panel_schedule", "review",
                                        "site_plan", "labels", "general_notes"},
}
UNKNOWN = "unknown"
SKIP_QUOTES = {"", UNKNOWN, "not_stated"}
HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/126.0 Safari/537.36"),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,application/pdf,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
}


# ---------------------------------------------------------------- load

def resolve_same_as(jobs: dict) -> dict:
    """Copy the named job's block wherever a block says same_as: <job>. Local keys win."""
    def block(job: str, name: str, seen: frozenset):
        node = (jobs.get(job) or {}).get(name)
        if not isinstance(node, dict) or "same_as" not in node:
            return copy.deepcopy(node)
        if job in seen:
            return None  # circular
        base = block(node["same_as"], name, seen | {job})
        local = {k: v for k, v in node.items() if k != "same_as"}
        return {**base, **local} if isinstance(base, dict) else base

    resolved = {job: {name: block(job, name, frozenset()) for name in (jobs[job] or {})} for job in jobs}
    return {job: {k: v for k, v in found.items() if v is not None} for job, found in resolved.items()}


def load() -> dict[str, list[tuple[str, dict]]]:
    cities = defaultdict(list)
    for path in sorted(EVIDENCE.glob("*.yaml")):
        if path.name == "section_overrides.yaml":
            continue
        data = yaml.safe_load(path.read_text()) or {}
        key = data.get("jurisdiction_key") or path.name.split(".")[0]
        data["jobs"] = resolve_same_as(data.get("jobs") or {})
        cities[key].append((path.name, data))
    return cities


def walk(node):
    if isinstance(node, dict):
        yield node
        for value in node.values():
            yield from walk(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk(value)


# ---------------------------------------------------------------- fetch and match

def is_web(url) -> bool:
    return isinstance(url, str) and url.startswith(("http://", "https://"))


def rejected(url: str) -> bool:
    parts = urlsplit(url)
    return (parts.hostname or "").startswith("search.") or "/search" in parts.path.lower()


def normalize(text: str) -> str:
    return re.sub(r"[^a-z0-9]", "", text.lower())


MIN_TEXT_CHARS = 300  # below this, a PDF (or a cached page) has no usable text layer
_ocr_warned = False


def ocr_pdf(path: str) -> str:
    """Normalized OCR text of a scanned PDF (pdftoppm + tesseract). Empty if either tool is missing."""
    global _ocr_warned
    if not (shutil.which("pdftoppm") and shutil.which("tesseract")):
        if not _ocr_warned:
            print("warning: scanned PDF found but pdftoppm/tesseract are not installed (brew install tesseract poppler)")
            _ocr_warned = True
        return ""
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "200", "-png", path, f"{tmp}/page"], capture_output=True, timeout=300)
        pages = sorted(Path(tmp).glob("page*.png"))
        out = [subprocess.run(["tesseract", str(png), "-"], capture_output=True, timeout=120).stdout.decode("utf-8", "replace")
               for png in pages]
    return normalize(" ".join(out))


def to_text(body: bytes, content_type: str) -> str:
    if body[:1024].lstrip().startswith(b"%PDF") or "application/pdf" in content_type:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            handle.write(body)
            handle.flush()
            texts = []
            for flags in ([], ["-layout"]):
                done = subprocess.run(["pdftotext", *flags, handle.name, "-"], capture_output=True, timeout=120)
                texts.append(normalize(done.stdout.decode("utf-8", "replace")))
            if max(len(t) for t in texts) < MIN_TEXT_CHARS:  # a scanned PDF with no text layer
                texts.append(ocr_pdf(handle.name))
        return "\n".join(texts)
    charset = re.search(r"charset=([\w-]+)", content_type)
    try:
        page = body.decode(charset.group(1) if charset else "utf-8", "replace")
    except LookupError:
        page = body.decode("utf-8", "replace")
    return normalize(html.unescape(re.sub(r"<[^>]*>", " ", page)))


def with_ocr_snapshot(url: str, result: dict) -> dict:
    """A scanned PDF has no text layer: use its committed OCR snapshot when one exists."""
    if len(result.get("text", "")) >= MIN_TEXT_CHARS:
        return result
    snapshot = OCR_SNAPSHOTS / (hashlib.sha256(url.encode()).hexdigest() + ".txt")
    if snapshot.exists():
        return {"text": result.get("text", "") + "\n" + normalize(snapshot.read_text()), "error": ""}
    return result


def fetch(url: str) -> dict:
    """{"text": normalized text, "error": ""}. Successful fetches are cached."""
    return with_ocr_snapshot(url, _fetch(url))


def _fetch(url: str) -> dict:
    """{"text": normalized text, "error": ""}. Successful fetches are cached."""
    cached = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
    if cached.exists():
        result = json.loads(cached.read_text())
        if len(result.get("text", "")) >= MIN_TEXT_CHARS:
            return result  # pages cached with almost no text (e.g. scanned PDFs before OCR) are fetched again
    error = ""
    for _ in range(2):  # one retry
        try:
            with httpx.Client(headers=HEADERS, timeout=30, follow_redirects=True) as client:
                response = client.get(url)
            if response.status_code >= 400:
                error = f"HTTP {response.status_code}"
                continue
            result = {"text": to_text(response.content, response.headers.get("content-type", "")), "error": ""}
            cached.write_text(json.dumps(result))
            return result
        except Exception as exc:  # any failure means the page cannot verify anything
            error = type(exc).__name__
    return {"text": "", "error": error}


# ---------------------------------------------------------------- verify

def checkable(node: dict) -> bool:
    quote = node.get("quote")
    return "quote" in node and "url" in node and isinstance(quote, str) and quote.strip().lower() not in SKIP_QUOTES


def find_url(node: dict, candidates: list[str], pages: dict) -> str | None:
    quote = normalize(node["quote"])
    if not quote:
        return None
    cited = node.get("url")
    ordered = ([cited] if cited in pages else []) + [u for u in candidates if u != cited]
    return next((u for u in ordered if any(quote in part for part in pages[u]["text"].split("\n"))), None)


def fail(node: dict) -> None:
    for name in node:
        if name in ("value", "quote", "url", "method", "city_worksheet", "ev_charger_load_factor", "sheet_size",
                    "copies_or_format", "signature_or_stamp", "owner_may_file", "conditions", "effective_date"):
            node[name] = UNKNOWN


def verify_file(data: dict, candidates: list[str], pages: dict, stats: dict) -> None:
    """Check every quoted object in place. ok=True marks the ones that verified."""
    for node in list(walk(data)):
        node.pop("ok", None)
        if not checkable(node):
            continue
        original = node["url"]
        found = find_url(node, candidates, pages)
        stats["seen"].add((node["quote"], str(original)))
        if found:
            stats["good"].add((node["quote"], str(original)))
            if found != original:
                stats["rewrites"].add((str(original), found))
            node["url"] = found
            node["ok"] = True
    # Whatever did not verify (including quote "unknown") becomes unknown; unverified list entries are dropped.
    for node in list(walk(data)):
        for name in ("code_edition", "who_may_file", *BLOCKS):
            block = node.get(name)
            if isinstance(block, dict) and not block.get("ok"):
                fail(block)
        for name in ("local_rules", "requirements"):
            if isinstance(node.get(name), list):
                node[name] = [item for item in node[name] if isinstance(item, dict) and item.get("ok")]


def ok(block) -> bool:
    return isinstance(block, dict) and bool(block.get("ok"))


def merge(files: list[tuple[str, dict]]) -> dict:
    """Each field comes from the first file where it verifies; unquoted fields from the first file that has them."""
    docs = [data for _, data in files]

    def pick(values):
        present = [v for v in values if v not in (None, "", UNKNOWN, [], {})]
        verified = [v for v in present if ok(v)]
        return copy.deepcopy((verified or present or [next((v for v in values if v is not None), None)])[0])

    def every_verified(values) -> list:
        """The ok=True entries from every file, in file order, de-duplicated by their item text."""
        out, seen = [], set()
        for entries in values:
            for entry in entries or []:
                if not isinstance(entry, dict) or not entry.get("ok"):
                    continue
                text = str(entry.get("item") or entry.get("rule") or "")
                key = " ".join(text.lower().split())
                if key and key not in seen:
                    seen.add(key)
                    out.append(copy.deepcopy(entry))
        return out

    out = {}
    for name in dict.fromkeys(k for d in docs for k in d):
        if name not in ("jobs", "utility", "open_questions"):
            out[name] = pick([d.get(name) for d in docs])
    utilities = [d.get("utility") or {} for d in docs]
    out["utility"] = {"name": pick([u.get("name") for u in utilities]),
                      "requirements": every_verified([u.get("requirements") for u in utilities])}
    out["open_questions"] = list(dict.fromkeys(q for d in docs for q in d.get("open_questions") or []))
    out["jobs"] = {}
    for job in dict.fromkeys(j for d in docs for j in d["jobs"]):
        blocks = [d["jobs"].get(job) or {} for d in docs]
        merged = {name: pick([b.get(name) for b in blocks]) for name in dict.fromkeys(k for b in blocks for k in b)}
        for name in LISTS:
            merged[name] = every_verified([b.get(name) for b in blocks])
        out["jobs"][job] = merged
    return out


def overrides(key: str, data: dict) -> list[str]:
    jobs, notes = data["jobs"], []
    if key == "san-jose-ca":
        block = jobs["subpanel"]["plans_required_single_family"]
        fail(block)
        block.pop("ok", None)
        block["value"] = UNKNOWN
        notes.append("subpanel plans_required_single_family forced to unknown")
    if key == "san-diego-ca":
        for job in ("service_upgrade", "subpanel"):
            jobs[job].setdefault("sheet_requirements", {})["sheet_size"] = "not_stated"
        notes.append("service_upgrade and subpanel sheet_size forced to not_stated")
    if key == "seattle-wa":
        solar = jobs["solar_storage"]
        stale = re.compile(r"\b12(\.0)?\s*-?\s*kw\b", re.I)
        for name in LISTS:
            kept = [i for i in solar[name] if not stale.search(json.dumps(i))]
            if len(kept) != len(solar[name]):
                notes.append(f"dropped {len(solar[name]) - len(kept)} solar {name} stating 12 kW")
            solar[name] = kept
        plans = solar.get("plans_required_single_family") or {}
        if stale.search(json.dumps(plans)):
            fail(plans)
            plans.pop("ok", None)
            notes.append("solar plans_required_single_family stated 12 kW: set unknown")
        if plans.get("ok") and plans.get("value") in (False, "no"):
            fail(plans)  # energy storage always requires plans, so the combined solar/storage job is never no-plan
            plans.pop("ok", None)
            notes.append("solar_storage cannot be no-plan: energy storage always requires plans")
    return notes


def known_value(block) -> bool:
    return ok(block) and block.get("value") not in (None, "", UNKNOWN)


def rules_verified(data: dict) -> bool:
    who = data.get("who_may_file")
    return (ok(who) and isinstance(who.get("owner_may_file"), bool)
            and all(known_value((data["jobs"].get(job) or {}).get(name))
                    for job in JOBS for name in ("permit_required", "plans_required_single_family")))


def unknown_fields(data: dict) -> list[str]:
    found = []

    def scan(node, path):
        if isinstance(node, dict):
            if "quote" in node and "url" in node and not node.get("ok"):
                found.append(path)
                return
            for name, value in node.items():
                scan(value, f"{path}.{name}" if path else name)

    scan({k: data.get(k) for k in ("code_edition", "who_may_file", "jobs")}, "")
    return [p.removeprefix("jobs.") for p in found]


# ---------------------------------------------------------------- update modules

def lit(value) -> str:
    return json.dumps(value, ensure_ascii=False)


def normalized(text: str) -> str:
    return " ".join(str(text).lower().split())


def load_overrides() -> dict[tuple[str, str, str], tuple[str, str]]:
    path = EVIDENCE / "section_overrides.yaml"
    if not path.exists():
        return {}
    out = {}
    for entry in yaml.safe_load(path.read_text()) or []:
        out[(entry["city"], entry["job"], entry["item"])] = (entry["section"], entry.get("who") or "")
    return out


def requirements_for(job: str, block: dict) -> list:
    from permit_packets.jurisdictions import Requirement

    rows, seen = [], set()
    for entry in block.get("requirements") or []:
        item = " ".join(str(entry.get("item", "")).split())
        key = normalized(item)
        if item and key not in seen:
            seen.add(key)
            rows.append(Requirement(item, str(entry.get("section") or "other"), entry.get("url") or ""))
    return rows


def requirement_source(req, indent: str) -> str:
    head = f"{indent}    Requirement({lit(req.item)}, {lit(req.section)}"
    if req.source and req.who:
        return (f"{head},\n{indent}                {lit(req.source)},\n"
                f"{indent}                who={lit(req.who)}),")
    if req.source:
        return f"{head},\n{indent}                {lit(req.source)}),"
    if req.who:
        return f"{head}, who={lit(req.who)}),"
    return f"{head}),"


def items_source(job: str, rows: list, indent: str) -> str:
    from permit_packets.jurisdictions import SURGE_PROTECTION

    lines = []
    for req in rows:
        if req.item == SURGE_PROTECTION.item and req.section == SURGE_PROTECTION.section:
            lines.append(f"{indent}    SURGE_PROTECTION,")
        else:
            lines.append(requirement_source(req, indent))
    if job == "service_upgrade" and not any(req.section == "surge" for req in rows):
        lines.append(f"{indent}    SURGE_PROTECTION,")
    return "(\n" + "\n".join(lines) + f"\n{indent})"


def plan_changes(city, data: dict, overrides: dict | None = None) -> tuple[dict, dict, list[str]]:
    """(keyword -> new value, job -> checklist requirements, report lines for replaced values)."""
    from dataclasses import replace as dataclass_replace

    from permit_packets.jurisdictions import SURGE_PROTECTION

    fields, replaced = {}, []
    who = data.get("who_may_file") or {}
    owner = who.get("owner_may_file") if ok(who) else None
    fields["owner_may_file"] = owner if isinstance(owner, bool) else None
    conditions = who.get("conditions") if ok(who) else None
    if isinstance(conditions, str) and conditions.strip().lower() not in SKIP_QUOTES | {"none"}:
        fields["who_may_pull"] = " ".join(conditions.split())

    no_plan = dict(city.no_plan_jobs)
    for job in JOBS:
        plans = (data["jobs"].get(job) or {}).get("plans_required_single_family")
        if known_value(plans):  # unknown never erases
            if plans["value"] in (False, "no"):
                no_plan[job] = plans["url"]
            else:
                no_plan.pop(job, None)
    fields["no_plan_jobs"] = no_plan

    checklists = {}
    for job in JOBS:
        verified = requirements_for(job, data["jobs"].get(job) or {})
        if not verified:
            continue
        base = list(city.checklist_for(job).items)
        base_keys = {normalized(req.item) for req in base}
        added = [req for req in verified if normalized(req.item) not in base_keys]
        combined = base + added
        if job == "service_upgrade" and not any(req.section == "surge" for req in combined):
            combined.append(SURGE_PROTECTION)
        for index, req in enumerate(combined):
            found = (overrides or {}).get((city.key, job, req.item))
            if found:
                combined[index] = dataclass_replace(req, section=found[0], who=found[1])
        checklists[job] = combined
        replaced.append(f"`checklists[{job}]` ({len(base)} base items + {len(added)} verified city items)")

    # Dates never get erased: set them only when this import verified what they stand for.
    if rules_verified(data):
        fields["permit_rules_verified"] = TODAY
        if all(requirements_for(job, data["jobs"].get(job) or {}) for job in JOBS):
            fields["last_verified"] = TODAY

    for name, value in list(fields.items()):
        old = getattr(city, name)
        if old == value:
            del fields[name]
        elif old not in (None, "", {}):
            replaced.append(f"`{name}`: {old!r} -> {value!r}")

    return fields, checklists, replaced


def add_import(source: str, module: str, names: list[str]) -> str:
    pattern = re.compile(rf"^from {re.escape(module)} import ([^\n(]+)$", re.M)
    match = pattern.search(source)
    if match:
        have = [n.strip() for n in match.group(1).split(",")]
        line = f"from {module} import {', '.join(sorted(set(have) | set(names)))}"
        return source[:match.start()] + line + source[match.end():]
    return f"from {module} import {', '.join(sorted(names))}\n" + source


SOURCE_LABEL = "From the city's published pages"


def checklist_source(rows) -> str:
    return next((req.source for req in rows if req.source), "")


def rewrite_literal(source: str, fields: dict, checklists: dict) -> str:
    """Edit the keyword values inside a module's Jurisdiction(...) call, in place."""
    tree = ast.parse(source)
    constants = {t.id: n.value.value for n in tree.body if isinstance(n, ast.Assign)
                 and isinstance(n.value, ast.Constant) for t in n.targets if isinstance(t, ast.Name)}
    call = next(n.value for n in tree.body if isinstance(n, ast.Assign) and isinstance(n.value, ast.Call)
                and getattr(n.value.func, "id", "") == "Jurisdiction")
    raw = source.encode()
    starts = [0]
    for line in raw.splitlines(keepends=True):
        starts.append(starts[-1] + len(line))

    def span(node):
        return starts[node.lineno - 1] + node.col_offset, starts[node.end_lineno - 1] + node.end_col_offset

    def before_close(node) -> tuple[int, int, str]:
        """Where to add an entry before a dict's closing brace, adding the comma it may need."""
        end = span(node)[1] - 1
        head = raw[:end].rstrip()
        return len(head), end, "" if head.endswith((b",", b"{")) else ","

    keywords = {k.arg: k for k in call.keywords}
    edits, added = [], []
    for name, value in fields.items():
        text = lit(value) if isinstance(value, str) else repr(value)
        if name in keywords:
            edits.append((*span(keywords[name].value), text))
        else:
            added.append(f"    {name}={text},\n")
    if added:
        at = starts[keywords["key"].value.end_lineno]
        edits.append((at, at, "".join(added)))

    if checklists:
        table = keywords["checklists"].value
        entries = {}
        for key, value in zip(table.keys, table.values):
            entries[key.value if isinstance(key, ast.Constant) else constants[key.id]] = value
        new = []
        for job, rows in checklists.items():
            if job in entries:
                parts = {k.arg: k for k in entries[job].keywords}
                edits.append((*span(parts["items"].value), items_source(job, rows, " " * 12)))
                for name, text in (("source_url", lit(checklist_source(rows))), ("source_label", lit(SOURCE_LABEL))):
                    if name in parts:
                        edits.append((*span(parts[name].value), text))
            else:
                code = "\n            code_note=CODE_NOTE," if "CODE_NOTE" in constants else ""
                new.append(f"\n        {lit(job)}: Checklist(\n            items={items_source(job, rows, ' ' * 12)},"
                           f"\n            source_url={lit(checklist_source(rows))},"
                           f"\n            source_label={lit(SOURCE_LABEL)},{code}\n        ),")
        if new:
            start, end, comma = before_close(table)
            edits.append((start, end, comma + "".join(new) + "\n    "))

    for start, end, text in sorted(edits, reverse=True):
        raw = raw[:start] + text.encode() + raw[end:]
    return raw.decode()


def rewrite_factory(source: str, name: str, city, fields: dict, checklists: dict) -> str:
    """A make_city(...) module: layer the verified values over it with dataclasses.replace."""
    lines = source.splitlines(keepends=True)
    for index, line in enumerate(lines):
        if line.rstrip("\r\n") == VERIFIED_MARKER:
            source = "".join(lines[:index]).rstrip()
            break
    args = [f"    {k}={lit(v) if isinstance(v, str) else repr(v)}," for k, v in fields.items()]
    if checklists:
        args.append(f"    checklists={{\n        **{name}.checklists,")
        for job, rows in checklists.items():
            head = f"        {lit(job)}: "
            body = (f"items={items_source(job, rows, ' ' * 12)},\n            source_url={lit(checklist_source(rows))},"
                    f"\n            source_label={lit(SOURCE_LABEL)}")
            if job in city.checklists:
                args.append(f"{head}replace(\n            {name}.checklists[{lit(job)}],\n            {body}),")
            else:
                args.append(f"{head}Checklist(\n            {body},\n            code_note={name}.code_note),")
        args.append("    },")
    return source.rstrip("\n") + f"\n\n{VERIFIED_MARKER}\n{name} = replace(\n    {name},\n" \
        + "\n".join(args) + "\n)\n"


def update_module(city, fields: dict, checklists: dict) -> None:
    if not fields and not checklists:
        return
    path = MODULES / (city.key.replace("-", "_") + ".py")
    source = path.read_text()
    name = city.key.rsplit("-", 1)[0].replace("-", "_").upper()
    factory = "make_city(*(" in source
    updated = rewrite_factory(source, name, city, fields, checklists) if factory \
        else rewrite_literal(source, fields, checklists)
    needed = []
    if checklists:
        needed.append("Requirement")
        if any(job not in city.checklists for job in checklists):
            needed.append("Checklist")
        if "service_upgrade" in checklists:
            from permit_packets.jurisdictions import SURGE_PROTECTION

            if any(req.item == SURGE_PROTECTION.item and req.section == SURGE_PROTECTION.section
                   for req in checklists["service_upgrade"]):
                needed.append("SURGE_PROTECTION")
    if needed:
        updated = add_import(updated, "permit_packets.jurisdictions", needed)
    if factory:
        updated = add_import(updated, "dataclasses", ["replace"])
    ast.parse(updated)
    path.write_text(updated)


# ---------------------------------------------------------------- run

def retry_blocked(pages: dict) -> None:
    """Retry every URL that failed in the thread pool, one at a time, in a real browser."""
    failed = [url for url, result in pages.items() if result["error"]]
    if not failed:
        print("0 blocked URLs retried in a browser, 0 recovered")
        return
    recovered = 0
    try:
        from playwright.sync_api import sync_playwright
    except Exception:
        print(f"{len(failed)} blocked URLs retried in a browser, 0 recovered")
        return
    import browser_fetch
    with sync_playwright() as p:
        browser = browser_fetch.launch(p)
        context = browser.new_context(user_agent=HEADERS["User-Agent"])
        for url in failed:
            try:
                body, ctype = browser_fetch.read_url(context, url)
                result = {"text": to_text(body, ctype), "error": ""}
                if "access denied" in result["text"][:400].lower():
                    continue  # still blocked: keep the original error
                cached = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".json")
                cached.write_text(json.dumps(result))
                pages[url] = with_ocr_snapshot(url, result)
                recovered += 1
            except Exception:  # keep the original error
                continue
        browser.close()
    print(f"{len(failed)} blocked URLs retried in a browser, {recovered} recovered")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="origin/main")
    args = parser.parse_args()

    sys.path.insert(0, str(ROOT))
    cities = load()
    for key in sorted(cities):
        subprocess.run(["git", "checkout", args.base, "--",
                        f"permit_packets/jurisdictions/{key.replace('-', '_')}.py"], check=True, cwd=ROOT)
    from permit_packets.jurisdictions import KNOWN, Jurisdiction
    modules = {j.key: j for j in KNOWN.values()}
    for key in sorted(cities):
        path = MODULES / (key.replace("-", "_") + ".py")
        source = path.read_text()
        if VERIFIED_MARKER not in source:
            continue
        base = source.split(VERIFIED_MARKER, 1)[0].rstrip()
        namespace = {}
        exec(compile(base, str(path), "exec"), namespace)
        modules[key] = next(value for value in namespace.values() if isinstance(value, Jurisdiction))

    missing = sorted(set(cities) - set(modules))
    if missing:
        raise SystemExit(f"No module for: {', '.join(missing)}")
    cited = {key: sorted({n[f] for _, d in files for n in walk(d) for f in ("url", "portal_url")
                          if is_web(n.get(f)) and not rejected(n[f])})
             for key, files in cities.items()}
    wanted = sorted({u for urls in cited.values() for u in urls})
    CACHE.mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=8) as pool:
        pages = dict(zip(wanted, pool.map(fetch, wanted)))
    print(f"{len(wanted)} URLs, {sum(not p['error'] for p in pages.values())} fetched")
    retry_blocked(pages)

    OUT.mkdir(exist_ok=True)
    section_overrides = load_overrides()
    planned, invalid = {}, []
    for key, files in sorted(cities.items()):
        stats = {"seen": set(), "good": set(), "rewrites": set()}
        refused = sorted({n["url"] for _, d in files for n in walk(d)
                          if is_web(n.get("url")) and rejected(n["url"])})
        for _, data in files:
            verify_file(data, cited[key], pages, stats)
        merged = merge(files)
        applied = overrides(key, merged)
        unknown = unknown_fields(merged)
        verified = rules_verified(merged)
        blocked = defaultdict(set)
        for url in cited[key]:
            if pages[url]["error"]:
                blocked[urlsplit(url).hostname].add(pages[url]["error"])
        (OUT / f"{key}.json").write_text(json.dumps(merged, indent=2, ensure_ascii=False, default=str) + "\n")
        fields, checklists, replaced = plan_changes(modules[key], merged, section_overrides)
        for job, requirements in checklists.items():
            for req in requirements:
                if req.section not in ALLOWED_SECTIONS[job] or (req.section == "by_others" and not req.who):
                    invalid.append((key, job, req.section, req.item))
        planned[key] = {
            "city": modules[key], "fields": fields, "checklists": checklists, "replaced": replaced,
            "stats": stats, "refused": refused, "applied": applied, "unknown": unknown,
            "verified": verified, "blocked": blocked,
        }

    if invalid:
        print("Add these to evidence/section_overrides.yaml")
        for city_key, job, section, item in invalid:
            print(f"{city_key} | {job} | {section} | {item}")
        raise SystemExit(1)

    rows, details = [], []
    for key, found in planned.items():
        update_module(found["city"], found["fields"], found["checklists"])
        hosts = ", ".join(f"{h} ({'/'.join(sorted(e))})" for h, e in sorted(found["blocked"].items())) or "none"
        rows.append(f"| {key} | {len(found['stats']['good'])}/{len(found['stats']['seen'])} | "
                    f"{len(found['unknown'])} | {len(found['stats']['rewrites'])} | {hosts} | "
                    f"{found['verified']} |")
        section = [f"## {key}", "", f"Fields set unknown: {', '.join(found['unknown']) or 'none'}", "",
                   "URL rewrites:"]
        section += [f"- {old} -> {new}" for old, new in sorted(found["stats"]["rewrites"])] or ["- none"]
        if found["refused"]:
            section += ["", "Rejected search URLs:", *[f"- {u}" for u in found["refused"]]]
        if found["applied"]:
            section += ["", "Overrides:", *[f"- {n}" for n in found["applied"]]]
        section += ["", "Replaced module values:", *([f"- {r}" for r in found["replaced"]] or ["- none"])]
        details.append("\n".join(section))

    table = ["| City | Quotes verified/total | Fields set unknown | URL rewrites | Blocked hosts | permit_rules_verified |",
             "|---|---|---|---|---|---|", *rows]
    (OUT / "REPORT.md").write_text(f"# Evidence import, {TODAY}\n\n" + "\n".join(table) + "\n\n"
                                   + "\n\n".join(details) + "\n")
    print("\n".join(table))


if __name__ == "__main__":
    main()
