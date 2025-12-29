from datetime import datetime
from config import Config

class BotService:
    """Service for bot business logic"""
    
    stats = {
        "total_messages": 0,
        "total_users": set(),
        "start_time": datetime.now()
    }
    
    @staticmethod
    def update_stats(user_id: int):
        """Update bot statistics"""
        BotService.stats["total_messages"] += 1
        BotService.stats["total_users"].add(user_id)
    
    @staticmethod
    def get_stats() -> dict:
        """Get current statistics"""
        uptime = datetime.now() - BotService.stats["start_time"]
        return {
            "total_messages": BotService.stats["total_messages"],
            "unique_users": len(BotService.stats["total_users"]),
            "uptime": str(uptime).split('.')[0]
        }
    
    @staticmethod
    async def check_user_permission(user_id: int) -> bool:
        """Check user permissions"""
        return True
    
    @staticmethod
    async def moderate_message(message: str) -> tuple[bool, str]:
        """Moderate user messages"""
        if len(message) > Config.MAX_MESSAGE_LENGTH:
            return False, "Message too long"
        
        for word in Config.BANNED_WORDS:
            if word.lower() in message.lower():
                return False, f"Contains inappropriate content: {word}"
        
        return True, "OK"