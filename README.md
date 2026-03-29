# IntelliTripBot

Telegram travel assistant: Wikipedia summaries, nearby attractions (Google Maps links), and local time via timezone lookup.

## Commands

| Command | Description |
|--------|---------------|
| `/start` | Welcome |
| `/help` | Command list and data sources |
| `/wiki <place>` | Summary, image when available, link to Wikipedia |
| `/nearby <place>` | Tourist-oriented places near the geocoded location with Maps URLs |
| `/time <place>` | Local time, IANA zone name, and UTC offset |

## Setup

1. **Python 3.10+** recommended.

2. Create a virtual environment and install dependencies:

   ```bash
   cd IntelliTrip_Bot
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. Copy [`.env.example`](.env.example) to `.env` and fill in secrets:

   - **TELEGRAM_BOT_TOKEN** — from [@BotFather](https://t.me/BotFather).
   - **GOOGLE_PLACES_API_KEY** — Google Cloud project with **Places API (New)** enabled and [billing](https://developers.google.com/maps/documentation/places/web-service/get-api-key) active.
   - **TIMEZONEDB_API_KEY** — from [TimeZoneDB](https://timezonedb.com/api).
   - **NOMINATIM_USER_AGENT** — a clear app name and contact (required by the [Nominatim usage policy](https://operations.osmfoundation.org/policies/nominatim/)).
   - **WIKIPEDIA_USER_AGENT** — descriptive `User-Agent` for Wikipedia API requests (defaults to the same pattern as Nominatim if unset).

4. Run the bot from the project root (so `src` resolves as a package):

   ```bash
   python -m src.bot
   ```

## Configuration

Optional environment variables (see `.env.example`):

- `WIKIPEDIA_LANG` — Wikipedia language code (default `en`).
- `PLACES_SEARCH_RADIUS_METERS` — Nearby search radius (default `1500`).
- `NEARBY_MAX_RESULTS` — Max Places results, clamped 1–20 (default `8`).
- `LOG_LEVEL` — e.g. `DEBUG`, `INFO` (default `INFO`).

## External services and policies

- **Nominatim (OpenStreetMap)** — geocoding for `/nearby` and `/time`. Use a valid `User-Agent`, avoid high request rates, and follow the [usage policy](https://operations.osmfoundation.org/policies/nominatim/).
- **Wikipedia** — `/wiki` uses the public API; follow [Wikimedia API etiquette Foundation guidelines](https://foundation.wikimedia.org/wiki/Policy:Wikimedia_Foundation_API_guidelines).
- **Google Places API (New)** — `places:searchNearby` with field mask; fees and quotas apply under [Google Maps Platform](https://developers.google.com/maps/documentation/places/web-service) terms.
- **TimeZoneDB** — timezone by coordinates; see their [API terms](https://timezonedb.com/api).

## Deployment notes

- **Process manager**: run `python -m src.bot` under systemd, supervisord, or pm2—restart on failure, log stdout/stderr.
- **Docker** (example only): base image `python:3.12-slim`, `COPY` project, `pip install -r requirements.txt`, `ENV`/`secrets` for `.env` or inject env vars at runtime, `CMD ["python", "-m", "src.bot"]`.

## Manual checks

With valid keys, try:

- `/wiki Paris`
- `/nearby Colosseum Rome`
- `/time Tokyo`

Confirm graceful errors when a key is missing (bot replies with a short setup hint) and when a place is not found.

## Layout

- [`src/bot.py`](src/bot.py) — application wiring and `/start` / `/help`
- [`src/handlers/`](src/handlers/) — command implementations
- [`src/clients/`](src/clients/) — HTTP clients for Nominatim, Wikipedia, Google Places, TimeZoneDB
