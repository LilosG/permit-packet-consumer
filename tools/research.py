"""Research city permit rules automatically, verify every quote, and (optionally) import and open a PR.

    .venv/bin/python tools/research.py --check
    .venv/bin/python tools/research.py --cities tampa-fl,mesa-az
    .venv/bin/python tools/research.py --cities tampa-fl,mesa-az --import

For each city it researches only the facts still missing (who may file, the code edition, and whether each job needs
a permit and plans), using a web-search model on OpenRouter:
  1. the model finds official pages for the missing facts;
  2. each page is fetched here (a real Chrome window when a site blocks scripts) and its text kept;
  3. the model copies each answer's quote from that text;
  4. a quote counts only if it appears word for word in the fetched text (the importer's own test);
  5. a second, cheap model call checks that the quote itself states the fact and the source is official.
What passes is written to evidence/<city>.auto-<date>.yaml. --import then runs the importer, the city tests, commits to
a branch, opens a PR, waits for CI and merges it.

Needs OPENROUTER_API_KEY (environment or the repo's .env), pyyaml, httpx and playwright (tools/requirements.txt).
"""
from __future__ import annotations

import argparse
import concurrent.futures
import datetime
import hashlib
import html
import json
import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

import httpx
import yaml

ROOT = Path(__file__).resolve().parent.parent
EVIDENCE = ROOT / "evidence"
VERIFIED = EVIDENCE / "verified"
CACHE = ROOT / ".cache" / "research"
REPORTS = EVIDENCE / "research"
TODAY = datetime.date.today().isoformat()
API = "https://openrouter.ai/api/v1"
DEFAULT_MODEL = os.environ.get("RESEARCH_MODEL", "deepseek/deepseek-v4.1-flash")
DEFAULT_JUDGE = os.environ.get("RESEARCH_JUDGE_MODEL", DEFAULT_MODEL)
JOBS = ("ev_charger", "service_upgrade", "subpanel", "appliance_circuit", "generator", "solar_storage")
JOB_NAMES = {
    "ev_charger": "Level 2 EV charger (240 V)", "service_upgrade": "service / main panel upgrade",
    "subpanel": "subpanel", "appliance_circuit": "new 240 V appliance circuit",
    "generator": "standby generator with transfer switch or interlock", "solar_storage": "rooftop solar with battery",
}
UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
NOT_OFFICIAL = ("permitmint", "propertyzoned", "permitflow", "scribd", "buildpermitguide", "reddit", "yelp",
                "angi", "homeadvisor", "thumbtack", "quora", "facebook", "youtube", "wikipedia", "consumeraffairs")
KEYWORDS = re.compile(r"permit|plan|owner|homeowner|homestead|electric|generator|solar|photovoltaic|battery|storage|"
                      r"charg|panel|service|circuit|NEC|electrical code|license|contractor|affidavit|review", re.I)
PAGE_CHARS = 9000      # text kept per page for the model (keyword windows)
MAX_PAGES = 8


# ---------------------------------------------------------------- helpers

def normalize(text: str) -> str:
    """The importer's quote test: letters and digits only, lower case."""
    return re.sub(r"[^a-z0-9]", "", text.lower())


def api_key() -> str:
    key = os.environ.get("OPENROUTER_API_KEY", "")
    env = ROOT / ".env"
    if not key and env.exists():
        for line in env.read_text().splitlines():
            if line.strip().startswith("OPENROUTER_API_KEY="):
                key = line.split("=", 1)[1].strip().strip('"').strip("'")
    if not key:
        raise SystemExit("OPENROUTER_API_KEY is not set (environment or .env).")
    return key


def chat(model: str, messages: list[dict], *, web: bool = False, timeout: float = 180) -> dict:
    """One OpenRouter chat call that must answer with a JSON object."""
    body = {"model": model, "messages": messages, "temperature": 0, "response_format": {"type": "json_object"}}
    if web:
        body["plugins"] = [{"id": "web", "max_results": 8}]
    response = httpx.post(f"{API}/chat/completions", json=body, timeout=timeout,
                          headers={"Authorization": f"Bearer {api_key()}", "X-Title": "permit-packet research"})
    response.raise_for_status()
    data = response.json()
    content = data["choices"][0]["message"]["content"] or "{}"
    return parse_json(content)


