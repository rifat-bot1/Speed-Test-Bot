import os
import asyncio
from threading import Thread
from flask import Flask
import speedtest
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Flask dummy server (Render Port Fix)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is running healthy!"

def keep_alive():
    port = int(os.environ.get("PORT", 8080))
    web_app.run(host='0.0.0.0', port=port)

TOKEN = os.getenv("BOT_TOKEN", "8980876259:AAEdVOHbVpn4xVEbsiYFDKxJvNbeMVutyH4")

def run_speedtest():
    st = speedtest.Speedtest()
    st.get_best_server()
    download_speed = st.download() / 1_000_000
    upload_speed = st.upload() / 1_000_000
    ping = st.results.ping
    server = st.results.server.get('sponsor', 'Unknown')
    return download_speed, upload_speed, ping, server

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Swagotom! Speed test korte likhun: /speedtest")

async def speedtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_message = await update.message.reply_text("⏳ Speed test shuru hocche, kichuta shomoy lagte pare...")
    loop = asyncio.get_running_loop()
    try:
        download, upload, ping, server = await loop.run_in_executor(None, run_speedtest)
        result_text = (
            "🚀 **Internet Speed Report**\n\n"
            f"📡 **Server:** {server}\n"
            f"⚡ **Ping:** {ping:.2f} ms\n"
            f"📥 **Download:** {download:.2f} Mbps\n"
            f"📤 **Upload:** {upload:.2f} Mbps"
        )
        await status_message.edit_text(result_text, parse_mode="Markdown")
    except Exception as e:
        await status_message.edit_text(f"❌ Shomossha hoyeche: {str(e)}")

if __name__ == '__main__':
    # Web server background thread-e run kora
    Thread(target=keep_alive).start()

    # Telegram bot run kora
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("speedtest", speedtest_command))
    
    print("Bot is running...")
    app.run_polling()
