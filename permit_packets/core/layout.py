"""Page geometry: where the content frame and the title block sit on a sheet."""
from __future__ import annotations

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from reportlab.lib.units import inch


@dataclass(frozen=True)
class Sheet:
    key: str
    width: float
    height: float
    margin: float = 0.7 * inch
    top_margin: float = 0.6 * inch
    block_h: float = 66.0       # height of the title block
    block_y: float = 30.0       # from the bottom edge to the bottom of the title block
    gap: float = 8.0            # between the title block and the content frame

    @property
    def landscape(self) -> bool:
        return self.width > self.height

    @property
    def content_w(self) -> float:
        return self.width - 2 * self.margin

    @property
    def frame_y(self) -> float:
        return self.block_y + self.block_h + self.gap

    @property
    def content_h(self) -> float:
        return self.height - self.top_margin - self.frame_y


LETTER = Sheet("letter", 612.0, 792.0)
SHEETS = {"letter": LETTER}

_CURRENT: ContextVar[Sheet] = ContextVar("sheet", default=LETTER)


def current_sheet() -> Sheet:
    return _CURRENT.get()


def content_w() -> float:
    return current_sheet().content_w


@contextmanager
def use_sheet(sheet: Sheet):
    token = _CURRENT.set(sheet)
    try:
        yield sheet
    finally:
        _CURRENT.reset(token)
