import os
import logging
import time
import threading
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import yfinance as yf
import ta
import datetime
import pytz

logging.basicConfig(level=logging.INFO)
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = None
LAGOS = pytz.timezone("Africa/Lagos")

PAIRS = {"GOLD": "XAUUSD=X", "EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "USDJPY": "USDJPY=X"}

def get_signal(symbol, name):
    try:
        data = yf.Ticker(symbol).history(period="2d", interval="5m")
        rsi = ta.momentum.RSIIndicator(data['Close']).rsi().iloc[-1]
        price = data['Close'].iloc[-1]
        signal = "🟢 BUY" if rsi < 30 else "🔴 SELL" if rsi > 70 else "🟡 WAIT"
        return f"**{name}**\nPrice: {price:.3f}\nRSI: {rsi:.1f}\nSignal: {signal}"
    except: return f"**{name}**: ⚠️ Error"

def signal_loop():
    global CHAT_ID
    while True:
        if CHAT_ID:
            now = datetime.datetime.now(LAGOS)
            if now.weekday() < 5 and 8 <= now.hour < 22:
                signals = [get_signal(s, n) for n, s in PAIRS.items()]
                text = f"🌲 **FOREST AUTO SIGNAL** 🌲\nTime: {now.strftime('%H:%M WAT')}\n\n{'\n\n'.join(signals)}"
                Bot(BOT_TOKEN).send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')
        time.sleep(600) # 10 minutes

def start(update: Update, context: CallbackContext):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    update.message.reply_text('✅ FOREST SIGNALBOT AUTO ON\nSignals every 10mins 8AM-10PM WAT', parse_mode='Markdown')

def main():
    threading.Thread(target=signal_loop, daemon=True).start()
    updater = Updater(BOT_TOKEN, use_context=True)
    updater.dispatcher.add_handler(CommandHandler("start", start))
    print("Bot polling...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
