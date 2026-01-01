import logging
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
    """Handle incoming messages - SIMPLIFIED VERSION"""
    user_id = update.effective_user.id
    user_message = update.message.text
    chat_id = update.effective_chat.id
    
    logger.info(f"📥 Message from {user_id} in chat {chat_id}: {user_message[:50]}...")
    
    # Quick checks
    if len(user_message) > Config.MAX_MESSAGE_LENGTH:
        await update.message.reply_text(f"❌ Message too long (max {Config.MAX_MESSAGE_LENGTH} chars)")
        return
    
    # Get Groq client
    client = get_groq_client()
    if client is None:
        await update.message.reply_text("❌ AI service unavailable.")
        return
    
    # Initialize conversation for this chat
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
        # Try to show typing indicator (but don't crash if it fails)
        try:
            await update.message.chat.send_action(action="typing")
        except Exception as e:
            logger.warning(f"Could not send typing action: {e}")
        
        # Prepare messages for AI
        messages = [
            {
                "role": "system",
                "content": "You are a helpful AI assistant. Be friendly and concise."
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
        
        # Send response
        await update.message.reply_text(ai_response)
        logger.info(f"✅ Sent response to chat {chat_id}")
        
        # Update stats
        BotService.update_stats(user_id)
        LoggerService.track_user_request(user_id, update.effective_user.username)
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        await update.message.reply_text("❌ Sorry, I encountered an error. Please try again.")

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle errors"""
    logger.error(f"Update error: {context.error}")