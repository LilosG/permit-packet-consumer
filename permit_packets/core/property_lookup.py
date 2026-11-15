"""From a typed address to a property: city, building outlines, lot lines, aerial.

Sources were chosen so the result can go in a printed permit packet:
- US Census geocoder and FEMA/ORNL USA Structures are free public data.
- USGS National Map imagery is public domain.
- Lot lines come from county GIS, where the county is set up in COUNTIES.
- Mapbox satellite is used instead of USGS, and instead of any local orthophoto that is
  not sharper than it, when MAPBOX_TOKEN is set.
- San Francisco building outlines come from the city's own surveyed footprints (DataSF),
  because USA Structures has no outline for many San Francisco lots.
- Photon, built on OpenStreetMap, suggests addresses as the tech types. The chosen
  address still goes through the Census geocoder, so a suggestion is never trusted
  on its own.
"""
from __future__ import annotations

import math
import os
import re
from collections.abc import Callable
from dataclasses import dataclass
from io import BytesIO

import httpx
from PIL import Image, ImageFilter, ImageOps, ImageStat

from permit_packets.jurisdictions import Jurisdiction, jurisdiction_for
from permit_packets.core.property_plan import (
    EARTH_RADIUS_M,
    FEET_PER_METER,
    PLAN_UNITS,
    PLAN_WIDTH_IN,
    Point,
    PlanView,
    centroid,
    clip_to,
    contains,
    ground_distance_ft,
    plan_scale,
)

PHOTON_URL = "https://photon.komoot.io/api/"
CENSUS_URL = "https://geocoding.geo.census.gov/geocoder/geographies/onelineaddress"
STRUCTURES_URL = (
    "https://services2.arcgis.com/FiaPA4ga0iQKduv3/ArcGIS/rest/services/USA_Structures_View/FeatureServer/0/query"
)
USGS_IMAGE_URL = "https://imagery.nationalmap.gov/arcgis/rest/services/USGSNAIPPlus/ImageServer/exportImage"
# Local government orthophotos, much sharper than NAIP. Used first inside their coverage box.
# (west, south, east, north) in degrees, export URL, credit.
LOCAL_AERIALS = (
    (
        (-87.06, 35.96, -86.51, 36.41),
        "https://maps.nashville.gov/arcgis/rest/services/Imagery/2026Imagery_WGS84/MapServer/export",
        "Aerial: Metro Nashville-Davidson County, 2026 imagery",
    ),
    (
        (-84.33, 33.84, -75.46, 36.59),
        "https://services.nconemap.gov/secure/rest/services/Imagery/Orthoimagery_Latest/ImageServer/exportImage",
        "Aerial: NC OneMap, NC Orthoimagery Program (latest)",
    ),
    (
        (-113.34, 32.50, -111.04, 34.05),
        "https://gis.mcassessor.maricopa.gov/arcgis/rest/services/Imagery/Aerials2026/MapServer/export",
        "Aerial: Maricopa County Assessor, 2026 imagery",
    ),
    (
        (-117.60, 32.52, -116.08, 33.51),
        "https://gis-public.sandiegocounty.gov/arcgis/rest/services/COSDBaseMap_Imagery/MapServer/export",
        "Aerial: County of San Diego, 15 cm orthoimagery",
    ),
)
# Ground sample distance in meters of each local orthophoto, from the publisher. Mapbox satellite is
# taken as 0.3 m in built-up areas (Maxar). A local orthophoto at 0.3 m or finer is kept ahead of Mapbox.
LOCAL_AERIAL_GSD_M = {
    "https://maps.nashville.gov/arcgis/rest/services/Imagery/2026Imagery_WGS84/MapServer/export": 0.15,
    "https://services.nconemap.gov/secure/rest/services/Imagery/Orthoimagery_Latest/ImageServer/exportImage": 0.15,
    "https://gis.mcassessor.maricopa.gov/arcgis/rest/services/Imagery/Aerials2026/MapServer/export": 0.15,
    "https://gis-public.sandiegocounty.gov/arcgis/rest/services/COSDBaseMap_Imagery/MapServer/export": 0.15,
}
MAPBOX_GSD_M = 0.3
# Measured displacements, in feet (east, north), found with tools/measure_alignment.py. Every box is the
# city-sized area the measurement was made in; outside it nothing is moved.
#
# FOOTPRINT_SHIFT_FT: the shift that puts building outlines onto their parcels. Outline datasets are drawn from
# imagery or surveyed on their own base, so they sit a few feet from the county parcel base. Measured over
# hundreds of houses and the parcel holding each (bootstrap spread under 1 ft). Listed when 3 ft or more.
# ((west, south, east, north), east_ft, north_ft)
FOOTPRINT_SHIFT_FT: tuple[tuple[tuple[float, float, float, float], float, float], ...] = (
    ((-122.52, 37.70, -122.35, 37.84), 6.0, -4.0),    # San Francisco, city footprints
    ((-86.86, 36.09, -86.74, 36.21), 4.0, -1.0),      # Nashville
    ((-111.86, 33.36, -111.74, 33.48), 8.0, -5.0),    # Mesa
    ((-111.90, 33.245, -111.78, 33.365), 6.0, 5.0),   # Chandler
    ((-117.02, 32.735, -116.90, 32.855), 4.0, -3.0),  # El Cajon
    ((-111.01, 32.356, -110.89, 32.476), 2.0, 3.0),   # Oro Valley
)
# AERIAL_SHIFT_FT: where a picture shows a building, relative to the parcel base. It is the aerial-to-outline
# shift minus the outline-to-parcel shift above, so the outlines' own error drops out. The server is asked for
# a box moved by this much, which moves the picture the opposite way on the plan. Listed only where the
# measurement was stable across windows and 5 ft or more. (west, south, east, north), source, east_ft, north_ft
AERIAL_SHIFT_FT: tuple[tuple[tuple[float, float, float, float], str, float, float], ...] = (
    ((-122.52, 37.70, -122.35, 37.84), "usgs", -20.0, 6.0),   # San Francisco: NAIP sits ~20 ft west of the parcels
    ((-122.52, 37.70, -122.35, 37.84), "mapbox", -22.0, 9.0),  # San Francisco: Mapbox sits ~22 ft west of the parcels
    ((-111.01, 32.356, -110.89, 32.476), "usgs", 6.0, 5.0),   # Oro Valley
)
SF_FOOTPRINTS_URL = "https://data.sf.gov/resource/ynuv-fyni.geojson"
SF_FOOTPRINTS_CREDIT = "Building outlines: City and County of San Francisco, Building Footprints (DataSF)"
SAN_FRANCISCO_FIPS = "06075"
MAPBOX_IMAGE_URL = "https://api.mapbox.com/styles/v1/mapbox/satellite-v9/static/{lon},{lat},{zoom:.2f},0,0/{px}x{px}@2x"



