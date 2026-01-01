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

# REMOVED: periodic_report_task (Not supported on PythonAnywhere Web Workers)

async def post_init(application):
    logger.info("🤖 Bot initialized")

def setup_application():
    Config.validate()
    app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("clear", clear_command))
    app.add_handler(CommandHandler("stats", stats_command))
    app.add_handler(CommandHandler("myGroup", mygroup_command))
    app.add_handler(CommandHandler("testlog", test_log_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    app.post_init = post_init
    return app

main_application = setup_application()