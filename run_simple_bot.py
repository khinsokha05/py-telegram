#!/usr/bin/env python3
"""
Super simple bot that just responds to /start
Run this in a separate PythonAnywhere console
"""
import asyncio
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def start(update: Update, context):
    await update.message.reply_text("✅ Bot is working!")

async def echo(update: Update, context):
    await update.message.reply_text(f"You said: {update.message.text}")

async def main():
    # Your token here
    TOKEN = "7731781213:AAFh40WPgxY212wVITxZUSDGCNasiNhPsWM"
    
    # Create application
    application = Application.builder().token(TOKEN).build()
    
    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    
    # Start webhook
    await application.initialize()
    await application.start()
    
    # Set webhook
    url = "https://sokha.pythonanywhere.com/webhook"
    await application.bot.delete_webhook()
    await application.bot.set_webhook(url=url)
    
    logger.info(f"✅ Webhook set to: {url}")
    logger.info("🤖 Bot is running... Press Ctrl+C to stop")
    
    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("👋 Shutting down...")

if __name__ == '__main__':
    asyncio.run(main())