def _quoted(text: str) -> str:
    return text.replace("'", "''")


@dataclass(frozen=True)
class County:
    """A county GIS layer. Only parcel and address fields are read, never owner fields."""
    url: str
    parcel_field: str
    credit: str
    address_fields: str
    address_where: Callable[[str, str], str]
    house_number: Callable[[dict], str]
    # Narrows an address match by street type, where a county has e.g. both 27th Ave and 27th St.
    type_where: Callable[[str], str] | None = None


COUNTIES = {
    "32003": County(
        "https://mapdata.lasvegasnevada.gov/clvgis/rest/services/AdministrativeBoundaries/Parcels/MapServer/0/query",
        "PARCEL", "Lot lines: Clark County Assessor, City of Las Vegas GIS", "STRNO",
        lambda number, street: f"STRNO={int(number)} AND STRNAME='{_quoted(street)}'",
        lambda attributes: str(attributes.get("STRNO") or ""),
    ),
    "04019": County(
        "https://gisdata.pima.gov/arcgis1/rest/services/GISOpenData/LandRecords/MapServer/12/query",
        "PARCEL", "Lot lines: Pima County GIS", "ADDRESS_OL",
        lambda number, street: f"ADDRESS_OL LIKE '{_quoted(number)} %{_quoted(street)}%'",
        lambda attributes: str(attributes.get("ADDRESS_OL") or "").split(" ", 1)[0],
    ),
    "47037": County(
        "https://maps.nashville.gov/arcgis/rest/services/Cadastral/Parcels/MapServer/0/query",
        "APN", "Lot lines: Metro Nashville Planning, Parcels", "PropHouse,PropAddr",
        lambda number, street: f"PropHouse='{_quoted(number)}' AND PropAddr LIKE '{_quoted(number)} %{_quoted(street)}%'",
        lambda attributes: str(attributes.get("PropHouse") or ""),
    ),
    "06075": County(
        "https://sfplanninggis.org/arcgiswa/rest/services/PlanningData/MapServer/23/query",
        "blklot", "Lot lines: San Francisco Planning, Parcels", "from_st,street",
        lambda number, street: f"street='{_quoted(street)}' AND from_st='{_quoted(number)}'",
        lambda attributes: str(attributes.get("from_st") or "").lstrip("0"),
        lambda street_type: f"st_type='{_quoted(street_type.upper())}'",
    ),
    "37119": County(
        "https://meckgis.mecklenburgcountync.gov/server/rest/services/TaxParcel_camadata/FeatureServer/0/query",
        "pid", "Lot lines: Mecklenburg County GIS", "streetnumber,streetname",
        lambda number, street: f"streetnumber='{_quoted(number)}' AND streetname LIKE '{_quoted(street)}%'",
        lambda attributes: str(attributes.get("streetnumber") or ""),
        lambda street_type: f"streetname LIKE '% {_quoted(street_type.upper())}'",
    ),
    "04013": County(
        "https://gis.mcassessor.maricopa.gov/arcgis/rest/services/Parcels/MapServer/0/query",
        "APN_DASH", "Lot lines: Maricopa County Assessor", "PHYSICAL_STREET_NUM,PHYSICAL_STREET_NAME",
        lambda number, street: f"PHYSICAL_STREET_NUM='{_quoted(number)}' AND PHYSICAL_STREET_NAME='{_quoted(street.upper())}'",
        lambda attributes: str(attributes.get("PHYSICAL_STREET_NUM") or "").strip(),
        lambda street_type: f"PHYSICAL_STREET_TYPE='{_quoted(street_type.upper())}'",
    ),
    "04021": County(
        # Pinal County's own GIS host does not resolve; this is Arizona Department of Water Resources' public
        # statewide parcel service (Pinal layer, built from the county's parcel data).
        "https://azwatermaps.azwater.gov/arcgis/rest/services/General/Parcels/MapServer/11/query",
        "APN", "Lot lines: Pinal County parcels via Arizona Department of Water Resources", "SITE_ADDRESS",
        lambda number, street: f"SITE_ADDRESS LIKE '{_quoted(number)} %{_quoted(street.upper())}%'",
        lambda attributes: str(attributes.get("SITE_ADDRESS") or "").split(" ", 1)[0],
        lambda street_type: f"SITE_ADDRESS LIKE '% {_quoted(street_type.upper())}'",
    ),
    "06073": County(
        "https://gis-public.sandiegocounty.gov/arcgis/rest/services/DPW/LEAMS_Reference/MapServer/16/query",
        "APN", "Lot lines: San Diego County GIS", "SITUS_ADDRESS",
        lambda number, street: f"SITUS_ADDRESS={int(number)} AND SITUS_STREET='{_quoted(street)}'",
        lambda attributes: str(attributes.get("SITUS_ADDRESS") or ""),
    ),
}

