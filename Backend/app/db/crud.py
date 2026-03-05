"""Database CRUD operations"""
from sqlalchemy.orm import Session
from app.db.models import Video, AnalysisResult, AccidentEvent
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def create_video(db: Session, video_id: str, filename: str, filepath: str, size: int, 
                 duration: float = None, fps: float = None, resolution: str = None) -> Video:
    """Create a new video record"""
    db_video = Video(
        id=video_id,
        filename=filename,
        filepath=filepath,
        size=size,
        duration=duration,
        fps=fps,
        resolution=resolution,
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
        if status == "completed":
            db_video.processed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_video)
        logger.info(f"Video {video_id} status updated to: {status}")
    return db_video


def get_video(db: Session, video_id: str) -> Video | None:
    """Get video by ID"""
    return db.query(Video).filter(Video.id == video_id).first()


def create_analysis_result(db: Session, result: dict) -> AnalysisResult:
    """Save analysis result to database"""
    details = result.get("details", {})
    
    db_result = AnalysisResult(
        id=result["id"],
        video_id=result.get("video_id", result["id"].replace("result-", "")),
        is_accident=1 if result["status"] == "accident" else 0,
        confidence=result["confidence"],
        inference_time=result.get("inference_time"),
        temporal_stability=details.get("temporalStability"),
        total_frames=details.get("frameCount"),
        total_vehicles=details.get("totalVehicles"),
        max_confidence=details.get("maxConfidence"),
        mean_confidence=details.get("meanConfidence"),
        details=details,
        error_message=result.get("error_message")
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    logger.info(f"Analysis result saved: {db_result.id}")
    return db_result


def create_accident_events(db: Session, video_id: str, result_id: str,
                           event_frames: list, fps: float = 10.0) -> list[AccidentEvent]:
    """Save detected accident events to database"""
    events = []
    for start_frame, end_frame in event_frames:
        start_time = round(start_frame / fps, 2)
        end_time = round(end_frame / fps, 2)
        duration = round(end_time - start_time, 2)
        
        # Determine severity based on duration
        if duration < 2.0:
            severity = "low"
        elif duration < 5.0:
            severity = "medium"
        else:
            severity = "high"
        
        event = AccidentEvent(
            video_id=video_id,
            result_id=result_id,
            start_frame=start_frame,
            end_frame=end_frame,
            start_time=start_time,
            end_time=end_time,
            duration=duration,
            confidence=1.0,
            severity=severity
        )
        db.add(event)
        events.append(event)

    if events:
        db.commit()
        logger.info(f"Saved {len(events)} accident events for result {result_id}")

    return events


def get_result_by_id(db: Session, result_id: str) -> AnalysisResult | None:
    """Get analysis result by ID"""
    return db.query(AnalysisResult).filter(AnalysisResult.id == result_id).first()


def get_results_by_video(db: Session, video_id: str) -> list[AnalysisResult]:
    """Get all analysis results for a video"""
    return db.query(AnalysisResult).filter(AnalysisResult.video_id == video_id).all()


def get_accident_events_by_video(db: Session, video_id: str) -> list[AccidentEvent]:
    """Get all accident events for a video"""
    return db.query(AccidentEvent).filter(AccidentEvent.video_id == video_id).order_by(AccidentEvent.start_time).all()


def get_accident_events_by_result(db: Session, result_id: str) -> list[AccidentEvent]:
    """Get all accident events for a result"""
    return db.query(AccidentEvent).filter(AccidentEvent.result_id == result_id).order_by(AccidentEvent.start_time).all()


def create_accident_frames(db: Session, video_id: str, result_id: str, frames_data: list):
    """Save accident frame records to database as AccidentEvent entries"""
    for frame in frames_data:
        event = AccidentEvent(
            video_id=video_id,
            result_id=result_id,
            start_frame=frame['index'],
            end_frame=frame['index'],
            start_time=round(frame['index'] / 10.0, 2),
            end_time=round(frame['index'] / 10.0, 2),
            duration=0.0,
            confidence=frame.get('confidence', 1.0),
            severity="high"
        )
        db.add(event)
    if frames_data:
        db.commit()
        logger.info(f"Saved {len(frames_data)} accident frames for video {video_id}")


def get_accident_frames_by_video(db: Session, video_id: str):
    """Get accident frame records for a video (from accident_events table)"""
    events = db.query(AccidentEvent).filter(
        AccidentEvent.video_id == video_id
    ).order_by(AccidentEvent.start_frame).all()

    class FrameProxy:
        """Lightweight proxy to match the expected interface for frame queries"""
        def __init__(self, event, vid_id):
            self.frame_index = event.start_frame
            self.frame_path = f"/frames/{vid_id}/frame_{event.start_frame:04d}.jpg"
            self.confidence = event.confidence

    return [FrameProxy(e, video_id) for e in events]
