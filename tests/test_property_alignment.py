"""The lot outline, building footprint and street have to line up on the plan, in every county we pull from.

Each case is one real residential parcel. tests/fixtures/alignment/<name>.json holds exactly what the public
services returned for it (Census geocode, county parcel layer, building outlines, Census street centerline),
with no owner data. The real find_property runs over those responses, so the county's coordinate system,
the reprojection to latitude and longitude and the scaling onto the 1000 unit plan are all exercised.

Tolerance is 3 ft, set by TOLERANCE_FT.
"""
from __future__ import annotations

import json
import math
from pathlib import Path

import httpx
import pytest

from permit_packets.core import property_lookup as pl
from permit_packets.core.property_plan import centroid, contains, distance_to_segment

FIXTURES = Path(__file__).parent / "fixtures" / "alignment"
TOLERANCE_FT = 3.0
# name -> (county fips, what the county calls the parcel service, native coordinate system of that layer)
CASES = {
    "san_francisco": ("06075", "San Francisco Planning parcels", "WGS84 degrees"),
    "nashville": ("47037", "Metro Nashville parcels", "TN State Plane ft (EPSG:2274)"),
    "mesa": ("04013", "Maricopa County Assessor parcels", "Web Mercator (EPSG:3857)"),
    "chandler": ("04013", "Maricopa County Assessor parcels", "Web Mercator (EPSG:3857)"),
    "san_tan_valley": ("04021", "Pinal parcels via Arizona Dept of Water Resources", "UTM 12N (EPSG:26912)"),
    "el_cajon": ("06073", "San Diego County parcels", "CA State Plane VI ft (EPSG:2230)"),
    "oro_valley": ("04019", "Pima County parcels", "AZ Central State Plane ft (EPSG:2868)"),
    "las_vegas": ("32003", "Clark County / City of Las Vegas parcels", "NV East State Plane ft (EPSG:3421)"),
    "charlotte": ("37119", "Mecklenburg County parcels", "NC State Plane ft (EPSG:2264)"),
}


def _fixture(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text())


def _client(fixture: dict, fips: str) -> httpx.Client:
    county_host = httpx.URL(pl.COUNTIES[fips].url).host
    census = {"result": {"addressMatches": [{
        "matchedAddress": fixture["census"]["matchedAddress"],
        "coordinates": fixture["census"]["coordinates"],
        "addressComponents": fixture["census"]["addressComponents"],
        "geographies": fixture["census"]["geographies"],
    }]}}

    def serve(request: httpx.Request) -> httpx.Response:
        host = request.url.host
        if host == "geocoding.geo.census.gov":
            return httpx.Response(200, json=census)
        if host == county_host:
            return httpx.Response(200, json=fixture["parcel"])
        if host == httpx.URL(pl.SF_FOOTPRINTS_URL).host:
            return httpx.Response(200, json=fixture.get("footprints", {"features": []}))
        if host == httpx.URL(pl.STRUCTURES_URL).host:
            return httpx.Response(200, json=fixture.get("buildings", {"features": []}))
        return httpx.Response(200, json={"features": []})

    return httpx.Client(transport=httpx.MockTransport(serve))


def _distance_to_polygon(point, polygon) -> float:
    """0 inside the polygon, else the plan distance to its nearest edge."""
    if contains(polygon, point):
        return 0.0
    return min(distance_to_segment(point, a, b) for a, b in zip(polygon, polygon[1:] + polygon[:1]))


def _heading(a, b) -> float:
    return math.degrees(math.atan2(b[1] - a[1], b[0] - a[0])) % 180


def _angle_between(first: float, second: float) -> float:
    gap = abs(first - second) % 180
    return min(gap, 180 - gap)


