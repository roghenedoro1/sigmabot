import os
import logging
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("BOT_TOKEN")
YOUR_ID = 5564269252

PAIRS = {"EURUSD": "EURUSD=X","GBPUSD": "GBPUSD=X","GBPJPY": "GBPJPY=X","XAUUSD": "XAUUSD=X"}
RESULTS = []

def load_results(): return RESULTS
def save_results(data):
    global RESULTS
    RESULTS = data

async def get_5min_data(symbol):
    try:
        df = yf.Ticker(PAIRS[symbol]).history(period="5d", interval="5m")
        df.dropna(inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error fetching {symbol}: {e}")
        return pd.DataFrame()

async def generate_forest_signal(context, chat_id):
    for symbol in PAIRS.keys():
        df = await get_5min_data(symbol)
        if len(df) < 200: continue

        df['EMA50'] = ta.trend.ema_indicator(df['Close'], 50)
        df['EMA200'] = ta.trend.ema_indicator(df['Close'], 200)
        df['RSI'] = ta.momentum.rsi(df['Close'], 14)
        df['High5'] = df['High'].rolling(5).max().shift(1)
        df['Low5'] = df['Low'].rolling(5).min().shift(1)

        last, prev = df.iloc[-1], df.iloc[-2]
        direction, entry = None, last['Close']

        pip = 0.0015 if symbol!= "XAUUSD" else 0.30
        tp_pip = 0.0030 if symbol!= "XAUUSD" else 0.60

        # FOREST BUY: EMA50 > EMA200 AND RSI > 50 AND Break 5-candle High
        if last['EMA50'] > last['EMA200'] and last['RSI'] > 50 and prev['Close'] > prev['High5']:
            direction, sl, tp = "BUY 🔥", entry - pip, entry + tp_pip

        # FOREST SELL: EMA50 < EMA200 AND RSI < 50 AND Break 5-candle Low
        elif last['EMA50'] < last['EMA200'] and last['RSI'] < 50 and prev['Close'] < prev['Low5']:
            direction, sl, tp = "SELL ❄️", entry + pip, entry - tp_pip

        if direction:
            trade_id = int(datetime.now().timestamp())
            trade = {"id": trade_id,"symbol": symbol,"time": datetime.now().strftime('%Y-%m-%d %H:%M'),"direction": "BUY" if "BUY" in direction else "SELL","entry": round(entry, 5),"sl": round(sl, 5),"tp": round(tp, 5),"status": "OPEN"}
            results = load_results(); results.append(trade); save_results(results)
            keyboard = [[InlineKeyboardButton("✅ WIN", callback_data=f"result_WIN_{trade_id}")],[InlineKeyboardButton("❌ LOSS", callback_data=f"result_LOSS_{trade_id}")]]
            msg = f"🌲 **FOREST SIGNAL: {trade['symbol']}**\nID: `{trade['id']}`\nTime: {trade['time']}\nDirection: {direction}\nEntry: {trade['entry']}\nSL: {trade['sl']}\nTP: {trade['tp']}\nTF: 5M"
            await context.bot.send_message(chat_id=chat_id, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
            logging.info(f"Signal sent for {symbol}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')],[InlineKeyboardButton("📊 P&L Report", callback_data='pnl')]]
    await update.message.reply_text('Welcome to Forest Signalbot! 👋', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query; await query.answer(); data = query.data
    if data == 'signal':
        await query.edit_message_text("🌲 Scanning markets... Please wait 10-20s")
        await generate_forest_signal(context, query.message.chat_id)
    elif data == 'pnl':
        results = load_results(); closed = [r for r in results if r['status']!= 'OPEN']
        wins = len([r for r in closed if r['status'] == 'WIN']); losses = len([r for r in closed if r['status'] == 'LOSS'])
        total = wins + losses; winrate = (wins/total*100) if total > 0 else 0
        await query.edit_message_text(f"📊 **P&L REPORT**\n\nWins: {wins} ✅\nLosses: {losses} ❌\nWinrate: {winrate:.2f}%")
    elif data.startswith('result_'):
        parts = data.split('_'); result, trade_id = parts[1], int(parts[2])
        results = load_results()
        for r in results:
            if r['id'] == trade_id: r['status'] = result; break
        save_results(results); await query.edit_message_text(f"✅ Trade {trade_id} marked as {result}")

async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    logging.info("Running auto scan...")
    await generate_forest_signal(context, YOUR_ID) # Auto every 10mins

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.job_queue.run_repeating(send_signals, interval=600, first=30)
    logging.info("Bot is running...")
    

# NEW
PORT = int(os.environ.get('PORT', 10000))
app.run_webhook(
    listen="0.0.0.0",
    port=PORT,
    url_path=os.environ.get('TOKEN'),
    webhook_url=f"https://your-render-url.onrender.com/{os.environ.get('TOKEN')}"
)

if __name__ == '__main__': main()
