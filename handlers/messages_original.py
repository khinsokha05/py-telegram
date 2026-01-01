import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from config import Config
from services.logger import LoggerService
from services.bot_service import BotService
from handlers.commands import chat_conversations

logger = logging.getLogger(__name__)

# Lazy Groq client
groq_client = None

def get_groq_client():
    """Get Groq client"""
    global groq_client
    
    if groq_client is not None:
        return groq_client
    
    try:
        from groq import Groq
        import httpx
        
        logger.info(f"🤖 Initializing Groq client with model: {Config.GROQ_MODEL}")
        
        groq_client = Groq(
            api_key=Config.GROQ_API_KEY,
            http_client=httpx.Client()
        )
        
        logger.info("✅ Groq client initialized")
        return groq_client
        
    except Exception as e:
        logger.error(f"❌ Groq client error: {e}")
        return None

def format_message_for_telegram(text: str) -> str:
    """Format AI response for Telegram"""
    if '```' in text:
        parts = text.split('```')
        for i in range(0, len(parts), 2):
            parts[i] = escape_markdown_v2(parts[i])
        return '```'.join(parts)
    else:
        return escape_markdown_v2(text)

def escape_markdown_v2(text: str) -> str:
    """Escape Telegram MarkdownV2 characters"""
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages with AI"""
    # Get Groq client
    client = get_groq_client()
    if client is None:
        await update.message.reply_text("❌ AI service unavailable.")
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_message = update.message.text

    # Check if AI is enabled
    if not BotService.is_ai_enabled(chat_id):
        return

    # Track user
    try:
        LoggerService.track_user_request(user_id, update.effective_user.username)
        BotService.update_stats(user_id)
    except:
        pass
    
    # Simple permission check
    if not await BotService.check_user_permission(user_id):
        await update.message.reply_text("❌ No permission.")
        return
    
    # Simple moderation
    if len(user_message) > Config.MAX_MESSAGE_LENGTH:
        await update.message.reply_text(f"❌ Message too long (max {Config.MAX_MESSAGE_LENGTH} chars)")
        return
    
    # Initialize conversation
    if chat_id not in chat_conversations:
        chat_conversations[chat_id] = []
    
    # Add user message
    chat_conversations[chat_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Limit history
    if len(chat_conversations[chat_id]) > Config.MAX_HISTORY:
        chat_conversations[chat_id] = chat_conversations[chat_id][-Config.MAX_HISTORY:]
    
    try:
        await update.message.chat.send_action(action="typing")
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Respond helpfully and concisely."
            }
        ] + chat_conversations[chat_id]
        
        # Get AI response
        response = client.chat.completions.create(
            messages=messages,
            model=Config.GROQ_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
        )
        
        ai_response = response.choices[0].message.content
        
        # Save AI response
        chat_conversations[chat_id].append({
            "role": "assistant",
            "content": ai_response
        })

        # Format and send
        formatted_message = format_message_for_telegram(ai_response)
        
        await update.message.reply_text(
            formatted_message,
            parse_mode='MarkdownV2'
        )
        
        logger.info(f"✅ AI response sent to chat {chat_id}")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        await update.message.reply_text("❌ Error. Try again.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update error: {context.error}")
