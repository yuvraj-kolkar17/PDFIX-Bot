import pikepdf
from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import generate_unique_filename, get_temp_path, cleanup_files

async def start_decryption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start decryption process"""
    await update.callback_query.message.reply_text(
        "🔓 Please enter the password to decrypt the PDF:"
    )
    context.user_data['waiting_for'] = 'decrypt_password'

async def handle_decryption_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password input and decrypt PDF"""
    password = update.message.text
    
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.message.reply_text("❌ No file found. Please upload a file first.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.message.reply_text("⏳ Decrypting PDF...")
    
    try:
        # Generate output path
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        # Open encrypted PDF with password
        with pikepdf.open(input_path, password=password) as pdf:
            # Save without encryption
            pdf.save(output_path)
        
        await status_msg.edit_text("✅ PDF decrypted successfully!")
        
        # Send decrypted file
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"decrypted_{file_info['name']}"
            )
        
        # Cleanup
        cleanup_files(input_path, output_path)
        context.user_data['files'] = []
        context.user_data['waiting_for'] = None
        
    except pikepdf.PasswordError:
        await status_msg.edit_text(
            "❌ Incorrect password! Please try again.\n\n"
            "Send the correct password or upload a new file."
        )
    except Exception as e:
        await status_msg.edit_text(f"❌ Decryption failed: {str(e)}")
        cleanup_files(input_path)