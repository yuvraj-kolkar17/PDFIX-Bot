import pikepdf
from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler
from utils.file_utils import generate_unique_filename, get_temp_path, cleanup_files

WAITING_FOR_PASSWORD = 1

async def start_encryption(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start encryption process"""
    await update.callback_query.message.reply_text(
        "🔒 Please enter a password to encrypt the PDF:\n\n"
        "The password should be strong and memorable."
    )
    context.user_data['waiting_for'] = 'encrypt_password'
    return WAITING_FOR_PASSWORD

async def handle_encryption_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle password input and encrypt PDF"""
    password = update.message.text
    
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.message.reply_text("❌ No file found. Please upload a file first.")
        return ConversationHandler.END
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.message.reply_text("⏳ Encrypting PDF...")
    
    try:
        # Generate output path
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        # Open and encrypt PDF
        with pikepdf.open(input_path) as pdf:
            # Set encryption
            pdf.save(
                output_path,
                encryption=pikepdf.Encryption(
                    owner=password,
                    user=password,
                    R=6,  # AES-256 encryption
                    allow=pikepdf.Permissions(
                        accessibility=True,
                        extract=False,
                        modify_annotation=False,
                        modify_assembly=False,
                        modify_form=False,
                        modify_other=False,
                        print_lowres=False,
                        print_highres=False
                    )
                )
            )
        
        await status_msg.edit_text(
            "✅ PDF encrypted successfully!\n\n"
            "🔒 Your PDF is now password-protected with AES-256 encryption."
        )
        
        # Send encrypted file
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"encrypted_{file_info['name']}"
            )
        
        # Cleanup
        cleanup_files(input_path, output_path)
        context.user_data['files'] = []
        context.user_data['waiting_for'] = None
        
        return ConversationHandler.END
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Encryption failed: {str(e)}")
        cleanup_files(input_path)
        return ConversationHandler.END

async def cancel_operation(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel current operation"""
    await update.message.reply_text("Operation cancelled.")
    context.user_data['waiting_for'] = None
    return ConversationHandler.END