def measure(name: str) -> dict:
    """Run one case and return its alignment numbers in feet."""
    fips = CASES[name][0]
    fixture = _fixture(name)
    client = _client(fixture, fips)
    found = pl.find_property(fixture["address"], client)
    view, feet = found.view, found.view.feet_per_unit
    assert found.located_by == "county" and len(found.lot) >= 4, "the county parcel was not used"

    # Raw footprints, before the plan clips the house to its lot, so a misplaced outline is not hidden.
    lot_ll = [view.to_latlon(*point) for point in found.lot]
    features = pl.buildings_around(client, centroid(lot_ll), 90, fips)
    middle = centroid(lot_ll)
    inside = [
        feature for feature in features
        if contains(lot_ll, pl._center(feature)) or contains(pl._rings(feature), middle)
    ]
    house = pl.pick_building(inside, middle)
    assert house is not None, "no building outline sits on the lot"
    footprint = [view.to_plan(lat, lon) for lat, lon in pl._rings(house)]
    excursion = max(_distance_to_polygon(point, found.lot) for point in footprint) * feet

    # Frontage: the lot edge that runs along the address's street.
    street_paths = [[view.to_plan(lat, lon) for lon, lat in path] for path in fixture["street"]["paths"]]
    street_segments = [(a, b) for path in street_paths for a, b in zip(path, path[1:])]
    assert street_segments, "no street centerline in the fixture"
    best = None
    for a, b in zip(found.lot, found.lot[1:] + found.lot[:1]):
        if math.dist(a, b) * feet < 15:
            continue
        nearest = min(street_segments, key=lambda s: distance_to_segment(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), *s))
        if _angle_between(_heading(a, b), _heading(*nearest)) > 20:
            continue
        gap = distance_to_segment(((a[0] + b[0]) / 2, (a[1] + b[1]) / 2), *nearest) * feet
        if best is None or gap < best[0]:
            best = (gap, a, b)
    assert best is not None, "no lot edge runs along the street"
    street_gap, a, b = best
    # How far the house reaches past the front lot line, toward the street.
    inward = centroid(found.lot)
    side = (b[0] - a[0]) * (inward[1] - a[1]) - (b[1] - a[1]) * (inward[0] - a[0])
    length = math.dist(a, b)
    past_front = 0.0
    for point in footprint:
        signed = ((b[0] - a[0]) * (point[1] - a[1]) - (b[1] - a[1]) * (point[0] - a[0])) / length
        past_front = max(past_front, (-signed if side > 0 else signed) * feet)

    # The plan must hand back the county's own coordinates: plan -> latitude/longitude -> plan.
    round_trip = max(
        math.dist(view.to_plan(*view.to_latlon(*point)), point) for point in found.lot + footprint
    ) * feet
    return {
        "excursion_ft": excursion, "past_front_ft": past_front, "street_gap_ft": street_gap,
        "round_trip_ft": round_trip, "footprint_credit": pl.footprint_credit(fips, features),
        "scale": view.scale_ft_per_in,
    }


@pytest.mark.parametrize("name", sorted(CASES))
def test_lot_outline_lines_up_with_house_and_street(name):
    numbers = measure(name)
    assert numbers["round_trip_ft"] < 0.2, "plan coordinates drift from latitude/longitude"
    assert numbers["excursion_ft"] <= TOLERANCE_FT, (
        f"the house sticks {numbers['excursion_ft']:.1f} ft outside the lot outline")
    assert numbers["past_front_ft"] <= TOLERANCE_FT, (
        f"the house reaches {numbers['past_front_ft']:.1f} ft past the front property line")
    # A front lot line sits one right-of-way half width back from the street centerline.
    assert 8 <= numbers["street_gap_ft"] <= 80, f"front lot line is {numbers['street_gap_ft']:.0f} ft from the street"


def test_san_francisco_uses_the_citys_footprints_because_usa_structures_misses_the_lot():
    numbers = measure("san_francisco")
    assert "San Francisco" in numbers["footprint_credit"]


def test_every_county_source_has_an_alignment_case():
    covered = {fips for fips, _, _ in CASES.values()}
    assert covered == set(pl.COUNTIES), "a county was added without an alignment case"


