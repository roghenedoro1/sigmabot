import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")

ADMIN_CHAT_ID = 5564269252 # Replace with your Telegram ID so support messages reach you

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
        await query.edit_message_text(text="ℹ️ **Help & Info**\n\n/start - Show menu\nJust chat with me and I go reply you\nMore features coming soon!")
    
    elif query.data == 'support':
        await query.edit_message_text(text="🎧 **Support**\n\nJust type your problem here.\nYour message go reach Admin directly.\n\nExample: 'My order no dey show'")
        context.user_data['waiting_for_support'] = True
    
    elif query.data == 'calendar':
        await query.edit_message_text(text="📅 **Calendar**\n\nCalendar link go dey here soon.\nSend /today to check events.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # If user clicked support, send their message to admin
    if context.user_data.get('waiting_for_support'):
        user_msg = update.message.text
        user = update.message.from_user
        
        # Send to admin
        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🆘 New Support Request\nFrom: {user.first_name} @{user.username}\nID: {user.id}\n\nMessage: {user_msg}"
        )
        await update.message.reply_text("✅ Your message don reach Support. We go reply you soon.")
        context.user_data['waiting_for_support'] = False
        return

    # Normal auto-reply
    text = update.message.text.lower()
    if "hello" in text or "hi" in text:
        await update.message.reply_text("Hey! 👋 How can I help you? Use /start for menu")
    elif "help" in text:
        await update.message.reply_text("Need help? Click /start and press 'Support' button")
    else:
        await update.message.reply_text(f"I got: '{update.message.text}'\n\nUse /start to see menu")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()

if __name__ == '__main__':
    main()
