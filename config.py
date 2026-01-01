import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    # Required
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
    GROQ_API_KEY = os.getenv('GROQ_API_KEY')
    
    # Optional with defaults
    GROQ_MODEL = os.getenv('GROQ_MODEL', 'llama-3.3-70b-versatile')
    MAX_HISTORY = int(os.getenv('MAX_HISTORY', '10'))
    MAX_TOKENS = int(os.getenv('MAX_TOKENS', '1024'))
    TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
    MAX_MESSAGE_LENGTH = int(os.getenv('MAX_MESSAGE_LENGTH', '1000'))
    
    # Optional
    LOG_GROUP_ID = os.getenv('LOG_GROUP_ID')
    ADMIN_IDS = os.getenv('ADMIN_IDS', '').split(',') if os.getenv('ADMIN_IDS') else []
    BANNED_WORDS = os.getenv('BANNED_WORDS', '').split(',') if os.getenv('BANNED_WORDS') else []
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN is not set in .env file")
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY is not set in .env file")