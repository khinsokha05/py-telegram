import logging
from datetime import datetime
from config import Config

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class LoggerService:
    """Logging service for bot operations"""
    
    # Track user activity
    user_activity = {}  # {user_id: {"username": "...", "requests": 0, "last_active": datetime}}
    
    @staticmethod
    async def log_to_group(context, message: str, log_type: str = "INFO"):
        """Send log messages to designated log group"""
        if not Config.LOG_GROUP_ID:
            logger.warning("LOG_GROUP_ID not set")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_message = f"🤖 [{log_type}] {timestamp}\n\n{message}"
            await context.bot.send_message(
                chat_id=Config.LOG_GROUP_ID,
                text=log_message,
                parse_mode='HTML'
            )
        except Exception as e:
            logger.error(f"Failed to log to group: {e}")
    
    @staticmethod
    async def log_user_activity(context, user_id: int, username: str, action: str, details: str = "", chat_name: str = None):
        """Log user activity"""
        message = (
            f"👤 <b>User Activity</b>\n"
            f"User ID: <code>{user_id}</code>\n"
            f"Username: @{username or 'N/A'}\n"
        )
        
        if chat_name:
            message += f"Chat: {chat_name}\n"
        
        message += (
            f"Action: {action}\n"
            f"Details: {details}"
        )
        await LoggerService.log_to_group(context, message, "USER")
    
    @staticmethod
    async def log_error(context, error_msg: str, user_id: int = None, chat_name: str = None):
        """Log errors"""
        message = f"❌ <b>Error Occurred</b>\n"
        if user_id:
            message += f"User ID: <code>{user_id}</code>\n"
        if chat_name:
            message += f"Chat: {chat_name}\n"
        message += f"Error: {error_msg}"
        await LoggerService.log_to_group(context, message, "ERROR")
    
    @staticmethod
    def track_user_request(user_id: int, username: str):
        """Track user requests for statistics"""
        if user_id not in LoggerService.user_activity:
            LoggerService.user_activity[user_id] = {
                "username": username,
                "requests": 0,
                "last_active": datetime.now()
            }
        
        LoggerService.user_activity[user_id]["requests"] += 1
        LoggerService.user_activity[user_id]["last_active"] = datetime.now()
        LoggerService.user_activity[user_id]["username"] = username  # Update in case it changed