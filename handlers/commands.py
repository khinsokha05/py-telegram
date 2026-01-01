from telegram import Update
from telegram.ext import ContextTypes
from services.logger import LoggerService
from services.bot_service import BotService
import datetime
from zoneinfo import ZoneInfo

# Changed from user_conversations to chat_conversations
# This makes each chat completely separate
chat_conversations = {}

def get_cambodia_time():
    """Get current Cambodia time"""
    cambodia_tz = ZoneInfo('Asia/Phnom_Penh')
    return datetime.datetime.now(cambodia_tz).strftime('%Y-%m-%d %H:%M:%S')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username
    chat_conversations[chat_id] = []
    
    welcome_msg = f"""🇰🇭 ជំរាបសួរ! (Hello!)

🤖 I'm a smart AI chatbot.
🕐 Time: {get_cambodia_time()}

You can:
• Chat with me naturally
• Ask questions on any topic
• Use /clear to reset conversation
• Use /stats to see bot statistics
• Use /help for more info

What would you like to talk about?"""
    
    await update.message.reply_text(welcome_msg)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🤖 Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show help\n"
        "/clear - Clear conversation\n"
        "/stats - Show statistics\n\n"
        "Just send me any message!"
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command"""
    chat_id = update.effective_chat.id
    chat_conversations[chat_id] = []
    await update.message.reply_text("✅ Conversation cleared!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    stats = BotService.get_stats()
    chat_id = update.effective_chat.id
    messages_in_chat = len(chat_conversations.get(chat_id, []))
    
    stats_message = (
        "📊 Bot Statistics\n\n"
        f"📨 Total Messages: {stats['total_messages']}\n"
        f"💬 This Chat: {messages_in_chat}\n"
        f"👥 Users: {stats['unique_users']}\n"
        f"⏱ Uptime: {stats['uptime']}"
    )
    
    await update.message.reply_text(stats_message)

async def mygroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myGroup command"""
    chat_id = update.effective_chat.id
    chat_title = update.effective_chat.title or "Private Chat"
    user_id = update.effective_user.id
    
    message = (
        f"ℹ️ Chat Info\n\n"
        f"📱 Chat: {chat_title}\n"
        f"🆔 Chat ID: {chat_id}\n"
        f"👤 Your ID: {user_id}\n\n"
        f"💡 Each chat has its own history!"
    )
    
    await update.message.reply_text(message)

async def test_log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test logging"""
    from config import Config
    
    if not Config.LOG_GROUP_ID:
        await update.message.reply_text("❌ LOG_GROUP_ID not set!")
        return
    
    await update.message.reply_text("✅ Testing log...")
    
    try:
        await LoggerService.log_to_group(
            context,
            f"🧪 Test Log\nFrom: @{update.effective_user.username or 'Unknown'}",
            "TEST"
        )
        await update.message.reply_text("✅ Log sent!")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def stop_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stopAI command"""
    chat_id = update.effective_chat.id
    BotService.disable_ai(chat_id)
    await update.message.reply_text(
        "🔴 AI Disabled\n\n"
        "I won't respond to messages.\n"
        "Use /startAI to enable again."
    )

async def start_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /startAI command"""
    chat_id = update.effective_chat.id
    BotService.enable_ai(chat_id)
    await update.message.reply_text(
        "🟢 AI Enabled\n\n"
        "I'm back! Send me messages."
    )
async def debug_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Debug command to check AI status"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    is_enabled = BotService.is_ai_enabled(chat_id)
    
    # Get conversation length
    conv_length = len(chat_conversations.get(chat_id, []))
    
    # Get stats
    stats = BotService.get_stats()
    
    message = (
        f"🔍 <b>Debug Information</b>\n\n"
        f"<b>Chat Info:</b>\n"
        f"• Chat ID: <code>{chat_id}</code>\n"
        f"• Chat Type: {update.effective_chat.type}\n"
        f"• Chat Title: {update.effective_chat.title or 'Private Chat'}\n\n"
        
        f"<b>User Info:</b>\n"
        f"• User ID: <code>{user_id}</code>\n"
        f"• Username: @{update.effective_user.username or 'N/A'}\n\n"
        
        f"<b>AI Status:</b>\n"
        f"• AI Enabled: {'✅ YES' if is_enabled else '❌ NO'}\n"
        f"• Messages in chat: {conv_length}\n"
        f"• Active conversations: {len(chat_conversations)}\n\n"
        
        f"<b>Bot Stats:</b>\n"
        f"• Total Messages: {stats['total_messages']}\n"
        f"• Unique Users: {stats['unique_users']}\n"
        f"• Uptime: {stats['uptime']}\n\n"
        
        f"<i>Use /startAI to enable AI, /stopAI to disable</i>"
    )
    
    await update.message.reply_text(message, parse_mode='HTML')
    
    # Log this activity
    await LoggerService.log_user_activity(
        context, user_id,
        update.effective_user.username,
        "Used debug command",
        f"AI enabled: {is_enabled}, Conv length: {conv_length}"
    )
