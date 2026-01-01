import logging
from flask import Flask, request, jsonify
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
import asyncio

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global bot application
application = None

def init_bot():
    """Initialize the bot - SIMPLE AND RELIABLE"""
    global application
    
    try:
        logger.info("🚀 Initializing bot...")
        
        # Import config here to avoid circular imports
        from config import Config
        Config.validate()
        
        # Create application
        application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        
        # Import handlers
        from handlers.commands import (
            start, help_command, clear_command, 
            stats_command, mygroup_command, test_log_command,
            stop_ai_command, start_ai_command
        )
        from handlers.messages import handle_message, error_handler
        
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
        
        # Initialize - THIS IS CRITICAL
        application.initialize()
        
        logger.info("✅ Bot initialized successfully!")
        return application
        
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None

# Initialize bot on startup
application = init_bot()

@app.route('/')
def home():
    return "🤖 Telegram Bot is running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """Handle Telegram webhook updates"""
    global application
    
    if application is None:
        logger.error("Bot not initialized!")
        return "Bot not initialized", 500
    
    try:
        # Get update data
        update_data = request.get_json()
        if not update_data:
            return "No data", 400
            
        # Create update object
        update = Update.de_json(update_data, application.bot)
        
        # Process the update
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(application.process_update(update))
        
        return 'OK', 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return 'Error', 500

@app.route('/webhook_info', methods=['GET'])
def webhook_info():
    """Get webhook information"""
    try:
        from config import Config
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        info = loop.run_until_complete(bot.get_webhook_info())
        
        return jsonify({
            'url': info.url,
            'pending_update_count': info.pending_update_count,
            'last_error_message': info.last_error_message,
            'max_connections': info.max_connections
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/set_webhook', methods=['GET'])
def set_webhook_route():
    """Set webhook endpoint"""
    try:
        from config import Config
        url = request.args.get('url', 'https://sokha.pythonanywhere.com/webhook')
        bot = Bot(Config.TELEGRAM_BOT_TOKEN)
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Delete old webhook
        loop.run_until_complete(bot.delete_webhook(drop_pending_updates=True))
        
        # Set new webhook
        result = loop.run_until_complete(bot.set_webhook(
            url=url,
            max_connections=100,
            drop_pending_updates=True
        ))
        
        return f'✅ Webhook set to: {url}<br>Result: {result}', 200
        
    except Exception as e:
        return f'❌ Error: {e}', 500

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    status = {
        'flask': 'running',
        'bot_initialized': application is not None,
        'webhook_url': 'https://sokha.pythonanywhere.com/webhook'
    }
    return jsonify(status), 200

if __name__ == '__main__':
    app.run(debug=False)
