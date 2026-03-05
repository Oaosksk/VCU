"""Configuration for ML Model Database Storage System"""

# ═══════════════════════════════════════════════════════
# DATABASE CONNECTION (XAMPP MySQL)
# ═══════════════════════════════════════════════════════
DB_HOST = "localhost"
DB_PORT = 3306
DB_USER = "root"
DB_PASSWORD = ""
DB_NAME = "accident_detection"

# ═══════════════════════════════════════════════════════
# MODEL LOADING STRATEGY
# ═══════════════════════════════════════════════════════
LOAD_FROM = "db"  # Options: "db" or "filesystem"

# ═══════════════════════════════════════════════════════
# YOLO MODEL PATH (External File - Not Stored in DB)
# ═══════════════════════════════════════════════════════
# IMPORTANT: Update this path on each machine or use relative path
YOLO_PATH = "./yolov8s.pt"  # Relative to Backend directory

# ═══════════════════════════════════════════════════════
# BLOB CHUNKING (For Large Model Files)
# ═══════════════════════════════════════════════════════
CHUNK_SIZE = 1048576  # 1MB per chunk
