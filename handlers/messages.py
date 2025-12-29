import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from groq import Groq
from config import Config
from services.logger import LoggerService
from services.bot_service import BotService
from handlers.commands import chat_conversations  # Changed from user_conversations

logger = logging.getLogger(__name__)

groq_client = Groq(api_key=Config.GROQ_API_KEY)

def format_message_for_telegram(text: str) -> str:
    """Format message for Telegram MarkdownV2"""
    # If message contains code blocks, format them properly
    if '```' in text:
        # Already has code blocks, just escape special characters outside code blocks
        parts = text.split('```')
        for i in range(0, len(parts), 2):  # Only escape text parts, not code parts
            # Escape MarkdownV2 special characters
            parts[i] = escape_markdown_v2(parts[i])
        return '```'.join(parts)
    else:
        # No code blocks, just escape special characters
        return escape_markdown_v2(text)

def escape_markdown_v2(text: str) -> str:
    """Escape special characters for MarkdownV2"""
    # Characters that need to be escaped in MarkdownV2
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    
    return text

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user messages"""
    chat_id = update.effective_chat.id  # Added for chat-based separation
    user_id = update.effective_user.id
    username = update.effective_user.username
    user_message = update.message.text
    chat_type = update.effective_chat.type

    # Get chat name
    chat_name = update.effective_chat.title if update.effective_chat.title else "Private Chat"

    # Check if AI is enabled for this chat
    if not BotService.is_ai_enabled(chat_id):
        return

    # Track user request for statistics
    LoggerService.track_user_request(user_id, username)
    BotService.update_stats(user_id)
    
    if not await BotService.check_user_permission(user_id):
        await update.message.reply_text("❌ You don't have permission.")
        return
    
    is_valid, reason = await BotService.moderate_message(user_message)
    if not is_valid:
        await update.message.reply_text(f"❌ {reason}")
        await LoggerService.log_to_group(
            context,
            f"⚠️ <b>Moderation triggered</b>\n"
            f"User: <code>{user_id}</code>, @{username or 'Unknown'}\n"
            f"Chat: <code>{chat_id}</code>, {chat_name}\n"
            f"Reason: {reason}",
            "WARNING"
        )
        return
    
    # Use chat_id instead of user_id for separate conversations per chat
    if chat_id not in chat_conversations:
        chat_conversations[chat_id] = []
    
    chat_conversations[chat_id].append({
        "role": "user",
        "content": user_message
    })
    
    if len(chat_conversations[chat_id]) > Config.MAX_HISTORY:
        chat_conversations[chat_id] = chat_conversations[chat_id][-Config.MAX_HISTORY:]
    
    try:
        await update.message.chat.send_action(action="typing")
        
        # Add system prompt to help with code formatting
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant created by Sokha. When providing code examples, always wrap them in triple backticks with the language name. Example: ```python\nprint('hello')\n```"
            }
        ] + chat_conversations[chat_id]
        
        chat_completion = groq_client.chat.completions.create(
            messages=messages,
            model=Config.GROQ_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
        )
        
        assistant_message = chat_completion.choices[0].message.content
        
        chat_conversations[chat_id].append({
            "role": "assistant",
            "content": assistant_message
        })

        # Format code blocks properly for Telegram
        formatted_message = format_message_for_telegram(assistant_message)
        
        await update.message.reply_text(
            formatted_message,
            parse_mode='MarkdownV2'
        )
        
        # await LoggerService.log_user_activity(
        #     context, user_id, username,
        #     "Message processed",
        #     f"Chat: {chat_id} ({chat_type}), Message: {user_message[:50]}..."
        # )
        
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error in chat {chat_id}: {error_msg}")
        await LoggerService.log_error(context, error_msg, user_id)
        await update.message.reply_text(
            "❌ An error occurred. Please try again or use /clear."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update {update} caused error {context.error}")
    if context.application:
        await LoggerService.log_error(context, f"Update error: {context.error}")