BUILDING_SEARCH_M = 90
# A better location for the address has to agree roughly with the Census street match.
MAX_LOCATION_DISAGREEMENT_FT = 2000
STRUCTURES_CREDIT = "Building outlines: FEMA/ORNL USA Structures"
USGS_CREDIT = "Map services and data available from U.S. Geological Survey, National Geospatial Program."
MAPBOX_CREDIT = "Imagery © Mapbox © OpenStreetMap © Maxar"
LOOKUP_TIMEOUT = httpx.Timeout(14, connect=6)
AERIAL_TIMEOUT = httpx.Timeout(40, connect=6)
AERIAL_PIXELS = 1400
TARGET_BRIGHTNESS = 110  # mean 0-255; darker pictures are lifted to about this
JPEG_QUALITY = 78
USER_AGENT = "LilosGrowth-PermitPackets/1.0"
SUGGEST_TIMEOUT = httpx.Timeout(5, connect=3)
SUGGESTION_LIMIT = 5
STATE_CODES = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR", "California": "CA", "Colorado": "CO",
    "Connecticut": "CT", "Delaware": "DE", "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA",
    "Hawaii": "HI", "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA", "Kansas": "KS",
    "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME", "Maryland": "MD", "Massachusetts": "MA",
    "Michigan": "MI", "Minnesota": "MN", "Mississippi": "MS", "Missouri": "MO", "Montana": "MT",
    "Nebraska": "NE", "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH", "Oklahoma": "OK",
    "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI", "South Carolina": "SC", "South Dakota": "SD",
    "Tennessee": "TN", "Texas": "TX", "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY",
}
DIRECTION_WORDS = {
    "n": "n", "north": "n", "s": "s", "south": "s", "e": "e", "east": "e", "w": "w", "west": "w",
}
STREET_TYPES = {"st", "street", "ave", "avenue", "dr", "drive", "rd", "road", "ln", "lane", "ct", "court",
                "blvd", "boulevard", "way", "pl", "place", "cir", "circle"}
DIRECTIONS = {"N", "S", "E", "W", "NE", "NW", "SE", "SW"}
LatLon = tuple[float, float]


