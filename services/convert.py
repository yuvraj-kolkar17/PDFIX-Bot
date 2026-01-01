from pdf2docx import Converter
from pdf2image import convert_from_path
import pdfplumber
import fitz  # PyMuPDF
from PIL import Image
from telegram import Update
from telegram.ext import ContextTypes
from utils.file_utils import generate_unique_filename, get_temp_path, cleanup_files
import subprocess
import os

async def convert_pdf_to_word(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert PDF to Word document"""
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.callback_query.message.reply_text("❌ No file found.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.callback_query.message.reply_text("⏳ Converting PDF to Word...")
    
    try:
        output_filename = generate_unique_filename('.docx')
        output_path = get_temp_path(output_filename)
        
        # Convert using pdf2docx
        cv = Converter(input_path)
        cv.convert(output_path)
        cv.close()
        
        await status_msg.edit_text("✅ Conversion complete!")
        
        # Send Word file
        with open(output_path, 'rb') as f:
            await update.callback_query.message.reply_document(
                document=f,
                filename=f"{os.path.splitext(file_info['name'])[0]}.docx"
            )
        
        cleanup_files(input_path, output_path)
        context.user_data['files'] = []
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Conversion failed: {str(e)}")
        cleanup_files(input_path)

async def convert_word_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert Word to PDF"""
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.callback_query.message.reply_text("❌ No file found.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.callback_query.message.reply_text("⏳ Converting Word to PDF...")
    
    try:
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        # Use LibreOffice for conversion
        cmd = [
            'libreoffice',
            '--headless',
            '--convert-to',
            'pdf',
            '--outdir',
            os.path.dirname(output_path),
            input_path
        ]
        
        subprocess.run(cmd, check=True, capture_output=True)
        
        # LibreOffice creates file with original name
        expected_output = os.path.join(
            os.path.dirname(output_path),
            os.path.splitext(os.path.basename(input_path))[0] + '.pdf'
        )
        
        if os.path.exists(expected_output):
            os.rename(expected_output, output_path)
        
        await status_msg.edit_text("✅ Conversion complete!")
        
        # Send PDF
        with open(output_path, 'rb') as f:
            await update.callback_query.message.reply_document(
                document=f,
                filename=f"{os.path.splitext(file_info['name'])[0]}.pdf"
            )
        
        cleanup_files(input_path, output_path)
        context.user_data['files'] = []
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Conversion failed: {str(e)}\n\nMake sure LibreOffice is installed.")
        cleanup_files(input_path)

async def convert_pdf_to_images(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert PDF pages to images"""
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.callback_query.message.reply_text("❌ No file found.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.callback_query.message.reply_text("⏳ Converting PDF to images...")
    
    try:
        # Convert PDF to images
        images = convert_from_path(input_path, dpi=200)
        
        await status_msg.edit_text(f"✅ Converted {len(images)} pages!")
        
        # Send each page as image
        for i, image in enumerate(images, 1):
            output_filename = f"page_{i}.jpg"
            output_path = get_temp_path(output_filename)
            
            image.save(output_path, 'JPEG', quality=95)
            
            with open(output_path, 'rb') as f:
                await update.callback_query.message.reply_photo(
                    photo=f,
                    caption=f"Page {i}/{len(images)}"
                )
            
            cleanup_files(output_path)
        
        cleanup_files(input_path)
        context.user_data['files'] = []
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Conversion failed: {str(e)}")
        cleanup_files(input_path)

async def convert_images_to_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Convert images to PDF"""
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.callback_query.message.reply_text("❌ No images found.")
        return
    
    image_files = [f for f in context.user_data['files'] if f['type'] in ['jpg', 'jpeg', 'png']]
    
    if not image_files:
        await update.callback_query.message.reply_text("❌ No images found.")
        return
    
    status_msg = await update.callback_query.message.reply_text("⏳ Creating PDF from images...")
    
    try:
        # Open all images
        images = []
        for file_info in image_files:
            img = Image.open(file_info['path'])
            if img.mode != 'RGB':
                img = img.convert('RGB')
            images.append(img)
        
        # Generate output
        output_filename = generate_unique_filename('.pdf')
        output_path = get_temp_path(output_filename)
        
        # Save as PDF
        if images:
            images[0].save(output_path, save_all=True, append_images=images[1:])
        
        await status_msg.edit_text(f"✅ Created PDF from {len(images)} images!")
        
        # Send PDF
        with open(output_path, 'rb') as f:
            await update.callback_query.message.reply_document(
                document=f,
                filename="images_to_pdf.pdf"
            )
        
        # Cleanup
        for file_info in image_files:
            cleanup_files(file_info['path'])
        cleanup_files(output_path)
        context.user_data['files'] = []
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Conversion failed: {str(e)}")

async def extract_text_from_pdf(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Extract text from PDF"""
    if 'files' not in context.user_data or not context.user_data['files']:
        await update.callback_query.message.reply_text("❌ No file found.")
        return
    
    file_info = context.user_data['files'][-1]
    input_path = file_info['path']
    
    status_msg = await update.callback_query.message.reply_text("⏳ Extracting text...")
    
    try:
        text_content = []
        
        with pdfplumber.open(input_path) as pdf:
            for i, page in enumerate(pdf.pages, 1):
                text = page.extract_text()
                if text:
                    text_content.append(f"--- Page {i} ---\n{text}\n")
        
        full_text = "\n".join(text_content)
        
        if not full_text.strip():
            await status_msg.edit_text("❌ No text found in PDF. The PDF might contain only images.")
            cleanup_files(input_path)
            return
        
        # Save as text file
        output_filename = generate_unique_filename('.txt')
        output_path = get_temp_path(output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        await status_msg.edit_text("✅ Text extracted successfully!")
        
        # Send text file
        with open(output_path, 'rb') as f:
            await update.callback_query.message.reply_document(
                document=f,
                filename=f"{os.path.splitext(file_info['name'])[0]}.txt"
            )
        
        cleanup_files(input_path, output_path)
        context.user_data['files'] = []
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Extraction failed: {str(e)}")
        cleanup_files(input_path)