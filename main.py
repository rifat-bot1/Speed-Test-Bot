import os
import asyncio
from threading import Thread
from flask import Flask
from fastdotcom import fast_speed
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Render port fix
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running healthy!"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

TOKEN = os.getenv("BOT_TOKEN", "8980876259:AAEdVOHbVpn4xVEbsiYFDKxJvNbeMVutyH4")

def run_fast_test():
    # Background-e Fast.com er backend servers theke test run kora
    speed = fast_speed()
    return speed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 Swagotom!\n\n"
        "Fast.com er maddhome speed check korte command din:\n"
        "`/speedtest`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def speedtest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("🔄 Fast.com-er server-er maddhome background-e speed check shuru hocche... thakun ekhane.")

    loop = asyncio.get_running_loop()
    try:
        # Background-e Fast.com run kora
        speed_mbps = await loop.run_in_executor(None, run_fast_test)

        report = (
            "⚡ **Fast.com Speed Report**\n\n"
            f"🚀 **Download Speed:** `{speed_mbps:.2f} Mbps`\n"
            "✅ Check shompurno hoyeche!"
        )
        await status_msg.edit_text(report, parse_mode="Markdown")

    except Exception as e:
        await status_msg.edit_text(f"❌ Speed check korte shomossha hoyeche: {str(e)}")

if __name__ == '__main__':
    Thread(target=keep_alive).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("speedtest", speedtest_cmd))

    print("Bot is running...")
    app.run_polling()
