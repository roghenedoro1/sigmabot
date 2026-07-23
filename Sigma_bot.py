import os
import logging
import time
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext
import yfinance as yf
import ta
import datetime
import pytz

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = None
LAGOS = pytz.timezone("Africa/Lagos")

PAIRS = {
    "GOLD": "XAUUSD=X",
    "EURUSD": "EURUSD=X",
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X"
}

TRADING_HOURS = range(8, 22)

def get_signal(symbol, name):
    try:
        data = yf.Ticker(symbol).history(period="2d", interval="5m")
        if len(data) < 20: return f"**{name}**: ⚠️ No data"
        rsi = ta.momentum.RSIIndicator(data['Close']).rsi().iloc[-1]
        price = data['Close'].iloc[-1]
        if rsi < 30: signal = "🟢 BUY"
        elif rsi > 70: signal = "🔴 SELL"
        else: signal = "🟡 WAIT"
        return f"**{name}**\nPrice: {price:.3f}\nRSI: {rsi:.1f}\nSignal: {signal}"
    except: return f"**{name}**: ⚠️ Error"

def send_auto_signal(context: CallbackContext):
    global CHAT_ID
    if CHAT_ID is None: return
    now = datetime.datetime.now(LAGOS)
    if now.weekday() >= 5 or now.hour not in TRADING_HOURS: return

    signals = [get_signal(symbol, name) for name, symbol in PAIRS.items()]
    
    text = f"""🌲 **FOREST AUTO SIGNAL** 🌲
Time: {now.strftime("%H:%M WAT")}

{'\n\n'.join(signals)}

**Risk:** TP 100pips | SL 50pips | Risk 1-2%
"""
    context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')

def start(update: Update, context: CallbackContext):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    context.job_queue.run_repeating(send_auto_signal, interval=600, first=10)
    update.message.reply_text(
        '✅ **FOREST SIGNALBOT AUTO ON**\n\nI go send signals every 10 minutes\nTime: 8AM - 10PM WAT, Mon-Fri',
        parse_mode='Markdown'
    )

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    print("Bot polling...")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
