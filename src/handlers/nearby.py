from __future__ import annotations

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes

from src import config
from src.clients.google_places import GooglePlacesClient
from src.clients.nominatim import NominatimClient
from src.handlers.common import place_from_command, send_typing

logger = logging.getLogger(__name__)


async def nearby_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    place = place_from_command(context.args)
    if not place:
        await update.message.reply_text(
            "Usage: /nearby <place>\nExample: /nearby Eiffel Tower"
        )
        return

    await send_typing(update, context)
    nominatim = NominatimClient(user_agent=config.NOMINATIM_USER_AGENT)
    places_client = GooglePlacesClient()

    try:
        geo = await nominatim.geocode(place)
    except Exception:
        logger.exception("Nominatim error for %r", place)
        await update.message.reply_text(
            "Location lookup failed. Please try again in a moment."
        )
        return

    if not geo:
        await update.message.reply_text(
            f"Could not find coordinates for “{place}”. Try a different spelling or add a country."
        )
        return

    await send_typing(update, context)

    try:
        items = await places_client.nearby_attractions(geo.lat, geo.lon)
    except ValueError as e:
        await update.message.reply_text(
            "Google Places is not configured. Set GOOGLE_PLACES_API_KEY."
        )
        logger.warning("%s", e)
        return
    except Exception:
        logger.exception("Google Places error near %s", geo.display_name)
        await update.message.reply_text(
            "Could not load nearby attractions. Check your Google API key and billing, then try again."
        )
        return

    if not items:
        await update.message.reply_text(
            f"No attractions found near {geo.display_name!r} within the search radius.",
        )
        return

    header = (
        f"<b>{html.escape(geo.display_name)}</b>\n"
        f"<i>Within {config.PLACES_SEARCH_RADIUS_METERS} m — tourist spots, museums, parks</i>\n"
    )
    parts: list[str] = [header]
    for i, p in enumerate(items, start=1):
        rating = f" · {p.rating:.1f}★" if p.rating is not None else ""
        addr = f"\n   <i>{html.escape(p.address)}</i>" if p.address else ""
        name_e = html.escape(p.name)
        maps_e = html.escape(p.maps_url, quote=True)
        parts.append(
            f"{i}. <b>{name_e}</b>{html.escape(rating)}{addr}\n"
            f'   <a href="{maps_e}">Google Maps</a>'
        )

    text = "\n".join(parts)
    await update.message.reply_text(
        text[:4096],
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
