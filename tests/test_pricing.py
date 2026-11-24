"""permit_packets/pricing.py: the one place prices live, the launch offer, packs and the bonus-credit window."""
import datetime

import pytest

from permit_packets import pricing

LA = pricing.TZ


def at(*args):
    return datetime.datetime(*args, tzinfo=LA)


BEFORE_BONUS = at(2026, 11, 20, 12, 0)
IN_BONUS = at(2026, 11, 28, 9, 30)
DEC_15 = at(2026, 12, 15, 12, 0)
JAN_2 = at(2027, 1, 2, 12, 0)


def test_constants():
    assert pricing.REGULAR == {"load_calc": 39, "instant_packet": 89, "city_checked_24h": 149}
    assert pricing.LAUNCH == {"load_calc": 29, "instant_packet": 59, "city_checked_24h": 109}
    assert pricing.PACKS == {"pack_5": 5, "pack_10": 10, "pack_25": 25}
    assert pricing.PACK_REGULAR == {"pack_5": 299, "pack_10": 449, "pack_25": 899}
    assert pricing.PACK_LAUNCH == {"pack_5": 199, "pack_10": 349, "pack_25": 749}
    assert pricing.BONUS_CREDITS == {"pack_5": 6, "pack_10": 13, "pack_25": 33}
    assert pricing.launch_end_label() == "Dec 31"


@pytest.mark.parametrize("now", [BEFORE_BONUS, IN_BONUS, DEC_15])
def test_launch_prices_while_the_offer_runs(now):
    assert pricing.launch_active(now)
    for key in pricing.TIER_KEYS:
        assert pricing.on_sale(key, now)
        assert pricing.price(key, now) == pricing.LAUNCH[key]
        assert pricing.regular_price(key, now) == pricing.REGULAR[key]
    for key in pricing.PACKS:
        assert pricing.pack_price(key, now) == pricing.PACK_LAUNCH[key]


def test_regular_prices_after_the_offer_ends():
    assert not pricing.launch_active(JAN_2)
    for key in pricing.TIER_KEYS:
        assert not pricing.on_sale(key, JAN_2)
        assert pricing.price(key, JAN_2) == pricing.REGULAR[key]
    for key in pricing.PACKS:
        assert pricing.pack_price(key, JAN_2) == pricing.PACK_REGULAR[key]


def test_launch_end_boundary():
    assert pricing.launch_active(at(2026, 12, 31, 23, 59, 59))
    assert not pricing.launch_active(at(2027, 1, 1, 0, 0, 0))
    # the same instant seen from another timezone is still Los Angeles time
    utc = datetime.timezone.utc
    assert pricing.launch_active(datetime.datetime(2027, 1, 1, 7, 59, 59, tzinfo=utc))
    assert not pricing.launch_active(datetime.datetime(2027, 1, 1, 8, 0, 0, tzinfo=utc))


def test_bonus_window():
    assert not pricing.bonus_active(BEFORE_BONUS)
    assert not pricing.bonus_active(at(2026, 11, 26, 23, 59, 59))
    assert pricing.bonus_active(at(2026, 11, 27, 0, 0, 0))
    assert pricing.bonus_active(IN_BONUS)
    assert pricing.bonus_active(at(2026, 12, 1, 23, 59, 59))
    assert not pricing.bonus_active(at(2026, 12, 2, 0, 0, 0))
    assert not pricing.bonus_active(DEC_15) and not pricing.bonus_active(JAN_2)


def test_pack_credits_and_per_credit():
    for key, base in pricing.PACKS.items():
        assert pricing.pack_credits(key, BEFORE_BONUS) == base
        assert pricing.pack_credits(key, IN_BONUS) == pricing.BONUS_CREDITS[key]
        assert pricing.pack_credits(key, DEC_15) == base
        assert pricing.pack_credits(key, JAN_2) == base
    assert pricing.per_credit("pack_5", BEFORE_BONUS) == round(199 / 5, 2) == 39.8
    assert pricing.per_credit("pack_5", IN_BONUS) == round(199 / 6, 2) == 33.17
    assert pricing.per_credit("pack_25", IN_BONUS) == round(749 / 33, 2) == 22.70
    assert pricing.per_credit("pack_10", JAN_2) == round(449 / 10, 2) == 44.9


def test_a_naive_now_is_los_angeles_time():
    assert pricing.launch_active(datetime.datetime(2026, 12, 31, 23, 0))
    assert not pricing.launch_active(datetime.datetime(2027, 1, 1, 0, 0))


def test_tokens_resolve():
    text = "{price:instant_packet} (regularly {regular:instant_packet}) through {launch_end}; {price:load_calc}"
    assert pricing.resolve(text, DEC_15) == "$59 (regularly $89) through Dec 31; $29"
    assert pricing.resolve(text, JAN_2) == "$89 (regularly $89) through Dec 31; $39"
    assert pricing.resolve("no tokens {x:y}", DEC_15) == "no tokens {x:y}"


def test_prices_json_for_js():
    data = pricing.prices_json(DEC_15)
    assert data["onSale"] is True and data["tiers"]["city_checked_24h"] == {
        "price": 109, "regular": 149, "name": "24-Hour City-Checked Packet"}
    assert pricing.prices_json(JAN_2)["tiers"]["load_calc"]["price"] == 39
