import os
from dotenv import load_dotenv

load_dotenv()

# Bot Configuration
BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
ADMIN_USER_ID = int(os.getenv('ADMIN_USER_ID', 0))

# File Configuration
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE', 50))
TEMP_DIR = 'temp'
ALLOWED_FORMATS = ['.pdf', '.docx', '.jpg', '.jpeg', '.png']

# Performance settings
CHUNK_SIZE = 65536  # 64KB chunks for file operations
CONNECT_TIMEOUT = 30.0
READ_TIMEOUT = 30.0
WRITE_TIMEOUT = 30.0

# Compression Levels
COMPRESSION_LEVELS = {
    'low': '/prepress',
    'medium': '/ebook',
    'high': '/screen'
}

# Create temp directory if not exists
os.makedirs(TEMP_DIR, exist_ok=True)