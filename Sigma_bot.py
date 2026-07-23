import os
import logging
import asyncio
import yfinance as yf
import pandas as pd
import ta
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5564269252

# PAIRS MAP FOR YFINANCE
PAIRS = {
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "GBPJPY": "GBPJPY=X",
    "XAUUSD": "XAUUSD=X"
}

async def get_5min_data(symbol):
    ticker = yf.Ticker(PAIRS[symbol])
    df = ticker.history(period="2d", interval="5m")
    df.dropna(inplace=True)
    return df

async def generate_forest_signal():
    signals = []

    for symbol in PAIRS.keys():
        df = await get_5min_data(symbol)
        if len(df) < 200: continue

        # INDICATORS
        df['EMA50'] = ta.trend.ema_indicator(df['Close'], 50)
        df['EMA200'] = ta.trend.ema_indicator(df['Close'], 200)
        df['RSI'] = ta.momentum.rsi(df['Close'], 14)
        df['High5'] = df['High'].rolling(5).max().shift(1)
        df['Low5'] = df['Low'].rolling(5).min().shift(1)

        last = df.iloc[-1]
        prev = df.iloc[-2]

        direction = None
        # BUY LOGIC
        if last['EMA50'] > last['EMA200'] and last['RSI'] > 50 and prev['Close'] > prev['High5']:
            direction = "BUY 🔥"
            entry = last['Close']
            sl = entry - (0.0015 if symbol!= "XAUUSD" else 0.30)
            tp = entry + (0.0030 if symbol!= "XAUUSD" else 0.60)

        # SELL LOGIC
        elif last['EMA50'] < last['EMA200'] and last['RSI'] < 50 and prev['Close'] < prev['Low5']:
            direction = "SELL ❄️"
            entry = last['Close']
            sl = entry + (0.0015 if symbol!= "XAUUSD" else 0.30)
            tp = entry - (0.0030 if symbol!= "XAUUSD" else 0.60)

        if direction:
            signals.append(f"""🌲 **FOREST SIGNAL: {symbol}**
Time: {datetime.now().strftime('%H:%M')}
Direction: {direction}
Entry: {entry:.5f}
SL: {sl:.5f}
TP: {tp:.5f}
TF: 5M | Valid for next candle
""")

    if not signals:
        return "🌲 Forest Scan: No signal yet. Market dey sleep 😴"

    return "\n".join(signals)

async def send_signals(application):
    while True:
        # Send every 10 minutes, 3 mins before :00 :10 :20
        now = datetime.now()
        sleep_seconds = 600 - (now.minute % 10 * 60 + now.second) + 180 # 3mins before
        await asyncio.sleep(sleep_seconds)

        signal = await generate_forest_signal()
        await application.bot.send_message(chat_id=ADMIN_CHAT_ID, text=signal, parse_mode='Markdown')

#...KEEP ALL YOUR OLD start, button, handle_message CODE HERE...

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    asyncio.create_task(send_signals(app)) # START AUTO SIGNALS

    app.run_polling()

if __name__ == '__main__':
    main()
