import os
import json

RESULTS_FILE = "results.json"

def load_results():
    try:
        with open(RESULTS_FILE, 'r') as f:
            return json.load(f)
    except:
        return []

def save_results(data):
    with open(RESULTS_FILE, 'w') as f:
        json.dump(data, f, indent=4)
import logging
import asyncio
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = 5564269252 # YOUR ID

PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "GBPJPY": "GBPJPY=X",
    "XAUUSD": "XAUUSD=X"
}

# 1. SIGNAL FUNCTIONS
async def get_5min_data(symbol):
    try:
        ticker = yf.Ticker(PAIRS[symbol])
        df = ticker.history(period="5d", interval="5m")
        df.dropna(inplace=True)
        return df
    except:
        return pd.DataFrame()

async def generate_forest_signal():
    signals = []
    for symbol in PAIRS.keys():
        df = await get_5min_data(symbol)
        if len(df) < 200: continue

        df['EMA50'] = ta.trend.ema_indicator(df['Close'], 50)
        df['EMA200'] = ta.trend.ema_indicator(df['Close'], 200)
        df['RSI'] = ta.momentum.rsi(df['Close'], 14)
        df['High5'] = df['High'].rolling(5).max().shift(1)
        df['Low5'] = df['Low'].rolling(5).min().shift(1)

        last = df.iloc[-1]
        prev = df.iloc[-2]

        direction = None
        if last['EMA50'] > last['EMA200'] and last['RSI'] > 50 and prev['Close'] > prev['High5']:
            direction = "BUY 🔥"
            entry = last['Close']
            sl = entry - (0.0015 if symbol!= "XAUUSD" else 0.30)
            tp = entry + (0.0030 if symbol!= "XAUUSD" else 0.60)
        elif last['EMA50'] < last['EMA200'] and last['RSI'] < 50 and prev['Close'] < prev['Low5']:
            direction = "SELL ❄️"
            entry = last['Close']
            sl = entry + (0.0015 if symbol!= "XAUUSD" else 0.30)
            tp = entry - (0.0030 if symbol!= "XAUUSD" else 0.60)

        if direction:
            signals.append(f"🌲 **FOREST SIGNAL: {symbol}**\nTime: {datetime.now().strftime('%H:%M')}\nDirection: {direction}\nEntry: {entry:.5f}\nSL: {sl:.5f}\nTP: {tp:.5f}\nTF: 5M")

    if not signals:
        return "🌲 Forest Scan: No signal yet. Market dey sleep 😴"
    return "\n\n".join(signals)

# 2. BOT HANDLERSasync def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')],
        [InlineKeyboardButton("📊 P&L Report", callback_data='pnl')],
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data='help')],
        [InlineKeyboardButton("🎧 Support", callback_data='support')]
    ]
    await update.message.reply_text('Welcome to Signalbot! 👋\nChoose an option:', reply_markup=InlineKeyboardMarkup(keyboard))
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'signal':
        signal = await generate_forest_signal()
        await query.edit_message_text(signal, parse_mode='Markdown')
    elif query.data == 'help':
        await query.edit_message_text(text="ℹ️ Use /start to see menu")
    elif query.data == 'support':
        await query.edit_message_text(text="🎧 Type your problem here.")
        context.user_data['waiting_for_support'] = True
    elif query.data == 'calendar':
        await query.edit_message_text(text="📅 Calendar link soon.")
    elif query.data.startswith('reply_'):
        user_id = query.data.split('_')[1]
        context.user_data['replying_to'] = user_id
        await query.edit_message_text(f"Type your reply now.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('replying_to'):
        user_id = context.user_data['replying_to']
        await context.bot.send_message(chat_id=int(user_id), text=f"📩 Support Reply:\n\n{update.message.text}")
        await update.message.reply_text("✅ Reply sent!")
        context.user_data['replying_to'] = None
        return
    if context.user_data.get('waiting_for_support'):
        user_msg = update.message.text
        user = update.message.from_user
        keyboard = [[InlineKeyboardButton("↩️ Reply This User", callback_data=f"reply_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🆘 New Support\nFrom: {user.first_name}\nID: {user.id}\n\n{user_msg}", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ Message don reach Support.")
        context.user_data['waiting_for_support'] = False
        return
    await update.message.reply_text("Use /start for menu")

# 3. AUTO SIGNAL JOB - Render friendly version
async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    signal = await generate_forest_signal()
    await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=signal, parse_mode='Markdown')

# 4. MAIN - THE FIX
def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # START AUTO SIGNALS every 10 minutes. First signal in 10 seconds
    app.job_queue.run_repeating(send_signals, interval=600, first=10)

    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