def test_moving_the_view_center_moves_the_aerial_box_the_same_distance():
    """The aerial is asked for with the same box the plan is drawn in, so a shift moves them together."""
    view = pl.PlanView(37.776, -122.4327, 20)
    west, south, east, north = view.bbox()
    shifted = view.bbox((-20, 0))
    metres_per_foot = 1 / pl.FEET_PER_METER / math.cos(math.radians(view.latitude))
    assert shifted[0] - west == pytest.approx(-20 * metres_per_foot)
    assert shifted[3] - north == pytest.approx(0)
    assert east - west == pytest.approx(shifted[2] - shifted[0])


def _jpeg(color) -> bytes:
    from io import BytesIO
    from PIL import Image
    import random
    image = Image.new("RGB", (60, 60), color)
    pixels = image.load()
    for x in range(60):
        for y in range(60):
            pixels[x, y] = tuple(min(255, max(0, c + random.randint(-12, 12))) for c in color)
    out = BytesIO()
    image.save(out, "JPEG")
    return out.getvalue()


def test_parcels_are_never_moved_only_outlines_are():
    fixture = _fixture("nashville")
    client = _client(fixture, "47037")
    ring = fixture["parcel"]["features"][0]["geometry"]["rings"][0]
    found = pl.find_property(fixture["address"], client)
    back = [found.view.to_latlon(*p) for p in found.lot]
    assert max(
        pl.ground_distance_ft((lat, lon), (b_lat, b_lon))
        for (lon, lat), (b_lat, b_lon) in zip(ring[:-1], back)
    ) < 0.2


def test_outlines_move_by_the_measured_feet_inside_the_area_and_not_outside(monkeypatch):
    feature = {"geometry": {"rings": [[[-86.80, 36.15], [-86.80, 36.1501], [-86.7999, 36.15], [-86.80, 36.15]]]}}
    moved = pl._moved([feature], (36.15, -86.80))[0]["geometry"]["rings"][0][0]
    east = pl.ground_distance_ft((36.15, -86.80), (36.15, moved[0]))
    assert east == pytest.approx(4.0, abs=0.05)
    assert pl._moved([feature], (40.0, -100.0))[0] is feature


def test_san_francisco_aerial_is_asked_for_in_a_box_moved_by_the_measured_shift(monkeypatch):
    monkeypatch.delenv("MAPBOX_TOKEN", raising=False)
    seen = []

    def serve(request: httpx.Request) -> httpx.Response:
        seen.append(request.url.params["bbox"])
        return httpx.Response(200, content=_jpeg((90, 90, 90)), headers={"content-type": "image/jpeg"})

    view = pl.PlanView(37.776, -122.4327, 20)
    pl.fetch_aerial(view, httpx.Client(transport=httpx.MockTransport(serve)))
    assert seen == [",".join(map(str, view.bbox((-20, 6))))]


def test_dark_aerials_are_lifted():
    from io import BytesIO
    from PIL import Image, ImageStat
    out = Image.open(BytesIO(pl._finish(_jpeg((35, 35, 40)))))
    assert ImageStat.Stat(out.convert("L")).mean[0] > 85


def test_local_orthophoto_is_asked_for_no_finer_than_it_can_draw():
    sizes = []

    def serve(request: httpx.Request) -> httpx.Response:
        sizes.append(int(request.url.params["size"].split(",")[0]))
        return httpx.Response(200, content=_jpeg((120, 110, 90)), headers={"content-type": "image/jpeg"})

    _, credit = pl.fetch_aerial(pl.PlanView(32.7935, -116.958, 30), httpx.Client(transport=httpx.MockTransport(serve)))
    assert "San Diego" in credit and sizes[0] < pl.AERIAL_PIXELS


