"""The importer reads scanned PDFs (no text layer) with OCR, so quotes from them can verify."""
import importlib.util
import shutil
from io import BytesIO
from pathlib import Path

import pytest
from PIL import Image, ImageDraw, ImageFont
from reportlab.lib.utils import ImageReader
from reportlab.pdfgen.canvas import Canvas

SPEC = importlib.util.spec_from_file_location("import_evidence", Path(__file__).resolve().parent.parent / "tools" / "import_evidence.py")
ie = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(ie)

SENTENCE = "Permits for electrical work may be issued to the homeowner"


def _scanned_pdf() -> bytes:
    """A PDF whose only content is a picture of a sentence: pdftotext finds nothing in it."""
    image = Image.new("RGB", (2400, 400), "white")
    draw = ImageDraw.Draw(image)
    try:
        font = ImageFont.truetype("DejaVuSans.ttf", 64)
    except OSError:
        font = ImageFont.load_default(size=64)
    draw.text((60, 150), SENTENCE, fill="black", font=font)
    png = BytesIO()
    image.save(png, format="PNG")
    out = BytesIO()
    canvas = Canvas(out, pagesize=(1200, 200))
    canvas.drawImage(ImageReader(BytesIO(png.getvalue())), 0, 0, 1200, 200)
    canvas.save()
    return out.getvalue()


@pytest.mark.skipif(not (shutil.which("tesseract") and shutil.which("pdftoppm") and shutil.which("pdftotext")),
                    reason="needs tesseract and poppler (brew install tesseract poppler)")
def test_a_scanned_pdf_is_read_with_ocr():
    text = ie.to_text(_scanned_pdf(), "application/pdf")
    assert ie.normalize(SENTENCE) in text.replace("\n", "")


def test_a_cached_page_with_no_text_is_fetched_again(tmp_path, monkeypatch):
    monkeypatch.setattr(ie, "CACHE", tmp_path)
    url = "https://example.invalid/scanned.pdf"
    cached = tmp_path / (ie.hashlib.sha256(url.encode()).hexdigest() + ".json")
    cached.write_text('{"text": "x", "error": ""}')
    calls = []

    class Client:
        def __init__(self, *a, **k): pass
        def __enter__(self): return self
        def __exit__(self, *a): return False
        def get(self, url):
            calls.append(url)
            raise ie.httpx.ConnectError("offline")

    monkeypatch.setattr(ie.httpx, "Client", Client)
    result = ie.fetch(url)
    assert calls, "a near-empty cached page must be fetched again"
    assert result["error"]
