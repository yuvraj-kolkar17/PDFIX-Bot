import os
import uuid
from pathlib import Path
import config

def generate_unique_filename(extension='.pdf'):
    """Generate unique filename with UUID"""
    return f"{uuid.uuid4()}{extension}"

def get_file_size_mb(filepath):
    """Get file size in MB"""
    return os.path.getsize(filepath) / (1024 * 1024)

def validate_file_size(filepath, max_size_mb=None):
    """Check if file size is within limits"""
    if max_size_mb is None:
        max_size_mb = config.MAX_FILE_SIZE_MB
    
    size_mb = get_file_size_mb(filepath)
    return size_mb <= max_size_mb, size_mb

def cleanup_file(filepath):
    """Delete a file safely"""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            return True
    except Exception as e:
        print(f"Error deleting file {filepath}: {e}")
    return False

def cleanup_files(*filepaths):
    """Delete multiple files"""
    for filepath in filepaths:
        cleanup_file(filepath)

def get_temp_path(filename):
    """Get full path for temp file"""
    return os.path.join(config.TEMP_DIR, filename)

def validate_pdf(filepath):
    """Check if file is a valid PDF"""
    try:
        with open(filepath, 'rb') as f:
            header = f.read(5)
            return header == b'%PDF-'
    except:
        return False