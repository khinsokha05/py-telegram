import logging
import asyncio
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from dotenv import load_dotenv

# --- PHNOM PENH TIME LOGGING SETUP ---
class PhnomPenhFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=ZoneInfo('Asia/Phnom_Penh'))
        return dt.strftime(datefmt or '%Y-%m-%d %H:%M:%S %Z')

# Setup logging with Cambodia Time
handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(PhnomPenhFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False 

app = Flask(__name__)

# Global instances
bot_app = None
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)

def reload_config():
    """Force reload the .env file to ensure the NEW token is used"""
    project_home = '/home/sokha/py-telegram'
    # load_dotenv with override=True is critical to replace the old token in memory
    load_dotenv(os.path.join(project_home, '.env'), override=True)
    
    import importlib
    import config
    importlib.reload(config)
    
    token = Config.TELEGRAM_BOT_TOKEN or ""
    logger.info(f"🔄 Config reloaded (KH Time). Token prefix: {token[:8]}...")

async def initialize_bot():
    """Initialize bot for Webhook mode with fresh token"""
    global bot_app
    
    try:
        # 1. Reload the environment variables first
        reload_config()
        
        logger.info("🇰🇭 Starting bot initialization in Phnom Penh time...")
        
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
        
        # Register ALL handlers
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
        
        # Initialize the internal telegram-bot state
        await bot_app.initialize()
        logger.info("✅ Bot initialized successfully with current token")
        return bot_app
        
    except Exception as e:
        logger.error(f"❌ Initialization Error: {e}")
        bot_app = None
        return None

# Trigger initial startup
bot_app = loop.run_until_complete(initialize_bot())

@app.route('/')
def index():
    status = "✅ ACTIVE" if bot_app else "❌ FAILED"
    token_val = Config.TELEGRAM_BOT_TOKEN or "MISSING"
    kh_time = datetime.now(ZoneInfo('Asia/Phnom_Penh')).strftime('%Y-%m-%d %H:%M:%S')
    return f"🤖 Bot Status: {status}<br>Time: {kh_time}<br>Token Prefix: {token_val[:8]}...", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram updates with self-healing check"""
    global bot_app
    
    # Self-healing: If bot failed to initialize, try again when a message arrives
    if bot_app is None:
        logger.warning("⚠️ Bot was None at webhook call. Attempting emergency re-init...")
        bot_app = loop.run_until_complete(initialize_bot())
        if bot_app is None:
            return "Bot Initialization Failed", 500
        
    try:
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, bot_app.bot)
        loop.run_until_complete(bot_app.process_update(update))
        return "OK", 200
    except Exception as e:
        logger.error(f"❌ Webhook Error: {e}")
        return "Error", 500

@app.route('/set_webhook')
def set_webhook():
    """Force Telegram to use the current URL and Token"""
    try:
        url = "https://sokha.pythonanywhere.com/webhook"
        # Use fresh token from Config
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        temp_loop = asyncio.new_event_loop()
        # Clean old webhooks first to avoid conflicts
        temp_loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
        # Set new
        success = temp_loop.run_until_complete(bot.set_webhook(url=url))
        
        return f"✅ Webhook set to {url}. Success: {success}"
    except Exception as e:
        logger.error(f"❌ Set Webhook Error: {e}")
        return f"❌ Error: {e}"