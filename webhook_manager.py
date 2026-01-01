"""
Webhook Management Script for Telegram Bot
This script helps you manage webhooks for your bot
"""

import asyncio
import sys
from telegram import Bot
from config import Config

class WebhookManager:
    def __init__(self):
        Config.validate()
        self.bot = Bot(token=Config.TELEGRAM_BOT_TOKEN)
    
    async def get_webhook_info(self):
        """Get current webhook information"""
        print("\n📋 Fetching webhook information...")
        info = await self.bot.get_webhook_info()
        
        print("\n" + "="*50)
        print("🔗 WEBHOOK INFORMATION")
        print("="*50)
        print(f"URL: {info.url or 'Not set'}")
        print(f"Pending updates: {info.pending_update_count}")
        print(f"Max connections: {info.max_connections}")
        
        if info.last_error_date:
            print(f"\n⚠️  Last error date: {info.last_error_date}")
            print(f"Last error message: {info.last_error_message}")
        else:
            print("\n✅ No errors reported")
        
        print("="*50 + "\n")
        return info
    
    async def set_webhook(self, url: str):
        """Set webhook URL"""
        print(f"\n🔧 Setting webhook to: {url}")
        
        try:
            # First delete old webhook
            await self.bot.delete_webhook()
            print("✅ Old webhook deleted")
            
            # Set new webhook
            result = await self.bot.set_webhook(
                url=url,
                drop_pending_updates=True,
                max_connections=100
            )
            
            if result:
                print(f"✅ Webhook successfully set to: {url}")
                await self.get_webhook_info()
            else:
                print("❌ Failed to set webhook")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def delete_webhook(self):
        """Delete webhook (switch to polling mode)"""
        print("\n🗑️  Deleting webhook...")
        
        try:
            result = await self.bot.delete_webhook(drop_pending_updates=True)
            
            if result:
                print("✅ Webhook deleted successfully")
                print("ℹ️  Bot is now ready for polling mode (bot.py)")
            else:
                print("❌ Failed to delete webhook")
                
        except Exception as e:
            print(f"❌ Error: {e}")
    
    async def test_bot(self):
        """Test if bot is accessible"""
        print("\n🧪 Testing bot connection...")
        
        try:
            me = await self.bot.get_me()
            print(f"✅ Bot is accessible!")
            print(f"   Username: @{me.username}")
            print(f"   Name: {me.first_name}")
            print(f"   ID: {me.id}")
        except Exception as e:
            print(f"❌ Error connecting to bot: {e}")

def print_menu():
    """Print menu options"""
    print("\n" + "="*50)
    print("🤖 TELEGRAM BOT WEBHOOK MANAGER")
    print("="*50)
    print("1. Get webhook info")
    print("2. Set webhook (PythonAnywhere)")
    print("3. Set webhook (Custom URL)")
    print("4. Delete webhook")
    print("5. Test bot connection")
    print("6. Exit")
    print("="*50)

async def main():
    """Main function"""
    manager = WebhookManager()
    
    while True:
        print_menu()
        choice = input("\nEnter your choice (1-6): ").strip()
        
        if choice == "1":
            await manager.get_webhook_info()
            
        elif choice == "2":
            username = input("Enter your PythonAnywhere username: ").strip()
            url = f"https://{username}.pythonanywhere.com/webhook"
            await manager.set_webhook(url)
            
        elif choice == "3":
            url = input("Enter webhook URL: ").strip()
            if url:
                await manager.set_webhook(url)
            else:
                print("❌ URL cannot be empty")
                
        elif choice == "4":
            confirm = input("⚠️  Delete webhook? (yes/no): ").strip().lower()
            if confirm == "yes":
                await manager.delete_webhook()
                
        elif choice == "5":
            await manager.test_bot()
            
        elif choice == "6":
            print("\n👋 Goodbye!")
            break
            
        else:
            print("❌ Invalid choice. Please try again.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted by user. Goodbye!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        sys.exit(1)