#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config import Config

def test_config():
    print("🔧 Testing configuration...")
    try:
        Config.validate()
        print("✅ Configuration is valid!")
        print(f"🤖 Bot Token: {'✓' if Config.TELEGRAM_BOT_TOKEN else '✗'}")
        print(f"🔑 Groq API Key: {'✓' if Config.GROQ_API_KEY else '✗'}")
        print(f"📝 Model: {Config.GROQ_MODEL}")
        print(f"👥 Admin IDs: {Config.ADMIN_IDS}")
        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_imports():
    print("\n📦 Testing imports...")
    try:
        from flask_app import app
        print("✅ Flask app imported")
        
        from handlers.commands import chat_conversations
        print("✅ Commands imported")
        
        from handlers.messages import get_groq_client
        print("✅ Messages imported")
        
        from services.bot_service import BotService
        print("✅ Bot service imported")
        
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Running bot tests...")
    
    config_ok = test_config()
    imports_ok = test_imports()
    
    if config_ok and imports_ok:
        print("\n🎉 All tests passed! Bot should work correctly.")
    else:
        print("\n⚠️  Some tests failed. Please fix the issues above.")
        sys.exit(1)