class AddressNotFound(Exception):
    pass


class AerialUnavailable(Exception):
    pass


@dataclass(frozen=True)
class Match:
    address: str
    latitude: float
    longitude: float
    city: str
    state: str
    county_fips: str
    house_number: str = ""
    street_name: str = ""
    street_type: str = ""  # Census suffixType, e.g. AVE or ST


@dataclass(frozen=True)
class Parcel:
    outline: list[LatLon]
    number: str
    house_number: str


@dataclass(frozen=True)
class FoundProperty:
    address: str
    city: str
    state: str
    county_fips: str
    house_number: str
    jurisdiction: Jurisdiction
    anchor: LatLon
    located_by: str  # county, map, street or tap
    address_confirmed: bool | None
    parcel_house_number: str
    view: PlanView
    buildings: list[list[Point]]
    primary_building: int | None
    lot: list[Point]
    parcel_number: str
    credits: list[str]


def tidy_address(matched: str) -> str:
    """The Census writes addresses in capitals: 12 N OAK ST, TUCSON, AZ, 85701."""
    def word(match: re.Match) -> str:
        text = match.group(0)
        return text if text in DIRECTIONS else text.capitalize()

    parts = [part.strip() for part in matched.split(",")]
    if len(parts) < 4:
        return matched
    street, city, state, zip_code = parts[0], parts[1], parts[-2], parts[-1]
    return f"{re.sub(r'\b[0-9]*[A-Z]+\b', word, street)}, {city.title()}, {state} {zip_code}"


# Consolidated city-counties come back from the Census as e.g.
# "Nashville-Davidson metropolitan government (balance)". The city is the first name.
CONSOLIDATED_PLACE = re.compile(
    r"^([^-]+)-.*\b(metropolitan government|urban county|unified government|consolidated government)\b.*$",
    re.IGNORECASE,
)


def place_name(census_name: str) -> str:
    """The city a Census incorporated-place name stands for."""
    name = census_name.strip()
    consolidated = CONSOLIDATED_PLACE.match(name)
    if consolidated:
        return consolidated.group(1).strip()
    return re.sub(r"\s+(city|town|village|CDP|borough)$", "", name)


def geocode(client: httpx.Client, address: str) -> Match:
    try:
        response = client.get(CENSUS_URL, timeout=LOOKUP_TIMEOUT, params={
            "address": address, "benchmark": "Public_AR_Current", "vintage": "Current_Current",
            "format": "json", "layers": "all",
        })
        response.raise_for_status()
        matches = response.json()["result"]["addressMatches"]
    except (httpx.HTTPError, KeyError, ValueError) as error:
        raise AddressNotFound("The address service didn't respond. Try again.") from error
    if not matches:
        raise AddressNotFound(
            "That exact address wasn't found. Check the street name, and include the city and state."
        )
    match = matches[0]
    geographies = match["geographies"]
    place = next(iter(geographies.get("Incorporated Places") or []), {})
    county = next(iter(geographies.get("Counties") or []), {})
    city = place_name(place.get("NAME", ""))
    parts = match["matchedAddress"].split(",")
    return Match(
        address=tidy_address(match["matchedAddress"]),
        latitude=match["coordinates"]["y"],
        longitude=match["coordinates"]["x"],
        city=city or county.get("NAME", ""),
        state=parts[-2].strip() if len(parts) >= 3 else "",
        county_fips=county.get("GEOID", ""),
        house_number=match["matchedAddress"].split(" ", 1)[0],
        street_name=match.get("addressComponents", {}).get("streetName", ""),
        street_type=match.get("addressComponents", {}).get("suffixType", ""),
    )


def _suggestion(properties: dict, house_number: str) -> str | None:
    """OpenStreetMap lacks many house numbers, so a street match takes the typed number."""
    state = STATE_CODES.get(properties.get("state", ""))
    street = properties.get("street") or (properties.get("name") if properties.get("type") == "street" else None)
    city = properties.get("city") or properties.get("town") or properties.get("district")
    number = properties.get("housenumber") or house_number
    if properties.get("countrycode") != "US" or not (state and street and city and number) or "@" in street:
        return None
    tail = f" {properties['postcode']}" if properties.get("postcode") else ""
    return f"{number} {street}, {city}, {state}{tail}"


def _street_words(text: str) -> tuple[list[str], str | None]:
    """The words that name the street, and any direction typed: 'e naranja dr' is (naranja, e)."""
    words = re.findall(r"[a-z0-9]+", text.lower())
    if words and words[0][0].isdigit():
        words = words[1:]
    direction = next((DIRECTION_WORDS[word] for word in words[:1] if word in DIRECTION_WORDS), None)
    return [word for word in words if word not in DIRECTION_WORDS and word not in STREET_TYPES], direction


