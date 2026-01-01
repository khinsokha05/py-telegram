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
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_message = update.message.text
    
    logger.info(f"📨 Message from {user_id} in chat {chat_id}: {user_message[:50]}...")
    
    # ENABLE AI BY DEFAULT FOR PRIVATE CHATS
    if update.effective_chat.type == 'private' and not BotService.is_ai_enabled(chat_id):
        logger.info(f"🤖 Auto-enabling AI for private chat {chat_id}")
        BotService.enable_ai(chat_id)
    
    # If AI is not enabled for this chat, don't respond
    if not BotService.is_ai_enabled(chat_id):
        logger.info(f"🚫 AI not enabled for chat {chat_id}")
        return
    
    # Get Groq client
    client = get_groq_client()
    if client is None:
        await update.message.reply_text("❌ AI service is currently unavailable. Please try again later.")
        return

    # Track user
    try:
        LoggerService.track_user_request(user_id, update.effective_user.username)
        BotService.update_stats(user_id)
    except Exception as e:
        logger.error(f"Error tracking user: {e}")
    
    # Simple permission check
    if not await BotService.check_user_permission(user_id):
        await update.message.reply_text("❌ You don't have permission to use this bot.")
        return
    
    # Simple moderation
    if len(user_message) > Config.MAX_MESSAGE_LENGTH:
        await update.message.reply_text(f"❌ Message too long (max {Config.MAX_MESSAGE_LENGTH} characters)")
        return
    
    # Initialize conversation
    if chat_id not in chat_conversations:
        chat_conversations[chat_id] = []
        logger.info(f"📝 Created new conversation for chat {chat_id}")
    
    # Add user message
    chat_conversations[chat_id].append({
        "role": "user",
        "content": user_message
    })
    
    # Limit history
    if len(chat_conversations[chat_id]) > Config.MAX_HISTORY:
        chat_conversations[chat_id] = chat_conversations[chat_id][-Config.MAX_HISTORY:]
        logger.info(f"📚 Trimmed history for chat {chat_id}")
    
    try:
        # Show typing indicator
        await update.message.chat.send_action(action="typing")
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Respond helpfully and concisely. Use markdown for code when appropriate."
            }
        ] + chat_conversations[chat_id]
        
        logger.info(f"🤖 Sending request to Groq API with model: {Config.GROQ_MODEL}")
        
        # Get AI response
        response = client.chat.completions.create(
            messages=messages,
            model=Config.GROQ_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"✅ Received AI response ({len(ai_response)} chars)")
        
        # Save AI response
        chat_conversations[chat_id].append({
            "role": "assistant",
            "content": ai_response
        })

        # Format and send
        try:
            formatted_message = format_message_for_telegram(ai_response)
            await update.message.reply_text(
                formatted_message,
                parse_mode='MarkdownV2'
            )
            logger.info(f"✅ AI response sent to chat {chat_id}")
        except Exception as e:
            # Fallback to plain text if markdown fails
            logger.error(f"Markdown error: {e}, falling back to plain text")
            await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"❌ Error in AI processing: {e}")
        # Remove failed conversation entry
        if chat_id in chat_conversations and chat_conversations[chat_id]:
            chat_conversations[chat_id].pop()  # Remove user message
        
        await update.message.reply_text(
            "❌ Sorry, I encountered an error while processing your message. "
            "Please try again in a moment."
        )

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update error: {context.error}")
    
    # Log to group if available
    if update and update.effective_user:
        try:
            await LoggerService.log_error(
                context,
                str(context.error),
                user_id=update.effective_user.id,
                chat_name=update.effective_chat.title if update.effective_chat.title else "Private"
            )
        except:
            pass
