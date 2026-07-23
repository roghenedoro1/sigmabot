import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_TOKEN")

AUTO_USERS = set()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Welcome to Sigma Bot!\n\n"
        "Commands:\n"
        "/start - Show this message\n"
        "/auto - Turn on 5min EURUSD signals\n"
        "/stop - Turn off signals"
    )

async def auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    AUTO_USERS.add(user_id)
    await update.message.reply_text("✅ Auto signals ON. You will get EURUSD alerts every 5 minutes.")
    asyncio.create_task(send_signals(context.application))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    AUTO_USERS.discard(user_id)
    await update.message.reply_text("🛑 Auto signals OFF.")

async def send_signals(app):
    while True:
        await asyncio.sleep(300)
        for user_id in list(AUTO_USERS):
            try:
                signal = "EURUSD: Waiting for setup... No trade now."
                await app.bot.send_message(chat_id=user_id, text=signal)
            except Exception as e:
                print(f"Error sending to {user_id}: {e}")

def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_TOKEN environment variable not set!")
        return
    
    print("Bot starting...")
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("auto", auto))
    app.add_handler(CommandHandler("stop", stop))
    
    app.run_polling()

if __name__ == "__main__":
    main()
