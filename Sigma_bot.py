import asyncio, threading
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.request import HTTPXRequest
import yfinance as yf

TOKEN = "8994021774:AAFwzRGdPLOnRuy40U4jg8AQ7Tx6S1TEaKQ"
user_ids = set()

def get_signal(pair):
    tickers = {"EURUSD": "EURUSD=X", "GBPUSD": "GBPUSD=X", "XAUUSD": "XAUUSD=X"}
    ticker = tickers.get(pair)
    if not ticker: return "Pair not found"
    try:
        data = yf.Ticker(ticker).history(period="1d", interval="1m")
        if data.empty or len(data) < 2: return "No data"
        last_price = float(data['Close'].iloc[-1])
        prev_price = float(data['Close'].iloc[-2])
        if last_price > prev_price:
            return f"BUY {pair} ✅\nPrice: {last_price:.4f}\nSL: 20 pips | TP: 40 pips"
        else:
            return f"SELL {pair} ❌\nPrice: {last_price:.4f}\nSL: 20 pips | TP: 40 pips"
    except Exception as e: 
        return f"Error: {e}"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Sigma Bot v3.6 LIVE ✅\n/eurusd /gbpusd /xauusd = Instant Signal\n/auto = Auto alerts every 5min")

async def eurusd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"EURUSD Signal:\n{get_signal('EURUSD')}")
async def gbpusd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"GBPUSD Signal:\n{get_signal('GBPUSD')}")
async def xauusd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(f"GOLD Signal:\n{get_signal('XAUUSD')}")
async def auto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_ids.add(update.effective_chat.id)
    await update.message.reply_text("Auto alerts ON ✅ Every 5min")

async def send_alerts(app):
    while True:
        await asyncio.sleep(300)
        for chat_id in list(user_ids):
            try:
                text = "⏰ 5min Update\n" + get_signal("EURUSD") + "\n\n" + get_signal("GBPUSD") + "\n\n" + get_signal("XAUUSD")
                await app.bot.send_message(chat_id=chat_id, text=text)
            except: 
                user_ids.discard(chat_id)

def run_alerts(app): 
    asyncio.run(send_alerts(app))

def main():
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0)
    app = ApplicationBuilder().token(TOKEN).request(request).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("eurusd", eurusd))
    app.add_handler(CommandHandler("gbpusd", gbpusd))
    app.add_handler(CommandHandler("xauusd", xauusd))
    app.add_handler(CommandHandler("auto", auto))
    threading.Thread(target=run_alerts, args=(app,), daemon=True).start()
    print("Bot Running - 5min updates")
    app.run_polling(drop_pending_updates=True)

if name == "main":
    main()
