from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import get_temp_path, cleanup_files
import os

async def start_rename(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start rename process"""
    await update.callback_query.message.reply_text(
        "📝 Please enter the new name for your PDF file:\n\n"
        "Example: my_document\n"
        "(Don't include .pdf extension, it will be added automatically)"
    )
    context.user_data['waiting_for'] = 'rename_input'

async def handle_rename_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle new filename input"""
    new_name = update.message.text.strip()
    
    # Remove .pdf if user included it
    if new_name.lower().endswith('.pdf'):
        new_name = new_name[:-4]
    
    # Validate filename
    invalid_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    for char in invalid_chars:
        new_name = new_name.replace(char, '_')
    
    if not new_name:
        await update.message.reply_text("❌ Invalid filename. Please try again.")
        return
    
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.message.reply_text("❌ No file found. Please upload a file first.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.message.reply_text("⏳ Renaming file...")
    
    try:
        # Add .pdf extension
        new_filename = f"{new_name}.pdf"
        
        await status_msg.edit_text(f"✅ File renamed to: {new_filename}")
        
     
        with open(input_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=new_filename,
                caption=f"✅ Renamed to: {new_filename}"
            )
        
        # Cleanup
        cleanup_files(input_path)
        context.user_data['files'] = []
        context.user_data['waiting_for'] = None
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
        cleanup_files(input_path)
