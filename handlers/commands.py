from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    welcome_message = """
🤖 **Welcome to PDF Utility Bot!**

I can help you with various PDF operations:

📄 **Available Features:**
• Compress PDF (reduce file size)
• Encrypt PDF (password protection)
• Decrypt PDF (remove password)
• Split PDF (extract pages)
• Merge PDFs (combine multiple files)
• PDF to Word conversion
• Word to PDF conversion
• PDF to Images
• Extract text from PDF
• Images to PDF

**How to use:**
Simply send me a PDF file and select the operation you want to perform!

Use /help for more details.
    """
    
    await update.message.reply_text(
        welcome_message,
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_message = """
📖 **How to Use PDF Utility Bot**

**1. Compress PDF**
   • Send a PDF file
   • Choose "Compress"
   • Select compression level (Low/Medium/High)

**2. Encrypt PDF**
   • Send a PDF file
   • Choose "Encrypt"
   • Enter password when prompted

**3. Decrypt PDF**
   • Send an encrypted PDF
   • Choose "Decrypt"
   • Enter the correct password

**4. Split PDF**
   • Send a PDF file
   • Choose "Split"
   • Specify page ranges (e.g., 1-5, 7, 9-12)

**5. Merge PDFs**
   • Send multiple PDF files
   • Choose "Merge" after uploading all
   • Files will be combined in order

**6. Convert to Word**
   • Send a PDF file
   • Choose "PDF to Word"
   • Receive editable DOCX file

**7. Convert to PDF**
   • Send a Word document
   • Choose "Word to PDF"

**8. PDF to Images**
   • Send a PDF file
   • Choose "PDF to Images"
   • Receive each page as image

**9. Extract Text**
   • Send a PDF file
   • Choose "Extract Text"
   • Get text content

**10. Images to PDF**
   • Send multiple images
   • Choose "Images to PDF"
   • Images combined into single PDF

⚠️ **Limits:**
• Maximum file size: 50 MB
• Files are automatically deleted after processing

Need help? Contact support or report issues!
    """
    
    await update.message.reply_text(
        help_message,
        parse_mode='Markdown'
    )