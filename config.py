import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Telegram Bot Token
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    
    # Groq API Configuration
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')  # Updated model!
    
    # Bot Configuration
    MAX_HISTORY = int(os.getenv('MAX_HISTORY', '10'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1024'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    
    # Message Moderation (ADD THESE!)
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '1000'))
    BANNED_WORDS = os.getenv('BANNED_WORDS', '').split(',') if os.getenv('BANNED_WORDS') else []
    
    # Logging
    LOG_GROUP_ID = os.getenv('LOG_GROUP_ID')
    
    # Admin IDs (comma separated)
    ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',') if os.getenv('ADMIN_IDS') else []
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in .env file")
