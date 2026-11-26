"""site.js keeps the visitor's role for the session. The real script runs in Node against a small stand-in DOM."""
import json
import shutil
import subprocess

import pytest

import app as app_module

SITE_JS = app_module.ASSETS / "js" / "site.js"
pytestmark = pytest.mark.skipif(shutil.which("node") is None, reason="node is not installed")

HARNESS = r"""
const vm = require('vm'), fs = require('fs');
const { path, search = '', stored = null, blocked = false } = JSON.parse(process.argv[1]);
const store = new Map(stored ? [['pp_role', stored]] : []);
const guard = () => { if (blocked) throw new Error('storage blocked'); };
const sessionStorage = {
  getItem: (k) => { guard(); return store.has(k) ? store.get(k) : null; },
  setItem: (k, v) => { guard(); store.set(k, String(v)); },
};
const link = (href) => ({ href, getAttribute() { return this.href; }, setAttribute(_, v) { this.href = v; } });
const links = ['/start/', '/start/?tier=load_calc', '/start/?role=diy', '/start/?job=ev-charger&address=1%20Main#x',
               '/pricing/', 'https://elsewhere.example/start/', 'mailto:a@b.co'].map(link);
const form = (action, own) => ({ added: [], getAttribute: () => action,
  querySelector() { return own || this.added[0] || null; }, append(el) { this.added.push(el); } });
const forms = [form('/start/'), form('/start/', {}), form('/search/')];
const document = {
  querySelector: () => null, addEventListener() {}, createElement: () => ({}),
  querySelectorAll: (s) => (s === 'a[href]' ? links : s === 'form[action]' ? forms : []),
};
const window = { matchMedia: () => ({ matches: false, addEventListener() {} }) };
const location = { pathname: path, search, origin: 'https://site.example', href: 'https://site.example' + path + search };
vm.runInNewContext(fs.readFileSync(process.argv[2], 'utf8'),
  { window, document, location, sessionStorage, URL, URLSearchParams, matchMedia: window.matchMedia });
console.log(JSON.stringify({ role: store.get('pp_role') || null, links: links.map((l) => l.href),
  forms: forms.map((f) => f.added.map((i) => [i.type, i.name, i.value])), api: typeof window.PP.savedRole }));
"""

UNTOUCHED = ["/start/", "/start/?tier=load_calc", "/start/?role=diy", "/start/?job=ev-charger&address=1%20Main#x",
             "/pricing/", "https://elsewhere.example/start/", "mailto:a@b.co"]


def visit(path, **state):
    done = subprocess.run(["node", "-e", HARNESS, json.dumps({"path": path, **state}), str(SITE_JS)],
                          capture_output=True, text=True, timeout=30)
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)


@pytest.mark.parametrize("path, role", [
    ("/for/electricians/", "electrician"), ("/for/contractors/", "contractor"), ("/pro-credits/", "electrician"),
    ("/for/diy-homeowners/", "diy"), ("/for/homeowners-hiring-an-electrician/", "hiring"), ("/", None)])
def test_each_page_sets_its_role(path, role):
    assert visit(path)["role"] == role


def test_pro_credits_keeps_a_contractor_a_contractor():
    assert visit("/pro-credits/", stored="contractor")["role"] == "contractor"
    assert visit("/pro-credits/", stored="diy")["role"] == "electrician"


def test_an_explicit_role_in_the_url_wins_and_junk_is_ignored():
    assert visit("/for/electricians/", search="?role=contractor")["role"] == "contractor"
    assert visit("/", search="?role=admin")["role"] is None
    assert visit("/", search="?role=admin", stored="diy")["role"] == "diy"


@pytest.mark.parametrize("role", ["electrician", "contractor"])
def test_a_pro_carries_the_role_into_start_links_and_forms(role):
    page = visit("/", stored=role)
    assert page["links"] == [
        f"/start/?role={role}", f"/start/?tier=load_calc&role={role}", "/start/?role=diy",
        f"/start/?job=ev-charger&address=1+Main&role={role}#x", *UNTOUCHED[4:]]
    assert page["forms"] == [[["hidden", "role", role]], [], []] and page["api"] == "function"


@pytest.mark.parametrize("state", [{}, {"stored": "diy"}, {"stored": "hiring"}, {"stored": "nonsense"},
                                   {"stored": "electrician", "blocked": True}])
def test_everyone_else_gets_the_page_as_served(state):
    page = visit("/", **state)
    assert page["links"] == UNTOUCHED and page["forms"] == [[], [], []]


def test_the_wizard_restores_a_saved_pro_role_and_remembers_a_new_choice():
    js = (app_module.ASSETS / "js" / "app.js").read_text(encoding="utf-8")
    assert "restoreProRole();\n    applyRole();" in js and "window.PP.saveRole(role())" in js
    assert "if (new URLSearchParams(location.search).get('role')) return;" in js