def _fits(properties: dict, house_number: str, wanted: list[str], direction: str | None) -> bool:
    street = str(properties.get("street") or properties.get("name") or "").lower().split()
    if house_number and properties.get("housenumber") not in (None, house_number):
        return False
    place = street + str(properties.get("city") or "").lower().split()
    # The first two words name the street. Later ones may be a city with another postal name.
    if not all(any(word.startswith(part) for word in place) for part in wanted[:2]):
        return False
    found = next((DIRECTION_WORDS[word] for word in street[:1] if word in DIRECTION_WORDS), None)
    return not (direction and found and direction != found)


def _photon_search(client: httpx.Client, text: str) -> list[dict]:
    response = client.get(PHOTON_URL, timeout=SUGGEST_TIMEOUT, headers={"User-Agent": USER_AGENT}, params=[
        ("q", text), ("limit", 20), ("lang", "en"), ("layer", "house"), ("layer", "street"),
        ("bbox", "-125,24,-66,50"),
    ])
    response.raise_for_status()
    return response.json().get("features", [])


def suggest_addresses(text: str, client: httpx.Client | None = None) -> list[str]:
    """Best effort: when this fails the tech can still type the whole address."""
    owns_client = client is None
    client = client or httpx.Client(follow_redirects=True)
    leading = re.match(r"\s*(\d+[A-Za-z]?)\s", text)
    house_number = leading.group(1) if leading else ""
    wanted, direction = _street_words(text)
    suggestions: list[str] = []
    searches = [text, text[leading.end():]] if leading else [text]
    try:
        for search in searches:
            for feature in _photon_search(client, search):
                properties = feature.get("properties", {})
                suggestion = _suggestion(properties, house_number)
                if suggestion and suggestion not in suggestions and _fits(properties, house_number, wanted, direction):
                    suggestions.append(suggestion)
            if suggestions:
                break
    except (httpx.HTTPError, ValueError):
        pass
    finally:
        if owns_client:
            client.close()
    return suggestions[:SUGGESTION_LIMIT]


def _rings(feature: dict) -> list[LatLon]:
    ring = feature.get("geometry", {}).get("rings", [[]])[0]
    return [(lat, lon) for lon, lat in ring[:-1]]


def _arcgis_features(client: httpx.Client, url: str, params: dict) -> list[dict]:
    try:
        response = client.get(url, timeout=LOOKUP_TIMEOUT, params={
            "geometryType": "esriGeometryPoint", "inSR": 4326, "outSR": 4326, "f": "json",
            "returnGeometry": "true", "spatialRel": "esriSpatialRelIntersects", **params,
        })
        response.raise_for_status()
        return response.json().get("features", [])
    except (httpx.HTTPError, ValueError):
        return []


def _san_francisco_footprints(client: httpx.Client, point: LatLon, radius_m: float) -> list[dict]:
    """San Francisco's surveyed building outlines, shaped like ArcGIS features so the rest can read them."""
    try:
        response = client.get(SF_FOOTPRINTS_URL, timeout=LOOKUP_TIMEOUT, params={
            "$where": f"within_circle(shape,{point[0]},{point[1]},{round(radius_m)})", "$limit": 300,
        })
        response.raise_for_status()
        shapes = [feature.get("geometry") or {} for feature in response.json().get("features", [])]
    except (httpx.HTTPError, ValueError):
        return []
    features = []
    for shape in shapes:
        polygons = shape.get("coordinates", []) if shape.get("type") == "MultiPolygon" else [shape.get("coordinates", [])]
        for polygon in polygons:
            if polygon and len(polygon[0]) >= 4:
                features.append({"geometry": {"rings": [polygon[0]]}, "attributes": {}})
    return features


def _moved(features: list[dict], point: LatLon) -> list[dict]:
    """Outlines moved onto the county parcel base, where a shift has been measured for this area."""
    east_ft, north_ft = next((
        (east, north) for (west, south, east_edge, north_edge), east, north in FOOTPRINT_SHIFT_FT
        if west <= point[1] <= east_edge and south <= point[0] <= north_edge
    ), (0.0, 0.0))
    if not (east_ft or north_ft):
        return features
    d_lat = north_ft / FEET_PER_METER / 111320
    d_lon = east_ft / FEET_PER_METER / (111320 * math.cos(math.radians(point[0])))
    return [
        {**feature, "geometry": {"rings": [[[lon + d_lon, lat + d_lat] for lon, lat in ring] for ring in feature["geometry"]["rings"]]}}
        for feature in features
    ]


