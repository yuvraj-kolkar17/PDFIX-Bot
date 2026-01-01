from PyPDF2 import PdfReader, PdfWriter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.file_utils import generate_unique_filename, get_temp_path, cleanup_files

async def start_merge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start merge process"""
    if 'files' not in context.user_data:
        context.user_data['files'] = []
    
    pdf_files = [f for f in context.user_data['files'] if f['type'] == 'pdf']
    
    if len(pdf_files) < 2:
        keyboard = [[InlineKeyboardButton("Upload More PDFs", callback_data="upload_more")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.message.reply_text(
            f"📄 You have uploaded {len(pdf_files)} PDF(s).\n\n"
            "Please upload at least 2 PDFs to merge.\n"
            "Send more PDF files, then select 'Merge PDFs' again.",
            reply_markup=reply_markup
        )
        return
    
    # Show merge confirmation
    file_list = "\n".join([f"{i+1}. {f['name']}" for i, f in enumerate(pdf_files)])
    
    keyboard = [
        [InlineKeyboardButton("✅ Merge Now", callback_data="confirm_merge")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel_merge")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        f"📑 Ready to merge {len(pdf_files)} PDFs:\n\n{file_list}\n\n"
        "Files will be merged in this order.",
        reply_markup=reply_markup
    )

async def confirm_merge(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Merge uploaded PDFs"""
    query = update.callback_query
    await query.answer()
    
    pdf_files = [f for f in context.user_data.get('files', []) if f['type'] == 'pdf']
    
    if len(pdf_files) < 2:
        await query.message.reply_text("❌ Not enough PDFs to merge.")
        return
    
    status_msg = await query.message.reply_text("⏳ Merging PDFs...")
    
    try:
        # Create merger
        writer = PdfWriter()
        
        # Add all PDFs
        for file_info in pdf_files:
            reader = PdfReader(file_info['path'])
            for page in reader.pages:
                writer.add_page(page)
        
        # Generate output
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        await status_msg.edit_text(
            f"✅ Successfully merged {len(pdf_files)} PDFs!"
        )
        
        # Send merged file
        with open(output_path, 'rb') as f:
            await query.message.reply_document(
                document=f,
                filename="merged_document.pdf"
            )
        
        # Cleanup all files
        for file_info in pdf_files:
            cleanup_files(file_info['path'])
        cleanup_files(output_path)
        
        context.user_data['files'] = []
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Merge failed: {str(e)}")
        for file_info in pdf_files:
            cleanup_files(file_info['path'])