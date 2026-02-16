"""Video upload and analysis routes"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
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
from app.db import crud
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)
router = APIRouter()

# In-memory cache for fast explanation lookups (DB is the source of truth)
results_cache = {}


@router.post("/upload", response_model=VideoUploadResponse)
async def upload_video(video: UploadFile = File(...), db: Session = Depends(get_db)):
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

        # Save file to disk
        filepath = await save_uploaded_video(video, video_id)
        logger.info(f"Video saved successfully: {filepath}")

        # Save video record to database
        crud.create_video(
            db=db,
            video_id=video_id,
            filename=video.filename,
            filepath=str(filepath),
            size=video.size
        )

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
async def analyze_video(request: VideoAnalyzeRequest, db: Session = Depends(get_db)):
    """Analyze uploaded video"""
    try:
        logger.info(f"Analysis request received for video: {request.video_id}")

        # Validate video exists in DB
        db_video = crud.get_video(db, request.video_id)
        if not db_video:
            raise HTTPException(status_code=404, detail="Video not found in database")

        # Update status to processing
        crud.update_video_status(db, request.video_id, "processing")

        result = await analyze_video_file(request.video_id, db)

        # Save analysis result to database
        crud.create_analysis_result(db, result)
        
        # Save accident frames to database if any
        if result["status"] == "accident" and result.get("details", {}).get("accidentFrameUrls"):
            frame_urls = result["details"]["accidentFrameUrls"]
            frames_data = [
                {
                    'index': int(url.split('_')[-1].split('.')[0]),  # Extract frame index from URL
                    'path': url,
                    'confidence': 1.0
                }
                for url in frame_urls
            ]
            if frames_data:
                crud.create_accident_frames(db, request.video_id, result["id"], frames_data)

        # Save detected events to database
        event_frames = result.get("details", {}).get("eventFrames", [])
        if event_frames:
            crud.create_events(db, request.video_id, result["id"], event_frames)

        # Update video status
        crud.update_video_status(db, request.video_id, "completed")

        # Cache result for fast explanation lookups
        results_cache[result["id"]] = result
        logger.info(f"Analysis complete. Result saved: {result['id']}")

        return VideoAnalyzeResponse(
            id=result["id"],
            status=result["status"],
            confidence=result["confidence"],
            timestamp=result["timestamp"],
            details=result["details"]
        )
    except HTTPException:
        raise
    except FileNotFoundError:
        logger.error(f"Video file not found: {request.video_id}")
        crud.update_video_status(db, request.video_id, "failed")
        raise HTTPException(status_code=404, detail="Video file not found on disk")
    except TimeoutError as e:
        logger.error(f"Analysis timed out: {request.video_id}")
        crud.update_video_status(db, request.video_id, "failed")
        raise HTTPException(status_code=504, detail=f"Analysis timed out: {str(e)}")
    except RuntimeError as e:
        logger.error(f"Analysis runtime error: {str(e)}")
        crud.update_video_status(db, request.video_id, "failed")
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}", exc_info=True)
        crud.update_video_status(db, request.video_id, "failed")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")


@router.get("/explanation/{result_id}", response_model=ExplanationResponse)
async def get_explanation(result_id: str, db: Session = Depends(get_db)):
    """Get AI explanation for result"""
    try:
        logger.info(f"Explanation request for result: {result_id}")

        from app.services.groq_service import groq_service

        # Try cache first, then fall back to database
        result = results_cache.get(result_id)
        if not result:
            db_result = crud.get_result_by_id(db, result_id)
            if not db_result:
                logger.warning(f"Result not found: {result_id}")
                raise HTTPException(
                    status_code=404,
                    detail="Result not found. Please analyze the video first."
                )
            # Reconstruct result dict from DB record
            result = {
                "id": db_result.id,
                "status": db_result.status,
                "confidence": db_result.confidence,
                "details": db_result.details or {},
                "inference_time": db_result.inference_time,
            }

        explanation = groq_service.generate_explanation(result)
        logger.info(f"Explanation generated for result: {result_id}")

        return ExplanationResponse(explanation=explanation)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Explanation generation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to generate explanation: {str(e)}")



@router.get("/frames/{video_id}")
async def get_video_frames(video_id: str, db: Session = Depends(get_db)):
    """Get accident frames for a specific video"""
    try:
        # Get frames from database
        frames = crud.get_accident_frames_by_video(db, video_id)
        
        if not frames:
            return {"video_id": video_id, "frames": [], "count": 0}
        
        frame_data = [
            {
                "index": frame.frame_index,
                "url": frame.frame_path,
                "confidence": frame.confidence
            }
            for frame in frames
        ]
        
        return {
            "video_id": video_id,
            "frames": frame_data,
            "count": len(frame_data)
        }
    except Exception as e:
        logger.error(f"Failed to get frames for video {video_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get frames: {str(e)}")
