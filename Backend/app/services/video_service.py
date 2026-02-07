"""Video handling service"""
from pathlib import Path
from fastapi import UploadFile
import shutil

from app.core.config import settings


async def save_uploaded_video(video: UploadFile, video_id: str) -> Path:
    """Save uploaded video to storage"""
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    # Get file extension
    ext = Path(video.filename).suffix
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
