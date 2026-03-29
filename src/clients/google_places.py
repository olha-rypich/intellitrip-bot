from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from src import config

logger = logging.getLogger(__name__)

PLACES_NEARBY_URL = "https://places.googleapis.com/v1/places:searchNearby"


@dataclass(frozen=True)
class NearbyPlace:
    name: str
    rating: float | None
    maps_url: str
    address: str | None


class GooglePlacesClient:
    """Places API (New) — Nearby Search."""

    def __init__(self, api_key: str | None = None, timeout: float = 20.0) -> None:
        self._api_key = api_key or config.GOOGLE_PLACES_API_KEY
        self._timeout = timeout
        self._radius = float(config.PLACES_SEARCH_RADIUS_METERS)
        self._max_results = config.NEARBY_MAX_RESULTS

    async def nearby_attractions(
        self,
        lat: float,
        lon: float,
    ) -> list[NearbyPlace]:
        if not self._api_key:
            raise ValueError("Google Places API key is not configured")

        body = {
            "includedTypes": [
                "tourist_attraction",
                "museum",
                "park",
            ],
            "maxResultCount": self._max_results,
            "locationRestriction": {
                "circle": {
                    "center": {"latitude": lat, "longitude": lon},
                    "radius": self._radius,
                }
            },
        }

        headers = {
            "Content-Type": "application/json",
            "X-Goog-Api-Key": self._api_key,
            "X-Goog-FieldMask": ",".join(
                [
                    "places.displayName",
                    "places.rating",
                    "places.googleMapsUri",
                    "places.formattedAddress",
                    "places.location",
                ]
            ),
        }

        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.post(PLACES_NEARBY_URL, json=body, headers=headers)
            if r.status_code >= 400:
                logger.error("Google Places error %s: %s", r.status_code, r.text[:500])
            r.raise_for_status()
            payload = r.json()

        places_raw = payload.get("places") or []
        out: list[NearbyPlace] = []
        for p in places_raw:
            if not isinstance(p, dict):
                continue
            dn = p.get("displayName") or {}
            name = str(dn.get("text", "")).strip() or "Unknown place"
            rating_val = p.get("rating")
            rating: float | None = None
            if rating_val is not None:
                try:
                    rating = float(rating_val)
                except (TypeError, ValueError):
                    pass
            gmu = p.get("googleMapsUri")
            maps_url = str(gmu).strip() if gmu else ""
            loc = p.get("location") or {}
            lat_f = loc.get("latitude")
            lng_f = loc.get("longitude")
            if not maps_url and lat_f is not None and lng_f is not None:
                maps_url = f"https://www.google.com/maps/search/?api=1&query={lat_f},{lng_f}"
            if not maps_url:
                continue
            addr = p.get("formattedAddress")
            out.append(
                NearbyPlace(
                    name=name,
                    rating=rating,
                    maps_url=maps_url,
                    address=str(addr).strip() if addr else None,
                )
            )
        return out
