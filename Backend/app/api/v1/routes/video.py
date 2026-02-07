"""Video upload and analysis routes"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from pathlib import Path
import uuid

from app.api.v1.schemas.video import VideoUploadResponse, VideoAnalyzeRequest, VideoAnalyzeResponse
from app.api.v1.schemas.response import ErrorResponse, ExplanationResponse
from app.core.config import settings
from app.utils.file_utils import validate_video_file
from app.services.video_service import save_uploaded_video
from app.services.inference_service import analyze_video_file

router = APIRouter()


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(video: UploadFile = File(...)):
    """Upload video file"""
    # Validate file
    validation = validate_video_file(video.filename, video.size)
    if not validation["valid"]:
        raise HTTPException(status_code=400, detail=validation["error"])
    
    # Generate unique ID
    video_id = str(uuid.uuid4())
    
    # Save file
    try:
        filepath = await save_uploaded_video(video, video_id)
        
        return VideoUploadResponse(
            video_id=video_id,
            message="Video uploaded successfully",
            filename=video.filename,
            size=video.size
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/analyze", response_model=VideoAnalyzeResponse)
async def analyze_video(request: VideoAnalyzeRequest):
    """Analyze uploaded video"""
    try:
        result = await analyze_video_file(request.video_id)
        
        return VideoAnalyzeResponse(
            id=result["id"],
            status=result["status"],
            confidence=result["confidence"],
            timestamp=result["timestamp"],
            details=result["details"]
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Video not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/explanation/{result_id}", response_model=ExplanationResponse)
async def get_explanation(result_id: str):
    """Get AI explanation for result"""
    from app.services.groq_service import groq_service
    
    # Mock result for now - in production, fetch from database
    result = {
        "id": result_id,
        "status": "accident",
        "confidence": 0.87,
        "details": {
            "spatialFeatures": "Vehicle collision detected with high impact force",
            "temporalFeatures": "Sudden deceleration and erratic movement patterns",
            "frameCount": 450,
            "duration": "15 seconds"
        }
    }
    
    explanation = groq_service.generate_explanation(result)
    return ExplanationResponse(explanation=explanation)
