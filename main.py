import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ConversationHandler
import config

from handlers.commands import start_command, help_command
from handlers.file_handler import handle_document, handle_callback
from services.encrypt import handle_encryption_password, cancel_operation, WAITING_FOR_PASSWORD
from services.decrypt import handle_decryption_password
from services.split import handle_split_pages
from services.compress import handle_compression_level
from services.merge import confirm_merge

#  logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_text_messages(update, context):
    """Route text messages based on context"""
    
    if 'waiting_for' not in context.user_data:
        await update.message.reply_text(
            "Please send me a PDF file to get started!\n\n"
            "Use /help to see all available features."
        )
        return
    
    waiting_for = context.user_data.get('waiting_for')
    
    if waiting_for == 'encrypt_password':
        await handle_encryption_password(update, context)
    elif waiting_for == 'decrypt_password':
        await handle_decryption_password(update, context)
    elif waiting_for == 'split_pages':
        await handle_split_pages(update, context)
    else:
        await update.message.reply_text("Please upload a file first.")

async def handle_all_callbacks(update, context):
    """Handle all callback queries"""
    query = update.callback_query
    
    #handle compressin callback
    if query.data.startswith('compress_'):
        await handle_compression_level(update, context)
    # Handle merge cnf
    elif query.data == 'confirm_merge':
        await confirm_merge(update, context)
    #Handle general callbacks
    else:
        await handle_callback(update, context)

def main():
    """Start the bot"""
    application = (
        Application.builder()
        .token(config.BOT_TOKEN)
        .connect_timeout(30.0)
        .read_timeout(30.0)
        .write_timeout(30.0)
        .pool_timeout(30.0)
        .concurrent_updates(True)
        .build()
    )
    
    #cmd
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    
    
    application.add_handler(MessageHandler(
        filters.Document.ALL | filters.PHOTO,
        handle_document
    ))
    
    # Text message handler
    application.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_text_messages
    ))
    
    
    application.add_handler(CallbackQueryHandler(handle_all_callbacks))
    
  
    logger.info("Bot is starting...")
    application.run_polling(allowed_updates=["message", "callback_query"])

if __name__ == '__main__':
    main()