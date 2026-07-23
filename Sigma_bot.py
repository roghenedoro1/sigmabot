import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import yfinance as yf
import ta
import datetime
import pytz

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = None  # will save your chat id when you do /start

LAGOS = pytz.timezone("Africa/Lagos")

PAIRS = {
    "GOLD": "XAUUSD=X",
    "EURUSD": "EURUSD=X", 
    "GBPUSD": "GBPUSD=X",
    "USDJPY": "USDJPY=X"
}

TRADING_HOURS = range(8, 22)  # 8AM - 10PM WAT. Mon-Fri

def get_signal(symbol, name):
    try:
        data = yf.Ticker(symbol).history(period="2d", interval="5m")
        if len(data) < 20: 
            return f"**{name}**: ⚠️ No data"
        
        rsi = ta.momentum.RSIIndicator(data['Close']).rsi().iloc[-1]
        price = data['Close'].iloc[-1]

        if rsi < 30: signal = "🟢 BUY"
        elif rsi > 70: signal = "🔴 SELL"
        else: signal = "🟡 WAIT"
        
        return f"**{name}**\nPrice: {price:.3f}\nRSI: {rsi:.1f}\nSignal: {signal}"
    except Exception as e:
        logger.error(f"Error for {name}: {e}")
        return f"**{name}**: ⚠️ Error"

async def send_auto_signal(context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    if CHAT_ID is None: 
        return

    now = datetime.datetime.now(LAGOS)
    
    # Skip weekends and outside trading hours
    if now.weekday() >= 5 or now.hour not in TRADING_HOURS:
        return

    logger.info(f"Sending auto signal at {now.strftime('%H:%M')}")
    
    signals = [get_signal(s, n) for n, s in PAIRS.items()]
    text = f"""🌲 **FOREST AUTO SIGNAL** 🌲
Time: {now.strftime("%H:%M WAT")}

{'\n\n'.join(signals)}

**Risk:** TP 100pips | SL 50pips | Risk 1-2%
Trade at your own risk.
"""
    await context.bot.send_message(chat_id=CHAT_ID, text=text)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global CHAT_ID
    CHAT_ID = update.effective_chat.id
    
    # Run every 600 seconds = 10 minutes. First run in 10 seconds
    context.job_queue.run_repeating(send_auto_signal, interval=600, first=10)
    
    await update.message.reply_text(
        '✅ **FOREST SIGNALBOT AUTO ON**\n\n'
        'I go send you GOLD, EURUSD, GBPUSD, USDJPY signals\n'
        'Every 10 minutes\n'
        'Time: 8AM - 10PM WAT, Mon-Fri\n\n'
        'Send /stop to pause'
    )

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.job_queue.stop()
    await update.message.reply_text('⏸️ Auto signals stopped. Send /start to resume')

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    logger.info("Bot starting with POLLING...")
    app.run_polling()

if __name__ == '__main__':
    main()
