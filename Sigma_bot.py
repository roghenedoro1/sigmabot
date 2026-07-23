import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- CONFIG ---
TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))  # Render sets PORT automatically
WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # we will set this

app = Flask(__name__)

# Create the bot application
application = Application.builder().token(TOKEN).build()

# --- YOUR HANDLERS GO HERE ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive! Webhook mode working ✅")

application.add_handler(CommandHandler("start", start))
# --- END HANDLERS ---

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    """Handle incoming updates from Telegram"""
    await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
    return "ok"

@app.route("/")
def index():
    return "Bot is running"

async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

if __name__ == "__main__":
    # Set webhook when the server starts
    asyncio.run(set_webhook())
    # Run with gunicorn on Render. Locally you can use app.run
    app.run(host="0.0.0.0", port=PORT)
