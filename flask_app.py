import asyncio
from flask import Flask, request
from telegram import Update
from bot import main_application  # We will update bot.py to export this

app = Flask(__name__)

@app.route('/telegram', methods=['POST'])
def webhook():
    """Handle incoming Telegram updates"""
    if request.method == "POST":
        # Get the JSON data from the request
        update_data = request.get_json(force=True)
        # Convert it into a Telegram Update object
        update = Update.de_json(update_data, main_application.bot)
        
        # Process the update using the bot's application
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_application.process_update(update))
        
        return "OK", 200

# This is just a health check to see if your site is live
@app.route('/')
def index():
    return "Bot is running live!"