import os
import io
import time
from threading import Thread
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Render Port Fix
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
        "👋 **স্বাগতম! আপনার ফোনের আসল ইন্টারনেট স্পিড মাপতে নিচে কমান্ড দিন:**\n\n"
        "📥 ডাউনলোড স্পিড মাপতে: `/download`\n"
        "📤 আপলোড স্পিড মাপতে: যেকোনো একটি ছবি বা ফাইল এই চ্যাটে পাঠান।"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def test_download(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ আপনার ফোনে টেস্ট ফাইল পাঠানো হচ্ছে, স্পিড পরিমাপ করা হচ্ছে...")

    file_size_mb = 4  # ৪ মেগাবাইট টেস্ট ডেটা
    data = io.BytesIO(b"0" * (file_size_mb * 1024 * 1024))
    data.name = "speedtest.bin"

    start_time = time.time()
    await update.message.reply_document(
        document=data,
        caption="📥 আপনার ডিভাইসে ফাইলটি ডাউনলোড হচ্ছে..."
    )
    end_time = time.time()

    duration = end_time - start_time
    speed_mbps = (file_size_mb * 8) / duration if duration > 0 else 0

    result = (
        "📊 **আপনার ডিভাইসের আসল ডাউনলোড স্পিড:**\n\n"
        f"⚡ **গতি:** `{speed_mbps:.2f} Mbps`\n"
        f"⏱️ **সময় লেগেছে:** `{duration:.2f}` সেকেন্ড\n"
        f"📦 **ফাইলের সাইজ:** `{file_size_mb} MB`"
    )
    await status_msg.edit_text(result, parse_mode="Markdown")

async def test_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    status_msg = await update.message.reply_text("⏳ আপলোড স্পিড হিসাব করা হচ্ছে...")

    # Document ba Photo shob dhoroner file handle kora
    file_obj = None
    file_size = 0
    if update.message.document:
        file_obj = update.message.document
        file_size = file_obj.file_size
    elif update.message.photo:
        file_obj = update.message.photo[-1]
        file_size = file_obj.file_size

    if not file_obj or file_size == 0:
        await status_msg.edit_text("❌ ফাইলটি পড়া যায়নি।")
        return

    start_time = time.time()
    bot_file = await file_obj.get_file()
    await bot_file.download_as_bytearray()
    end_time = time.time()

    duration = end_time - start_time
    file_size_mb = file_size / (1024 * 1024)
    speed_mbps = (file_size_mb * 8) / duration if duration > 0 else 0

    result = (
        "📊 **আপনার ডিভাইসের আসল আপলোড স্পিড:**\n\n"
        f"⚡ **গতি:** `{speed_mbps:.2f} Mbps`\n"
        f"⏱️ **সময় লেগেছে:** `{duration:.2f}` সেকেন্ড\n"
        f"📦 **ফাইলের সাইজ:** `{file_size_mb:.2f} MB`"
    )
    await status_msg.edit_text(result, parse_mode="Markdown")

if __name__ == '__main__':
    Thread(target=keep_alive).start()

    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("download", test_download))
    app.add_handler(CommandHandler("speedtest", test_download))
    app.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, test_upload))

    print("Bot is running...")
    app.run_polling()
