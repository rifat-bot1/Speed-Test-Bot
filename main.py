import os
import asyncio
from threading import Thread
from flask import Flask
import fastdotcom
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

TOKEN = os.getenv("BOT_TOKEN", "8980876259:AAH0R5-AZ4gnWUIxJtUZawkglBo5oHdqHYs")

def run_fast_test():
    # fastdotcom.fast_com() shorashori Mbps hishebe speed return kore
    speed = fastdotcom.fast_com()
    return speed

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 **স্বাগতম!**\n\n"
        "Fast.com-এর সার্ভার দিয়ে ব্যাকগ্রাউন্ডে স্পিড চেক করতে লিখুন:\n"
        "`/speedtest`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def speedtest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ Fast.com সার্ভারে স্পিড টেস্ট চলছে... অনুগ্রহ করে কিছুক্ষণ অপেক্ষা করুন।")

    loop = asyncio.get_running_loop()
    try:
        # Background worker thread-e Fast.com run kora
        speed_mbps = await loop.run_in_executor(None, run_fast_test)

        report = (
            "🚀 **Fast.com ইন্টারনেট স্পিড রিপোর্ট**\n\n"
            f"📥 **ডাউনলোড স্পিড:** `{speed_mbps:.2f} Mbps`\n\n"
            "✅ টেস্ট সফলভাবে সম্পন্ন হয়েছে!"
        )
        await status_msg.edit_text(report, parse_mode="Markdown")

    except Exception as e:
        await status_msg.edit_text(f"❌ স্পিড টেস্টে সমস্যা হয়েছে: {str(e)}")

if __name__ == '__main__':
    Thread(target=keep_alive).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("speedtest", speedtest_cmd))

    print("Bot is running...")
    app.run_polling()
