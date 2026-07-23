import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_CHAT_ID = 5564269252 # Your ID

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("ℹ️ Help & Info", callback_data='help')],
        [InlineKeyboardButton("🎧 Support", callback_data='support')],
        [InlineKeyboardButton("📅 Calendar", callback_data='calendar')]
    ]
    await update.message.reply_text('Welcome to Signalbot! 👋\nChoose an option:', reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == 'help':
        await query.edit_message_text(text="ℹ️ **Help & Info**\n\nUse /start to see menu again")

    elif query.data == 'support':
        await query.edit_message_text(text="🎧 **Support**\n\nJust type your problem here.\nI go forward am to Admin.")
        context.user_data['waiting_for_support'] = True

    elif query.data == 'calendar':
        await query.edit_message_text(text="📅 **Calendar**\n\nCalendar link go dey here soon.")

    # NEW: Reply button handler
    elif query.data.startswith('reply_'):
        user_id = query.data.split('_')[1]
        context.user_data['replying_to'] = user_id
        await query.edit_message_text(f"Type your reply now. I go send am to the user.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # 1. If admin is replying
    if context.user_data.get('replying_to'):
        user_id = context.user_data['replying_to']
        await context.bot.send_message(chat_id=int(user_id), text=f"📩 Support Reply:\n\n{update.message.text}")
        await update.message.reply_text("✅ Reply sent!")
        context.user_data['replying_to'] = None
        return

    # 2. If user is sending support
    if context.user_data.get('waiting_for_support'):
        user_msg = update.message.text
        user = update.message.from_user
        user_id = user.id

        keyboard = [[InlineKeyboardButton("↩️ Reply This User", callback_data=f"reply_{user_id}")]]

        await context.bot.send_message(
            chat_id=ADMIN_CHAT_ID,
            text=f"🆘 New Support Request\nFrom: {user.first_name} @{user.username}\nID: {user_id}\n\nMessage: {user_msg}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        await update.message.reply_text("✅ Your message don reach Support. We go reply you soon.")
        context.user_data['waiting_for_support'] = False
        return

    # 3. Normal chat
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
