from __future__ import annotations

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes

from src import config
from src.clients.nominatim import NominatimClient
from src.clients.timezonedb import TimeZoneDbClient
from src.handlers.common import place_from_command, send_typing

logger = logging.getLogger(__name__)


def _format_offset(seconds: int) -> str:
    sign = "+" if seconds >= 0 else "−"
    s = abs(seconds)
    h = s // 3600
    m = (s % 3600) // 60
    if m:
        return f"UTC{sign}{h}:{m:02d}"
    return f"UTC{sign}{h}"


async def time_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    place = place_from_command(context.args)
    if not place:
        await update.message.reply_text(
            "Usage: /time <place>\nExample: /time Tokyo"
        )
        return

    await send_typing(update, context)
    nominatim = NominatimClient(user_agent=config.NOMINATIM_USER_AGENT)
    tz_client = TimeZoneDbClient()

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
            f"Could not find “{place}”. Try a different spelling or add a region/country."
        )
        return

    await send_typing(update, context)

    try:
        tz_info = await tz_client.get_for_position(geo.lat, geo.lon)
    except ValueError:
        await update.message.reply_text(
            "TimeZoneDB is not configured. Set TIMEZONEDB_API_KEY."
        )
        return
    except Exception:
        logger.exception("TimeZoneDB error for %s", geo.display_name)
        await update.message.reply_text(
            "Could not load timezone data. Please try again later."
        )
        return

    if not tz_info:
        await update.message.reply_text(
            f"Timezone data unavailable for {geo.display_name!r}.",
        )
        return

    off = _format_offset(tz_info.gmt_offset_seconds)
    abbr = f" ({tz_info.abbreviation})" if tz_info.abbreviation else ""
    loc = html.escape(geo.display_name)
    zn = html.escape(tz_info.zone_name)
    timestr = html.escape(tz_info.local_time_formatted)

    text = (
        f"<b>{loc}</b>\n\n"
        f"Local time: <b>{timestr}</b>\n"
        f"Time zone: <code>{zn}</code>{html.escape(abbr)}\n"
        f"Offset: <code>{html.escape(off)}</code>"
    )
    await update.message.reply_text(text, parse_mode="HTML")
