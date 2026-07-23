import os
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5564269252 # Your ID

# 1. SIGNAL FUNCTION - Replace this with your real strategy
async def generate_forest_signal():
    # THIS IS DEMO. Replace with your real indicator logic
    # Example: Check RSI, MA, Bollinger on 5min chart
    
    pairs = ["EURUSD", "GBPUSD", "XAUUSD"]
    directions = ["BUY 🔥", "SELL ❄️"]
    
    import random
    pair = random.choice(pairs)
    direction = random.choice(directions)
    entry = round(random.uniform(1.0500, 1.1000), 5)
    sl = round(entry - 0.0010, 5) if "BUY" in direction else round(entry + 0.0010, 5)
    tp = round(entry + 0.0020, 5) if "BUY" in direction else round(entry - 0.0020, 5)
    
    signal = f"""🌲 **FOREST SIGNAL** 🌲
Time: {datetime.now().strftime('%H:%M')}
Pair: {pair}
Direction: {direction}
Entry: {entry}
SL: {sl}
TP: {tp}
TF: 5M | Valid for next 5mins
Risk: 1-2%
"""
    return signal

# 2. AUTO SENDER - Runs every 10 minutes
async def send_signals(application):
    while True:
        await asyncio.sleep(600) # 600 seconds = 10 minutes
        try:
            signal = await generate_forest_signal()
            await application.bot.send_message(chat_id=ADMIN_CHAT_ID, text=signal, parse_mode='Markdown')
            logging.info("Signal sent")
        except Exception as e:
            logging.error(f"Error sending signal: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data='help')],
        [InlineKeyboardButton("🎧 Support", callback_data='support')],
        [InlineKeyboardButton("📅 Calendar", callback_data='calendar')],
        [InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')] # NEW BUTTON
    ]
    await update.message.reply_text('Welcome to Signalbot! 👋\nChoose an option:', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'signal': # NEW
        signal = await generate_forest_signal()
        await query.edit_message_text(signal, parse_mode='Markdown')

    # ... keep your old help/support/calendar/reply code here

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # START AUTO SIGNAL LOOP
    asyncio.create_task(send_signals(app))
    
    app.run_polling()

if __name__ == '__main__':
    main()
