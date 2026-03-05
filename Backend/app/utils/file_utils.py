"""File validation utilities (mirrors frontend/utils/fileValidation.js)"""
import math
from app.utils.constants import FILE_CONFIG


def validate_video_file(filename: str, file_size: int) -> dict:
    """Validates video file"""
    if not filename:
        return {"valid": False, "error": "No file provided"}
    
    # Check extension
    filename_lower = filename.lower()
    has_valid_ext = any(filename_lower.endswith(ext) for ext in FILE_CONFIG["ALLOWED_EXTENSIONS"])
    
    if not has_valid_ext:
        allowed = ", ".join(FILE_CONFIG["ALLOWED_EXTENSIONS"])
        return {"valid": False, "error": f"Invalid file type. Allowed: {allowed}"}
    
    # Check size
    if file_size > FILE_CONFIG["MAX_SIZE"]:
        max_mb = FILE_CONFIG["MAX_SIZE"] / (1024 * 1024)
        return {"valid": False, "error": f"File size exceeds {max_mb}MB limit"}
    
    return {"valid": True, "error": None}


def format_file_size(size_bytes: int) -> str:
    """Formats file size to human-readable format"""
    if size_bytes == 0:
        return "0 Bytes"
    
    k = 1024
    sizes = ["Bytes", "KB", "MB", "GB"]
    i = int(math.floor(math.log(size_bytes) / math.log(k)))
    i = min(i, len(sizes) - 1)
    
    return f"{round(size_bytes / (k ** i), 2)} {sizes[i]}"