def parse_json(content: str) -> dict:
    content = content.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", content, re.S)
    if fenced:
        content = fenced.group(1)
    start, end = content.find("{"), content.rfind("}")
    if start == -1 or end == -1:
        return {}
    try:
        return json.loads(content[start:end + 1])
    except json.JSONDecodeError:
        return {}


def official(url: str) -> bool:
    host = re.sub(r"^https?://", "", url).split("/")[0].lower()
    return url.startswith(("http://", "https://")) and not any(bad in host for bad in NOT_OFFICIAL) \
        and "google." not in host and "/search" not in url.lower()


# ---------------------------------------------------------------- what is missing

def gaps(key: str) -> list[str]:
    """Facts still unverified for this city: who_may_file, code_edition, <job>.permit_required / .plans_required."""
    path = VERIFIED / f"{key}.json"
    data = json.loads(path.read_text()) if path.exists() else {}

    def ok(block):
        return isinstance(block, dict) and bool(block.get("ok"))

    def known(block):
        return ok(block) and block.get("value") not in (None, "", "unknown")

    missing = []
    who = data.get("who_may_file")
    if not (ok(who) and isinstance(who.get("owner_may_file"), bool)):
        missing.append("who_may_file")
    if not ok(data.get("code_edition")):
        missing.append("code_edition")
    jobs = data.get("jobs") or {}
    for job in JOBS:
        block = jobs.get(job) or {}
        if not known(block.get("permit_required")):
            missing.append(f"{job}.permit_required")
        if not known(block.get("plans_required_single_family")):
            missing.append(f"{job}.plans_required")
    return missing


def describe(fact: str, city: str) -> str:
    if fact == "who_may_file":
        return (f"who_may_file: may the owner of a single-family home they live in pull their own electrical permit in "
                f"{city}? owner_may_file true/false, plus conditions.")
    if fact == "code_edition":
        return f"code_edition: which edition of the National Electrical Code {city} enforces today (and its effective date)."
    job, kind = fact.split(".")
    if kind == "permit_required":
        return f"{fact}: does a {JOB_NAMES[job]} at a single-family home need an electrical permit in {city}? yes/no."
    return (f"{fact}: does a {JOB_NAMES[job]} at a single-family home need plans / plan review in {city}? "
            "yes, no, or depends (give the threshold).")


# ---------------------------------------------------------------- fetching

def page_text(body: bytes, content_type: str) -> str:
    """Readable text of a page or PDF (whitespace collapsed), the way the importer reads it."""
    if body[:1024].lstrip().startswith(b"%PDF") or "application/pdf" in content_type:
        with tempfile.NamedTemporaryFile(suffix=".pdf") as handle:
            handle.write(body)
            handle.flush()
            text = subprocess.run(["pdftotext", handle.name, "-"], capture_output=True, timeout=120).stdout
        return re.sub(r"\s+", " ", text.decode("utf-8", "replace"))
    charset = re.search(r"charset=([\w-]+)", content_type)
    try:
        page = body.decode(charset.group(1) if charset else "utf-8", "replace")
    except LookupError:
        page = body.decode("utf-8", "replace")
    page = re.sub(r"(?is)<(script|style|noscript)\b.*?</\1>", " ", page)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]*>", " ", page)))


