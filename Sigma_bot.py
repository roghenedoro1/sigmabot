import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.info(f"START RECEIVED FROM: {update.effective_user.id}")
    keyboard = [[InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')]]
    await update.message.reply_text('✅ Forest Signalbot IS LIVE WITH POLLING! 👋', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer()
    await query.edit_message_text("🌲 Test Signal: EURUSD BUY\nEntry: 1.08500\nPOLLING WORKS! 🎉")

def main():
    logger.info("Starting BOT with POLLING...")
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    
    # NO WEBHOOK. JUST POLLING
    app.run_polling()

if __name__ == '__main__':
    main()
