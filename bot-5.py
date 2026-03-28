import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)
from gtts import gTTS
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")
GROUP_USERNAME = "thats_me_denji"  # without @
GROUP_LINK = "https://t.me/thats_me_denji"

# ─── Check membership ────────────────────────────────────────────────────────

async def is_member(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=f"@{GROUP_USERNAME}", user_id=user_id
        )
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        logger.error(f"Membership check failed: {e}")
        return False

# ─── /start ──────────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    joined = await is_member(user.id, context)

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
        await send_welcome(update.message, user.first_name)

# ─── Verify button callback ───────────────────────────────────────────────────

async def verify_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    joined = await is_member(user.id, context)

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

# ─── Welcome helper ──────────────────────────────────────────────────────────

async def send_welcome(message, first_name: str):
    await message.reply_text(
        f"✅ *Welcome to Denji World, {first_name}!*\n"
        "You got verified 😃\n\n"
        "🎙️ *Now send your voice!*\n"
        "Type any text and I'll convert it into a deep voice note for you.",
        parse_mode="Markdown"
    )

# ─── Text → Voice ─────────────────────────────────────────────────────────────

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    joined = await is_member(user.id, context)

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

    text = update.message.text.strip()
    if not text:
        return

    await update.message.chat.send_action("record_voice")

    try:
        tts = gTTS(text=text, lang="en", slow=False)
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as tmp:
            tmp_path = tmp.name

        # Save as mp3 first then send as voice
        mp3_path = tmp_path.replace(".ogg", ".mp3")
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

# ─── Main ─────────────────────────────────────────────────────────────────────

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify_callback, pattern="^verify$"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    # Webhook for Vercel / production
    webhook_url = os.environ.get("WEBHOOK_URL")
    if webhook_url:
        app.run_webhook(
            listen="0.0.0.0",
            port=int(os.environ.get("PORT", 8000)),
            webhook_url=webhook_url,
        )
    else:
        logger.info("Running in polling mode (local dev)")
        app.run_polling()

if __name__ == "__main__":
    main()
