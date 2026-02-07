"""Video upload and analysis routes"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from datetime import datetime
from pathlib import Path
import uuid
import logging

from app.api.v1.schemas.video import VideoUploadResponse, VideoAnalyzeRequest, VideoAnalyzeResponse
from app.api.v1.schemas.response import ErrorResponse, ExplanationResponse
from app.core.config import settings
from app.utils.file_utils import validate_video_file
from app.services.video_service import save_uploaded_video
from app.services.inference_service import analyze_video_file
from app.db.database import get_db
from app.db.models import AnalysisResult
from sqlalchemy.orm import Session
from fastapi import Depends

logger = logging.getLogger(__name__)
router = APIRouter()

# Store results in memory for explanation endpoint
results_cache = {}


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(video: UploadFile = File(...)):
    """Upload video file"""
    try:
        logger.info(f"Upload request received: {video.filename}")
        
        # Validate file
        validation = validate_video_file(video.filename, video.size)
        if not validation["valid"]:
            logger.warning(f"Validation failed: {validation['error']}")
            raise HTTPException(status_code=400, detail=validation["error"])
        
        # Generate unique ID
        video_id = str(uuid.uuid4())
        logger.info(f"Generated video ID: {video_id}")
        
        # Save file
        filepath = await save_uploaded_video(video, video_id)
        logger.info(f"Video saved successfully: {filepath}")
        
        return VideoUploadResponse(
            video_id=video_id,
            message="Video uploaded successfully",
            filename=video.filename,
            size=video.size
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.post("/analyze", response_model=VideoAnalyzeResponse)
async def analyze_video(request: VideoAnalyzeRequest):
    """Analyze uploaded video"""
    try:
        logger.info(f"Analysis request received for video: {request.video_id}")
        
        result = await analyze_video_file(request.video_id)
        
        # Cache result for explanation endpoint
        results_cache[result["id"]] = result
        logger.info(f"Analysis complete. Result cached: {result['id']}")
        
        return VideoAnalyzeResponse(
            id=result["id"],
            status=result["status"],
            confidence=result["confidence"],
            timestamp=result["timestamp"],
            details=result["details"]
        )
    except FileNotFoundError as e:
        logger.error(f"Video not found: {request.video_id}")
        raise HTTPException(status_code=404, detail="Video not found")
    except RuntimeError as e:
        logger.error(f"Analysis runtime error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/explanation/{result_id}", response_model=ExplanationResponse)
async def get_explanation(result_id: str):
    """Get AI explanation for result"""
    try:
        logger.info(f"Explanation request for result: {result_id}")
        
        from app.services.groq_service import groq_service
        
        # Get result from cache
        result = results_cache.get(result_id)
        if not result:
            logger.warning(f"Result not found in cache: {result_id}")
            raise HTTPException(status_code=404, detail="Result not found. Please analyze the video first.")
        
        explanation = groq_service.generate_explanation(result)
        logger.info(f"Explanation generated for result: {result_id}")
        
        return ExplanationResponse(explanation=explanation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")
