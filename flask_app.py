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

# Global bot instance
bot_app = None
loop = None

def initialize_bot_once():
    """Initialize bot once and keep it running"""
    global bot_app, loop
    
    if bot_app is not None:
        return bot_app
    
    try:
        logger.info("🚀 Starting bot initialization...")
        
        # Import handlers inside function to avoid circular imports
        from handlers.commands import (
            start, help_command, clear_command, stats_command,
            mygroup_command, test_log_command, stop_ai_command,
            start_ai_command, debug_command
        )
        from handlers.messages import handle_message, error_handler
        
        # Validate config
        Config.validate()
        logger.info("✅ Config validated")
        
        # Create event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Create and setup bot
        bot_app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        logger.info("✅ Bot application created")
        
        # Add handlers
        bot_app.add_handler(CommandHandler("start", start))
        bot_app.add_handler(CommandHandler("help", help_command))
        bot_app.add_handler(CommandHandler("clear", clear_command))
        bot_app.add_handler(CommandHandler("stats", stats_command))
        bot_app.add_handler(CommandHandler("myGroup", mygroup_command))
        bot_app.add_handler(CommandHandler("testlog", test_log_command))
        bot_app.add_handler(CommandHandler("stopAI", stop_ai_command))
        bot_app.add_handler(CommandHandler("startAI", start_ai_command))
        bot_app.add_handler(CommandHandler("debug", debug_command))
        bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        bot_app.add_error_handler(error_handler)
        logger.info("✅ Handlers registered")
        
        # Initialize the bot
        loop.run_until_complete(bot_app.initialize())
        logger.info("✅ Bot initialized successfully")
        
        # Start the bot in webhook mode (but don't start polling)
        logger.info("✅ Bot ready for webhook mode")
        
        return bot_app
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        import traceback
        traceback.print_exc()
        return None

# Initialize on import
bot_app = initialize_bot_once()

@app.route('/')
def index():
    return "🤖 Telegram Bot is running!", 200

@app.route('/health')
def health():
    if bot_app and hasattr(bot_app, '_initialized') and bot_app._initialized:
        return jsonify({
            "status": "healthy",
            "bot": "running",
            "initialized": True,
            "message": "Bot is fully operational"
        }), 200
    else:
        return jsonify({
            "status": "unhealthy",
            "bot": "not running",
            "initialized": False,
            "message": "Bot initialization failed or not complete"
        }), 500

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    global bot_app, loop
    
    if bot_app is None:
        bot_app = initialize_bot_once()
        if bot_app is None:
            return "Bot not initialized", 500
    
    try:
        # Get the update
        json_data = request.get_json(force=True)
        logger.info("📥 Received webhook update")
        
        # Create Update object
        update = Update.de_json(json_data, bot_app.bot)
        
        # Process the update
        loop.run_until_complete(bot_app.process_update(update))
        
        logger.info("✅ Update processed successfully")
        return "OK", 200
        
    except Exception as e:
        logger.error(f"❌ Error processing webhook: {e}")
        import traceback
        traceback.print_exc()
        return "Error", 500

@app.route('/test_bot')
def test_bot():
    """Test bot connection"""
    try:
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        # Create temporary loop for this request
        temp_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(temp_loop)
        
        bot_info = temp_loop.run_until_complete(bot.get_me())
        
        return jsonify({
            "status": "success",
            "bot_username": bot_info.username,
            "bot_name": bot_info.first_name,
            "bot_id": bot_info.id,
            "message": "Telegram API connection successful"
        }), 200
        
    except Exception as e:
        return jsonify({
            "status": "error",
            "error": str(e),
            "message": "Failed to connect to Telegram API"
        }), 500

@app.route('/set_webhook')
def set_webhook():
    """Set webhook endpoint"""
    try:
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        # Create temporary loop for this request
        temp_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(temp_loop)
        
        url = request.args.get('url', 'https://sokha.pythonanywhere.com/webhook')
        
        # Delete old webhook
        temp_loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
        
        # Set new webhook
        result = temp_loop.run_until_complete(bot.set_webhook(
            url=url,
            drop_pending_updates=True,
            max_connections=100,
            allowed_updates=Update.ALL_TYPES
        ))
        
        return f"✅ Webhook set to: {url}<br>Result: {result}", 200
        
    except Exception as e:
        return f"❌ Error: {e}", 500

@app.route('/webhook_info')
def webhook_info():
    """Get webhook information"""
    try:
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        
        # Create temporary loop for this request
        temp_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(temp_loop)
        
        info = temp_loop.run_until_complete(bot.get_webhook_info())
        
        return jsonify({
            "url": info.url,
            "pending_update_count": info.pending_update_count,
            "last_error_message": info.last_error_message,
            "max_connections": info.max_connections
        }), 200
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=False)