def fetch(url: str) -> str:
    """Page text, cached. httpx first (as the importer does); '' when blocked (the browser pass retries)."""
    cached = CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".txt")
    if cached.exists():
        return cached.read_text()
    try:
        with httpx.Client(headers={"User-Agent": UA}, timeout=30, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code >= 400:
            return ""
        text = page_text(response.content, response.headers.get("content-type", ""))
    except Exception:
        return ""
    if len(normalize(text)) >= 200 and "access denied" not in text[:400].lower():
        cached.write_text(text)
        return text
    return ""


def fetch_in_browser(urls: list[str]) -> dict[str, str]:
    """Blocked pages, one at a time, in a real Chrome window."""
    if not urls:
        return {}
    out = {}
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        try:
            browser = p.chromium.launch(channel="chrome", headless=False)
        except Exception:
            browser = p.chromium.launch(headless=False)
        context = browser.new_context(user_agent=UA)
        for url in urls:
            try:
                response = context.request.get(url, timeout=60000)
                body, ctype = response.body(), response.headers.get("content-type", "")
                if not (response.ok and (body[:5] == b"%PDF" or "pdf" in ctype)):
                    page = context.new_page()
                    page.goto(url, wait_until="networkidle", timeout=60000)
                    body, ctype = page.content().encode(), "text/html"
                    page.close()
                text = page_text(body, ctype)
                if len(normalize(text)) >= 200 and "access denied" not in text[:400].lower():
                    (CACHE / (hashlib.sha256(url.encode()).hexdigest() + ".txt")).write_text(text)
                    out[url] = text
            except Exception:
                pass
        browser.close()
    return out


def windows(text: str, limit: int = PAGE_CHARS) -> str:
    """The parts of a long page that mention permits, plans, owners and the job types."""
    if len(text) <= limit:
        return text
    sentences = re.split(r"(?<=[.!?:;])\s+", text)
    keep = set()
    for i, sentence in enumerate(sentences):
        if KEYWORDS.search(sentence):
            keep.update((i - 1, i, i + 1))
    picked = " … ".join(sentences[i] for i in sorted(keep) if 0 <= i < len(sentences))
    return picked[:limit]


# ---------------------------------------------------------------- research

SYSTEM = ("You research residential electrical permit rules for one US city. Use only official sources: the city or "
          "county building/permit office, the state licensing or building agency, or the local electric utility. "
          "Never use blogs, contractor sites, permit-guide websites, forums or AI summaries.")


def find_pages(model: str, city: str, state: str, facts: list[str]) -> list[str]:
    asks = "\n".join("- " + describe(f, f"{city}, {state}") for f in facts)
    answer = chat(model, [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": (
            f"Find the official web pages and PDFs that answer these questions for {city}, {state}:\n{asks}\n\n"
            "Prefer the city's permit pages for each job type, its homeowner/owner-builder permit page or affidavit, "
            "its list of permits that need no plans, and the code-adoption page. Return JSON: "
            '{"urls": ["<direct url>", ...]} with at most 10 direct links (no search-result links).')},
    ], web=True)
    urls = [u for u in answer.get("urls") or [] if isinstance(u, str) and official(u)]
    return list(dict.fromkeys(urls))[:MAX_PAGES + 2]


def extract(model: str, city: str, state: str, facts: list[str], pages: dict[str, str]) -> dict:
    asks = "\n".join("- " + describe(f, f"{city}, {state}") for f in facts)
    sources = "\n\n".join(f"=== SOURCE {i + 1}: {url}\n{windows(text)}" for i, (url, text) in enumerate(pages.items()))
    return chat(model, [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": (
            f"Answer these questions for {city}, {state} using ONLY the sources below:\n{asks}\n\n"
            "Rules:\n"
            "1. The quote must be copied character for character from one source, one continuous piece, 8 to 45 "
            "words. Never paraphrase or join pieces.\n"
            "2. The quote must itself state the answer: someone reading only the quote must see it. A heading or a "
            "general sentence that merely sits on the same page does not count.\n"
            "3. If no source states an answer, omit that fact. Do not guess.\n"
            "4. value: for permit_required yes/no; for plans_required yes/no/depends; for who_may_file use "
            "owner_may_file true/false; for code_edition a short text like '2023 NEC'.\n\n"
            'Return JSON: {"facts": [{"fact": "<fact id>", "value": ..., "conditions": "<limits or none>", '
            '"effective_date": "<YYYY-MM-DD or unknown, code_edition only>", "quote": "<exact text>", '
            '"url": "<the SOURCE url it came from>"}]}\n\n' + sources)},
    ])


def judge(model: str, city: str, fact: str, item: dict) -> tuple[bool, str]:
    answer = chat(model, [
        {"role": "system", "content": "You check evidence strictly. Answer only with JSON."},
        {"role": "user", "content": (
            f"City: {city}\nQuestion: {describe(fact, city)}\nClaimed answer: {json.dumps(item.get('value'))}"
            f" (conditions: {item.get('conditions', '')})\nSource URL: {item.get('url')}\nQuote: \"{item.get('quote')}\"\n\n"
            "Does the quote by itself clearly state this answer for this city, and is the URL an official government "
            "or electric-utility source for this city or its state? Return JSON: "
            '{"supported": true/false, "reason": "<one short sentence>"}')},
    ], timeout=90)
    return bool(answer.get("supported")), str(answer.get("reason", ""))[:200]


