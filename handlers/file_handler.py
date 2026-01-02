from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from utils.file_utils import generate_unique_filename, get_temp_path, validate_file_size, validate_pdf
import config

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle uploaded documents and photos"""
    #handle document and photos
    if update.message.document:
        document = update.message.document
        file_name = document.file_name
        file_id = document.file_id
        file_size = document.file_size
        file_extension = file_name.split('.')[-1].lower()
    elif update.message.photo:
        # get the large photo size
        photo = update.message.photo[-1]
        file_id = photo.file_id
        file_size = photo.file_size if photo.file_size else 0
        file_name = f"photo_{file_id[:10]}.jpg"
        file_extension = 'jpg'
    else:
        await update.message.reply_text(
            "❌ Please send a document or image file."
        )
        return
    
    # Check file type
    if file_extension not in ['pdf', 'docx', 'jpg', 'jpeg', 'png']:
        await update.message.reply_text(
            "❌ Unsupported file format. Please send PDF, DOCX, or image files."
        )
        return
    
    if file_extension not in ['pdf', 'docx', 'jpg', 'jpeg', 'png']:
        await update.message.reply_text(
            "❌ Unsupported file format. Please send PDF, DOCX, or image files."
        )
        return
    # Check file size (Telegram limit is 20MB for bots)
    file_size_mb = file_size / (1024 * 1024) if file_size else 0
    if file_size_mb > config.MAX_FILE_SIZE_MB:
        await update.message.reply_text(
            f"❌ File too large! Maximum size is {config.MAX_FILE_SIZE_MB} MB.\n"
            f"Your file: {file_size_mb:.2f} MB"
        )
        return
    
    # Download file
    status_msg = await update.message.reply_text(
        f"⏳ Downloading {file_name}...\n"
        f"Size: {file_size_mb:.2f} MB\n\n"
        "This may take a moment..."
    )
    
    try:
        file = await context.bot.get_file(file_id)
        temp_filename = generate_unique_filename(f'.{file_extension}')
        temp_path = get_temp_path(temp_filename)
        
        await file.download_to_drive(temp_path)
        
        # Store file info in context
        if 'files' not in context.user_data:
            context.user_data['files'] = []
        
        context.user_data['files'].append({
            'path': temp_path,
            'name': file_name,
            'type': file_extension
        })
        
        await status_msg.edit_text("✅ File downloaded successfully!")
        
        # Show operation menu
        await show_operations_menu(update, context, file_extension)
        
    except Exception as e:
        await status_msg.edit_text(f"❌ Error downloading file: {str(e)}")

async def show_operations_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, file_type: str):
    """Display operation options based on file type"""
    
    keyboard = []
    
    if file_type == 'pdf':
        keyboard = [
            [
                InlineKeyboardButton("🗜 Compress", callback_data="compress"),
                InlineKeyboardButton("🔒 Encrypt", callback_data="encrypt")
            ],
            [
                InlineKeyboardButton("🔓 Decrypt", callback_data="decrypt"),
                InlineKeyboardButton("✂️ Split", callback_data="split")
            ],
            [
                InlineKeyboardButton("🔗 Merge PDFs", callback_data="merge"),
                InlineKeyboardButton("📝 Rename", callback_data="rename")
            ],
            [
                InlineKeyboardButton("📄 To Word", callback_data="pdf_to_word"),
                InlineKeyboardButton("🖼 To Images", callback_data="pdf_to_images")
            ],
            [
                InlineKeyboardButton("📋 Extract Text", callback_data="extract_text")
            ]
        ]
    elif file_type == 'docx':
        keyboard = [
            [InlineKeyboardButton("📄 Convert to PDF", callback_data="word_to_pdf")]
        ]
    elif file_type in ['jpg', 'jpeg', 'png']:
        keyboard = [
            [InlineKeyboardButton("📄 Create PDF", callback_data="images_to_pdf")]
        ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "Please select an operation:",
        reply_markup=reply_markup
    )

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button callbacks"""
    query = update.callback_query
    await query.answer()
    
    operation = query.data
    
    # Import services dynamically to avoid circular imports
    if operation == "compress":
        from services.compress import start_compression
        await start_compression(update, context)
    
    elif operation == "encrypt":
        from services.encrypt import start_encryption
        await start_encryption(update, context)
    
    elif operation == "decrypt":
        from services.decrypt import start_decryption
        await start_decryption(update, context)
    
    elif operation == "split":
        from services.split import start_split
        await start_split(update, context)
    
    elif operation == "merge":
        from services.merge import start_merge
        await start_merge(update, context)
    
    elif operation == "pdf_to_word":
        from services.convert import convert_pdf_to_word
        await convert_pdf_to_word(update, context)
    
    elif operation == "word_to_pdf":
        from services.convert import convert_word_to_pdf
        await convert_word_to_pdf(update, context)
    
    elif operation == "pdf_to_images":
        from services.convert import convert_pdf_to_images
        await convert_pdf_to_images(update, context)
    
    elif operation == "images_to_pdf":
        from services.convert import convert_images_to_pdf
        await convert_images_to_pdf(update, context)
    
    elif operation == "extract_text":
        from services.convert import extract_text_from_pdf
        await extract_text_from_pdf(update, context)
    
    elif operation == "rename": 
        from services.rename import start_rename
        await start_rename(update, context)