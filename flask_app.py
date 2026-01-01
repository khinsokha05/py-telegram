import asyncio
from flask import Flask, request
from telegram import Update
from bot import main_application

app = Flask(__name__)

@app.route('/telegram', methods=['POST'])
def webhook():
    if request.method == "POST":
        update_data = request.get_json(force=True)
        update = Update.de_json(update_data, main_application.bot)
        
        loop = asyncio.get_event_loop()
        loop.run_until_complete(main_application.process_update(update))
        
        return "OK", 200

@app.route('/')
def index():
    return "Bot is running live!"