def buildings_around(client: httpx.Client, point: LatLon, radius_m: float, county_fips: str = "") -> list[dict]:
    if county_fips == SAN_FRANCISCO_FIPS:
        city = _san_francisco_footprints(client, point, radius_m)
        if city:
            return _moved(city, point)
    return _moved(_arcgis_features(client, STRUCTURES_URL, {
        "geometry": f"{point[1]},{point[0]}", "distance": round(radius_m),
        "units": "esriSRUnit_Meter", "outFields": "SQFEET",
    }), point)


def footprint_credit(county_fips: str, features: list[dict]) -> str:
    """SQFEET is only on USA Structures records, so its absence marks the city's own outlines."""
    if county_fips == SAN_FRANCISCO_FIPS and features and "SQFEET" not in features[0].get("attributes", {}):
        return SF_FOOTPRINTS_CREDIT
    return STRUCTURES_CREDIT


def pick_building(features: list[dict], point: LatLon) -> dict | None:
    """The building holding the point, else the closest one."""
    if not features:
        return None
    holding = [feature for feature in features if contains(_rings(feature), point)]
    return min(holding or features, key=lambda feature: ground_distance_ft(point, _center(feature)))


def _center(feature: dict) -> LatLon:
    return centroid(_rings(feature))


def _parcel_fields(county: County) -> str:
    return f"{county.parcel_field},{county.address_fields}"


def _parcel(county: County, feature: dict) -> Parcel:
    attributes = feature["attributes"]
    return Parcel(
        _rings(feature), str(attributes.get(county.parcel_field) or "").strip(), county.house_number(attributes),
    )


def parcel_at(client: httpx.Client, county_fips: str, point: LatLon) -> Parcel | None:
    county = COUNTIES.get(county_fips)
    if not county:
        return None
    features = _arcgis_features(client, county.url, {
        "geometry": f"{point[1]},{point[0]}", "outFields": _parcel_fields(county),
    })
    return _parcel(county, features[0]) if features else None


def parcel_for_address(client: httpx.Client, match: Match) -> Parcel | None:
    county = COUNTIES.get(match.county_fips)
    if not county or not match.house_number.isdigit() or not match.street_name:
        return None
    features = _arcgis_features(client, county.url, {
        "where": county.address_where(match.house_number, match.street_name) + (
            f" AND {county.type_where(match.street_type)}" if county.type_where and match.street_type else ""),
        "outFields": _parcel_fields(county),
    })
    features = [feature for feature in features if _rings(feature)]
    return _parcel(county, features[0]) if len(features) == 1 else None


def map_location(client: httpx.Client, match: Match, address: str) -> LatLon | None:
    """The house's own map point, when OpenStreetMap has this exact number."""
    try:
        response = client.get(PHOTON_URL, timeout=SUGGEST_TIMEOUT, headers={"User-Agent": USER_AGENT}, params={
            "q": address, "limit": 5, "lang": "en", "layer": "house", "bbox": "-125,24,-66,50",
        })
        response.raise_for_status()
        features = response.json().get("features", [])
    except (httpx.HTTPError, ValueError):
        return None
    street = match.street_name.lower()
    for feature in features:
        properties = feature.get("properties", {})
        if properties.get("housenumber") != match.house_number:
            continue
        if not street or street not in str(properties.get("street", "")).lower():
            continue
        longitude, latitude = feature["geometry"]["coordinates"]
        point = (latitude, longitude)
        if ground_distance_ft(point, (match.latitude, match.longitude)) <= MAX_LOCATION_DISAGREEMENT_FT:
            return point
    return None


def _extent_ft(points: list[LatLon]) -> tuple[float, LatLon]:
    south, north = min(p[0] for p in points), max(p[0] for p in points)
    west, east = min(p[1] for p in points), max(p[1] for p in points)
    tall = ground_distance_ft((south, west), (north, west))
    wide = ground_distance_ft((south, west), (south, east))
    return max(tall, wide), ((south + north) / 2, (west + east) / 2)


