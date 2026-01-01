import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

# ADD THIS LINE
from config import Config 

from handlers.commands import start, help_command, clear_command, stats_command, mygroup_command, test_log_command
from handlers.messages import handle_message, error_handler

def setup_application():
    Config.validate()
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    return app

# flask_app.py needs this exact variable name
main_application = setup_application()