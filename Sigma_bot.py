import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot is alive! Webhook mode working ✅")

application.add_handler(CommandHandler("start", start))

@app.route(f"/{TOKEN}", methods=["POST"])
async def webhook():
    await application.update_queue.put(Update.de_json(data=request.json, bot=application.bot))
    return "ok"

@app.route("/")
def index():
    return "Bot is running"

async def set_webhook():
    await application.bot.set_webhook(url=f"{WEBHOOK_URL}/{TOKEN}")

asyncio.run(set_webhook())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT)