def assemble_property(
    client: httpx.Client,
    *,
    address: str,
    city: str,
    state: str,
    county_fips: str,
    house_number: str,
    point: LatLon,
    located_by: str,
    parcel: Parcel | None = None,
    scale: int | None = None,
    center: LatLon | None = None,
) -> FoundProperty:
    radius = max(BUILDING_SEARCH_M, (scale or 0) * PLAN_WIDTH_IN / FEET_PER_METER * 0.75)
    features = buildings_around(client, point, radius, county_fips)
    primary = pick_building(features, point)
    anchor = _center(primary) if primary and located_by == "street" else point
    parcel = parcel or parcel_at(client, county_fips, anchor)
    lot = parcel.outline if parcel else []
    if lot and primary:
        middle = centroid(lot)
        inside = [
            feature for feature in features
            if contains(lot, _center(feature)) or contains(_rings(feature), middle)
        ]
        primary = pick_building(inside, middle) or primary

    frame = lot or (_rings(primary) if primary else [])
    extent, frame_center = _extent_ft(frame) if frame else (0, anchor)
    if not lot:
        extent = max(extent, 150)
    view = PlanView(*(center or frame_center), scale or plan_scale(extent))

    buildings: list[list[Point]] = []
    primary_index = None
    for feature in features:
        outline = [view.to_plan(lat, lon) for lat, lon in _rings(feature)]
        if not all(0 <= value <= PLAN_UNITS for value in centroid(outline)):
            continue
        if feature is primary:
            primary_index = len(buildings)
            if lot:
                outline = clip_to(outline, [view.to_plan(lat, lon) for lat, lon in lot])
        buildings.append(outline)

    credits = [footprint_credit(county_fips, features)] if features else []
    if lot:
        credits.append(COUNTIES[county_fips].credit)
    on_record = parcel.house_number if parcel else ""
    return FoundProperty(
        address=address, city=city, state=state, county_fips=county_fips, house_number=house_number,
        jurisdiction=jurisdiction_for(city, state), anchor=anchor, located_by=located_by,
        address_confirmed=(on_record == house_number) if on_record and house_number else None,
        parcel_house_number=on_record, view=view, buildings=buildings, primary_building=primary_index,
        lot=[view.to_plan(lat, lon) for lat, lon in lot],
        parcel_number=parcel.number if parcel else "", credits=credits,
    )


def find_property(address: str, client: httpx.Client | None = None) -> FoundProperty:
    """Locate the house itself. The Census only estimates a position along the street."""
    owns_client = client is None
    client = client or httpx.Client(follow_redirects=True)
    try:
        match = geocode(client, address)
        parcel = parcel_for_address(client, match)
        map_point = None if parcel else map_location(client, match, match.address)
        if parcel:
            point, located_by = centroid(parcel.outline), "county"
        elif map_point:
            point, located_by = map_point, "map"
        else:
            point, located_by = (match.latitude, match.longitude), "street"
        return assemble_property(
            client, address=match.address, city=match.city, state=match.state,
            county_fips=match.county_fips, house_number=match.house_number,
            point=point, located_by=located_by, parcel=parcel,
        )
    finally:
        if owns_client:
            client.close()


def property_at(
    *,
    address: str,
    city: str,
    state: str,
    county_fips: str,
    house_number: str,
    point: LatLon,
    located_by: str,
    scale: int | None = None,
    center: LatLon | None = None,
    client: httpx.Client | None = None,
) -> FoundProperty:
    owns_client = client is None
    client = client or httpx.Client(follow_redirects=True)
    try:
        return assemble_property(
            client, address=address, city=city, state=state, county_fips=county_fips,
            house_number=house_number, point=point, located_by=located_by, scale=scale, center=center,
        )
    finally:
        if owns_client:
            client.close()


def _balance(image: Image.Image) -> Image.Image:
    """Stretch the levels and lift shadows. Orthophotos of tree-lined or hilly lots come out dark."""
    image = ImageOps.autocontrast(image, cutoff=0.5)
    mean = ImageStat.Stat(image.convert("L")).mean[0]
    if mean < TARGET_BRIGHTNESS:
        gamma = max(0.55, math.log(TARGET_BRIGHTNESS / 255) / math.log(max(mean, 1) / 255))
        table = [round(255 * (value / 255) ** gamma) for value in range(256)]
        image = image.point(table * 3)
    return image


def _finish(image_bytes: bytes) -> bytes:
    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    if image.width != AERIAL_PIXELS:
        image = image.resize((AERIAL_PIXELS, AERIAL_PIXELS), Image.Resampling.LANCZOS)
    image = _balance(image).filter(ImageFilter.UnsharpMask(radius=2, percent=70, threshold=2))
    buffer = BytesIO()
    image.save(buffer, format="JPEG", quality=JPEG_QUALITY, optimize=True)
    return buffer.getvalue()


def shift_for(view: PlanView, source: str) -> tuple[float, float]:
    """The measured (east, north) feet this source's picture sits from the parcel base around the view."""
    for (west, south, east, north), name, east_ft, north_ft in AERIAL_SHIFT_FT:
        if name == source and west <= view.longitude <= east and south <= view.latitude <= north:
            return east_ft, north_ft
    return 0.0, 0.0


