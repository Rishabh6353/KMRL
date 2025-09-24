import os
import magic
import hashlib
from datetime import datetime
import logging
import json
import tempfile
import shutil

def get_file_type(file_path):
    """
    Detect file type using python-magic
    """
    try:
        mime = magic.Magic(mime=True)
        return mime.from_file(file_path)
    except Exception:
        # Fallback to extension-based detection
        ext = os.path.splitext(file_path)[1].lower()
        mime_types = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            '.txt': 'text/plain',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.tiff': 'image/tiff',
            '.bmp': 'image/bmp'
        }
        return mime_types.get(ext, 'application/octet-stream')

def calculate_file_hash(file_path, algorithm='md5'):
    """
    Calculate hash of a file
    """
    hash_algorithms = {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha256': hashlib.sha256()
    }
    
    hasher = hash_algorithms.get(algorithm, hashlib.md5())
    
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()

def safe_filename(filename):
    """
    Create a safe filename by removing/replacing dangerous characters
    """
    import re
    # Remove path separators and other dangerous characters
    safe_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    # Limit length
    if len(safe_name) > 255:
        name, ext = os.path.splitext(safe_name)
        safe_name = name[:250] + ext
    return safe_name

def ensure_directory(directory_path):
    """
    Ensure a directory exists, create if it doesn't
    """
    try:
        os.makedirs(directory_path, exist_ok=True)
        return True
    except Exception as e:
        logging.error(f"Error creating directory {directory_path}: {e}")
        return False

def format_file_size(size_bytes):
    """
    Format file size in human readable format
    """
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def create_temp_file(suffix=None, prefix='idp_'):
    """
    Create a temporary file
    """
    return tempfile.NamedTemporaryFile(
        delete=False,
        suffix=suffix,
        prefix=prefix
    )

def cleanup_temp_files(temp_dir=None):
    """
    Clean up temporary files
    """
    if temp_dir is None:
        temp_dir = tempfile.gettempdir()
    
    try:
        for filename in os.listdir(temp_dir):
            if filename.startswith('idp_'):
                file_path = os.path.join(temp_dir, filename)
                if os.path.isfile(file_path):
                    # Only delete files older than 1 hour
                    if os.path.getctime(file_path) < (datetime.now().timestamp() - 3600):
                        os.unlink(file_path)
    except Exception as e:
        logging.error(f"Error cleaning temp files: {e}")

def log_processing_time(func):
    """
    Decorator to log processing time of functions
    """
    def wrapper(*args, **kwargs):
        start_time = datetime.now()
        try:
            result = func(*args, **kwargs)
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logging.info(f"{func.__name__} completed in {processing_time:.2f} seconds")
            return result
        except Exception as e:
            end_time = datetime.now()
            processing_time = (end_time - start_time).total_seconds()
            logging.error(f"{func.__name__} failed after {processing_time:.2f} seconds: {e}")
            raise
    return wrapper

def validate_file_upload(file, allowed_extensions, max_size_mb=16):
    """
    Validate uploaded file
    """
    errors = []
    
    if not file:
        errors.append("No file provided")
        return errors
    
    if not file.filename:
        errors.append("No filename provided")
        return errors
    
    # Check file extension
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in allowed_extensions:
        errors.append(f"File type {file_ext} not allowed. Allowed types: {', '.join(allowed_extensions)}")
    
    # Check file size
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset file pointer
    
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_size > max_size_bytes:
        errors.append(f"File size ({format_file_size(file_size)}) exceeds maximum allowed size ({max_size_mb}MB)")
    
    if file_size == 0:
        errors.append("File is empty")
    
    return errors

def extract_text_preview(text, max_length=500):
    """
    Create a preview of extracted text
    """
    if not text:
        return ""
    
    text = text.strip()
    if len(text) <= max_length:
        return text
    
    # Try to cut at a sentence boundary
    preview = text[:max_length]
    last_sentence_end = max(
        preview.rfind('.'),
        preview.rfind('!'),
        preview.rfind('?')
    )
    
    if last_sentence_end > max_length * 0.7:  # If we found a good break point
        return preview[:last_sentence_end + 1] + "..."
    else:
        # Just cut at word boundary
        last_space = preview.rfind(' ')
        if last_space > max_length * 0.7:
            return preview[:last_space] + "..."
        else:
            return preview + "..."

def sanitize_json_for_api(data):
    """
    Sanitize data for JSON API response
    """
    if isinstance(data, dict):
        return {k: sanitize_json_for_api(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [sanitize_json_for_api(item) for item in data]
    elif isinstance(data, datetime):
        return data.isoformat()
    elif isinstance(data, bytes):
        return data.decode('utf-8', errors='ignore')
    else:
        return data

def create_processing_metadata(document_id, module_name, status, message=None, processing_time=None):
    """
    Create processing metadata entry
    """
    return {
        'document_id': document_id,
        'module': module_name,
        'status': status,
        'message': message,
        'processing_time': processing_time,
        'timestamp': datetime.now().isoformat()
    }

def setup_logging(log_level='INFO', log_file=None):
    """
    Setup logging configuration
    """
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    logging.basicConfig(
        level=getattr(logging, log_level.upper()),
        format=log_format,
        handlers=[
            logging.StreamHandler(),
        ] + ([logging.FileHandler(log_file)] if log_file else [])
    )

class ProcessingStatus:
    """Constants for processing status"""
    PENDING = 'pending'
    PROCESSING = 'processing'
    COMPLETED = 'completed'
    FAILED = 'failed'
    REVIEW_REQUIRED = 'review_required'

class DocumentTypes:
    """Constants for document types"""
    PDF = 'application/pdf'
    DOC = 'application/msword'
    DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
    TXT = 'text/plain'
    PNG = 'image/png'
    JPG = 'image/jpeg'
    JPEG = 'image/jpeg'
    TIFF = 'image/tiff'

class Priority:
    """Constants for priority levels"""
    URGENT = 'urgent'
    HIGH = 'high'
    MEDIUM = 'medium'
    LOW = 'low'