"""Video handling service with input sanitization"""
import re
from pathlib import Path
from fastapi import UploadFile
import shutil

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
    upload_dir.mkdir(parents=True, exist_ok=True)

    # Get and sanitize file extension
    safe_name = sanitize_filename(video.filename)
    ext = Path(safe_name).suffix
    filepath = upload_dir / f"{video_id}{ext}"

    # Save file
    with filepath.open("wb") as buffer:
        shutil.copyfileobj(video.file, buffer)

    return filepath


def get_video_path(video_id: str) -> Path:
    """Get path to uploaded video"""
    upload_dir = Path(settings.UPLOAD_DIR)

    # Find file with matching video_id
    for ext in [".mp4", ".avi", ".mov", ".mkv"]:
        filepath = upload_dir / f"{video_id}{ext}"
        if filepath.exists():
            return filepath

    raise FileNotFoundError(f"Video {video_id} not found")
