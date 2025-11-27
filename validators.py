"""
Validation utilities for file uploads and data processing.
"""

import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {'pdf'}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5 MB in bytes

def allowed_file(filename):
    """
    Check if the uploaded file has an allowed extension.
    
    Args:
        filename (str): Name of the uploaded file
        
    Returns:
        bool: True if file extension is allowed
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_file_size(file_size):
    """
    Check if the file size is within allowed limits.
    
    Args:
        file_size (int): Size of the file in bytes
        
    Returns:
        bool: True if file size is acceptable
    """
    return file_size <= MAX_FILE_SIZE

def sanitize_filename(filename):
    """
    Sanitize the filename to prevent security issues.
    
    Args:
        filename (str): Original filename
        
    Returns:
        str: Sanitized filename
    """
    return secure_filename(filename)

def validate_upload(file):
    """
    Comprehensive validation for uploaded files.
    
    Args:
        file: FileStorage object from Flask request
        
    Returns:
        tuple: (is_valid, error_message)
    """
    if not file:
        return False, "No file provided"
    
    if file.filename == '':
        return False, "No file selected"
    
    if not allowed_file(file.filename):
        return False, "Only PDF files are allowed"
    
    # Check file size by seeking to end
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # Reset to beginning
    
    if not validate_file_size(file_size):
        return False, f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024 * 1024):.1f} MB"
    
    return True, None