def to_evidence(key: str, city: str, state: str, accepted: list[tuple[str, dict]]) -> dict:
    doc: dict = {"jurisdiction_key": key, "city": city, "state": state, "checked_on": TODAY, "jobs": {}}
    for fact, item in accepted:
        quote, url = " ".join(str(item["quote"]).split()), item["url"]
        if fact == "who_may_file":
            doc["who_may_file"] = {"owner_may_file": bool(item["value"]), "conditions": item.get("conditions") or "none",
                                   "quote": quote, "url": url}
        elif fact == "code_edition":
            doc["code_edition"] = {"value": str(item["value"]), "effective_date": item.get("effective_date") or "unknown",
                                   "quote": quote, "url": url}
        else:
            job, kind = fact.split(".")
            block = {"value": str(item["value"]).lower(), "quote": quote, "url": url}
            if kind == "plans_required":
                block["conditions"] = item.get("conditions") or "none"
                kind = "plans_required_single_family"
            doc["jobs"].setdefault(job, {})[kind] = block
    return doc


def valid_value(fact: str, value) -> bool:
    if fact == "who_may_file":
        return isinstance(value, bool)
    if fact == "code_edition":
        return isinstance(value, str) and bool(value.strip())
    allowed = {"yes", "no"} if fact.endswith("permit_required") else {"yes", "no", "depends"}
    return str(value).lower() in allowed


def research_city(key: str, model: str, judge_model: str) -> dict:
    sys.path.insert(0, str(ROOT))
    from permit_packets.jurisdictions import KNOWN
    city_obj = next(j for j in KNOWN.values() if j.key == key)
    city, state = city_obj.name, city_obj.state
    facts = gaps(key)
    result = {"key": key, "city": f"{city}, {state}", "asked": facts, "accepted": [], "rejected": [], "file": None}
    if not facts:
        return result
    urls = find_pages(model, city, state, facts)
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        texts = dict(zip(urls, pool.map(fetch, urls)))
    texts.update(fetch_in_browser([u for u, t in texts.items() if not t]))
    pages = {u: t for u, t in texts.items() if t}
    result["pages"] = list(pages)
    if not pages:
        result["rejected"].append(("all", "no official page could be read"))
        return result
    answer = extract(model, city, state, facts, dict(list(pages.items())[:MAX_PAGES]))
    accepted = []
    for item in answer.get("facts") or []:
        fact = item.get("fact")
        if fact not in facts or not isinstance(item.get("quote"), str) or item.get("url") not in pages:
            result["rejected"].append((str(fact), "not one of the asked facts, or no quote/source"))
            continue
        if not valid_value(fact, item.get("value")):
            result["rejected"].append((fact, f"unusable value {item.get('value')!r}"))
            continue
        if len(normalize(item["quote"])) < 25 or normalize(item["quote"]) not in normalize(pages[item["url"]]):
            result["rejected"].append((fact, "quote not found word for word in the page"))
            continue
        supported, reason = judge(judge_model, f"{city}, {state}", fact, item)
        if not supported:
            result["rejected"].append((fact, f"check failed: {reason}"))
            continue
        if any(f == fact for f, _ in accepted):
            continue
        accepted.append((fact, item))
    result["accepted"] = [(f, i["value"], i["url"]) for f, i in accepted]
    if accepted:
        path = EVIDENCE / f"{key}.auto-{TODAY}.yaml"
        path.write_text(yaml.safe_dump(to_evidence(key, city, state, accepted), sort_keys=False, allow_unicode=True,
                                       width=1000))
        result["file"] = str(path.relative_to(ROOT))
    return result


# ---------------------------------------------------------------- import, test, PR

def run(cmd: str) -> None:
    print("$", cmd, flush=True)
    subprocess.run(cmd, shell=True, check=True, cwd=ROOT)


def pin_last_verified() -> None:
    """Keep tests/test_title_block.py's last_verified list in step with the cities the import just verified."""
    code = (
        "import re,sys; sys.path.insert(0,'.')\n"
        "from permit_packets.jurisdictions import KNOWN\n"
        "v={j.key:j.last_verified for j in KNOWN.values() if j.last_verified}\n"
        "p='tests/test_title_block.py'; s=open(p).read()\n"
        "body='assert verified == {\\n'+''.join(f'        \"{k}\": \"{v[k]}\",\\n' for k in sorted(v))+'    }'\n"
        "s2,n=re.subn(r'assert verified == \\{.*?\\n    \\}',body,s,count=1,flags=re.S)\n"
        "assert n==1,'pin not found'; open(p,'w').write(s2)\n"
    )
    subprocess.run([sys.executable, "-c", code], check=True, cwd=ROOT)


