# py-telegram
test bot

https://sokha.pythonanywhere.com/
https://sokha.pythonanywhere.com/webhook
https://sokha.pythonanywhere.com/webhook_info
https://sokha.pythonanywhere.com/set_webhook?url=WEBHOOK_URL
https://sokha.pythonanywhere.com/delete_webhook

🔧 Fix the Issue
Step 1: Create/Check .env file

cd ~/py-telegram

# Check if .env exists
ls -la .env

# If it doesn't exist or is empty, create it:
nano .env

Step 2: Verify .env file was created:
cat .env


Step 3: Secure the file:
chmod 600 .env

🔧 Webhook Management
Using webhook_manager.py (Interactive):

cd ~/PY-TELEGRAM
workon mybot
python webhook_manager.py

#Manual webhook commands:
# Set webhook
python -c "
import asyncio
from telegram import Bot
from config import Config
bot = Bot(Config.TELEGRAM_BOT_TOKEN)
asyncio.run(bot.set_webhook('https://YOUR_USERNAME.pythonanywhere.com/webhook'))
"

# Delete webhook
python -c "
import asyncio
from telegram import Bot
from config import Config
bot = Bot(Config.TELEGRAM_BOT_TOKEN)
asyncio.run(bot.delete_webhook())
"

# Check webhook info
python -c "
import asyncio
from telegram import Bot
from config import Config
bot = Bot(Config.TELEGRAM_BOT_TOKEN)
info = asyncio.run(bot.get_webhook_info())
print(f'URL: {info.url}')
print(f'Pending: {info.pending_update_count}')
"

# Test loading environment variables
python -c "
from dotenv import load_dotenv
import os
load_dotenv()
print('TELEGRAM_BOT_TOKEN:', os.getenv('TELEGRAM_BOT_TOKEN')[:20] + '...' if os.getenv('TELEGRAM_BOT_TOKEN') else 'NOT SET')
print('GROQ_API_KEY:', os.getenv('GROQ_API_KEY')[:20] + '...' if os.getenv('GROQ_API_KEY') else 'NOT SET')
"
```

You should see something like:
```
TELEGRAM_BOT_TOKEN: 1234567890:ABCdefGH...
GROQ_API_KEY: gsk_1234567890abcd...

#📊 Monitoring
Check Logs in PythonAnywhere:

Go to Web tab
Click Error log (errors from Flask)
Click Server log (access logs)

View Logs via Console:
# Error log
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.error.log

# Server log
tail -f /var/log/YOUR_USERNAME.pythonanywhere.com.server.log

🔄 Deploy/Update Process
Quick Update Steps:
# 1. Upload new code (if using git)
cd ~/PY-TELEGRAM
git pull origin main

# 2. Activate virtual environment
workon mybot

# 3. Update dependencies (if needed)
pip install -r requirements.txt

# 4. Reload web app
# Go to Web tab → Click Reload button

Or use this one-liner:
cd ~/PY-TELEGRAM && git pull && workon mybot && pip install -r requirements.txt

🐛 Debugging Checklist
When bot is not working:

 ✅ Check .env file exists and has correct values
 ✅ Virtual environment is set in Web tab
 ✅ WSGI file is configured correctly
 ✅ Web app is reloaded after changes
 ✅ Webhook is set correctly (visit /webhook_info)
 ✅ Check error logs for Python errors
 ✅ Test Flask app directly (visit main URL)
 ✅ Verify all dependencies are installed
 ✅ Check bot token is valid (test with webhook_manager.py)

 🆘 Common Error Solutions
"ModuleNotFoundError"
workon mybot
pip install MISSING_MODULE
# Reload web app

"Unauthorized" or "Invalid token"
# Check .env file
cat .env
# Verify TELEGRAM_BOT_TOKEN is correct

"Webhook not working"
# Delete and reset webhook
python webhook_manager.py
# Choose option 4 (delete), then option 2 (set)

"502 Bad Gateway"
# Check WSGI configuration
# Make sure paths are correct
# Reload web app

📋 File Structure Reminder
PY-TELEGRAM/
├── handlers/
│   ├── __init__.py
│   ├── commands.py
│   └── messages.py
├── services/
│   ├── __init__.py
│   ├── bot_service.py
│   └── logger.py
├── .env                    # Your secrets
├── config.py
├── bot.py                  # Polling mode (local)
├── flask_app.py           # Webhook mode (production)
├── webhook_manager.py     # Helper script
└── requirements.txt

🎯 Testing Workflow
Local Testing (on your computer):
python bot.py  # Uses polling
# Test all commands
# Ctrl+C to stop
python bot.py  # Uses polling
# Test all commands
# Ctrl+C to stop