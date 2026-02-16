"""Database CRUD operations"""
import json
from sqlalchemy.orm import Session
from app.db.models import Video, AnalysisResult, Event, AccidentFrame
import logging

logger = logging.getLogger(__name__)


def create_video(db: Session, video_id: str, filename: str, filepath: str, size: int) -> Video:
    """Create a new video record"""
    db_video = Video(
        id=video_id,
        filename=filename,
        filepath=filepath,
        size=size,
        status="pending"
    )
    db.add(db_video)
    db.commit()
    db.refresh(db_video)
    logger.info(f"Video record created: {video_id}")
    return db_video


def update_video_status(db: Session, video_id: str, status: str) -> Video | None:
    """Update video processing status"""
    db_video = db.query(Video).filter(Video.id == video_id).first()
    if db_video:
        db_video.status = status
        db.commit()
        db.refresh(db_video)
        logger.info(f"Video {video_id} status updated to: {status}")
    return db_video


def get_video(db: Session, video_id: str) -> Video | None:
    """Get video by ID"""
    return db.query(Video).filter(Video.id == video_id).first()


def create_analysis_result(db: Session, result: dict) -> AnalysisResult:
    """Save analysis result to database"""
    db_result = AnalysisResult(
        id=result["id"],
        video_id=result.get("video_id", result["id"].replace("result-", "")),
        status=result["status"],
        confidence=result["confidence"],
        details=result.get("details"),
        inference_time=result.get("inference_time"),
        temporal_stability=result.get("details", {}).get("temporalStability")
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    logger.info(f"Analysis result saved: {db_result.id}")
    return db_result


def create_events(db: Session, video_id: str, result_id: str,
                  event_frames: list, fps: float = 10.0) -> list[Event]:
    """Save detected event frames to database"""
    events = []
    for start_frame, end_frame in event_frames:
        event = Event(
            video_id=video_id,
            result_id=result_id,
            start_frame=start_frame,
            end_frame=end_frame,
            start_time=round(start_frame / fps, 2),
            end_time=round(end_frame / fps, 2),
            confidence=1.0  # Event frames already passed threshold
        )
        db.add(event)
        events.append(event)

    if events:
        db.commit()
        logger.info(f"Saved {len(events)} events for result {result_id}")

    return events


def get_result_by_id(db: Session, result_id: str) -> AnalysisResult | None:
    """Get analysis result by ID"""
    return db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()


def get_results_by_video(db: Session, video_id: str) -> list[AnalysisResult]:
    """Get all analysis results for a video"""
    return db.query(AnalysisResult).filter(AnalysisResult.video_id == video_id).all()


def create_accident_frames(db: Session, video_id: str, result_id: str, 
                           frames_data: list) -> list[AccidentFrame]:
    """Save accident frame paths to database"""
    frames = []
    for frame_data in frames_data:
        frame = AccidentFrame(
            video_id=video_id,
            result_id=result_id,
            frame_index=frame_data['index'],
            frame_path=frame_data['path'],
            confidence=frame_data.get('confidence', 1.0)
        )
        db.add(frame)
        frames.append(frame)
    
    if frames:
        db.commit()
        logger.info(f"Saved {len(frames)} accident frames for result {result_id}")
    
    return frames


def get_accident_frames_by_video(db: Session, video_id: str) -> list[AccidentFrame]:
    """Get all accident frames for a video"""
    return db.query(AccidentFrame).filter(AccidentFrame.video_id == video_id).order_by(AccidentFrame.frame_index).all()


def get_accident_frames_by_result(db: Session, result_id: str) -> list[AccidentFrame]:
    """Get all accident frames for a result"""
    return db.query(AccidentFrame).filter(AccidentFrame.result_id == result_id).order_by(AccidentFrame.frame_index).all()