def import_and_ship(keys: list[str], report: Path) -> None:
    branch = f"research-{TODAY}-{hashlib.sha1(','.join(keys).encode()).hexdigest()[:6]}"
    py = sys.executable
    run("git checkout main && git pull --ff-only")  # new evidence files are untracked, so they come along
    run(f"git checkout -B {branch}")
    run(f"{py} tools/import_evidence.py")
    pin_last_verified()
    run(f"{py} -m pytest -q -n auto tests/test_city_compliance.py tests/test_title_block.py tests/test_jurisdictions.py")
    run("git add evidence permit_packets/jurisdictions tests/test_title_block.py")
    run(f'git commit -m "Automated research: {", ".join(keys)}"')
    run(f"git push -u origin {branch}")
    run(f'gh pr create --base main --head {branch} --title "Automated research: {len(keys)} cities" '
        f'--body-file "{report}"')
    run(f"gh pr checks {branch} --watch --fail-fast")
    run(f"gh pr merge {branch} --squash --delete-branch")
    run("git checkout main && git pull --ff-only")


# ---------------------------------------------------------------- main

def check(model: str) -> None:
    key = api_key()
    print("OPENROUTER_API_KEY: found")
    models = httpx.get(f"{API}/models", headers={"Authorization": f"Bearer {key}"}, timeout=30).json().get("data", [])
    ids = {m.get("id") for m in models}
    if model not in ids:
        near = sorted(i for i in ids if i and "deepseek" in i)[:15]
        raise SystemExit(f"Model {model!r} not found on OpenRouter. DeepSeek models available: {near}")
    print(f"model: {model} (available)")
    for tool in ("pdftotext", "gh", "git"):
        found = subprocess.run(["which", tool], capture_output=True).returncode == 0
        print(f"{tool}: {'found' if found else 'MISSING'}")
    from playwright.sync_api import sync_playwright  # noqa: F401
    print("playwright: installed")
    ping = chat(model, [{"role": "user", "content": 'Reply with JSON {"ok": true}.'}])
    print("OpenRouter call:", "ok" if ping.get("ok") else f"unexpected reply {ping}")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--cities", help="comma-separated city keys, or 'all'")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--judge-model", default=DEFAULT_JUDGE)
    parser.add_argument("--check", action="store_true", help="verify the setup and exit")
    parser.add_argument("--import", dest="do_import", action="store_true",
                        help="after research: import, test, commit, open a PR, wait for CI and merge")
    args = parser.parse_args()
    if args.check:
        check(args.model)
        return
    if not args.cities:
        parser.error("--cities is required (or --check)")
    sys.path.insert(0, str(ROOT))
    from permit_packets.jurisdictions import KNOWN
    known = sorted(j.key for j in KNOWN.values())
    keys = known if args.cities == "all" else [k.strip() for k in args.cities.split(",") if k.strip()]
    unknown = [k for k in keys if k not in known]
    if unknown:
        raise SystemExit(f"Unknown city keys: {unknown}")
    CACHE.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    lines = [f"# Automated research, {TODAY}", "", f"Model: {args.model}; check: {args.judge_model}", ""]
    for key in keys:
        print(f"\n== {key}", flush=True)
        try:
            r = research_city(key, args.model, args.judge_model)
        except Exception as exc:  # one city failing must not stop the batch
            r = {"key": key, "city": key, "asked": [], "accepted": [], "rejected": [("all", f"error: {exc}")]}
        still = [f for f in r["asked"] if f not in {a[0] for a in r["accepted"]}]
        lines += [f"## {r['city']}", "", f"Asked: {len(r['asked'])} facts. Found: {len(r['accepted'])}.", ""]
        lines += [f"- found `{f}` = {v!r} ({u})" for f, v, u in r["accepted"]]
        lines += [f"- dropped `{f}`: {why}" for f, why in r["rejected"]]
        lines += [f"- still unknown: {', '.join(still) or 'none'}", ""]
        print("\n".join(lines[-(len(r['accepted']) + len(r['rejected']) + 2):]), flush=True)
    report = REPORTS / f"{TODAY}-{hashlib.sha1(','.join(keys).encode()).hexdigest()[:6]}.md"
    report.write_text("\n".join(lines) + "\n")
    print(f"\nReport: {report.relative_to(ROOT)}")
    if args.do_import:
        import_and_ship(keys, report)


if __name__ == "__main__":
    main()
