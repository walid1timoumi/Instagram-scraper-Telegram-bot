import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv
load_dotenv()

from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters
from scraper.insta_scraper import scrape_instagram
import re

BOT_TOKEN = os.getenv("BOT_TOKEN")  # 🔐 Loaded from .env file

MAX_CAPTION_LEN = 1000  # Telegram allows up to 1024 characters

def is_valid_username(username: str) -> bool:
    return bool(re.match(r'^[a-zA-Z0-9._]{1,30}$', username))


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    username = update.message.text.strip().replace("@", "")

    if not is_valid_username(username):
        await update.message.reply_text("❌ Invalid Instagram username format.")
        return

    await update.message.reply_text(f"🔍 Scraping @{username}...")

    data = scrape_instagram(username)

    if "error" in data:
        await update.message.reply_text(data["error"])
        return

    if data.get("profile_pic"):
        await context.bot.send_photo(chat_id=update.effective_chat.id, photo=data["profile_pic"])

    text = (
        f"👤 <b>{data['name']}</b>\n"
        f"📝 <i>{data['bio']}</i>\n"
        f"👥 Followers: {data['followers']}"
    )
    await update.message.reply_html(text)

    for post in data.get("posts", []):
        img = post.get("image")
        caption = post.get("caption", "")
        if img:
            trimmed_caption = caption[:MAX_CAPTION_LEN] + ("..." if len(caption) > MAX_CAPTION_LEN else "")
            await context.bot.send_photo(chat_id=update.effective_chat.id, photo=img, caption=trimmed_caption)

if __name__ == '__main__':
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("🤖 Bot is running...")
    app.run_polling()
