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
                "angi", "homeadvisor", "thumbtack", "quora", "facebook", "youtube", "wikipedia", "consumeraffairs", "corpuslaw", "municipalcodeonline", "casetext", "justia", "law.cornell")
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
    message = data["choices"][0]["message"]
    parsed = parse_json(message.get("content") or "{}")
    cited = [a.get("url_citation", {}).get("url") for a in message.get("annotations") or []
             if a.get("type") == "url_citation"]
    parsed["_cited"] = [u for u in cited if isinstance(u, str)]
    return parsed


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


# Hosts that publish cities' own adopted codes and documents, or run their permit portals.
CODE_HOSTS = ("library.municode.com", "codelibrary.amlegal.com", "ecode360.com", "codepublishing.com",
              "content.civicplus.com", "accela.com", "floridabuilding.org")


def host_of(url: str) -> str:
    return re.sub(r"^https?://", "", url).split("/")[0].split(":")[0].lower()


def base_domain(host: str) -> str:
    parts = host.split(".")
    return ".".join(parts[-2:]) if len(parts) >= 2 else host


def official(url: str, city_domains: frozenset = frozenset()) -> bool:
    """Government sites, the city's own domains (from its module) and official code/portal hosts. Decided here,
    in code, never by the model."""
    if not url.startswith(("http://", "https://")):
        return False
    host = host_of(url)
    if any(bad in host for bad in NOT_OFFICIAL) or "google." in host or "/search" in url.lower() \
            or host.startswith("search."):
        return False
    # .us only in the government pattern (city.tx.us); a bare name.us is anyone's site
    return (host.endswith((".gov", ".mil")) or ".gov." in host or re.search(r"\.[a-z]{2}\.us$", host)
            or base_domain(host) in city_domains
            or any(host == h or host.endswith("." + h) for h in CODE_HOSTS))


def city_domains(city_obj) -> frozenset:
    urls = [city_obj.portal_url, city_obj.website, *city_obj.sources]
    return frozenset(base_domain(host_of(u)) for u in urls if isinstance(u, str) and u.startswith("http")
                     and not any(h in host_of(u) for h in CODE_HOSTS))


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
          "county building/permit office, its published municipal code, the state licensing or building agency, or "
          "the local electric utility. Never use blogs, contractor sites, permit-guide websites, forums or AI summaries.")

# Facts are researched in small groups: one search and one reading pass per group, so none gets skipped.
GROUPS = {
    "filing_and_code": ("who_may_file", "code_edition"),
    "ev_and_appliance": ("ev_charger.permit_required", "ev_charger.plans_required",
                         "appliance_circuit.permit_required", "appliance_circuit.plans_required"),
    "service_and_subpanel": ("service_upgrade.permit_required", "service_upgrade.plans_required",
                             "subpanel.permit_required", "subpanel.plans_required"),
    "generator_and_solar": ("generator.permit_required", "generator.plans_required",
                            "solar_storage.permit_required", "solar_storage.plans_required"),
}
SEARCH_HINTS = {
    "filing_and_code": "homeowner / owner-builder electrical permit rules or affidavit, and the code adoption page "
                       "or ordinance that names the National Electrical Code edition",
    "ev_and_appliance": "electrical permit page, permits that need no plans / express or over-the-counter permits, "
                        "EV charger permit page",
    "service_and_subpanel": "electrical permit page, service change / panel upgrade permit, permits that need no "
                            "plans / express or over-the-counter permits",
    "generator_and_solar": "standby generator permit page or checklist, residential solar and battery storage "
                           "permit page or checklist",
}
GROUP_WORDS = {
    "filing_and_code": r"owner|homeowner|homestead|affidavit|occup|license|contractor|NEC|national electrical code|"
                       r"electrical code|edition|adopt|ordinance|amendment",
    "ev_and_appliance": r"EV|electric vehicle|charg|appliance|circuit|range|dryer|water heater|plan|exempt|express|"
                        r"over.the.counter|no plans|permit",
    "service_and_subpanel": r"service|panel|subpanel|sub-panel|meter|amp|upgrade|change of service|plan|exempt|"
                            r"express|over.the.counter|no plans|permit",
    "generator_and_solar": r"generator|transfer switch|interlock|standby|solar|photovoltaic|PV|battery|storage|ESS|"
                           r"plan|checklist|permit",
}
LINK_WORDS = re.compile(r"electric|permit|homeowner|owner|solar|photovoltaic|generator|vehicle|charg|code|plan review|"
                        r"express|checklist|residential|panel|service", re.I)
SKIP_LINKS = re.compile(r"police|alarm|hydrant|complaint|enforcement|login|log in|sign in|register|\bpay\b|payment|fees|career|"
                        r"news|agenda|calendar|/cap/|captcha|facebook|twitter|instagram|linkedin", re.I)
MAX_PAGES_PER_GROUP = 8
MAX_FETCH = 30


