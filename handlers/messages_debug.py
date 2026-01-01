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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """DEBUG VERSION - Log everything"""
    logger.info(f"📥 DEBUG: Received message from {update.effective_user.id}: {update.message.text}")
    
    # Get Groq client
    client = get_groq_client()
    if client is None:
        logger.error("DEBUG: Groq client is None")
        await update.message.reply_text("❌ AI service unavailable.")
        return
    
    chat_id = update.effective_chat.id
    user_id = update.effective_user.id
    user_message = update.message.text
    
    logger.info(f"DEBUG: Chat ID: {chat_id}, User ID: {user_id}")
    
    # Check if AI is enabled
    ai_enabled = BotService.is_ai_enabled(chat_id)
    logger.info(f"DEBUG: AI enabled for chat {chat_id}: {ai_enabled}")
    
    if not ai_enabled:
        logger.info(f"DEBUG: AI disabled for chat {chat_id}, enabling...")
        BotService.enable_ai(chat_id)  # Auto-enable
        # await update.message.reply_text("🤖 AI enabled for this chat!")
    
    # Track user
    try:
        LoggerService.track_user_request(user_id, update.effective_user.username)
        BotService.update_stats(user_id)
        logger.info("DEBUG: User tracked")
    except Exception as e:
        logger.error(f"DEBUG: User tracking error: {e}")
    
    # Check permission
    has_permission = await BotService.check_user_permission(user_id)
    logger.info(f"DEBUG: User {user_id} has permission: {has_permission}")
    
    if not has_permission:
        await update.message.reply_text("❌ No permission.")
        return
    
    # Check message length
    logger.info(f"DEBUG: Message length: {len(user_message)}, Max: {Config.MAX_MESSAGE_LENGTH}")
    if len(user_message) > Config.MAX_MESSAGE_LENGTH:
        await update.message.reply_text(f"❌ Message too long (max {Config.MAX_MESSAGE_LENGTH} chars)")
        return
    
    # Initialize conversation
    if chat_id not in chat_conversations:
        chat_conversations[chat_id] = []
        logger.info(f"DEBUG: Created new conversation for chat {chat_id}")
    
    # Add user message
    chat_conversations[chat_id].append({
        "role": "user",
        "content": user_message
    })
    
    logger.info(f"DEBUG: Conversation history length: {len(chat_conversations[chat_id])}")
    
    # Limit history
    if len(chat_conversations[chat_id]) > Config.MAX_HISTORY:
        chat_conversations[chat_id] = chat_conversations[chat_id][-Config.MAX_HISTORY:]
    
    try:
        await update.message.chat.send_action(action="typing")
        logger.info("DEBUG: Sent typing action")
        
        # Prepare messages
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Respond concisely."
            }
        ] + chat_conversations[chat_id]
        
        logger.info(f"DEBUG: Sending to Groq model {Config.GROQ_MODEL}")
        
        # Get AI response
        response = client.chat.completions.create(
            messages=messages,
            model=Config.GROQ_MODEL,
            temperature=Config.TEMPERATURE,
            max_tokens=Config.MAX_TOKENS,
        )
        
        ai_response = response.choices[0].message.content
        logger.info(f"DEBUG: Got AI response: {ai_response[:50]}...")
        
        # Save AI response
        chat_conversations[chat_id].append({
            "role": "assistant",
            "content": ai_response
        })
        
        # Send response
        await update.message.reply_text(f"🤖 {ai_response}")
        logger.info(f"✅ DEBUG: Response sent to chat {chat_id}")
        
    except Exception as e:
        logger.error(f"DEBUG: Error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        await update.message.reply_text("❌ Error. Try again.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update error: {context.error}")
