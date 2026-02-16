"""FastAPI application entry point"""
import logging
import shutil
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI, Query, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy import text
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.logging_config import setup_logging
from app.api.v1.routes import video
from app.db.database import init_db, get_db

# ── Structured logging (replaces basicConfig) ──
setup_logging(
    log_dir="./storage/logs",
    level="DEBUG" if settings.DEBUG else "INFO",
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Include routers
app.include_router(video.router, prefix="/api", tags=["video"])

# Mount static file directories for serving frames and clips
Path("./storage/frames").mkdir(parents=True, exist_ok=True)
Path("./storage/clips").mkdir(parents=True, exist_ok=True)
app.mount("/frames", StaticFiles(directory="./storage/frames"), name="frames")
app.mount("/clips", StaticFiles(directory="./storage/clips"), name="clips")



@app.on_event("startup")
async def startup_event():
    """Initialize database and validate configuration on startup"""
    logger.info("Starting %s v%s", settings.APP_NAME, settings.APP_VERSION)
    logger.info("Debug mode: %s", settings.DEBUG)
    logger.info("CORS origins: %s", settings.cors_origins)

    # Initialize database tables
    try:
        init_db()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error("Database initialization failed: %s", e)

    # Verify model files exist
    yolo_path = Path(settings.YOLO_MODEL_PATH)
    lstm_path = Path(settings.LSTM_MODEL_PATH)
    if not yolo_path.exists():
        logger.warning("YOLO model not found at %s", yolo_path)
    if not lstm_path.exists():
        logger.warning("LSTM model not found at %s", lstm_path)

    # Ensure upload directory exists
    Path(settings.UPLOAD_DIR).mkdir(parents=True, exist_ok=True)


@app.get("/")
async def root():
    return {"message": "Accident Detection API", "version": settings.APP_VERSION}


@app.get("/health")
async def health(db: Session = Depends(get_db)):
    """Health check with real system validation"""
    checks = {}
    degraded = False

    # 1. Database check
    try:
        db.execute(text("SELECT 1"))
        checks["database"] = {"status": "pass", "message": "Connected"}
    except Exception as e:
        checks["database"] = {"status": "fail", "message": str(e)}
        degraded = True

    # 2. Model files check
    yolo_ok = Path(settings.YOLO_MODEL_PATH).exists()
    lstm_ok = Path(settings.LSTM_MODEL_PATH).exists()
    checks["models"] = {
        "status": "pass" if (yolo_ok and lstm_ok) else "warn",
        "yolo": yolo_ok,
        "lstm": lstm_ok,
    }
    if not (yolo_ok and lstm_ok):
        degraded = True

    # 3. Disk space check
    try:
        upload_dir = Path(settings.UPLOAD_DIR)
        upload_dir.mkdir(parents=True, exist_ok=True)
        usage = shutil.disk_usage(str(upload_dir))
        free_gb = round(usage.free / (1024 ** 3), 1)
        checks["disk"] = {"status": "pass" if free_gb >= 1.0 else "warn", "free_gb": free_gb}
        if free_gb < 1.0:
            degraded = True
    except Exception:
        checks["disk"] = {"status": "unknown"}

    # 4. GPU check
    try:
        import torch
        if torch.cuda.is_available():
            checks["gpu"] = {
                "status": "pass",
                "available": True,
                "device": torch.cuda.get_device_name(0),
            }
        else:
            checks["gpu"] = {"status": "pass", "available": False, "device": "CPU"}
    except ImportError:
        checks["gpu"] = {"status": "warn", "available": False, "device": "torch not installed"}

    overall = "degraded" if degraded else "healthy"
    return {"status": overall, "checks": checks, "timestamp": datetime.utcnow().isoformat()}


@app.post("/api/cleanup")
async def run_cleanup(days: int = Query(default=7, ge=1, le=365)):
    """Manually trigger video cleanup for files older than `days` days."""
    from app.services.cleanup_service import cleanup_old_videos, get_storage_usage

    stats = cleanup_old_videos(retention_days=days)
    usage = get_storage_usage()
    return {"cleanup": stats, "storage": usage}
