import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") # This must be https://...
PORT = int(os.getenv("PORT", 10000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')]]
    await update.message.reply_text('✅ Bot is LIVE!', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.edit_message_text("✅ Buttons working!")

async def post_init(application):
    if not WEBHOOK_URL or not WEBHOOK_URL.startswith("https://"):
        logger.error(f"CRITICAL: WEBHOOK_URL is wrong: '{WEBHOOK_URL}'. Must start with https://")
        return
    webhook_full_url = f"{WEBHOOK_URL}/{BOT_TOKEN}"
    logger.info(f"Trying to set webhook to: {webhook_full_url}")
    await application.bot.set_webhook(url=webhook_full_url)
    logger.info("Webhook set successfully")

def main():
    logger.info(f"BOT_TOKEN loaded: {BOT_TOKEN[:10]}...")
    logger.info(f"WEBHOOK_URL loaded: {WEBHOOK_URL}")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.post_init = post_init
    app.run_webhook(listen="0.0.0.0", port=PORT, url_path=BOT_TOKEN)

if __name__ == '__main__':
    main()
