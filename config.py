import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Bot configuration"""
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    LOG_GROUP_ID = os.environ.get("LOG_GROUP_ID")
    
    # Bot settings
    MAX_HISTORY = 20
    GROQ_MODEL = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.7
    MAX_TOKENS = 1024
    
    # Moderation
    BANNED_WORDS = ["spam", "abuse"]
    MAX_MESSAGE_LENGTH = 1000
    
    @classmethod
    def validate(cls):
        """Validate required config"""
        if not cls.TELEGRAM_BOT_TOKEN:
            raise ValueError("TELEGRAM_BOT_TOKEN not set")
        if not cls.GROQ_API_KEY:
            raise ValueError("GROQ_API_KEY not set")
        return True