def test_mapbox_goes_ahead_of_usgs_and_coarse_sources_but_not_sharp_local_orthophotos(monkeypatch):
    monkeypatch.setenv("MAPBOX_TOKEN", "pk.test")

    def first_host(view) -> str:
        hosts = []

        def serve(request: httpx.Request) -> httpx.Response:
            hosts.append(request.url.host)
            return httpx.Response(200, content=_jpeg((120, 110, 90)), headers={"content-type": "image/jpeg"})

        pl.fetch_aerial(view, httpx.Client(transport=httpx.MockTransport(serve)))
        return hosts[0]

    assert first_host(pl.PlanView(36.17, -115.14, 30)) == "api.mapbox.com"      # Las Vegas, no local orthophoto
    assert first_host(pl.PlanView(37.776, -122.4327, 20)) == "api.mapbox.com"   # San Francisco
    assert first_host(pl.PlanView(36.15, -86.80, 30)) == "maps.nashville.gov"   # 15 cm local orthophoto


def _gradient_tile(column: int, row: int, size: int = 512) -> bytes:
    """A tile whose red channel counts global x pixels (three per step) and green counts global y, so where a
    stitched picture came from can be read back from its pixels."""
    import numpy as np
    from io import BytesIO
    from PIL import Image

    xs = (column * size + np.arange(size)) // 3 % 256
    ys = (row * size + np.arange(size)) // 3 % 256
    pixels = np.zeros((size, size, 3), dtype=np.uint8)
    pixels[:, :, 0] = xs[None, :]
    pixels[:, :, 1] = ys[:, None]
    pixels[:, :, 2] = 128
    out = BytesIO()
    Image.fromarray(pixels).save(out, "JPEG", quality=95, subsampling=0)
    return out.getvalue()


def _tile_server(requests: list[tuple[int, int, int]]):
    def serve(request: httpx.Request) -> httpx.Response:
        z, x, y = request.url.path.split("/v4/mapbox.satellite/")[1].split("@")[0].split("/")
        requests.append((int(z), int(x), int(y)))
        return httpx.Response(200, content=_gradient_tile(int(x), int(y)), headers={"content-type": "image/jpeg"})
    return httpx.Client(transport=httpx.MockTransport(serve))


def _picture(view: pl.PlanView, shifted: bool = True):
    from io import BytesIO
    from PIL import Image
    requests: list[tuple[int, int, int]] = []
    raw = pl._mapbox_aerial(_tile_server(requests), view, "pk.test", shifted=shifted)
    return Image.open(BytesIO(raw)).convert("RGB"), requests


def test_mapbox_is_asked_for_z19_tiles_at_double_size_that_resolve_015_m_or_finer():
    for latitude, longitude, scale in ((37.776, -122.4327, 20), (36.17, -115.14, 40), (33.4, -111.8, 100), (35.2, -80.83, 30)):
        view = pl.PlanView(latitude, longitude, scale)
        picture, requests = _picture(view)
        assert {z for z, _, _ in requests} == {19}
        ground_m_per_pixel = view.size_ft / pl.FEET_PER_METER / picture.width
        assert ground_m_per_pixel <= 0.15, f"{ground_m_per_pixel:.3f} m per pixel at {scale} ft/in"
        assert picture.width == picture.height and len(requests) <= pl.MAPBOX_TILE_LIMIT
    assert pl.mapbox_zoom(37.776) == 19


