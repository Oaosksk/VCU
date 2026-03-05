"""Database models for Accident Detection System"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Text, Index, ForeignKey
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime


class Base(DeclarativeBase):
    pass


class Video(Base):
    """Uploaded video metadata"""
    __tablename__ = "videos"
    
    id = Column(String(36), primary_key=True, comment="UUID")
    filename = Column(String(255), nullable=False, comment="Original filename")
    filepath = Column(String(500), nullable=False, comment="Storage path")
    size = Column(Integer, nullable=False, comment="File size in bytes")
    duration = Column(Float, nullable=True, comment="Video duration in seconds")
    fps = Column(Float, nullable=True, comment="Frames per second")
    resolution = Column(String(20), nullable=True, comment="Video resolution (e.g., 1920x1080)")
    status = Column(String(20), default="pending", nullable=False, comment="pending|processing|completed|failed")
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    processed_at = Column(DateTime, nullable=True, comment="When analysis completed")
    
    __table_args__ = (
        Index('idx_videos_status', 'status'),
        Index('idx_videos_uploaded_at', 'uploaded_at'),
    )


class AnalysisResult(Base):
    """Accident detection analysis results"""
    __tablename__ = "analysis_results"
    
    id = Column(String(50), primary_key=True, comment="result-{video_id}")
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False, index=True, comment="Foreign key to videos.id")
    
    # Detection result
    is_accident = Column(Integer, nullable=False, comment="1=accident, 0=no_accident")
    confidence = Column(Float, nullable=False, comment="Model confidence (0-100 integer, enforced ranges: 91-100 or 0-49)")
    
    # Performance metrics
    inference_time = Column(Float, nullable=True, comment="Processing time in seconds")
    temporal_stability = Column(Float, nullable=True, comment="TCA stability score (0.0-1.0)")
    
    # Detection details
    total_frames = Column(Integer, nullable=True, comment="Total frames processed")
    total_vehicles = Column(Integer, nullable=True, comment="Total vehicles detected")
    max_confidence = Column(Float, nullable=True, comment="Peak confidence score")
    mean_confidence = Column(Float, nullable=True, comment="Average confidence score")
    
    # Additional data
    details = Column(JSON, nullable=True, comment="Full analysis details (JSON)")
    error_message = Column(Text, nullable=True, comment="Error message if failed")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_results_video_id', 'video_id'),
        Index('idx_results_is_accident', 'is_accident'),
        Index('idx_results_confidence', 'confidence'),
    )


class AccidentEvent(Base):
    """Detected accident event timeframes"""
    __tablename__ = "accident_events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False, index=True)
    result_id = Column(String(50), ForeignKey('analysis_results.id'), nullable=False, index=True)
    
    # Event timeframe
    start_frame = Column(Integer, nullable=False, comment="Event start frame number")
    end_frame = Column(Integer, nullable=False, comment="Event end frame number")
    start_time = Column(Float, nullable=False, comment="Event start time (seconds)")
    end_time = Column(Float, nullable=False, comment="Event end time (seconds)")
    duration = Column(Float, nullable=False, comment="Event duration (seconds)")
    
    # Event confidence
    confidence = Column(Float, nullable=False, comment="Event confidence score")
    severity = Column(String(20), nullable=True, comment="low|medium|high")
    
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    __table_args__ = (
        Index('idx_events_video_id', 'video_id'),
        Index('idx_events_result_id', 'result_id'),
    )
