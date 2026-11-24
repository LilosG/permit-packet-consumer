"""The one place prices live: tier prices, the launch offer, credit packs and the bonus-credit window.

Everything else (templates, copy, JSON-LD, emails, JS) reads from here. Copy strings in the .py content files use
the tokens {price:TIER}, {regular:TIER} and {launch_end}; `resolve()` replaces them (pages.render and pages.fill
call it). Every function takes an optional `now` so tests can pin the date; without it the clock below is used.
"""
from __future__ import annotations

import datetime
import re
from zoneinfo import ZoneInfo

TZ = ZoneInfo("America/Los_Angeles")

TIER_KEYS = ("load_calc", "instant_packet", "city_checked_24h")
REGULAR = {"load_calc": 39, "instant_packet": 89, "city_checked_24h": 149}
LAUNCH = {"load_calc": 29, "instant_packet": 59, "city_checked_24h": 109}
LAUNCH_ENDS = datetime.datetime(2026, 12, 31, 23, 59, 59, tzinfo=TZ)

PACKS = {"pack_5": 5, "pack_10": 10, "pack_25": 25}  # credits
PACK_REGULAR = {"pack_5": 299, "pack_10": 449, "pack_25": 899}
PACK_LAUNCH = {"pack_5": 199, "pack_10": 349, "pack_25": 749}

BONUS_START = datetime.datetime(2026, 11, 27, 0, 0, 0, tzinfo=TZ)
BONUS_END = datetime.datetime(2026, 12, 1, 23, 59, 59, tzinfo=TZ)
BONUS_CREDITS = {"pack_5": 6, "pack_10": 13, "pack_25": 33}

# Legacy ?tier= URL values (the old prices, and the new regular city-checked price) and their tiers.
TIER_ALIASES = {"39": "load_calc", "89": "instant_packet", "169": "city_checked_24h", "149": "city_checked_24h"}

# Display names. Internal keys never change.
TIER_NAMES = {
    "load_calc": "Panel Capacity Report",
    "instant_packet": "Instant Permit Packet",
    "city_checked_24h": "24-Hour City-Checked Packet",
}
PANEL_REPORT_DESCRIPTION = (
    "A submittal-ready NEC 220 load calculation and panel schedule for your address, so you know your panel's "
    "capacity before you get quotes.")


def _clock() -> datetime.datetime:
    return datetime.datetime.now(TZ)


def _at(now: datetime.datetime | None) -> datetime.datetime:
    """`now` as an aware Los Angeles time (a naive value is taken to be Los Angeles time already)."""
    if now is None:
        return _clock()
    return now.replace(tzinfo=TZ) if now.tzinfo is None else now.astimezone(TZ)


def launch_active(now: datetime.datetime | None = None) -> bool:
    return _at(now) <= LAUNCH_ENDS


def bonus_active(now: datetime.datetime | None = None) -> bool:
    return BONUS_START <= _at(now) <= BONUS_END


def regular_price(key: str, now: datetime.datetime | None = None) -> int:
    return REGULAR[key]


def on_sale(key: str, now: datetime.datetime | None = None) -> bool:
    return launch_active(now) and (key in LAUNCH or key in PACK_LAUNCH)


def price(key: str, now: datetime.datetime | None = None) -> int:
    """What a tier costs right now: the launch price while the offer runs, else the regular price."""
    return LAUNCH[key] if on_sale(key, now) else REGULAR[key]


def pack_price(key: str, now: datetime.datetime | None = None) -> int:
    return PACK_LAUNCH[key] if launch_active(now) else PACK_REGULAR[key]


def pack_regular_price(key: str, now: datetime.datetime | None = None) -> int:
    return PACK_REGULAR[key]


def pack_credits(key: str, now: datetime.datetime | None = None) -> int:
    """Credits in a pack: the bonus count during the Black Friday-Cyber Monday window, else the base count."""
    return BONUS_CREDITS[key] if bonus_active(now) else PACKS[key]


def per_credit(key: str, now: datetime.datetime | None = None) -> float:
    return round(pack_price(key, now) / pack_credits(key, now), 2)


def launch_end_label() -> str:
    return "Dec 31"


def money(amount: int) -> str:
    return f"${amount:,}"


def prices_json(now: datetime.datetime | None = None) -> dict:
    """The small object the server renders for JS and static pages (window.PP_PRICES)."""
    on = launch_active(now)
    return {"onSale": on, "launchEnd": launch_end_label(), "tiers": {
        key: {"price": price(key, now), "regular": REGULAR[key], "name": TIER_NAMES[key]} for key in TIER_KEYS}}


_TOKEN = re.compile(r"\{(price|regular):(load_calc|instant_packet|city_checked_24h)\}|\{launch_end\}")


def resolve(text: str, now: datetime.datetime | None = None) -> str:
    """Replace {price:TIER}, {regular:TIER} and {launch_end} with the current numbers."""
    def sub(match: re.Match) -> str:
        if match.group(1) == "price":
            return money(price(match.group(2), now))
        if match.group(1) == "regular":
            return money(REGULAR[match.group(2)])
        return launch_end_label()
    return _TOKEN.sub(sub, text) if "{" in text else text
