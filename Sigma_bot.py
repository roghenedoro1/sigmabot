import os
import asyncio
from flask import Flask, request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")
PORT = int(os.getenv("PORT", 10000))

app = Flask(__name__)
application = Application.builder().token(TOKEN).build()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="Bot is alive! ✅")

application.add_handler(CommandHandler("start", start))

# Create event loop once
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    data = request.get_json(force=True)
    update = Update.de_json(data, application.bot)
    loop.create_task(application.process_update(update))  # Changed this line
    return "ok", 200

@app.route("/")
def index():
    return "Bot is running"

if __name__ == "__main__":
    loop.run_until_complete(application.initialize())
    app.run(host="0.0.0.0", port=PORT)
