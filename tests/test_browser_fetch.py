"""tools/browser_fetch.py: a PDF that only a real Chrome can open comes back as a PDF, not as the viewer's empty page."""
import base64
import importlib.util
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent.parent / "tools"
sys.path.insert(0, str(TOOLS))
SPEC = importlib.util.spec_from_file_location("browser_fetch", TOOLS / "browser_fetch.py")
bf = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(bf)


class FakePage:
    def __init__(self, fetched, html="<html><body>rendered page</body></html>", goto_error=False):
        self.fetched, self.html, self.goto_error, self.closed = fetched, html, goto_error, False

    def goto(self, url, **kw):
        if self.goto_error:
            raise RuntimeError("Download is starting")

    def wait_for_timeout(self, ms):
        pass

    def wait_for_load_state(self, *a, **kw):
        pass

    def evaluate(self, js, url):
        if isinstance(self.fetched, Exception):
            raise self.fetched
        return self.fetched

    def content(self):
        return self.html

    def close(self):
        self.closed = True


class FakeContext:
    def __init__(self, page):
        self.page = page

    def new_page(self):
        return self.page


def result(body: bytes, status=200, ctype="application/pdf"):
    return {"status": status, "type": ctype, "b64": base64.b64encode(body).decode()}


def test_a_pdf_is_read_as_bytes_through_chrome():
    page = FakePage(result(b"%PDF-1.6 homestead affidavit"))
    body, ctype = bf.read_url(FakeContext(page), "https://city.gov/a.pdf")
    assert body.startswith(b"%PDF") and "pdf" in ctype and page.closed


def test_a_pdf_still_reads_when_the_navigation_ends_early():
    page = FakePage(result(b"%PDF-1.6 x"), goto_error=True)
    assert bf.read_url(FakeContext(page), "https://city.gov/a.pdf")[0].startswith(b"%PDF")


def test_an_html_page_comes_back_as_the_rendered_page():
    page = FakePage(result(b"<html>raw</html>", ctype="text/html"))
    body, ctype = bf.read_url(FakeContext(page), "https://city.gov/page")
    assert b"rendered page" in body and ctype == "text/html"


def test_a_blocked_fetch_falls_back_to_the_page_and_closes_it():
    page = FakePage(result(b"Access Denied", status=403, ctype="text/html"))
    assert b"rendered page" in bf.read_url(FakeContext(page), "https://city.gov/x")[0] and page.closed
    page = FakePage(RuntimeError("fetch failed"))
    assert bf.read_url(FakeContext(page), "https://city.gov/x")[1] == "text/html" and page.closed
