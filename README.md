# PDF Utility Telegram Bot 🤖

A powerful Telegram bot for PDF operations including compression, encryption, merging, splitting, and format conversion.

## Features

- 🗜 **Compress PDF** - Reduce file size with multiple quality levels
- 🔒 **Encrypt PDF** - Add AES-256 password protection
- 🔓 **Decrypt PDF** - Remove password protection
- ✂️ **Split PDF** - Extract specific pages
- 🔗 **Merge PDFs** - Combine multiple PDFs
- 📄 **PDF to Word** - Convert to editable DOCX
- 📝 **Word to PDF** - Convert DOCX to PDF
- 🖼 **PDF to Images** - Extract pages as images
- 📋 **Extract Text** - Get text content from PDF
- 🖼 **Images to PDF** - Create PDF from images

## Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/pdf-utility-bot.git
cd pdf-utility-bot
```

2. Create virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y ghostscript poppler-utils libreoffice
```

5. Create `.env` file:
```bash
cp .env.example .env
# Edit .env and add your bot token and user ID
```

6. Run the bot:
```bash
python main.py
```

## Deployment

This bot is configured for deployment on [Render](https://render.com). Simply:

1. Push to GitHub
2. Connect your repo on Render
3. Add environment variables
4. Deploy!

## Environment Variables

- `TELEGRAM_BOT_TOKEN` - Get from @BotFather
- `ADMIN_USER_ID` - Get from @userinfobot
- `MAX_FILE_SIZE` - Maximum file size in MB (default: 50)