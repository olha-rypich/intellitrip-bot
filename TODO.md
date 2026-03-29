# IntelliTripBot — Implementation plan

This document tracks development tasks for v1. Aligns with the technical stack: **python-telegram-bot**, **Nominatim**, **Wikipedia API**, **Google Places API (New)**, **TimeZoneDB**.

Use `[ ]` / `[x]` to mark progress locally as you work.

---

## Phase 1 — Project scaffold

- [ ] Add `requirements.txt` (`python-telegram-bot` v21+, `httpx`, `python-dotenv`).
- [ ] Add `.env.example` with all required variable names (no secrets).
- [ ] Add `src/` package layout: `config.py`, `bot.py`, `clients/`, `handlers/`.
- [ ] Load settings from environment in `config.py` (tokens, keys, optional tuning).
- [ ] Add `.gitignore` for `.env`, virtualenvs, `__pycache__`.
- [ ] Document run instructions in `README.md` (install, `.env`, `python -m src.bot`).

---

## Phase 2 — HTTP clients

### Nominatim (OpenStreetMap)

- [ ] Implement async `geocode(query) -> lat, lon, display_name | None`.
- [ ] Set a compliant `User-Agent` header (policy requirement).
- [ ] Use reasonable HTTP timeouts; avoid burst traffic.

### Wikipedia

- [ ] Resolve search string → article title (e.g. `opensearch`).
- [ ] Fetch REST `page/summary/{title}` for extract, image URLs, article link.
- [ ] Handle disambiguation / missing page with clear behavior.
- [ ] Send a descriptive `User-Agent` for Wikimedia API requests.

### Google Places (New)

- [ ] Implement **Nearby Search**: `POST https://places.googleapis.com/v1/places:searchNearby`.
- [ ] Send `X-Goog-Api-Key` and mandatory `X-Goog-FieldMask` (e.g. display name, rating, `googleMapsUri`, location).
- [ ] Filter by tourist-relevant `includedTypes`; configurable radius and max results.
- [ ] Fallback Maps URL from coordinates if `googleMapsUri` is absent.

### TimeZoneDB

- [ ] Implement `get-time-zone` by lat/lon (`by=position`).
- [ ] Parse zone name, UTC offset, and local time from the response.

---

## Phase 3 — Telegram handlers

- [ ] `/wiki <place>` — summary + optional photo + Wikipedia link; truncate for Telegram caption limits; text fallback if photo fails.
- [ ] `/nearby <place>` — Nominatim geocode → Places nearby → formatted list with Maps links.
- [ ] `/time <place>` — Nominatim geocode → TimeZoneDB → local time, zone name, offset.
- [ ] `/start` and `/help` — command list and note that external APIs are used.
- [ ] Call `send_chat_action` (typing) before slow operations.
- [ ] Global error handler: log exception, reply with a generic user-safe message.

---

## Phase 4 — Wiring and operations

- [ ] Register `CommandHandler`s on the `Application`; set `bot_data` (e.g. Wikipedia language) if needed.
- [ ] Configure logging level via env (`LOG_LEVEL`).
- [ ] Validate startup: fail fast with a clear message if `TELEGRAM_BOT_TOKEN` is missing.

---

## Phase 5 — Verification and sign-off

- [ ] Manual E2E: `/wiki`, `/nearby`, `/time` with three representative places (city, landmark, small town).
- [ ] Confirm behavior when a place is not found or an API key is missing.
- [ ] Confirm README covers Nominatim policy, Google billing/Places API (New), and TimeZoneDB keys.
- [ ] Optional: run under a process manager or container per `README.md`.

---

## Dependency checklist (operator)

| Item | Notes |
| ---- | ----- |
| Telegram | Bot token from @BotFather |
| Google Cloud | Places API (New) enabled; API key; billing |
| TimeZoneDB | API key |
| Nominatim | Valid `User-Agent` with contact |

---

## Order of implementation (recommended)

1. Scaffold + config + README skeleton  
2. Nominatim client  
3. Wikipedia client + `/wiki`  
4. Google Places client + `/nearby`  
5. TimeZoneDB client + `/time`  
6. `/start`, `/help`, error handler, logging  
7. Manual tests + README completion  
