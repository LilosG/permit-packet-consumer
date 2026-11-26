"""Read pages and PDFs that block scripts, through a real Chrome window.

Some city sites (Akamai and similar) answer script-style requests with "Access Denied" but serve a real Chrome
page normally. Chrome opens a PDF in its own viewer, so reading the page's HTML returns an empty shell. This reads
the file's bytes through Chrome's own network stack instead, so PDFs come back as PDFs.
"""
from __future__ import annotations

import base64

UA = ("Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
LAUNCH_ARGS = ["--disable-blink-features=AutomationControlled"]
FETCH_JS = """async (u) => {
  const r = await fetch(u, {credentials: 'include'});
  const b = new Uint8Array(await r.arrayBuffer());
  let s = '';
  for (let i = 0; i < b.length; i += 32768) s += String.fromCharCode.apply(null, b.subarray(i, i + 32768));
  return {status: r.status, type: r.headers.get('content-type') || '', b64: btoa(s)};
}"""


def launch(playwright):
    """A visible Chrome (the real browser when installed, else Playwright's own)."""
    try:
        return playwright.chromium.launch(channel="chrome", headless=False, args=LAUNCH_ARGS)
    except Exception:
        return playwright.chromium.launch(headless=False, args=LAUNCH_ARGS)


def read_url(context, url: str) -> tuple[bytes, str]:
    """(body, content_type) for one URL, read the way Chrome sees it. Raises when nothing could be read."""
    page = context.new_page()
    try:
        try:
            page.goto(url, wait_until="domcontentloaded", timeout=60000)
        except Exception:
            pass  # a PDF can end the navigation early; the fetch below still works
        page.wait_for_timeout(1500)
        try:
            res = page.evaluate(FETCH_JS, url)
            body = base64.b64decode(res["b64"])
            if res["status"] < 400 and (body[:5] == b"%PDF" or "pdf" in res["type"].lower()):
                return body, res["type"] or "application/pdf"
        except Exception:
            pass
        try:
            page.wait_for_load_state("networkidle", timeout=20000)
        except Exception:
            pass
        return page.content().encode(), "text/html"
    finally:
        page.close()
