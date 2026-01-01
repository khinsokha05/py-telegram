import logging
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from handlers.commands import (
    start, help_command, clear_command, 
    stats_command, mygroup_command, test_log_command
)
from handlers.messages import handle_message, error_handler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Initialize Telegram bot application
application = None

def initialize_bot():
    """Initialize the bot application"""
    global application
    
    Config.validate()
    
    # Create application
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("myGroup", mygroup_command))
    application.add_handler(CommandHandler("testlog", test_log_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    logger.info("✅ Bot initialized successfully")
    return application

@app.route('/')
def index():
    """Health check endpoint"""
    return "🤖 Telegram Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    try:
        # Get JSON data from request
        json_data = request.get_json(force=True)
        
        # Create Update object
        update = Update.de_json(json_data, application.bot)
        
        # Process the update using asyncio
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
        
        return "OK", 200
    
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        return "Error", 500

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    """Get current webhook information"""
    try:
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        info = loop.run_until_complete(application.bot.get_webhook_info())
        
        return jsonify({
            "url": info.url,
            "has_custom_certificate": info.has_custom_certificate,
            "pending_update_count": info.pending_update_count,
            "last_error_date": str(info.last_error_date) if info.last_error_date else None,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections,
            "allowed_updates": info.allowed_updates
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting webhook info: {e}")
        return jsonify({"error": str(e)}), 500

# Initialize bot when app starts
try:
    initialize_bot()
    logger.info("🚀 Flask app initialized")
except Exception as e:
    logger.error(f"Failed to initialize bot: {e}")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)