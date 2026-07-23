import os
import logging
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
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

TRADING_HOURS = range(8, 22) # 8AM to 9PM WAT

async def get_signal(symbol, name):
    try:
        data = yf.Ticker(symbol).history(period="2d", interval="5m")
        if len(data) < 20: 
            return f"**{name}**: ⚠️ No data"
        rsi = ta.momentum.RSIIndicator(data['Close']).rsi().iloc[-1]
        price = data['Close'].iloc[-1]
        if rsi < 30: 
            signal = "🟢 BUY"
        elif rsi > 70: 
            signal = "🔴 SELL"
        else: 
            signal = "🟡 WAIT"
        return f"**{name}**\nPrice: {price:.3f}\nRSI: {rsi:.1f}\nSignal: {signal}"
    except: 
        return f"**{name}**: ⚠️ Error"

async def send_auto_signal(context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    if CHAT_ID is None: 
        return
    now = datetime.datetime.now(LAGOS)
    if now.weekday() >= 5 or now.hour not in TRADING_HOURS: 
        return

    signals = []
    for name, symbol in PAIRS.items():
        signals.append(await get_signal(symbol, name))
    
    text = f"""🌲 **FOREST AUTO SIGNAL** 🌲
Time: {now.strftime("%H:%M WAT")}

{'\n\n'.join(signals)}

**Risk:** TP 100pips | SL 50pips | Risk 1-2%
"""
    await context.bot.send_message(chat_id=CHAT_ID, text=text, parse_mode='Markdown')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    # First signal in 10 seconds
    context.job_queue.run_once(send_auto_signal, 10)
    # Then every 10 minutes
    context.job_queue.run_repeating(send_auto_signal, interval=600, first=610)
    
    await update.message.reply_text(
        '✅ **FOREST SIGNALBOT AUTO ON**\n\n'
        'I go send signals every 10 minutes\n'
        'Time: 8AM - 10PM WAT, Mon-Fri\n\n'
        'Use /stop to stop',
        parse_mode='Markdown'
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.job_queue.stop()
    await update.message.reply_text('🛑 Bot stopped')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    print("Bot polling...")
    app.run_polling()

if __name__ == '__main__':
    main()
