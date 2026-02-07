"""Database models"""
from sqlalchemy import Column, String, Float, Integer, DateTime, JSON
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
    created_at = Column(DateTime, default=datetime.utcnow)
