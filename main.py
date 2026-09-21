import os
import asyncio
import speedtest
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Render Environment Variable থেকে টোকেন নেওয়া হবে
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
    await update.message.reply_text(
        "👋 স্বাগতম! স্পিড টেস্ট করতে চ্যাটে লিখুন: /speedtest"
    )

async def speedtest_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_message = await update.message.reply_text("⏳ স্পিড টেস্ট শুরু হচ্ছে, কিছুটা সময় লাগতে পারে...")

    loop = asyncio.get_running_loop()
    try:
        download, upload, ping, server = await loop.run_in_executor(None, run_speedtest)

        result_text = (
            "🚀 **ইন্টারনেট স্পিড রিপোর্ট**\n\n"
            f"📡 **সার্ভার:** {server}\n"
            f"⚡ **পিং (Ping):** {ping:.2f} ms\n"
            f"📥 **ডাউনলোড স্পিড:** {download:.2f} Mbps\n"
            f"📤 **আপলোড স্পিড:** {upload:.2f} Mbps"
        )
        await status_message.edit_text(result_text, parse_mode="Markdown")

    except Exception as e:
        await status_message.edit_text(f"❌ স্পিড টেস্ট করতে সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("speedtest", speedtest_command))
    
    print("Bot is running...")
    app.run_polling()