def find_pages(model: str, city: str, state: str, facts: list[str], domains: frozenset = frozenset(),
               hint: str = "") -> list[str]:
    """One web search for one group of facts: the URLs the model lists plus the real search results it cites."""
    asks = "\n".join("- " + describe(f, f"{city}, {state}") for f in facts)
    sites = ", ".join(sorted(domains)) or "the city's own website"
    answer = chat(model, [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": (
            f"Find the official web pages and PDFs that answer these questions for {city}, {state}:\n{asks}\n\n"
            f"Look for: {hint}. The city's own sites are {sites}; prefer pages there, then the city's published "
            "municipal code, then the state agency. Return JSON: "
            '{"urls": ["<direct url>", ...]} with at most 10 direct links (no search-result links).')},
    ], web=True)
    urls = [u for u in (answer.get("urls") or []) + answer.get("_cited", []) if isinstance(u, str)]
    return list(dict.fromkeys(u.split("#")[0] for u in urls if official(u, domains)))


def crawl_links(url: str, domains: frozenset, limit: int = 15) -> list[str]:
    """Links on one of the city's own pages that look like permit pages (one level deep, no model involved)."""
    try:
        with httpx.Client(headers={"User-Agent": UA}, timeout=30, follow_redirects=True) as client:
            response = client.get(url)
        if response.status_code >= 400 or "html" not in response.headers.get("content-type", ""):
            return []
        page, base = response.text, str(response.url)
    except Exception:
        return []
    scored = []
    for href, label in re.findall(r'(?is)<a\b[^>]*href=["\']([^"\'#]+)["\'][^>]*>(.*?)</a>', page):
        link = str(httpx.URL(base).join(html.unescape(href.strip())))
        text = re.sub(r"<[^>]*>", " ", label) + " " + link
        hits = len(LINK_WORDS.findall(text))
        if hits and not SKIP_LINKS.search(text) and official(link, domains) and link.split("#")[0] != base \
                and "accela.com" not in host_of(link):
            scored.append((hits, link.split("#")[0]))
    return list(dict.fromkeys(link for _, link in sorted(scored, key=lambda x: -x[0])))[:limit]


def windows(text: str, limit: int = PAGE_CHARS, words: str = "") -> str:
    """The parts of a long page that mention permits, plans, owners and the job types."""
    if len(text) <= limit:
        return text
    pattern = re.compile(words, re.I) if words else KEYWORDS
    sentences = re.split(r"(?<=[.!?:;])\s+", text)
    keep = set()
    for i, sentence in enumerate(sentences):
        if pattern.search(sentence):
            keep.update((i - 1, i, i + 1))
    picked = " … ".join(sentences[i] for i in sorted(keep) if 0 <= i < len(sentences))
    return picked[:limit]


def rank_pages(pages: dict[str, str], words: str) -> dict[str, str]:
    """The pages most about this group of facts, best first."""
    pattern = re.compile(words, re.I)
    scored = sorted(pages.items(), key=lambda kv: -len(pattern.findall(kv[1][:200000])))
    return dict(scored[:MAX_PAGES_PER_GROUP])


def extract(model: str, city: str, state: str, facts: list[str], pages: dict[str, str], words: str = "") -> dict:
    asks = "\n".join("- " + describe(f, f"{city}, {state}") for f in facts)
    sources = "\n\n".join(f"=== SOURCE {i + 1}: {url}\n{windows(text, words=words)}"
                           for i, (url, text) in enumerate(pages.items()))
    return chat(model, [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": (
            f"Answer these questions for {city}, {state} using ONLY the sources below:\n{asks}\n\n"
            "Rules:\n"
            "1. Go through every question. For each one a source answers, give one fact.\n"
            "2. The quote must be copied character for character from one source, one continuous piece, 8 to 60 "
            "words. Never paraphrase, never join pieces, never add or drop words.\n"
            "3. The quote must show the answer. When the answer comes from a list (for example the kinds of work an "
            "electrical permit covers, or work that needs no plans), copy the list's lead-in together with the item "
            "if they are close enough to fit, otherwise the item with the words around it.\n"
            "4. If no source answers a question, leave it out. Do not guess.\n"
            "5. value: for permit_required yes/no; for plans_required yes/no/depends; for who_may_file use "
            "owner_may_file true/false; for code_edition a short text like '2023 NEC'.\n\n"
            'Return JSON: {"facts": [{"fact": "<fact id>", "value": ..., "conditions": "<limits or none>", '
            '"effective_date": "<YYYY-MM-DD or unknown, code_edition only>", "quote": "<exact text>", '
            '"url": "<the SOURCE url it came from>"}]}\n\n' + sources)},
    ])


def context_around(page: str, quote: str, chars: int = 700) -> str:
    """The page text around the quote, so the check reads it the way a person reading the page would."""
    flat = re.sub(r"\s+", " ", page)
    words = quote.split()
    probe = " ".join(words[:6]) if len(words) >= 6 else quote
    at = flat.lower().find(probe.lower())
    if at == -1:
        return ""
    return flat[max(0, at - chars):at + len(quote) + chars]


