"""
Bot Service - Simplified version
"""
import time
from config import Config

# Statistics
bot_start_time = time.time()
total_messages = 0
unique_users = set()

# AI enabled chats
ai_enabled_chats = set()

class BotService:
    @staticmethod
    def update_stats(user_id):
        """Update bot statistics"""
        global total_messages, unique_users
        total_messages += 1
        unique_users.add(user_id)
    
    @staticmethod
    def get_stats():
        """Get bot statistics"""
        global total_messages, unique_users, bot_start_time
        
        uptime = time.time() - bot_start_time
        hours = int(uptime // 3600)
        minutes = int((uptime % 3600) // 60)
        
        return {
            'total_messages': total_messages,
            'unique_users': len(unique_users),
            'uptime': f'{hours}h {minutes}m'
        }
    
    @staticmethod
    async def moderate_message(message):
        """Simple message moderation"""
        # Check message length
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            return False, f"Message too long (max {Config.MAX_MESSAGE_LENGTH} characters)"
        
        # Check for banned words
        for word in Config.BANNED_WORDS:
            if word and word in message.lower():
                return False, "Message contains inappropriate content"
        
        return True, ""
    
    @staticmethod
    async def check_user_permission(user_id):
        """Check if user has permission"""
        if not Config.ADMIN_IDS:
            return True  # No restrictions if no admin IDs set ..
        
        return str(user_id) in Config.ADMIN_IDS
    
    @staticmethod
    def is_ai_enabled(chat_id):
        """Check if AI is enabled for chat"""
        return chat_id in ai_enabled_chats
    
    @staticmethod
    def enable_ai(chat_id):
        """Enable AI for chat"""
        ai_enabled_chats.add(chat_id)
    
    @staticmethod
    def disable_ai(chat_id):
        """Disable AI for chat"""
        if chat_id in ai_enabled_chats:
            ai_enabled_chats.remove(chat_id)
