import os
import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
TOKEN = os.getenv("BOT_TOKEN")
YOUR_ID = 5564269252 # SAME ID

RESULTS = [] # Save for now in memory

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌲 Get Signal Now", callback_data='signal')],
        [InlineKeyboardButton("📊 P&L Report", callback_data='pnl')]
    ]
    await update.message.reply_text('Welcome to Signalbot! Bot is ALIVE 👋', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    logging.info(f"Button clicked: {query.data}") # This go show for logs
    data = query.data

    if data == 'signal':
        await query.edit_message_text("🌲 Scanning... Test OK!")
        # fake signal to test buttons
        trade_id = int(datetime.now().timestamp())
        keyboard = [
            [InlineKeyboardButton("✅ WIN", callback_data=f"result_WIN_{trade_id}")],
            [InlineKeyboardButton("❌ LOSS", callback_data=f"result_LOSS_{trade_id}")]
        ]
        RESULTS.append({"id": trade_id, "status": "OPEN"})
        msg = f"🌲 **TEST SIGNAL**\nID: `{trade_id}`\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nDirection: BUY 🔥\nEntry: 1.10000\nSL: 1.09850\nTP: 1.10300\nTF: 5M"
        await context.bot.send_message(chat_id=YOUR_ID, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif data == 'pnl':
        closed = [r for r in RESULTS if r['status']!= 'OPEN']
        wins = len([r for r in closed if r['status'] == 'WIN'])
        losses = len([r for r in closed if r['status'] == 'LOSS'])
        total = wins + losses
        winrate = (wins/total*100) if total > 0 else 0
        await query.edit_message_text(f"📊 **P&L REPORT**\n\nWins: {wins} ✅\nLosses: {losses} ❌\nWinrate: {winrate:.2f}%")

    elif data.startswith('result_'):
        parts = data.split('_')
        result, trade_id = parts[1], int(parts[2])
        for r in RESULTS:
            if r['id'] == trade_id: r['status'] = result
        logging.info(f"Trade {trade_id} marked as {result}")
        await query.edit_message_text(f"✅ Trade {trade_id} marked as {result}")

async def send_signals(context: ContextTypes.DEFAULT_TYPE):
    trade_id = int(datetime.now().timestamp())
    keyboard = [
        [InlineKeyboardButton("✅ WIN", callback_data=f"result_WIN_{trade_id}")],
        [InlineKeyboardButton("❌ LOSS", callback_data=f"result_LOSS_{trade_id}")]
    ]
    RESULTS.append({"id": trade_id, "status": "OPEN"})
    msg = f"🌲 **AUTO TEST SIGNAL**\nID: `{trade_id}`\nTime: {datetime.now().strftime('%Y-%m-%d %H:%M')}\nDirection: SELL ❄️\nEntry: 1.09500"
    logging.info(f"Sending auto signal to {YOUR_ID}")
    await context.bot.send_message(chat_id=YOUR_ID, text=msg, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.job_queue.run_repeating(send_signals, interval=600, first=30) # Auto every 10mins
    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