def test_stitched_mapbox_tiles_have_no_seam_where_two_tiles_meet():
    import numpy as np
    zoom, column = 19, 83_850
    longitude = column / 2 ** zoom * 360 - 180  # the left edge of a tile column, so the view straddles two tiles
    picture, requests = _picture(pl.PlanView(37.776, longitude, 20))
    assert len({x for _, x, _ in requests}) >= 2
    red = np.asarray(picture)[picture.height // 2, :, 0].astype(float)
    ahead = red[16:] - red[:-16]  # three pixels per red step, so 16 pixels is 16/3 steps wherever the row is
    clear = (red[:-16] > 12) & (red[16:] < 243) & (red[:-16] < red[16:] + 1)  # skip the places where red wraps
    assert clear.sum() > picture.width // 2
    assert np.abs(ahead[clear] - 16 / 3).max() < 3.5


def test_mapbox_shift_moves_the_picture_by_the_measured_feet():
    import numpy as np
    view = pl.PlanView(37.776, -122.4327, 20)  # inside the San Francisco shift box: 22 ft west, 9 ft north
    moved, _ = _picture(view)
    plain, _ = _picture(view, shifted=False)
    assert moved.size == plain.size
    centre = lambda im, band: np.asarray(im)[im.height // 2 - 8:im.height // 2 + 8, im.width // 2 - 8:im.width // 2 + 8, band].astype(float).mean()
    metres_per_pixel = view.size_ft / pl.FEET_PER_METER / plain.width
    west_px = (centre(plain, 0) - centre(moved, 0)) * 3   # red counts three pixels per step
    north_px = (centre(plain, 1) - centre(moved, 1)) * 3
    assert west_px * metres_per_pixel * pl.FEET_PER_METER == pytest.approx(22, abs=1.5)
    assert north_px * metres_per_pixel * pl.FEET_PER_METER == pytest.approx(9, abs=1.5)


def _mapbox_features(*addresses: tuple[str, str, str, str]) -> dict:
    return {"features": [{"properties": {
        "name": street, "name_preferred": street,
        "context": {"place": {"name": city}, "region": {"region_code": state}, "postcode": {"name": postcode}},
    }} for street, city, state, postcode in addresses]}


def test_suggestions_come_from_mapbox_with_its_zip_codes_and_one_line_per_street_and_city(monkeypatch):
    monkeypatch.setenv("MAPBOX_TOKEN", "pk.test")
    seen = []

    def serve(request: httpx.Request) -> httpx.Response:
        seen.append(request.url)
        return httpx.Response(200, json=_mapbox_features(
            ("710 Steiner Street", "San Francisco", "CA", "94117"),
            ("710 Steiner Street", "San Francisco", "CA", "94115"),   # same street and city: dropped
            ("710 Steiner Street", "San Jose", "CA", "95115"),
            ("Steiner Street", "San Francisco", "CA", "94117"),        # no house number: not an address
        ))

    suggestions = pl.suggest_addresses("710 Steiner", httpx.Client(transport=httpx.MockTransport(serve)))
    assert suggestions == ["710 Steiner Street, San Francisco, CA 94117", "710 Steiner Street, San Jose, CA 95115"]
    assert [u.host for u in seen] == ["api.mapbox.com"]
    assert seen[0].params["access_token"] == "pk.test" and seen[0].params["country"] == "us"


def test_photon_is_used_for_suggestions_only_without_a_token(monkeypatch):
    hosts = []

    def serve(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        return httpx.Response(200, json={"features": [{"properties": {
            "countrycode": "US", "housenumber": "710", "street": "Steiner Street", "city": "San Francisco",
            "state": "California", "postcode": "94115"}}]})

    client = httpx.Client(transport=httpx.MockTransport(serve))
    assert pl.suggest_addresses("710 Steiner", client) == ["710 Steiner Street, San Francisco, CA 94115"]
    assert hosts and set(hosts) == {"photon.komoot.io"}
    monkeypatch.setenv("MAPBOX_TOKEN", "pk.test")
    hosts.clear()
    pl.suggest_addresses("710 Steiner", client)
    assert set(hosts) == {"api.mapbox.com"}


def test_a_failed_mapbox_lookup_gives_no_suggestions_and_does_not_fall_back_to_photon(monkeypatch):
    monkeypatch.setenv("MAPBOX_TOKEN", "pk.test")
    hosts = []

    def serve(request: httpx.Request) -> httpx.Response:
        hosts.append(request.url.host)
        return httpx.Response(401)

    assert pl.suggest_addresses("710 Steiner", httpx.Client(transport=httpx.MockTransport(serve))) == []
    assert set(hosts) == {"api.mapbox.com"}
