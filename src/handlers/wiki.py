from __future__ import annotations

import html
import logging

from telegram import Update
from telegram.ext import ContextTypes

from src.clients.wikipedia import WikipediaClient
from src.handlers.common import place_from_command, send_typing

logger = logging.getLogger(__name__)

MAX_TEXT_EXTRACT = 3500
MAX_CAPTION = 950


def _truncate(s: str, max_len: int) -> str:
    s = s.strip()
    if len(s) <= max_len:
        return s
    return s[: max_len - 1].rstrip() + "…"


async def wiki_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    place = place_from_command(context.args)
    if not place:
        await update.message.reply_text(
            "Usage: /wiki <place>\nExample: /wiki Prague"
        )
        return

    await send_typing(update, context)
    client = WikipediaClient(lang=context.application.bot_data.get("wikipedia_lang", "en"))

    try:
        summary = await client.summary_for_place(place)
    except Exception:
        logger.exception("Wikipedia error for %r", place)
        await update.message.reply_text(
            "Could not fetch Wikipedia right now. Please try again later."
        )
        return

    if not summary:
        await update.message.reply_text(
            f"No Wikipedia article found for “{place}”. Try a more specific name."
        )
        return

    title_e = html.escape(summary.title)
    link = summary.article_url
    extract_full = _truncate(summary.extract, MAX_TEXT_EXTRACT)

    if summary.image_url:
        caption_txt = _truncate(summary.extract, MAX_CAPTION)
        caption = (
            f"<b>{title_e}</b>\n\n"
            f"{html.escape(caption_txt)}\n\n"
            f'<a href="{html.escape(link, quote=True)}">Read on Wikipedia</a>'
        )
        try:
            await update.message.reply_photo(
                photo=summary.image_url,
                caption=caption[:1024],
                parse_mode="HTML",
            )
            if len(extract_full) > len(caption_txt):
                remainder = extract_full[len(caption_txt) :].lstrip()
                if remainder:
                    follow = (
                        f"…{html.escape(remainder)}\n\n"
                        f'<a href="{html.escape(link, quote=True)}">Wikipedia</a>'
                    )
                    await update.message.reply_text(
                        follow[:4096],
                        parse_mode="HTML",
                        disable_web_page_preview=True,
                    )
            return
        except Exception as e:
            logger.warning("Photo send failed, falling back to text: %s", e)

    body = (
        f"<b>{title_e}</b>\n\n"
        f"{html.escape(extract_full)}\n\n"
        f'<a href="{html.escape(link, quote=True)}">Read on Wikipedia</a>'
    )
    await update.message.reply_text(
        body[:4096],
        parse_mode="HTML",
        disable_web_page_preview=False,
    )
