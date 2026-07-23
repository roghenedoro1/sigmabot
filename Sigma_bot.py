import os
import json
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
ADMIN_CHAT_ID = 5564269252 # CHANGE TO YOUR TELEGRAM ID

PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "GBPJPY": "GBPJPY=X",
    "XAUUSD": "XAUUSD=X"
}

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

async def get_5min_data(symbol):
    try:
        ticker = yf.Ticker(PAIRS[symbol])
        df = ticker.history(period="5d", interval="5m")
        df.dropna(inplace=True)
        return df
    except:
        return pd.DataFrame()

async def generate_forest_signal(context):
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
            trade = {
                "id": int(datetime.now().timestamp()),
                "symbol": symbol,
                "time": datetime.now().strftime('%Y-%m-%d %H:%M'),
                "direction": "BUY" if "BUY" in direction else "SELL",
                "entry": round(entry, 5),
                "sl": round(sl, 5),
                "tp": round(tp, 5),
                "status": "OPEN"
            }
            results = load_results()
            results.append(trade)
            save_results(results)

            # SEND SIGNAL + WIN/LOSS BUTTONS
            keyboard = [
                [InlineKeyboardButton("✅ WIN", callback_data=f"result_WIN_{trade['id']}")],
                [InlineKeyboardButton("❌ LOSS", callback_data=f"result_LOSS_{trade['id']}")]
            ]
            msg = f"🌲 **FOREST SIGNAL: {trade['symbol']}**\nID: `{trade['id']}`\nTime: {trade['time']}\nDirection: {direction}\nEntry: {trade['entry']}\nSL: {trade['sl']}\nTP: {trade['tp']}\nTF: 5M\n\nMark result:"
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')],
        [InlineKeyboardButton("📊 P&L Report", callback_data='pnl')],
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data='help')],
        [InlineKeyboardButton("🎧 Support", callback_data='support')],
        [InlineKeyboardButton("📅 Calendar", callback_data='calendar')]
    ]
    await update.message.reply_text('Welcome to Signalbot! 👋\nChoose an option:', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'signal':
        await query.edit_message_text("🌲 Scanning market...")
        await generate_forest_signal(context)

    elif data == 'pnl':
        results = load_results()
        closed = [r for r in results if r['status']!= 'OPEN']
        wins = len([r for r in closed if r['status'] == 'WIN'])
        losses = len([r for r in closed if r['status'] == 'LOSS'])
        total = wins + losses
        winrate = (wins/total*100) if total > 0 else 0
        open_trades = len([r for r in results if r['status'] == 'OPEN'])
        await query.edit_message_text(
            f"📊 **P&L REPORT**\n\n"
            f"Open Trades: {open_trades}\n"
            f"Total Closed: {total}\n"
            f"Wins: {wins} ✅\n"
            f"Losses: {losses} ❌\n"
            f"Winrate: {winrate:.2f}%"
        )

    elif data.startswith('result_'):
        parts = data.split('_')
        result = parts[1]
        trade_id = int(parts[2])
        results = load_results()
        for r in results:
            if r['id'] == trade_id:
                r['status'] = result
                break
        save_results(results)
        await query.edit_message_text(f"✅ Trade {trade_id} marked as {result}")

    elif data == 'help':
        await query.edit_message_text(text="ℹ️ Use /start to see menu\n🌲 Get signal\n📊 See P&L")
    elif data == 'support':
        await query.edit_message_text(text="🎧 Type your problem here.")
        context.user_data['waiting_for_support'] = True
    elif data == 'calendar':
        await query.edit_message_text(text="📅 Calendar link coming soon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_support'):
        user_msg = update.message.text
        user = update.message.from_user
        keyboard = [[InlineKeyboardButton("↩️ Reply This User", callback_data=f"reply_{user.id}")]]
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=f"🆘 New Support\nFrom: {user.first_name}\nID: {user.id}\n\n{user_msg}", reply_markup=InlineKeyboardMarkup(keyboard))
        await update.message.reply_text("✅ Message don reach Support.")
        context.user_data['waiting_for_support'] = False
        return
    await update.message.reply_text("Use /start for menu")

async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    await generate_forest_signal(context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.job_queue.run_repeating(send_signals, interval=600, first=10) # Auto every 10mins
    print("Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
