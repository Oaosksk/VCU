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
    confidence: int                        # 0-100 (enforced: 91-100 or 0-49)
    timestamp: str
    details: dict
    inference_time: float = None

    # New enforced detection fields
    isAccident: bool = False
    accidentType: Optional[str] = None
    severity: str = "none"                 # critical / moderate / minor / none
    frameEvidence: str = ""
    reasoning: str = ""
