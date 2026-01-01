import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config

# Import your existing handlers
from handlers.commands import (
    start, help_command, clear_command, stats_command, 
    mygroup_command, test_log_command, stop_ai_command, start_ai_command
)
from handlers.messages import handle_message, error_handler
from services.logger import LoggerService

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def post_init(application: Application):
    """
    Called after the bot is initialized.
    Note: asyncio.create_task for periodic reports is unreliable on 
    PythonAnywhere Free Tier because the server 'pauses' when not active.
    """
    logger.info("🤖 Bot application initialized")

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
    app.add_handler(CommandHandler("stopAI", stop_ai_command))
    app.add_handler(CommandHandler("startAI", start_ai_command))
    
    # Register message handler (Text only, non-command)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Register error handler
    app.add_error_handler(error_handler)
    
    # Set the post_init hook
    app.post_init = post_init
    
    return app

# GLOBAL INSTANCE: This is what your flask_app.py will import
main_application = setup_application()

if __name__ == '__main__':
    # This block allows you to test locally in a console
    print("Starting local polling for testing...")
    main_application.run_polling(drop_pending_updates=True)