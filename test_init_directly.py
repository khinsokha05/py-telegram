#!/usr/bin/env python3
import sys
import os
import asyncio

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_direct_initialization():
    """Test bot initialization directly"""
    print("🧪 Testing direct bot initialization...")
    
    try:
        from telegram.ext import Application, CommandHandler, MessageHandler, filters
        from config import Config
        from handlers.commands import (
            start, help_command, clear_command, stats_command,
            mygroup_command, test_log_command, stop_ai_command,
            start_ai_command, debug_command
        )
        from handlers.messages import handle_message, error_handler
        
        # Validate config
        Config.validate()
        print("✅ Config validated")
        
        # Create application
        app = Application.builder().token(Config.TELEGRAM_BOT_TOKEN).build()
        print("✅ Application created")
        
        # Add handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CommandHandler("help", help_command))
        app.add_handler(CommandHandler("clear", clear_command))
        app.add_handler(CommandHandler("stats", stats_command))
        app.add_handler(CommandHandler("myGroup", mygroup_command))
        app.add_handler(CommandHandler("testlog", test_log_command))
        app.add_handler(CommandHandler("stopAI", stop_ai_command))
        app.add_handler(CommandHandler("startAI", start_ai_command))
        app.add_handler(CommandHandler("debug", debug_command))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
        app.add_error_handler(error_handler)
        
        print("✅ Handlers added")
        
        # Initialize
        await app.initialize()
        print("✅ Application initialized")
        
        # Check if initialized
        print(f"✅ _initialized attribute: {hasattr(app, '_initialized')}")
        if hasattr(app, '_initialized'):
            print(f"   Value: {app._initialized}")
        
        # Test getMe
        bot_info = await app.bot.get_me()
        print(f"✅ Bot info: @{bot_info.username} ({bot_info.first_name})")
        
        # Test sending a message (to yourself)
        try:
            test_message = await app.bot.send_message(
                chat_id=bot_info.id,  # Send to yourself
                text="🤖 Bot self-test successful!"
            )
            print(f"✅ Test message sent: {test_message.message_id}")
        except Exception as e:
            print(f"⚠️ Could not send test message: {e}")
        
        # Don't shutdown - keep it running for webhook
        print("✅ Bot ready for webhook mode")
        
        return app
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        app = loop.run_until_complete(test_direct_initialization())
        if app:
            print("\n🎉 Direct initialization test PASSED!")
            print("\n📋 Bot is ready. Keep this running for webhook mode.")
            print("Press Ctrl+C to exit.")
            
            # Keep running for testing
            try:
                loop.run_forever()
            except KeyboardInterrupt:
                print("\n🛑 Shutting down...")
                loop.run_until_complete(app.shutdown())
        else:
            print("\n❌ Direct initialization test FAILED!")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n❌ Test interrupted")
        sys.exit(1)
