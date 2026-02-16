"""Database models"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String(36), primary_key=True)
    filename = Column(String(255), nullable=False)
    filepath = Column(String(500), nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String(50), default="pending")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(String(50), primary_key=True)
    video_id = Column(String(36), nullable=False)
    status = Column(String(50), nullable=False)
    confidence = Column(Float, nullable=False)
    details = Column(JSON)
    inference_time = Column(Float, nullable=True)  # Added
    temporal_stability = Column(Float, nullable=True)  # Added
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    """Event detection table for accident timestamps"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    result_id = Column(String(50), ForeignKey('analysis_results.id'), nullable=False)
    start_frame = Column(Integer, nullable=False)
    end_frame = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)  # In seconds
    end_time = Column(Float, nullable=False)  # In seconds
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class AccidentFrame(Base):
    """Accident frame storage table"""
    __tablename__ = "accident_frames"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String(36), ForeignKey('videos.id'), nullable=False)
    result_id = Column(String(50), ForeignKey('analysis_results.id'), nullable=False)
    frame_index = Column(Integer, nullable=False)
    frame_path = Column(String(500), nullable=False)
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
