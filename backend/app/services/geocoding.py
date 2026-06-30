from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta, timezone as dt_timezone
from json import loads
from typing import Any
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"
TIMEZONE_API_URL = "https://timeapi.io/api/TimeZone/coordinate"
USER_AGENT = "KPAstroGem/0.2 (+local-dev geocoding)"


@dataclass
class LocationCandidate:
    display_name: str
    city: str
    state_or_province: str | None
    country: str | None
    latitude: float
    longitude: float
    timezone: str | None
    confidence: float


@dataclass
class ValidatedLocation:
    normalized_utc_time: str
    confidence: float
    warnings: list[str]


@dataclass
class TimezoneLookup:
    timezone: str | None
    utc_offset_seconds: int | None


def search_locations(query: str, state: str | None = None, country: str | None = None) -> list[LocationCandidate]:
    normalized_query = query.strip()
    if not normalized_query:
        return []
    normalized_state = state.strip() if state and state.strip() else None
    normalized_country = country.strip() if country and country.strip() else None

    query_parts = [normalized_query]
    if normalized_state:
        query_parts.append(normalized_state)
    if normalized_country:
        query_parts.append(normalized_country)

    params = urlencode(
        {
            "q": ", ".join(query_parts),
            "format": "jsonv2",
            "addressdetails": 1,
            "limit": 5,
        }
    )
    request = Request(
        f"{NOMINATIM_SEARCH_URL}?{params}",
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )

    with urlopen(request, timeout=10) as response:
        payload = loads(response.read().decode("utf-8"))

    candidates = [
        _to_location_candidate(
            item,
            query=normalized_query,
            requested_state=normalized_state,
            requested_country=normalized_country,
        )
        for item in payload
    ]
    deduplicated: list[LocationCandidate] = []
    seen_keys: set[tuple[str, str | None, str | None]] = set()

    for candidate in sorted(candidates, key=lambda item: item.confidence, reverse=True):
        key = (
            candidate.city.casefold(),
            candidate.state_or_province.casefold() if candidate.state_or_province else None,
            candidate.country.casefold() if candidate.country else None,
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduplicated.append(candidate)

    return deduplicated[:5]


def resolve_timezone(latitude: float, longitude: float) -> str | None:
    result = _lookup_timezone(latitude, longitude)
    return result.timezone


def _lookup_timezone(latitude: float, longitude: float) -> TimezoneLookup:
    params = urlencode(
        {
            "latitude": latitude,
            "longitude": longitude,
        }
    )
    request = Request(
        f"{TIMEZONE_API_URL}?{params}",
        headers={
            "Accept": "application/json",
            "User-Agent": USER_AGENT,
        },
    )

    with urlopen(request, timeout=10) as response:
        payload = loads(response.read().decode("utf-8"))

    timezone_name = payload.get("timeZone")
    current_offset = payload.get("currentUtcOffset", {})

    return TimezoneLookup(
        timezone=str(timezone_name) if timezone_name else None,
        utc_offset_seconds=int(current_offset["seconds"]) if "seconds" in current_offset else None,
    )


def validate_location(
    *,
    birth_place: str,
    state: str | None,
    country: str,
    latitude: float,
    longitude: float,
    timezone: str,
    date_of_birth: str,
    time_of_birth: str,
) -> ValidatedLocation:
    warnings: list[str] = []
    confidence = 0.92

    if not state:
        warnings.append("State or province was not provided, so the location confidence is slightly reduced.")
        confidence -= 0.06

    timezone_lookup = _lookup_timezone(latitude=latitude, longitude=longitude)
    if timezone_lookup.timezone and timezone_lookup.timezone != timezone:
        warnings.append(
            f"The selected timezone was adjusted from {timezone} to {timezone_lookup.timezone} based on the resolved coordinates."
        )
        timezone = timezone_lookup.timezone
        confidence -= 0.04
    elif not timezone_lookup.timezone:
        warnings.append("Timezone lookup could not be revalidated from coordinates during this check.")
        confidence -= 0.08

    local_datetime = datetime.fromisoformat(f"{date_of_birth}T{time_of_birth}")
    try:
        utc_datetime = local_datetime.replace(tzinfo=ZoneInfo(timezone)).astimezone(UTC)
    except ZoneInfoNotFoundError:
        if timezone_lookup.utc_offset_seconds is None:
            raise

        fallback_timezone = dt_timezone(timedelta(seconds=timezone_lookup.utc_offset_seconds))
        utc_datetime = local_datetime.replace(tzinfo=fallback_timezone).astimezone(UTC)
        warnings.append(
            f"The local timezone database could not resolve {timezone}, so a fixed UTC offset fallback was used for normalization."
        )
        confidence -= 0.05

    warnings.append(
        f"Birth details were normalized for {birth_place}, {country} using timezone {timezone}. Historical DST edge cases are not fully audited in this version."
    )

    return ValidatedLocation(
        normalized_utc_time=utc_datetime.isoformat(),
        confidence=max(0.5, min(0.99, round(confidence, 2))),
        warnings=warnings,
    )


def _to_location_candidate(
    item: dict[str, Any],
    *,
    query: str,
    requested_state: str | None,
    requested_country: str | None,
) -> LocationCandidate:
    address = item.get("address", {})
    city = str(
        address.get("city")
        or address.get("town")
        or address.get("village")
        or address.get("municipality")
        or address.get("county")
        or item.get("name")
        or item.get("display_name", "").split(",")[0]
    )
    state_or_province = address.get("state") or address.get("region") or address.get("state_district")
    country = address.get("country")
    latitude = float(item["lat"])
    longitude = float(item["lon"])
    timezone = resolve_timezone(latitude=latitude, longitude=longitude)
    confidence = _estimate_confidence(
        query=query,
        city=city,
        state_or_province=state_or_province,
        country=country,
        timezone=timezone,
        requested_state=requested_state,
        requested_country=requested_country,
    )

    return LocationCandidate(
        display_name=str(item.get("display_name", city)),
        city=city,
        state_or_province=str(state_or_province) if state_or_province else None,
        country=str(country) if country else None,
        latitude=latitude,
        longitude=longitude,
        timezone=timezone,
        confidence=confidence,
    )


def _estimate_confidence(
    *,
    query: str,
    city: str,
    state_or_province: str | None,
    country: str | None,
    timezone: str | None,
    requested_state: str | None,
    requested_country: str | None,
) -> float:
    score = 0.58
    if city.casefold() == query.casefold():
        score += 0.18
    elif city.casefold().startswith(query.casefold()):
        score += 0.1
    if state_or_province:
        score += 0.1
    if requested_state and state_or_province and state_or_province.casefold() == requested_state.casefold():
        score += 0.07
    if country:
        score += 0.08
    if requested_country and country and country.casefold() == requested_country.casefold():
        score += 0.07
    if timezone:
        score += 0.08

    return round(min(score, 0.98), 2)
