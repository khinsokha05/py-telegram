import logging
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config import Config
from handlers.commands import start, help_command, clear_command, stats_command, mygroup_command, test_log_command
from handlers.messages import handle_message, error_handler
from services.logger import LoggerService

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def periodic_report_task(application):
    """Background task to send periodic reports"""
    # Wait 10 seconds before first report (so bot is fully started)
    await asyncio.sleep(10)
    logger.info("Starting periodic reports...")
    
    while True:
        try:
            # Create a simple context-like object with bot
            class SimpleContext:
                def __init__(self, bot):
                    self.bot = bot
            
            context = SimpleContext(application.bot)
            await LoggerService.send_periodic_report(context)
        except Exception as e:
            logger.error(f"Error in periodic report: {e}")
        
        await asyncio.sleep(120)  # Wait 2 minutes before next report

async def post_init(application):
    """Called after the bot is initialized"""
    # Start the periodic report task
    asyncio.create_task(periodic_report_task(application))
    logger.info("📊 Periodic report task started (every 2 minutes)")

def main():
    """Start the bot"""
    Config.validate()
    
    application = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
    
    # Register command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("clear", clear_command))
    application.add_handler(CommandHandler("stats", stats_command))
    application.add_handler(CommandHandler("myGroup", mygroup_command))
    application.add_handler(CommandHandler("testlog", test_log_command))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Set up post_init callback to start periodic task
    application.post_init = post_init
    
    logger.info("🤖 Bot started successfully!")
    print("🤖 Bot is running... Press Ctrl+C to stop.")
    print("📊 Sending activity reports every 2 minutes to log group")
    
    # Start bot
    application.run_polling(
        drop_pending_updates=True
    )

if __name__ == '__main__':
    main()