def _mapbox_aerial(client: httpx.Client, view: PlanView, token: str) -> bytes:
    pixels = 1000
    meters_per_pixel = view.size_ft / FEET_PER_METER / pixels
    zoom = math.log2(78271.517 * math.cos(math.radians(view.latitude)) / meters_per_pixel)
    x, y = view.shifted_center(shift_for(view, "mapbox"))
    latitude = math.degrees(2 * math.atan(math.exp(y / EARTH_RADIUS_M)) - math.pi / 2)
    longitude = math.degrees(x / EARTH_RADIUS_M)
    response = client.get(
        MAPBOX_IMAGE_URL.format(lon=longitude, lat=latitude, zoom=zoom, px=pixels),
        params={"access_token": token, "attribution": "false", "logo": "false"},
        timeout=AERIAL_TIMEOUT,
    )
    response.raise_for_status()
    return response.content


def _usgs_aerial(client: httpx.Client, view: PlanView) -> bytes:
    west, south, east, north = view.bbox(shift_for(view, "usgs"))
    response = client.get(USGS_IMAGE_URL, timeout=AERIAL_TIMEOUT, params={
        "bbox": f"{west},{south},{east},{north}", "bboxSR": 102100, "imageSR": 102100,
        "size": "1000,1000", "format": "jpg", "f": "image",
        "interpolation": "RSP_BilinearInterpolation",
    })
    response.raise_for_status()
    if not response.headers.get("content-type", "").startswith("image/"):
        raise httpx.HTTPError("no image returned")
    return response.content


def _local_sources(view: PlanView) -> list[tuple[str, str]]:
    return [
        (url, credit) for (west, south, east, north), url, credit in LOCAL_AERIALS
        if west <= view.longitude <= east and south <= view.latitude <= north
    ]


def _local_aerial(client: httpx.Client, view: PlanView) -> tuple[bytes, str] | None:
    """A local government orthophoto covering the view, if one is set up."""
    for url, credit in _local_sources(view):
        x_min, y_min, x_max, y_max = view.bbox(shift_for(view, url))
        # No finer than half the orthophoto's own pixel: some servers draw nothing past their display scale.
        pixels = min(AERIAL_PIXELS, max(400, math.ceil(view.size_ft / FEET_PER_METER / (LOCAL_AERIAL_GSD_M.get(url, 0.15) / 2))))
        response = client.get(url, timeout=AERIAL_TIMEOUT, params={
            "bbox": f"{x_min},{y_min},{x_max},{y_max}", "bboxSR": 102100, "imageSR": 102100,
            "size": f"{pixels},{pixels}", "format": "jpg", "f": "image",
        })
        response.raise_for_status()
        if not response.headers.get("content-type", "").startswith("image/"):
            raise httpx.HTTPError("no image returned")
        if _blank(response.content):
            continue  # the box reaches past this county's coverage
        return response.content, credit
    return None


def _blank(image: bytes) -> bool:
    """True for a single-color image, which map servers return outside their coverage."""
    low, high = Image.open(BytesIO(image)).convert("L").getextrema()
    return high - low < 8


def fetch_aerial(view: PlanView, client: httpx.Client | None = None) -> tuple[bytes, str]:
    """The sharpest correctly placed picture available: a local orthophoto at least as sharp as Mapbox,
    else Mapbox when a token is set, else a coarser local orthophoto, else USGS."""
    owns_client = client is None
    client = client or httpx.Client(follow_redirects=True)
    token = os.environ.get("MAPBOX_TOKEN")
    local_is_sharp = any(LOCAL_AERIAL_GSD_M.get(url, 1.0) <= MAPBOX_GSD_M for url, _ in _local_sources(view))

    def local() -> tuple[bytes, str] | None:
        found = _local_aerial(client, view)
        return (found[0], found[1]) if found else None

    def mapbox() -> tuple[bytes, str] | None:
        return (_mapbox_aerial(client, view, token), MAPBOX_CREDIT) if token else None

    try:
        for source in ((local, mapbox) if local_is_sharp or not token else (mapbox, local)):
            try:
                found = source()
            except (httpx.HTTPError, OSError):
                continue
            if found:
                return _finish(found[0]), found[1]
        for _ in range(2):
            try:
                return _finish(_usgs_aerial(client, view)), USGS_CREDIT
            except (httpx.HTTPError, OSError):
                continue
    finally:
        if owns_client:
            client.close()
    raise AerialUnavailable("The aerial photo didn't load. The plan still works from the building and lot data.")

