import os
from dotenv import load_dotenv

# Absolute path for the .env file
base_dir = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(base_dir, ".env"))

class Config:
    TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
    GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
    LOG_GROUP_ID = os.environ.get("LOG_GROUP_ID")
    
    GROQ_MODEL = "llama-3.3-70b-versatile"
    TEMPERATURE = 0.7
    MAX_TOKENS = 1024
    MAX_MESSAGE_LENGTH = 1000
    
    @classmethod
    def validate(cls):
        if not cls.TELEGRAM_BOT_TOKEN or not cls.GROQ_API_KEY:
            raise ValueError("Missing API Keys in .env file")
        return True