#!/usr/bin/env python3
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_complete():
    print("🧪 Running final comprehensive test...")
    print("=" * 60)
    
    # Test 1: Config
    print("1️⃣ Testing configuration...")
    try:
        from config import Config
        Config.validate()
        print("   ✅ Config valid")
        print(f"   Token: {'✓' if Config.TELEGRAM_BOT_TOKEN else '✗'}")
        print(f"   Groq Key: {'✓' if Config.GROQ_API_KEY else '✗'}")
    except Exception as e:
        print(f"   ❌ Config error: {e}")
        return False
    
    # Test 2: Bot creation
    print("\n2️⃣ Testing bot creation...")
    try:
        from telegram.ext import Application
        app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        print("   ✅ Bot app created")
    except Exception as e:
        print(f"   ❌ Bot creation error: {e}")
        return False
    
    # Test 3: Telegram API connection
    print("\n3️⃣ Testing Telegram API connection...")
    try:
        from telegram import Bot
        bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
        me = await bot.get_me()
        print(f"   ✅ Connected to Telegram")
        print(f"   Bot: @{me.username} ({me.first_name})")
    except Exception as e:
        print(f"   ❌ Telegram API error: {e}")
        return False
    
    # Test 4: Flask app
    print("\n4️⃣ Testing Flask app...")
    try:
        from flask_app import app as flask_app, ensure_bot_initialized
        print("   ✅ Flask app loaded")
        print(f"   Bot initialized: {ensure_bot_initialized()}")
    except Exception as e:
        print(f"   ❌ Flask app error: {e}")
        return False
    
    # Test 5: Webhook setup
    print("\n5️⃣ Testing webhook setup...")
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        print("   ✅ Old webhook deleted")
        
        result = await bot.set_webhook(
            url="https://sokha.pythonanywhere.com/webhook",
            drop_pending_updates=True,
            max_connections=100
        )
        print(f"   ✅ Webhook set: {result}")
    except Exception as e:
        print(f"   ❌ Webhook error: {e}")
        return False
    
    print("\n" + "=" * 60)
    print("🎉 ALL TESTS PASSED!")
    print("\n📋 Next steps:")
    print("1. Visit: https://sokha.pythonanywhere.com/")
    print("2. Visit: https://sokha.pythonanywhere.com/health")
    print("3. Visit: https://sokha.pythonanywhere.com/test_bot")
    print("4. Visit: https://sokha.pythonanywhere.com/set_webhook")
    print("5. Send /start to your bot")
    return True

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        success = loop.run_until_complete(test_complete())
        if not success:
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
