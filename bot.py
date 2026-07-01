import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request
import threading
import asyncio

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", 
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Get bot token from environment variable
TOKEN = os.environ.get("TELEGRAM_TOKEN")
if not TOKEN:
    raise ValueError("No TELEGRAM_TOKEN found in environment variables")

# Flask app for health checks
app = Flask(__name__)

@app.route('/health')
def health_check():
    """Health check endpoint to keep Render happy"""
    return "OK", 200

@app.route('/')
def home():
    return "Bot is running!", 200

# Bot command handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /start is issued."""
    user = update.effective_user
    keyboard = [
        [
            InlineKeyboardButton("Help", callback_data="help"),
            InlineKeyboardButton("About", callback_data="about"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Hi {user.first_name}! 👋\nI'm your bot running on Render!",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when /help is issued."""
    await update.message.reply_text(
        "🆘 How can I help you?\n\n"
        "Available commands:\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/echo <text> - Echo your message"
    )

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Echo the user message."""
    text_to_echo = " ".join(context.args)
    if not text_to_echo:
        await update.message.reply_text("Please provide text to echo. Example: /echo Hello World!")
        return
    await update.message.reply_text(f"🔊 {text_to_echo}")

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses."""
    query = update.callback_query
    await query.answer()
    
    if query.data == "help":
        await query.edit_message_text(
            "📚 **Help Section**\n\n"
            "I'm a simple bot to demonstrate deployment on Render.\n"
            "Try these commands:\n"
            "• /start - Start the bot\n"
            "• /help - Get help\n"
            "• /echo <text> - Echo your message"
        )
    elif query.data == "about":
        await query.edit_message_text(
            "🤖 **About Me**\n\n"
            "I'm a Telegram bot built with python-telegram-bot library.\n"
            "Deployed on Render.com with GitHub integration!\n"
            "🔄 I stay alive with UptimeRobot pinging me every 5 minutes."
        )

def run_flask():
    """Run Flask app for health checks."""
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)

def run_bot():
    """Create and run the bot application with polling."""
    # Create the Application
    application = Application.builder().token(TOKEN).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("echo", echo))
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Start the bot with polling
    logger.info("Starting bot with polling...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Run Flask in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()
    
    # Run the bot (this will block)
    try:
        run_bot()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot crashed: {e}")
        raise
