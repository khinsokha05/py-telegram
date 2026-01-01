#!/usr/bin/env python3
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

print("🧪 Testing imports...")

try:
    from telegram.ext import CommandHandler, MessageHandler, filters
    print("✅ telegram.ext imports OK")
except Exception as e:
    print(f"❌ telegram.ext import failed: {e}")

try:
    from config import Config
    print("✅ Config import OK")
except Exception as e:
    print(f"❌ Config import failed: {e}")

try:
    from handlers.commands import start
    print("✅ handlers.commands import OK")
except Exception as e:
    print(f"❌ handlers.commands import failed: {e}")

try:
    from handlers.messages import handle_message
    print("✅ handlers.messages import OK")
except Exception as e:
    print(f"❌ handlers.messages import failed: {e}")

try:
    from flask_app import app
    print("✅ Flask app import OK")
except Exception as e:
    print(f"❌ Flask app import failed: {e}")
