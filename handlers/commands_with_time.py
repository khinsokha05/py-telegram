from telegram import Update
from telegram.ext import ContextTypes
from services.logger import LoggerService
from services.bot_service import BotService
import datetime
import pytz

# Changed from user_conversations to chat_conversations
# This makes each chat completely separate
chat_conversations = {}

def get_cambodia_time():
    """Get current Cambodia time"""
    cambodia_tz = pytz.timezone('Asia/Phnom_Penh')
    return datetime.datetime.now(cambodia_tz).strftime('%Y-%m-%d %H:%M:%S')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id  # Changed from user_id
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_conversations[chat_id] = []  # Store by chat_id
    
    await LoggerService.log_user_activity(
        context, user_id, username, "Started bot",
        f"First name: {update.effective_user.first_name}, Chat ID: {chat_id}"
    )
    
    # Get Cambodia time
    cambodia_time = get_cambodia_time()
    
    welcome_msg = f"""🇰🇭 ជំរាបសួរ! (Hello from Cambodia!)

🤖 I'm a smart AI chatbot powered by Sokha.
🕐 Cambodia Time: {cambodia_time}

You can:
• Chat with me naturally
• Ask questions on any topic
• Get help with coding, writing, analysis
• Use /clear to reset conversation
• Use /stats to see bot statistics
• Use /help for more info

💡 Each chat has its own separate conversation!

What would you like to talk about?"""
    
    await update.message.reply_text(welcome_msg)

# ... (rest of your existing handlers remain the same)
# Copy your existing help_command, clear_command, etc. here
