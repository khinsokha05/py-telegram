import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from handlers.commands import start, help_command, clear_command, stats_command, mygroup_command, test_log_command
from handlers.messages import handle_message, error_handler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application):
    """Called after the bot is initialized - Keep simple for Webhooks"""
    logger.info("🤖 Bot application initialized for Webhook")

def setup_application():
    """Build and return the application instance"""
    Config.validate()
    
    # Initialize the Application
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("myGroup", mygroup_command))
    app.add_handler(CommandHandler("testlog", test_log_command))
    
    # Register message handler
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    app.add_error_handler(error_handler)
    
    app.post_init = post_init
    return app

# GLOBAL INSTANCE: This is what flask_app.py imports
main_application = setup_application()

if __name__ == '__main__':
    # For local testing only
    print("Starting local polling...")
    main_application.run_polling(drop_pending_updates=True)