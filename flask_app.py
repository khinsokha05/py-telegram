import logging
from flask import Flask, request
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio
from threading import Thread
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global application instance
application = None
loop = None

def run_bot():
    """Run the bot in background thread"""
    global application, loop
    
    logger.info("🚀 Starting bot in background...")
    
    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        # Import here to avoid circular imports
        from config import Config
        Config.validate()
        
        # Import handlers
        from handlers.commands import (
            start, help_command, clear_command, 
            stats_command, mygroup_command, test_log_command,
            stop_ai_command, start_ai_command
        )
        from handlers.messages import handle_message, error_handler
        
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("clear", clear_command))
        application.add_handler(CommandHandler("stats", stats_command))
        application.add_handler(CommandHandler("myGroup", mygroup_command))
        application.add_handler(CommandHandler("testlog", test_log_command))
        application.add_handler(CommandHandler("stopAI", stop_ai_command))
        application.add_handler(CommandHandler("startAI", start_ai_command))
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        application.add_error_handler(error_handler)
        
        # Initialize (but don't start polling since we use webhook)
        loop.run_until_complete(application.initialize())
        logger.info("✅ Bot initialized successfully!")
        
        # Keep the event loop running
        loop.run_forever()
        
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        import traceback
        traceback.print_exc()

def process_update_sync(update):
    """Process update synchronously"""
    global application
    if application:
        # Run in the bot's event loop
        future = asyncio.run_coroutine_threadsafe(
            application.process_update(update), 
            loop
        )
        future.result(timeout=10)

@app.route('/')
def home():
    return "🤖 Telegram Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    try:
        update_data = request.get_json(force=True)
        
        # Wait a bit if bot is still starting
        if application is None:
            time.sleep(1)
        
        if application:
            update = Update.de_json(update_data, application.bot)
            logger.info(f"📥 Processing update {update.update_id}")
            
            # Process update in bot's thread
            process_update_sync(update)
            
            logger.info(f"✅ Processed update {update.update_id}")
            return 'OK', 200
        else:
            logger.error("Bot not initialized yet")
            return 'Bot not ready', 503
            
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 'Error', 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Simple webhook setup"""
    try:
        from config import Config
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        
        # Create temporary event loop
        temp_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(temp_loop)
        
        url = "https://sokha.pythonanywhere.com/webhook"
        temp_loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
        result = temp_loop.run_until_complete(bot.set_webhook(
            url=url,
            max_connections=100,
            drop_pending_updates=True
        ))
        temp_loop.close()
        
        return f'✅ Webhook set to: {url}', 200
        
    except Exception as e:
        return f'❌ Error: {e}', 500

# Start bot in background thread when Flask starts
@app.before_first_request
def start_bot_thread():
    """Start bot in background thread"""
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("🤖 Bot thread started")

if __name__ == '__main__':
    # Start bot thread
    bot_thread = Thread(target=run_bot, daemon=True)
    bot_thread.start()
    logger.info("🤖 Bot thread started")
    
    # Start Flask
    app.run(debug=False, host='0.0.0.0', port=5000)