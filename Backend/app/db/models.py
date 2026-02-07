"""Database models"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON, Boolean, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()


class Video(Base):
    __tablename__ = "videos"
    
    id = Column(String, primary_key=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    size = Column(Integer, nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="pending")


class AnalysisResult(Base):
    __tablename__ = "analysis_results"
    
    id = Column(String, primary_key=True)
    video_id = Column(String, nullable=False)
    status = Column(String, nullable=False)
    confidence = Column(Float, nullable=False)
    details = Column(JSON)
    inference_time = Column(Float, nullable=True)  # Added
    temporal_stability = Column(Float, nullable=True)  # Added
    created_at = Column(DateTime, default=datetime.utcnow)


class Event(Base):
    """Event detection table for accident timestamps"""
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    video_id = Column(String, ForeignKey('videos.id'), nullable=False)
    result_id = Column(String, ForeignKey('analysis_results.id'), nullable=False)
    start_frame = Column(Integer, nullable=False)
    end_frame = Column(Integer, nullable=False)
    start_time = Column(Float, nullable=False)  # In seconds
    end_time = Column(Float, nullable=False)  # In seconds
    confidence = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
