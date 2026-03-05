"""Video handling service with input sanitization"""
import re
from pathlib import Path
from fastapi import UploadFile
import shutil
import os

from app.core.config import settings


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename to prevent path traversal attacks.
    Removes directory separators and special characters.
    """
    # Remove any directory components
    filename = Path(filename).name
    # Remove any non-alphanumeric chars except dots, hyphens, underscores
    filename = re.sub(r'[^\w\-.]', '_', filename)
    # Prevent hidden files
    filename = filename.lstrip('.')
    return filename or "unnamed_video"


async def save_uploaded_video(video: UploadFile, video_id: str) -> Path:
    """Save uploaded video to storage with sanitized filename"""
    upload_dir = Path(settings.UPLOAD_DIR)
    
    if not upload_dir.is_absolute():
        # Resolve relative to where the app is actually running
        upload_dir = Path(os.getcwd()) / upload_dir
        # Normalize to remove any duplicate path components
        upload_dir = upload_dir.resolve()
    
    upload_dir.mkdir(parents=True, exist_ok=True)

    safe_name = sanitize_filename(video.filename)
    ext = Path(safe_name).suffix
    filepath = upload_dir / f"{video_id}{ext}"

    with filepath.open("wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    return filepath


def get_video_path(video_id: str) -> Path:
    """Get path to uploaded video"""
    import logging
    logger = logging.getLogger(__name__)
    
    upload_dir = Path(settings.UPLOAD_DIR)
    
    if not upload_dir.is_absolute():
        upload_dir = Path(os.getcwd()) / upload_dir
        upload_dir = upload_dir.resolve()
    
    logger.info(f"Searching for video {video_id} in {upload_dir}")
    
    if not upload_dir.exists():
        raise FileNotFoundError(f"Upload directory not found: {upload_dir}")

    matches = list(upload_dir.glob(f"{video_id}.*"))
    logger.info(f"Found {len(matches)} matches: {matches}")
    
    for filepath in matches:
        if filepath.is_file():
            # Convert to string with proper Windows backslashes
            resolved_path = str(filepath.resolve()).replace('/', '\\')
            logger.info(f"Returning file: {resolved_path}")
            return Path(resolved_path)

    raise FileNotFoundError(f"Video {video_id} not found in {upload_dir}")
