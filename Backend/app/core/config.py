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
    MAX_UPLOAD_SIZE: int = 524_288_000
    
    YOLO_MODEL_PATH: str = "./storage/models/yolov8s.pt"
    LSTM_MODEL_PATH: str = "./storage/models/lstm_crash_detector.pth"
    CONFIDENCE_WINDOW_SIZE: int = 15
    CONFIDENCE_THRESHOLD: float = 0.75
    
    TARGET_FPS: int = 10
    MAX_VIDEO_DURATION: int = 300
    
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
