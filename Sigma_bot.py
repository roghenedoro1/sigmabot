import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data='help')],
        [InlineKeyboardButton("🎧 Support", callback_data='support')],
        [InlineKeyboardButton("📅 Calendar", callback_data='calendar')]
    ]
    await update.message.reply_text('Welcome to Sigma Bot! 👋\nChoose an option:', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'help':
        await query.edit_message_text(text="ℹ️ **Help & Info**\n\n/start - Show menu\nJust chat with me and I go reply you")
    
    elif query.data == 'support':
        await query.edit_message_text(text="🎧 **Support**\n\nJust type your problem here.\nI go see am and reply you.")
        context.user_data['waiting_for_support'] = True
    
    elif query.data == 'calendar':
        await query.edit_message_text(text="📅 **Calendar**\n\nCalendar link go dey here soon.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('waiting_for_support'):
        user_msg = update.message.text
        # Instead of forwarding, we just log it and reply you
        await update.message.reply_text(f"✅ I got your support message: '{user_msg}'\n\nAdmin go reply you soon.")
        print(f"SUPPORT MESSAGE: {user_msg}") # This go show for Render logs
        context.user_data['waiting_for_support'] = False
        return

    text = update.message.text.lower()
    if "hello" in text or "hi" in text:
        await update.message.reply_text("Hey! 👋 How can I help you? Use /start for menu")
    else:
        await update.message.reply_text("I got your message. Use /start to see menu")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
