from http.server import BaseHTTPRequestHandler
import json
import os
import asyncio
import logging
import tempfile

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters
from gtts import gTTS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_USERNAME = "thats_me_denji"
GROUP_LINK = "https://t.me/thats_me_denji"


async def is_member(user_id: int, bot: Bot) -> bool:
    try:
        member = await bot.get_chat_member(
            chat_id=f"@{GROUP_USERNAME}", user_id=user_id
        )
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.error(f"Membership check error: {e}")
        return False


async def process_update(update_data: dict):
    app = Application.builder().token(BOT_TOKEN).build()

    async with app:
        bot = app.bot
        update = Update.de_json(update_data, bot)

        if update.message and update.message.text:
            user = update.effective_user
            text = update.message.text.strip()

            if text == "/start":
                joined = await is_member(user.id, bot)
                if not joined:
                    keyboard = [
                        [InlineKeyboardButton("🔗 Join Denji World", url=GROUP_LINK)],
                        [InlineKeyboardButton("✅ I've Joined – Verify Me", callback_data="verify")]
                    ]
                    await update.message.reply_text(
                        f"👋 Hey *{user.first_name}*!\n\n"
                        "To use this bot, you must join *Denji World* first.\n\n"
                        "1️⃣ Click **Join Denji World** below\n"
                        "2️⃣ Then click **Verify Me** ✅",
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    await update.message.reply_text(
                        f"✅ *Welcome to Denji World, {user.first_name}!*\n"
                        "You got verified 😃\n\n"
                        "🎙️ *Now send your voice!*\n"
                        "Type any text and I'll convert it into a voice note for you.",
                        parse_mode="Markdown"
                    )
            else:
                # Text to voice
                joined = await is_member(user.id, bot)
                if not joined:
                    keyboard = [
                        [InlineKeyboardButton("🔗 Join Denji World", url=GROUP_LINK)],
                        [InlineKeyboardButton("✅ Verify Me", callback_data="verify")]
                    ]
                    await update.message.reply_text(
                        "⚠️ *You left the group!*\n\n"
                        "Re-join *Denji World* to keep using the bot.",
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    return

                try:
                    tts = gTTS(text=text, lang="en", slow=False)
                    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
                        mp3_path = tmp.name
                    tts.save(mp3_path)

                    with open(mp3_path, "rb") as audio:
                        await update.message.reply_voice(
                            voice=audio,
                            caption="🎙️ *Denji World TTS*",
                            parse_mode="Markdown"
                        )
                    os.unlink(mp3_path)
                except Exception as e:
                    logger.error(f"TTS error: {e}")
                    await update.message.reply_text("❌ Something went wrong. Try again!")

        elif update.callback_query:
            query = update.callback_query
            await query.answer()
            user = query.from_user

            if query.data == "verify":
                joined = await is_member(user.id, bot)
                if not joined:
                    keyboard = [
                        [InlineKeyboardButton("🔗 Join Denji World", url=GROUP_LINK)],
                        [InlineKeyboardButton("🔄 Try Again", callback_data="verify")]
                    ]
                    await query.edit_message_text(
                        "❌ *You haven't joined yet!*\n\n"
                        "Please join the group first, then click Verify again.",
                        parse_mode="Markdown",
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                else:
                    await query.edit_message_text(
                        f"✅ *Verified successfully!*\n\n"
                        f"🎉 *Welcome to Denji World, {user.first_name}!*\n"
                        "You got verified 😎\n\n"
                        "Now send your text and I'll turn it into a voice note 🎙️",
                        parse_mode="Markdown"
                    )


class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(content_length)

        try:
            update_data = json.loads(body)
            asyncio.run(process_update(update_data))
        except Exception as e:
            logger.error(f"Handler error: {e}")

        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"OK")

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"Denji World TTS Bot is running!")
