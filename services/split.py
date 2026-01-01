from PyPDF2 import PdfReader, PdfWriter
from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import generate_unique_filename, get_temp_path, cleanup_files
import re

async def start_split(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start split process"""
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.callback_query.message.reply_text("❌ No file found.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    try:
        # Get page count
        reader = PdfReader(input_path)
        page_count = len(reader.pages)
        
        await update.callback_query.message.reply_text(
            f"📄 This PDF has {page_count} pages.\n\n"
            f"Please specify which pages to extract:\n\n"
            f"Examples:\n"
            f"• Single page: 5\n"
            f"• Range: 1-10\n"
            f"• Multiple: 1-5, 8, 10-15\n"
            f"• All except: 1-{page_count} (for all pages)"
        )
        
        context.user_data['waiting_for'] = 'split_pages'
        context.user_data['total_pages'] = page_count
        
    except Exception as e:
        await update.callback_query.message.reply_text(f"❌ Error reading PDF: {str(e)}")

async def handle_split_pages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle page selection and split PDF"""
    pages_input = update.message.text.strip()
    
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.message.reply_text("❌ No file found.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    total_pages = context.user_data.get('total_pages', 0)
    
    status_msg = await update.message.reply_text("⏳ Splitting PDF...")
    
    try:
        # Parse page numbers
        pages_to_extract = parse_page_ranges(pages_input, total_pages)
        
        if not pages_to_extract:
            await status_msg.edit_text("❌ Invalid page format. Please try again.")
            return
        
        # Read PDF
        reader = PdfReader(input_path)
        
        # Create output PDF
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        writer = PdfWriter()
        
        # Add selected pages
        for page_num in pages_to_extract:
            if 1 <= page_num <= len(reader.pages):
                writer.add_page(reader.pages[page_num - 1])
        
        # Save output
        with open(output_path, 'wb') as output_file:
            writer.write(output_file)
        
        await status_msg.edit_text(
            f"✅ PDF split successfully!\n\n"
            f"Extracted {len(pages_to_extract)} pages."
        )
        
        # Send split file
        with open(output_path, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename=f"split_{file_info['name']}"
            )
        
        # Cleanup
        cleanup_files(input_path, output_path)
        context.user_data['files'] = []
        context.user_data['waiting_for'] = None
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Split failed: {str(e)}")
        cleanup_files(input_path)

def parse_page_ranges(page_string, max_pages):
    """Parse page ranges like '1-5, 8, 10-15' into list of page numbers"""
    pages = set()
    
    try:
        # Split by comma
        parts = page_string.split(',')
        
        for part in parts:
            part = part.strip()
            
            # Check if it's a range
            if '-' in part:
                start, end = part.split('-')
                start = int(start.strip())
                end = int(end.strip())
                
                if start > end:
                    start, end = end, start
                
                pages.update(range(start, end + 1))
            else:
                # Single page
                pages.add(int(part))
        
        # Filter valid pages
        valid_pages = sorted([p for p in pages if 1 <= p <= max_pages])
        return valid_pages
        
    except:
        return []