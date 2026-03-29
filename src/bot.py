from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from src import config
from src.handlers.nearby import nearby_command
from src.handlers.time_cmd import time_command
from src.handlers.wiki import wiki_command

HELP_TEXT = """\
<b>IntelliTripBot</b> — travel planning helper.

<b>Commands</b>
/wiki &lt;place&gt; — Wikipedia summary, photo (if any), and article link
/nearby &lt;place&gt; — attractions nearby with Google Maps links
/time &lt;place&gt; — local time and time zone

Data: Wikipedia, OpenStreetMap/Nominatim, Google Places, TimeZoneDB.
"""


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Welcome to IntelliTripBot. Use /help for commands.",
        parse_mode="HTML",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(HELP_TEXT, parse_mode="HTML")


async def on_error(
    update: object,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    logging.getLogger(__name__).error(
        "Unhandled error: update=%s",
        update,
        exc_info=context.error,
    )
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "Something went wrong. Please try again later."
        )


def main() -> None:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL.upper(), logging.INFO),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    if not config.TELEGRAM_BOT_TOKEN:
        raise SystemExit("TELEGRAM_BOT_TOKEN is not set")

    application = Application.builder().token(config.TELEGRAM_BOT_TOKEN).build()
    application.bot_data["wikipedia_lang"] = config.WIKIPEDIA_LANG
    application.add_error_handler(on_error)
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("wiki", wiki_command))
    application.add_handler(CommandHandler("nearby", nearby_command))
    application.add_handler(CommandHandler("time", time_command))

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
