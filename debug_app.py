import sys
import os
import logging

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def debug_flask_app():
    """Debug Flask app initialization"""
    print("🔧 Debugging Flask app...")
    
    try:
        # Test config first
        from config import Config
        print("✅ Config module loaded")
        
        try:
            Config.validate()
            print("✅ Config validation passed")
            print(f"   Bot Token: {'✓ Set' if Config.TELEGRAM_BOT_TOKEN else '✗ Missing'}")
            print(f"   Groq API Key: {'✓ Set' if Config.GROQ_API_KEY else '✗ Missing'}")
        except Exception as e:
            print(f"❌ Config validation failed: {e}")
            return False
        
    except ImportError as e:
        print(f"❌ Cannot import config: {e}")
        print("   Make sure .env file exists in the same directory")
        return False
    
    try:
        # Test Flask app creation
        print("\n🚀 Testing Flask app creation...")
        from flask_app import app, bot_app, initialize_bot
        
        print(f"✅ Flask app loaded")
        print(f"   Bot app initialized: {bot_app is not None}")
        
        # Try to initialize bot
        if bot_app is None:
            print("\n🔄 Attempting to initialize bot...")
            try:
                result = initialize_bot()
                print(f"   Initialize result: {'✓ Success' if result else '✗ Failed'}")
            except Exception as e:
                print(f"❌ Initialize failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        
        # Test webhook URL
        print("\n🌐 Testing webhook URL...")
        base_url = "https://sokha.pythonanywhere.com"
        print(f"   Base URL: {base_url}")
        print(f"   Webhook: {base_url}/webhook")
        print(f"   Health: {base_url}/health")
        
        return True
        
    except Exception as e:
        print(f"❌ Error debugging Flask app: {e}")
        import traceback
        traceback.print_exc()
        return False

def check_requirements():
    """Check installed packages"""
    print("\n📦 Checking requirements...")
    
    required_packages = [
        "flask",
        "python-telegram-bot",
        "groq",
        "httpx",
        "python-dotenv"
    ]
    
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"   ✅ {package}")
        except ImportError:
            print(f"   ❌ {package} (missing)")
    
    # Check Python version
    print(f"\n🐍 Python version: {sys.version}")

if __name__ == "__main__":
    print("🧪 Starting comprehensive debug...")
    print("=" * 50)
    
    check_requirements()
    print("\n" + "=" * 50)
    
    success = debug_flask_app()
    
    print("\n" + "=" * 50)
    if success:
        print("✅ Debug completed - check recommendations above")
    else:
        print("❌ Debug found issues - see errors above")
