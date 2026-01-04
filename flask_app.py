import logging
import asyncio
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global instances
bot_app = None

async def initialize_bot():
    """Initialize bot for Webhook mode"""
    global bot_app
    
    if bot_app is not None:
        return bot_app

    try:
        logger.info("🚀 Starting bot initialization...")
        
        # Import handlers inside function to avoid circular imports
        from handlers.commands import (
            start, help_command, clear_command, stats_command,
            mygroup_command, test_log_command, stop_ai_command,
            start_ai_command, debug_command, payroll_command
        )
        from handlers.messages import handle_message, error_handler
        
        # Validate config
        Config.validate()
        
        # Build application
        bot_app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Register ALL handlers (Sync with bot.py)
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_command))
        bot_app.add_handler(CommandHandler("clear", clear_command))
        bot_app.add_handler(CommandHandler("stats", stats_command))
        bot_app.add_handler(CommandHandler("myGroup", mygroup_command))
        bot_app.add_handler(CommandHandler("testlog", test_log_command))
        bot_app.add_handler(CommandHandler("stopAI", stop_ai_command))
        bot_app.add_handler(CommandHandler("startAI", start_ai_command))
        bot_app.add_handler(CommandHandler("debug", debug_command))
        bot_app.add_handler(CommandHandler("payroll", payroll_command))
        
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        bot_app.add_error_handler(error_handler)
        
        # Initialize
        await bot_app.initialize()
        logger.info("✅ Bot initialized successfully")
        return bot_app
        
    except Exception as e:
        logger.error(f"❌ Initialization Error: {e}")
        return None

# Trigger initialization on startup
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
bot_app = loop.run_until_complete(initialize_bot())

@app.route('/')
def index():
    return "🤖 Telegram Bot is Active!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram updates"""
    if request.method == "POST":
        try:
            update_data = request.get_json(force=True)
            update = Update.de_json(update_data, bot_app.bot)
            
            # This is the most stable way to process updates on PythonAnywhere
            loop.run_until_complete(bot_app.process_update(update))
            
            return "OK", 200
        except Exception as e:
            logger.error(f"❌ Webhook Processing Error: {e}")
            return "Error", 500

@app.route('/set_webhook')
def set_webhook():
    """Setup the URL connection with Telegram"""
    try:
        # Use your specific PythonAnywhere URL
        url = "https://sokha.pythonanywhere.com/webhook"
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        # Use a fresh loop for the setup task
        temp_loop = asyncio.new_event_loop()
        success = temp_loop.run_until_complete(bot.set_webhook(url=url, drop_pending_updates=True))
        
        return f"✅ Webhook set to {url}. Success: {success}"
    except Exception as e:
        return f"❌ Error: {e}"