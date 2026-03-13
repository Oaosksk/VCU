"""Application configuration"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    APP_NAME: str = "Accident Detection API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    DATABASE_URL: str = "sqlite:///./accident_detection.db"
    
    UPLOAD_DIR: str = "./storage/uploads"
    MODEL_DIR: str = "./storage/models"
    FRAMES_DIR: str = "./storage/frames"
    CLIPS_DIR: str = "./storage/clips"
    MAX_UPLOAD_SIZE: int = 524_288_000
    
    YOLO_MODEL_PATH: str = "./yolov8s.pt"
    LSTM_MODEL_PATH: str = "./storage/models/lstm_crash_detector.pth"
    CONFIDENCE_WINDOW_SIZE: int = 15
    CONFIDENCE_THRESHOLD: float = 0.75
    
    INFERENCE_TIMEOUT: int = 1800
    LSTM_WINDOW_SIZE: int = 30
    MAX_INFERENCE_FRAMES: int = 100
    
    TARGET_FPS: int = 10
    MAX_VIDEO_DURATION: int = 600
    
    ALLOWED_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    
    GROQ_API_KEY: str = ""
    
    USE_GPU: bool = True
    
    @property
    def cors_origins(self) -> List[str]:
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",")]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
