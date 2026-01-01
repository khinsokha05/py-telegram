from telegram import Update
from telegram.ext import ContextTypes
from services.logger import LoggerService
from services.bot_service import BotService

# Changed from user_conversations to chat_conversations
# This makes each chat completely separate
chat_conversations = {}

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
    
    await update.message.reply_text(
        "👋 Hello! I'm a smart AI chatbot powered by Sokha.\n\n"
        "You can:\n"
        "• Chat with me naturally\n"
        "• Ask questions on any topic\n"
        "• Get help with coding, writing, analysis\n"
        "• Use /clear to reset conversation\n"
        "• Use /stats to see bot statistics\n"
        "• Use /help for more info\n\n"
        "💡 Each chat has its own separate conversation!\n\n"
        "What would you like to talk about?"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    await update.message.reply_text(
        "🤖 Smart Chatbot Commands:\n\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/clear - Clear conversation history for THIS chat\n"
        "/myGroup - Information Group\n"
        "/stats - Show bot statistics\n\n"
        "/stopAI - Disable AI responses in this chat\n"
        "/startAI - Enable AI responses in this chat\n"
        "Just send me any message and I'll respond intelligently!\n\n"
        "ℹ️ Note: Each chat (private or group) has its own separate conversation history."
    )

async def clear_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /clear command"""
    chat_id = update.effective_chat.id  # Changed from user_id
    user_id = update.effective_user.id
    chat_conversations[chat_id] = []  # Clear by chat_id
    
    await LoggerService.log_user_activity(
        context, user_id,
        update.effective_user.username,
        f"Cleared conversation in chat {chat_id}"
    )
    
    await update.message.reply_text(
        "✅ Conversation history cleared for this chat! Let's start fresh."
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    stats = BotService.get_stats()
    chat_id = update.effective_chat.id
    
    # Count messages in current chat
    messages_in_chat = len(chat_conversations.get(chat_id, []))
    
    stats_message = (
        "📊 <b>Bot Statistics</b>\n\n"
        f"📨 Total Messages (All Chats): {stats['total_messages']}\n"
        f"💬 Messages in This Chat: {messages_in_chat}\n"
        f"👥 Unique Users: {stats['unique_users']}\n"
        f"⏱ Uptime: {stats['uptime']}"
    )
    
    await update.message.reply_text(stats_message, parse_mode='HTML')

async def mygroup_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /myGroup command - shows current chat ID"""
    chat_id = update.effective_chat.id
    chat_type = update.effective_chat.type
    chat_title = update.effective_chat.title if update.effective_chat.title else "Private Chat"
    user_id = update.effective_user.id
    
    message = (
        f"ℹ️ <b>Chat Information</b>\n\n"
        f"📱 Chat Title: {chat_title}\n"
        f"🆔 Chat ID: <code>{chat_id}</code>\n"
        f"📂 Chat Type: {chat_type}\n"
        f"👤 Your User ID: <code>{user_id}</code>\n\n"
        f"💡 Each chat has its own conversation history!\n"
        f"Use /help for more commands."
    )
    
    await update.message.reply_text(message, parse_mode='HTML')


async def test_log_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Test logging to group - for debugging"""
    from config import Config
    
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Check if LOG_GROUP_ID is set
    if not Config.LOG_GROUP_ID:
        await update.message.reply_text(
            "❌ LOG_GROUP_ID is not set in .env file!\n"
            "Please add it to continue."
        )
        return
    
    await update.message.reply_text(
        f"🧪 Testing log to group...\n"
        f"LOG_GROUP_ID: {Config.LOG_GROUP_ID}"
    )
    
    try:
        # Test simple log
        await LoggerService.log_to_group(
            context,
            f"🧪 <b>Test Log Message</b>\n\n"
            f"From User: @{username or 'Unknown'}\n"
            f"User ID: {user_id}\n"
            f"Message: Testing periodic reports",
            "TEST"
        )
        
        # Test user activity log
        await LoggerService.log_user_activity(
            context, user_id, username,
            "Test command executed",
            "Testing logging functionality"
        )
        
        # Show current tracked activity
        activity_count = len(LoggerService.user_activity)
        await update.message.reply_text(
            f"✅ Test messages sent to log group!\n"
            f"📊 Currently tracking {activity_count} users"
        )
        
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {str(e)}")

async def stop_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stopAI command - disable AI responses in this chat"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Disable AI for this chat
    BotService.disable_ai(chat_id)
    
    # Log the action
    await LoggerService.log_user_activity(
        context, user_id, username,
        "AI disabled",
        f"Chat ID: {chat_id}"
    )
    
    await update.message.reply_text(
        "🔴 <b>AI Responses Disabled</b>\n\n"
        "I will no longer respond to regular messages in this chat.\n\n"
        "Commands still work:\n"
        "• /startAI - Re-enable AI responses\n"
        "• /help - Show all commands\n"
        "• /stats - View statistics\n"
        "• /myGroup - Get chat info",
        parse_mode='HTML'
    )

async def start_ai_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /startAI command - enable AI responses in this chat"""
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    username = update.effective_user.username
    
    # Enable AI for this chat
    BotService.enable_ai(chat_id)
    
    # Log the action
    await LoggerService.log_user_activity(
        context, user_id, username,
        "AI enabled",
        f"Chat ID: {chat_id}"
    )
    
    await update.message.reply_text(
        "🟢 <b>AI Responses Enabled</b>\n\n"
        "I'm back! Send me any message and I'll respond.\n\n"
        "Use /stopAI to disable AI responses again.",
        parse_mode='HTML'
    )        