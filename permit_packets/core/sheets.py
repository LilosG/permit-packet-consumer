"""Sheet size for cities that want 11" x 17" sheets.

Packet pages are drawn on letter paper. On 11 x 17 they are placed at 100%, never scaled, so the
site plan's printed scale stays true: the full packet goes two pages to a 17 x 11 sheet, and each
single-document upload is centered on an 11 x 17 sheet. Manufacturer sheets larger than a letter
slot are the only pages ever reduced.
"""
from __future__ import annotations

from io import BytesIO

from pypdf import PageObject, PdfReader, PdfWriter, Transformation

LETTER = (612.0, 792.0)
TABLOID_LANDSCAPE = (1224.0, 792.0)
TABLOID_PORTRAIT = (792.0, 1224.0)


def _place(sheet: PageObject, page: PageObject, slot_x: float, slot_y: float, slot_w: float, slot_h: float):
    box = page.mediabox
    width, height = float(box.width), float(box.height)
    scale = min(1.0, slot_w / width, slot_h / height)
    x = slot_x + (slot_w - width * scale) / 2 - float(box.left) * scale
    y = slot_y + (slot_h - height * scale) / 2 - float(box.bottom) * scale
    sheet.merge_transformed_page(page, Transformation().scale(scale).translate(x, y))


def two_up_tabloid(pdf: bytes) -> bytes:
    """The whole packet, two letter pages side by side on each 17 x 11 sheet, at 100%."""
    reader = PdfReader(BytesIO(pdf))
    writer = PdfWriter()
    pages = list(reader.pages)
    for index in range(0, len(pages), 2):
        sheet = PageObject.create_blank_page(width=TABLOID_LANDSCAPE[0], height=TABLOID_LANDSCAPE[1])
        for offset, page in enumerate(pages[index:index + 2]):
            _place(sheet, page, offset * LETTER[0], 0, LETTER[0], LETTER[1])
        writer.add_page(sheet)
    if reader.metadata:
        writer.add_metadata({key: str(value) for key, value in reader.metadata.items()})
    out = BytesIO()
    writer.write(out)
    return out.getvalue()


def centered_tabloid(pdf: bytes) -> bytes:
    """Each page centered at 100% on an 11 x 17 sheet."""
    reader = PdfReader(BytesIO(pdf))
    writer = PdfWriter()
    for page in reader.pages:
        sheet = PageObject.create_blank_page(width=TABLOID_PORTRAIT[0], height=TABLOID_PORTRAIT[1])
        _place(sheet, page, 0, 0, TABLOID_PORTRAIT[0], TABLOID_PORTRAIT[1])
        writer.add_page(sheet)
    out = BytesIO()
    writer.write(out)
    return out.getvalue()
