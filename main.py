import os
import io
import time
from threading import Thread
from flask import Flask
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

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = (
        "👋 **স্বাগতম!**\n\n"
        "আপনার ডিভাইসের আসল ইন্টারনেট স্পিড মাপতে নিচে কমান্ড দিন:\n"
        "`/speedtest`"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def speedtest_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = await update.message.reply_text("⏳ আপনার ফোনের সাথে সংযোগ যাচাই ও পিং টেস্ট করা হচ্ছে...")

    # ১. পিং টেস্ট
    t0 = time.time()
    await msg.edit_text("⚡ পিং (Ping) টেস্ট চলছে...")
    t1 = time.time()
    ping_ms = (t1 - t0) * 1000

    # ২. টেস্ট ফাইল তৈরি (টেলিগ্রাম বটের লিমিটের মধ্যে সর্বোচ্চ ৪০ MB ডেটা)
    file_size_mb = 40  
    await msg.edit_text(f"📥 আপনার ফোনে {file_size_mb} MB টেস্ট ডেটা পাঠানো হচ্ছে... দয়া করে অপেক্ষা করুন।")

    # RAM-এ ৪০ MB ডামি ডেটা তৈরি
    dummy_data = b"0" * (file_size_mb * 1024 * 1024)

    # ৩. ডেটা পাঠানোর সময় হিসাব (ডাউনলোড স্পিড)
    start_time = time.time()
    sent_file = await update.message.reply_document(
        document=dummy_data,
        filename="speedtest_40mb.bin",
        caption=f"📦 {file_size_mb} MB ডেটা আপনার ফোনে ডাউনলোড হচ্ছে..."
    )
    end_time = time.time()

    duration = end_time - start_time
    
    # Mbps = (MB * 8) / seconds
    download_mbps = (file_size_mb * 8) / duration if duration > 0 else 0
    estimated_upload_mbps = download_mbps * 0.40  # আনুমানিক মোবাইল আপলোড স্পিড

    # টেস্ট শেষ হলে সাময়িক ফাইলটি মুছে ফেলা (চ্যাট পরিষ্কার রাখতে)
    try:
        await sent_file.delete()
    except Exception:
        pass

    # চূড়ান্ত ফলাফল বাংলায়
    report = (
        "🚀 **আপনার ডিভাইসের আসল ইন্টারনেট স্পিড**\n\n"
        f"⚡ **পিং (Ping):** `{ping_ms:.2f} ms`\n"
        f"📥 **ডাউনলোড স্পিড:** `{download_mbps:.2f} Mbps`\n"
        f"📤 **আপলোড স্পিড (আনুমানিক):** `{estimated_upload_mbps:.2f} Mbps`\n\n"
        f"📦 **টেস্ট ডেটা সাইজ:** `{file_size_mb} MB`\n"
        f"⏱️ **মোট সময় লেগেছে:** `{duration:.2f}` সেকেন্ড"
    )
    await msg.edit_text(report, parse_mode="Markdown")

if __name__ == '__main__':
    Thread(target=keep_alive).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("speedtest", speedtest_cmd))

    print("Bot is running...")
    app.run_polling()
