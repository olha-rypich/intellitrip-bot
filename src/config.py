from __future__ import annotations

import os

from dotenv import load_dotenv

load_dotenv()


def _env(key: str, default: str | None = None) -> str | None:
    val = os.environ.get(key, default)
    if val is not None and isinstance(val, str) and val.strip() == "":
        return default
    return val


def _env_int(key: str, default: int) -> int:
    raw = _env(key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


TELEGRAM_BOT_TOKEN = _env("TELEGRAM_BOT_TOKEN") or ""
GOOGLE_PLACES_API_KEY = _env("GOOGLE_PLACES_API_KEY") or ""
TIMEZONEDB_API_KEY = _env("TIMEZONEDB_API_KEY") or ""
NOMINATIM_USER_AGENT = _env(
    "NOMINATIM_USER_AGENT",
    "IntelliTripBot/1.0 (https://example.com/intellitrip; contact@example.com)",
)
WIKIPEDIA_USER_AGENT = _env(
    "WIKIPEDIA_USER_AGENT",
    "IntelliTripBot/1.0 (https://example.com/intellitrip; contact@example.com)",
)
WIKIPEDIA_LANG = _env("WIKIPEDIA_LANG", "en") or "en"
PLACES_SEARCH_RADIUS_METERS = _env_int("PLACES_SEARCH_RADIUS_METERS", 1500)
NEARBY_MAX_RESULTS = max(1, min(20, _env_int("NEARBY_MAX_RESULTS", 8)))
LOG_LEVEL = _env("LOG_LEVEL", "INFO") or "INFO"
