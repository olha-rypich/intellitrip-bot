from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

logger = logging.getLogger(__name__)

NOMINATIM_SEARCH_URL = "https://nominatim.openstreetmap.org/search"


@dataclass(frozen=True)
class GeocodeResult:
    lat: float
    lon: float
    display_name: str


class NominatimClient:
    def __init__(self, user_agent: str, timeout: float = 15.0) -> None:
        self._user_agent = user_agent
        self._timeout = timeout

    def _headers(self) -> dict[str, str]:
        return {
            "User-Agent": self._user_agent,
            "Accept": "application/json",
        }

    async def geocode(self, query: str) -> GeocodeResult | None:
        q = query.strip()
        if not q:
            return None
        params = {
            "q": q,
            "format": "json",
            "limit": 1,
        }
        async with httpx.AsyncClient(
            timeout=self._timeout,
            headers=self._headers(),
        ) as client:
            response = await client.get(NOMINATIM_SEARCH_URL, params=params)
            response.raise_for_status()
            data = response.json()
        if not data:
            return None
        first = data[0]
        try:
            return GeocodeResult(
                lat=float(first["lat"]),
                lon=float(first["lon"]),
                display_name=str(first.get("display_name", q)),
            )
        except (KeyError, TypeError, ValueError) as e:
            logger.warning("Unexpected Nominatim payload: %s", e)
            return None
