import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL") 
PORT = int(os.getenv("PORT", 10000))

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"START RECEIVED FROM: {update.effective_user.id}")
    keyboard = [[InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')]]
    await update.message.reply_text('✅ Bot is LIVE! Forest Signalbot ready! 👋', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.edit_message_text("🌲 Test Signal: EURUSD BUY\nEntry: 1.08500\nWe finally won! 🎉")
    
def main():
    logger.info(f"Starting with URL: {WEBHOOK_URL}")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    # KEY CHANGE: url_path is now just "webhook" not BOT_TOKEN
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path="webhook",  # <--- CHANGED THIS
        webhook_url=f"{WEBHOOK_URL}/webhook"  # <--- AND THIS
    )

if __name__ == '__main__':
    main()
