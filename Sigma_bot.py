import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)

TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logging.info(f"Received /start from {update.effective_user.id}")
    await update.message.reply_text("Bot is alive! ✅")
    logging.info("Sent reply successfully")

if __name__ == "__main__":
    application = ApplicationBuilder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    logging.info("Bot is starting and waiting for messages...")
    application.run_polling()
