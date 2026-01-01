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

# Global bot application
bot_app = None

def initialize_bot():
    """Initialize the bot application"""
    global bot_app
    
    try:
        logger.info("🤖 Initializing bot...")
        Config.validate()
        logger.info("✅ Configuration validated")
        
        # Create application
        bot_app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        logger.info("✅ Bot application created")
        
        # Register handlers
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_command))
        bot_app.add_handler(CommandHandler("clear", clear_command))
        bot_app.add_handler(CommandHandler("stats", stats_command))
        bot_app.add_handler(CommandHandler("myGroup", mygroup_command))
        bot_app.add_handler(CommandHandler("testlog", test_log_command))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        bot_app.add_error_handler(error_handler)
        
        logger.info("✅ Bot initialized successfully")
        return bot_app
    
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        return None

@app.route('/')
def index():
    """Health check endpoint"""
    return "🤖 Telegram Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    global bot_app
    
    # Ensure bot is initialized
    if not bot_app:
        logger.error("Bot application not initialized!")
        initialize_bot()
        if not bot_app:
            return "Bot initialization failed", 500
    
    try:
        # Get JSON data from request
        json_data = request.get_json(force=True)
        logger.info(f"📥 Received update: {json_data}")
        
        # Create Update object
        update = Update.de_json(json_data, bot_app.bot)
        
        # Process the update using asyncio
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(bot_app.process_update(update))
        
        logger.info("✅ Update processed successfully")
        return "OK", 200
    
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        return "Error", 500

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    """Get current webhook information"""
    try:
        import asyncio
        
        # Create a new bot instance just for this request
        from telegram import Bot
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        info = loop.run_until_complete(bot.get_webhook_info())
        
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
        logger.error(f"❌ Error getting webhook info: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    """Manually set webhook via browser"""
    try:
        import asyncio
        from telegram import Bot
        
        url = request.args.get('url', 'https://sokha.pythonanywhere.com/webhook')
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Delete old webhook
        loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
        
        # Set new webhook
        result = loop.run_until_complete(bot.set_webhook(
            url=url,
            drop_pending_updates=True,
            max_connections=100
        ))
        
        return f"✅ Webhook set to: {url}<br>Result: {result}", 200
    
    except Exception as e:
        return f"❌ Error: {e}", 500

# Initialize bot when module is imported
logger.info("🚀 Starting Flask app initialization...")
bot_app = initialize_bot()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)