def judge(model: str, city: str, fact: str, item: dict, context: str = "") -> tuple[bool, str]:
    answer = chat(model, [
        {"role": "system", "content": "You check evidence for a permit-rules database. Be strict about meaning, "
                                      "not about wording. Answer only with JSON."},
        {"role": "user", "content": (
            f"City: {city}\nQuestion: {describe(fact, city)}\nClaimed answer: {json.dumps(item.get('value'))}"
            f" (conditions: {item.get('conditions', '')})\nSource URL: {item.get('url')}\n"
            f"Quote: \"{item.get('quote')}\"\nPage text around the quote: \"{context}\"\n\n"
            "Does the quote, read with the page text around it, support this answer for this city?\n"
            "- Yes when the page is this city's (or, for a state-wide rule, this state's) and the quote states the "
            "answer, or is the item in a list whose lead-in states it (for example work listed under an electrical "
            "permit means that work needs that permit; work listed as needing no plans means no plans).\n"
            "- No when the quote is about different work, a different place, a commercial-only rule, or only a "
            "heading or general sentence that does not decide the question.\n"
            "- Do not judge whether the website is official (that is checked separately) and do not require an "
            "effective date.\n"
            'Return JSON: {"supported": true/false, "reason": "<one short sentence>"}')},
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
    domains = city_domains(city_obj)
    facts = gaps(key)
    result = {"key": key, "city": f"{city}, {state}", "asked": facts, "accepted": [], "rejected": [], "file": None,
              "pages": [], "blocked": []}
    if not facts:
        return result
    groups = {g: [f for f in fs if f in facts] for g, fs in GROUPS.items()}
    groups = {g: fs for g, fs in groups.items() if fs}

    # 1. pages: the city's own pages from its module, permit links found on them, and one search per group
    seeds = [u for u in dict.fromkeys([city_obj.portal_url, city_obj.website, *city_obj.sources])
             if isinstance(u, str) and official(u, domains)]
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        searches = pool.map(lambda g: find_pages(model, city, state, groups[g], domains, SEARCH_HINTS[g]), groups)
        crawled = pool.map(lambda u: crawl_links(u, domains), seeds)
        found = [u for batch in searches for u in batch]
        linked = [u for batch in crawled for u in batch]
    urls = list(dict.fromkeys(found + seeds + linked))[:MAX_FETCH]
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        texts = dict(zip(urls, pool.map(fetch, urls)))
    texts.update(fetch_in_browser([u for u, t in texts.items() if not t]))
    pages = {u: t for u, t in texts.items() if t}
    result["pages"] = list(pages)
    result["blocked"] = [u for u, t in texts.items() if not t]
    print(f"  pages: {len(urls)} found, {len(pages)} read, {len(result['blocked'])} unreadable", flush=True)
    if not pages:
        result["rejected"].append(("all", "no official page could be read"))
        return result

    # 2. one reading pass per group, over the pages most about that group
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        answers = list(pool.map(lambda g: extract(model, city, state, groups[g],
                                                  rank_pages(pages, GROUP_WORDS[g]), GROUP_WORDS[g]), groups))
    items = [item for answer in answers for item in answer.get("facts") or [] if isinstance(item, dict)]

    # 3. word-for-word quote test (the importer's own), then the meaning check
    candidates = []
    for item in items:
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
        candidates.append((fact, item))
    with concurrent.futures.ThreadPoolExecutor(max_workers=6) as pool:
        verdicts = list(pool.map(lambda fi: judge(judge_model, f"{city}, {state}", fi[0], fi[1],
                                                  context_around(pages[fi[1]["url"]], fi[1]["quote"])), candidates))
    accepted = []
    for (fact, item), (supported, reason) in zip(candidates, verdicts):
        if not supported:
            result["rejected"].append((fact, f"check failed: {reason}"))
        elif not any(f == fact for f, _ in accepted):
            accepted.append((fact, item))
    result["accepted"] = [(f, i["value"], i["url"], " ".join(i["quote"].split())) for f, i in accepted]
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
        summary = [f"Asked: {len(r['asked'])} facts. Found: {len(r['accepted'])}.", ""]
        summary += [f"- found `{f}` = {v!r} ({u})\n    quote: \"{q[:220]}\"" for f, v, u, q in r["accepted"]]
        summary += [f"- dropped `{f}`: {why}" for f, why in r["rejected"]]
        summary += [f"- still unknown: {', '.join(still) or 'none'}", ""]
        summary += [f"- unreadable page: {u}" for u in r.get("blocked", [])] + [""]
        print("\n".join(summary), flush=True)
        lines += [f"## {r['city']}", ""] + summary
        lines += ([f"<details><summary>{len(r.get('pages', []))} pages read, {len(r.get('blocked', []))} unreadable"
                   "</summary>", ""] + [f"- read: {u}" for u in r.get("pages", [])]
                  + [f"- unreadable: {u}" for u in r.get("blocked", [])] + ["", "</details>", ""])
    report = REPORTS / f"{TODAY}-{hashlib.sha1(','.join(keys).encode()).hexdigest()[:6]}.md"
    report.write_text("\n".join(lines) + "\n")
    print(f"\nReport: {report.relative_to(ROOT)}")
    if args.do_import:
        import_and_ship(keys, report)


if __name__ == "__main__":
    main()
