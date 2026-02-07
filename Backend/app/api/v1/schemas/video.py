"""Video schemas"""
from pydantic import BaseModel
from typing import Optional


class VideoUploadResponse(BaseModel):
    video_id: str
    message: str
    filename: str
    size: int


class VideoAnalyzeRequest(BaseModel):
    video_id: str


class VideoAnalyzeResponse(BaseModel):
    id: str
    status: str
    confidence: float
    timestamp: str
    details: dict
