"""Backend constants matching frontend configuration"""

# File Configuration (mirrors frontend/utils/constants.js)
FILE_CONFIG = {
    "MAX_SIZE": 524_288_000,  # 500MB
    "ALLOWED_TYPES": {
        "video/mp4": ".mp4",
        "video/quicktime": ".mov",
        "video/x-msvideo": ".avi",
        "video/x-matroska": ".mkv",
    },
    "ALLOWED_EXTENSIONS": [".mp4", ".mov", ".avi", ".mkv"],
}

# Video Processing
VIDEO_CONFIG = {
    "TARGET_FPS": 10,
    "MAX_DURATION": 300,  # 5 minutes
    "MIN_DURATION": 1,
}

# ML Configuration
ML_CONFIG = {
    "CONFIDENCE_THRESHOLD": 0.75,
    "CONFIDENCE_WINDOW_SIZE": 15,
    "YOLO_CONF_THRESHOLD": 0.25,
    "YOLO_IOU_THRESHOLD": 0.45,
}

# API Response Status
class Status:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
