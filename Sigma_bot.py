import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
PORT = int(os.getenv("PORT", 10000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info("START RECEIVED!")
    keyboard = [[InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')]]
    await update.message.reply_text('✅ Bot is LIVE! Forest Signalbot ready! 👋', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.edit_message_text("🌲 Test Signal: EURUSD BUY\nEntry: 1.08500\nIf you see this, we won! 🎉")
    
def main():
    logger.info(f"Starting with URL: {WEBHOOK_URL}")
    # CRITICAL: pass url and webhook_url here. PTB will set it ONCE
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}"  # PTB sets it only once
    )

if __name__ == '__main__':
    main()
