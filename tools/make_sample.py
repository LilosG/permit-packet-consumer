"""Regenerate the homepage sample sheets from one real lookup.

Pages are rendered 4000 px wide and downsampled to 300 / 1000 / 2000 px WebP (quality 90).

The sample job: EV charger, 48 A, 200 A panel, El Cajon CA, owner-builder, charger at a detached garage.
It runs the same lookup and packet build the site does, so the images, the homepage cards and the wizard
sample all carry the same numbers.

    python tools/make_sample.py            # writes permit_packets/static/assets/samples/*, prints the numbers
    python tools/make_sample.py --dry-run  # prints the numbers only

Needs network access (Census geocoder, San Diego County GIS, USA Structures).
"""
from __future__ import annotations

import base64
import io
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import pypdfium2  # noqa: E402
from PIL import Image  # noqa: E402

from app import _build, _property_json  # noqa: E402
from permit_packets.core.property_lookup import find_property, fetch_aerial  # noqa: E402
from permit_packets.core.property_plan import PlanView  # noqa: E402

SAMPLE_ADDRESS = "453 Brockton St, El Cajon, CA 92020"
OUT = ROOT / "permit_packets" / "static" / "assets" / "samples"
RISE_ALLOWANCE_FT = 10  # the same allowance the form adds to the measured route (ev-charger.js)
CHARGER_MODEL = "Tesla Wall Connector (Gen 3)"


def _centroid(poly):
    return sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)


def _nearest_edge_midpoint(poly, toward, inset=0.0):
    """The midpoint of the polygon's edge nearest `toward`, moved `inset` plan units toward the polygon's center."""
    cx, cy = _centroid(poly)
    best = min(
        (((a[0] + b[0]) / 2, (a[1] + b[1]) / 2) for a, b in zip(poly, poly[1:] + poly[:1])),
        key=lambda m: math.dist(m, toward))
    dx, dy = cx - best[0], cy - best[1]
    n = math.hypot(dx, dy) or 1
    return [round(best[0] + dx / n * inset, 1), round(best[1] + dy / n * inset, 1)]


def _area(poly):
    return abs(sum(poly[i - 1][0] * poly[i][1] - poly[i][0] * poly[i - 1][1] for i in range(len(poly)))) / 2


def build_request() -> dict:
    found = _property_json(find_property(SAMPLE_ADDRESS), "ev_charger")
    view = found["view"]
    house = found["buildings"][found["primary_building"]]
    others = [b for i, b in enumerate(found["buildings"]) if i != found["primary_building"]
              and _inside(_centroid(b), found["lot"])]
    garage = min(others, key=lambda b: math.dist(_centroid(b), _centroid(house)))
    panel = _nearest_edge_midpoint(house, _centroid(garage), inset=6)
    charger = _nearest_edge_midpoint(garage, _centroid(house), inset=0)
    aerial, credit = fetch_aerial(PlanView(view["latitude"], view["longitude"], view["scale_ft_per_in"]))
    credits = [c for c in found["credits"] if not c.startswith("Building")] + [credit]
    feet = math.dist(panel, charger) * view["feet_per_unit"]
    measured = round(feet)
    return {
        "customer": "Sample Homeowner",
        "address": found["address"],
        "contractor": "Homeowner (Owner-Builder)",
        "license_number": "Owner-Builder",
        "city": found["city"], "state": found["state"], "jurisdiction_key": found["jurisdiction"]["key"],
        "charger_model": CHARGER_MODEL, "charger_amps": 48, "connection": "hardwired",
        "location": "detached_garage",
        "run_ft": measured + RISE_ALLOWANCE_FT, "trench_ft": measured,
        "service_amps": 200, "open_breaker_spaces": 4,
        "home": {"square_feet": 2000, "range_va": 12000, "dryer_va": 5000, "water_heater_va": 4500,
                 "dishwasher_va": 1200, "disposal_va": 900, "microwave_va": 1500, "cooling_va": 7200},
        "plan": {
            "scale_ft_per_in": view["scale_ft_per_in"],
            "markers": {"panel": panel, "charger": charger}, "route": [],
            "buildings": found["buildings"], "primary_building": found["primary_building"], "lot": found["lot"],
            "parcel_number": found["parcel_number"], "aerial_base64": base64.b64encode(aerial).decode(),
            "credits": credits,
        },
    }


def _inside(pt, poly):
    x, y = pt
    c = False
    for i in range(len(poly)):
        x1, y1 = poly[i]
        x2, y2 = poly[i - 1]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def render(pdf: bytes) -> list[Image.Image]:
    doc = pypdfium2.PdfDocument(pdf)
    return [doc[i].render(scale=4000 / doc[i].get_width()).to_pil().convert("RGB") for i in range(len(doc))]


def main(dry_run: bool) -> None:
    request = build_request()
    job_type, result = _build("ev-charger", request, preview=False)
    body = result.body
    pages = render(result.pdf)
    text = [pypdfium2.PdfDocument(result.pdf)[i].get_textpage().get_text_range() for i in range(len(pages))]
    spec = next(i for i, t in enumerate(text) if "PRODUCT OVERVIEW" in t.upper() and i > 6)
    chosen = {"01-cover": 0, "02-site-plan": 2, "03-single-line": 3, "04-load-calc": 4, "05-spec-sheet": spec}
    print(json.dumps({k: body[k] for k in ("computed_amps", "total_va", "spare_amps", "breaker", "wire", "ground",
                                            "underground_conduit", "interior_conduit", "address")}, indent=1))
    print("parcel", request["plan"]["parcel_number"], "run_ft", request["run_ft"], "trench_ft", request["trench_ft"],
          "pages", len(pages), "spec page", spec + 1)
    if dry_run:
        return
    for name, index in chosen.items():
        image = pages[index]
        # 300 px tab thumbnail, 1000 px viewer, 2000 px lightbox zoom. All WebP q90; the page render is 2x the
        # zoom size so each is a LANCZOS downsample, never an upscale. No PNG is written.
        for width in (300, 1000, 2000):
            height = round(image.height * width / image.width)
            image.resize((width, height), Image.LANCZOS).save(OUT / f"{name}-{width}.webp", quality=90, method=6)
    # The link-preview image (og:image) is a JPEG because not every crawler reads WebP.
    site = pages[chosen["02-site-plan"]]
    site.resize((1200, round(site.height * 1200 / site.width)), Image.LANCZOS).save(
        OUT / "02-site-plan-og.jpg", quality=90, subsampling=0, optimize=True)

if __name__ == "__main__":
    main("--dry-run" in sys.argv)
