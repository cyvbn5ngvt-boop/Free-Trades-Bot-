
import os
import json
import urllib.request
from telegram import Update
from telegram.ext import (
    Application,
    MessageHandler,
    ContextTypes,
    filters,
)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
DISCORD_WEBHOOK = os.getenv("DISCORD_WEBHOOK")


async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):
    if not update.message or not update.message.text:
        return

    message = update.message.text

    if not DISCORD_WEBHOOK:
        await update.message.reply_text(
            "Discord is not connected yet."
        )
        return

    data = json.dumps({
        "content": message
    }).encode("utf-8")

    request = urllib.request.Request(
        DISCORD_WEBHOOK,
        data=data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )

    try:
        await context.application.bot_data[
            "send_discord"
        ](request)

        await update.message.reply_text(
            "Successfully sent to Discord!"
        )

    except Exception:
        await update.message.reply_text(
            "Sorry, sending to Discord failed."
        )


async def send_discord(request):
    import asyncio

    def send():
        with urllib.request.urlopen(
            request, timeout=15
        ) as response:
            return response.status

    return await asyncio.to_thread(send)


def main():
    if not TELEGRAM_TOKEN:
        raise RuntimeError("Missing TELEGRAM_TOKEN")

    application = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .build()
    )

    application.bot_data["send_discord"] = send_discord

    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    print("Bot is starting...")

    application.run_polling()


if __name__ == "__main__":
    main()
  
