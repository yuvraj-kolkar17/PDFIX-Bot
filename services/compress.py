import subprocess
import fitz  # PyMuPDF
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

async def compress_pdf_ghostscript(input_path, output_path, quality='medium'):
    """Compress PDF using Ghostscript"""
    quality_settings = config.COMPRESSION_LEVELS
    
    cmd = [
        'gs',
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        f'-dPDFSETTINGS={quality_settings[quality]}',
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={output_path}',
        input_path
    ]
    
    try:
        subprocess.run(cmd, check=True, capture_output=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Ghostscript error: {e}")
        return False
    except FileNotFoundError:
        # Ghostscript not installed, use PyMuPDF
        return await compress_pdf_pymupdf(input_path, output_path, quality)

async def compress_pdf_pymupdf(input_path, output_path, quality='medium'):
    """Compress PDF using PyMuPDF as fallback"""
    try:
        doc = fitz.open(input_path)
        
        # Quality settings for better performance
        if quality == 'low':
            # Minimal compression, fast
            doc.save(output_path, garbage=3, deflate=True)
        elif quality == 'medium':
            # Balanced compression
            doc.save(output_path, garbage=4, deflate=True, clean=True)
        else:  # high
            # Maximum compression, slower
            doc.save(output_path, garbage=4, deflate=True, clean=True, linear=True)
        
        doc.close()
        return True
    except Exception as e:
        print(f"PyMuPDF compression error: {e}")
        return False

async def handle_compression_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle compression level selection"""
    query = update.callback_query
    await query.answer()
    
    # Extract compression level
    level = query.data.replace('compress_', '')
    
    # Get file from user data
    if 'files' not in context.user_data or not context.user_data['files']:
        await query.message.reply_text("❌ No file found. Please upload a file first.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await query.message.reply_text("⏳ Compressing PDF...")
    
    try:
        # Generate output path
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        # Compress
        success = await compress_pdf_ghostscript(input_path, output_path, level)
        
        if success:
            # Get file sizes
            original_size = get_file_size_mb(input_path)
            compressed_size = get_file_size_mb(output_path)
            reduction = ((original_size - compressed_size) / original_size) * 100
            
            await status_msg.edit_text(
                f"✅ Compression complete!\n\n"
                f"Original: {original_size:.2f} MB\n"
                f"Compressed: {compressed_size:.2f} MB\n"
                f"Reduced by: {reduction:.1f}%\n\n"
                f"⏳ Uploading file..."
            )
            
            # Send compressed file
            with open(output_path, 'rb') as f:
                await query.message.reply_document(
                    document=f,
                    filename=f"compressed_{file_info['name']}",
                    caption=f"✅ Compressed by {reduction:.1f}%"
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