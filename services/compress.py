from PyPDF2 import PdfReader, PdfWriter
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.file_utils import generate_unique_filename, get_temp_path, cleanup_files, get_file_size_mb
import config

async def start_compression(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask user to select compression level"""
    keyboard = [
        [
            InlineKeyboardButton("Low (Best Quality)", callback_data="compress_low"),
            InlineKeyboardButton("Medium", callback_data="compress_medium")
        ],
        [
            InlineKeyboardButton("High (Smallest Size)", callback_data="compress_high")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.callback_query.message.reply_text(
        "Select compression level:",
        reply_markup=reply_markup
    )

async def compress_pdf_pypdf2(input_path, output_path, quality='medium'):
    """Compress PDF using PyPDF2"""
    try:
        reader = PdfReader(input_path)
        writer = PdfWriter()
        
        for page in reader.pages:
            writer.add_page(page)
        
        # Compression settings based on quality
        if quality == 'high':
            for page in writer.pages:
                page.compress_content_streams()
            writer.add_metadata(reader.metadata)
        elif quality == 'medium':
            for page in writer.pages:
                page.compress_content_streams()
        

        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        return True
    except Exception as e:
        print(f"PyPDF2 compression error: {e}")
        return False

async def handle_compression_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle compression level selection"""
    query = update.callback_query
    await query.answer()
    
    level = query.data.replace('compress_', '')
    
    if 'files' not in context.user_data or not context.user_data['files']:
        await query.message.reply_text("❌ No file found. Please upload a file first.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await query.message.reply_text("⏳ Compressing PDF...")
    
    try:
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        # Compress
        success = await compress_pdf_pypdf2(input_path, output_path, level)
        
        if success:
            # Get file sizes
            original_size = get_file_size_mb(input_path)
            compressed_size = get_file_size_mb(output_path)
            
            if compressed_size < original_size:
                reduction = ((original_size - compressed_size) / original_size) * 100
                reduction_text = f"Reduced by: {reduction:.1f}%"
            else:
                reduction = 0
                reduction_text = "File size similar (PDF was already optimized)"
            
            await status_msg.edit_text(
                f"✅ Compression complete!\n\n"
                f"Original: {original_size:.2f} MB\n"
                f"Compressed: {compressed_size:.2f} MB\n"
                f"{reduction_text}\n\n"
                f"⏳ Uploading file..."
            )
            
            with open(output_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"compressed_{file_info['name']}",
                    caption=f"✅ Compression complete"
                )
            
            # Cleanup
            cleanup_files(input_path, output_path)
            context.user_data['files'] = []
            
        else:
            await status_msg.edit_text("❌ Compression failed. Please try again.")
            cleanup_files(input_path, output_path)
    
    except Exception as e:
        await status_msg.edit_text(f"❌ Error: {str(e)}")
        cleanup_files(input_path, output_path)