from __future__ import annotations

import logging
from dataclasses import dataclass

import httpx

from src import config

logger = logging.getLogger(__name__)

TIMEZONEDB_URL = "https://api.timezonedb.com/v2.1/get-time-zone"


@dataclass(frozen=True)
class TimeZoneResult:
    zone_name: str
    abbreviation: str | None
    gmt_offset_seconds: int
    local_time_formatted: str


class TimeZoneDbClient:
    def __init__(self, api_key: str | None = None, timeout: float = 15.0) -> None:
        self._api_key = api_key or config.TIMEZONEDB_API_KEY
        self._timeout = timeout

    async def get_for_position(self, lat: float, lon: float) -> TimeZoneResult | None:
        if not self._api_key:
            raise ValueError("TimeZoneDB API key is not configured")

        params = {
            "key": self._api_key,
            "format": "json",
            "by": "position",
            "lat": lat,
            "lng": lon,
        }
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            r = await client.get(TIMEZONEDB_URL, params=params)
            if r.status_code >= 400:
                logger.error("TimeZoneDB error %s: %s", r.status_code, r.text[:300])
            r.raise_for_status()
            data = r.json()

        if data.get("status") != "OK":
            logger.warning("TimeZoneDB non-OK: %s", data.get("message") or data)
            return None

        zone_name = str(data.get("zoneName") or "").strip()
        if not zone_name:
            return None

        abbr = data.get("abbreviation")
        off = data.get("gmtOffset")
        try:
            gmt_offset = int(off) if off is not None else 0
        except (TypeError, ValueError):
            gmt_offset = 0

        local_fmt = str(data.get("formatted") or "").strip()
        if not local_fmt:
            local_fmt = "—"

        return TimeZoneResult(
            zone_name=zone_name,
            abbreviation=str(abbr).strip() if abbr else None,
            gmt_offset_seconds=gmt_offset,
            local_time_formatted=local_fmt,
        )
