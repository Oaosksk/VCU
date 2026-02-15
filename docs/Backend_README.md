# 🚗 Vehicle Crash Detection System — Backend

AI-powered vehicle accident detection using **YOLOv8** for spatial analysis, **LSTM** for temporal analysis, and a **novel Temporal Confidence Aggregation (TCA)** algorithm to reduce false positives.

## 🏗️ Architecture

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌───────────┐
│ Video Upload │ ──▶ │ YOLOv8       │ ──▶ │ LSTM         │ ──▶ │ TCA       │
│ (FastAPI)    │     │ (Spatial)    │     │ (Temporal)   │     │ (Novel)   │
└─────────────┘     └──────────────┘     └──────────────┘     └───────────┘
        │                                                           │
        ▼                                                           ▼
   ┌─────────┐                                                ┌──────────┐
   │ Database │ ◀──────────── Results ◀───────────────────── │ Decision │
   │ (MySQL)  │                                               └──────────┘
   └─────────┘
```

**Tech Stack:** FastAPI · PyTorch 2.x · Ultralytics YOLOv8 · SQLAlchemy · React 19

---

## 📦 Installation

### Prerequisites
- Python 3.11+
- MySQL 8.0+ (or SQLite for local dev)
- CUDA-capable GPU (optional, falls back to CPU)

### Setup

```bash
# 1. Clone and enter backend
cd Backend

# 2. Create virtual environment
python -m venv .venv
.venv\Scripts\activate        # Windows
# source .venv/bin/activate   # Linux/Mac

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy environment file and configure
copy .env.example .env
# Edit .env with your database URL and API keys
```

---

## ⚙️ Configuration

Edit `.env` to configure:

| Variable | Description | Default |
|---|---|---|
| `DATABASE_URL` | Database connection string | `sqlite:///./accident_detection.db` |
| `UPLOAD_DIR` | Video upload directory | `./storage/uploads` |
| `YOLO_MODEL_PATH` | Path to YOLOv8 weights | `./storage/models/yolov8s.pt` |
| `LSTM_MODEL_PATH` | Path to trained LSTM weights | `./storage/models/lstm_crash_detector.pth` |
| `GROQ_API_KEY` | Groq API key for AI explanations | _(optional)_ |
| `ALLOWED_ORIGINS` | CORS allowed origins | `http://localhost:5173` |
| `MAX_VIDEO_DURATION` | Max video length in seconds | `300` |
| `TARGET_FPS` | Frame extraction rate | `10` |

---

## 🚀 Running

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or use the batch script
run.bat
```

The API will be available at `http://localhost:8000`.  
Interactive docs at `http://localhost:8000/docs`.

---

## 📡 API Endpoints

### `GET /health`
Health check with system validation (DB, models, disk, GPU).

### `POST /api/upload`
Upload a video file for analysis.
- **Body:** `multipart/form-data` with `video` field
- **Limits:** 500MB, formats: `.mp4`, `.avi`, `.mov`, `.mkv`

```json
// Response
{
  "video_id": "uuid-string",
  "message": "Video uploaded successfully",
  "filename": "crash_video.mp4",
  "size": 15728640
}
```

### `POST /api/analyze`
Analyze an uploaded video for accidents.
- **Body:** `{"video_id": "uuid-string"}`

```json
// Response
{
  "id": "result-uuid",
  "status": "accident",
  "confidence": 0.847,
  "timestamp": "2024-01-15T10:30:00",
  "details": {
    "spatialFeatures": "Detected 245 objects across 150 frames",
    "temporalFeatures": "Temporal stability: 0.82",
    "frameCount": 150,
    "duration": "15.0 seconds",
    "temporalStability": 0.82,
    "eventFrames": [[45, 78]],
    "maxConfidence": 0.92,
    "meanConfidence": 0.65
  }
}
```

### `GET /api/explanation/{result_id}`
Get AI-generated explanation for an analysis result.

---

## ⭐ Novel Contribution: Temporal Confidence Aggregation

Located in `app/services/confidence_service.py`, TCA improves accident detection accuracy by:

1. **Spike Filtering** — Removes single-frame false positives
2. **Sliding Window Aggregation** — Weighted temporal smoothing (window=15 frames)
3. **Temporal Consistency Check** — Requires sustained high confidence across ≥3 consecutive frames
4. **Event Detection** — Groups high-confidence frames into accident event windows
5. **Multi-factor Decision** — Combines max window score (50%), consistency (30%), and mean confidence (20%)

This approach reduces false positive rates compared to per-frame detection baselines.

---

## 🧪 Testing

```bash
# Install test dependencies
pip install pytest httpx

# Run all tests
python -m pytest tests/ -v

# Run specific test suite
python -m pytest tests/services/test_confidence.py -v
```

---

## 📁 Project Structure

```
Backend/
├── app/
│   ├── api/v1/            # API routes and schemas
│   ├── core/              # Config and settings
│   ├── db/                # Database models, CRUD, connection
│   ├── ml/
│   │   ├── models/        # YOLOv8 + LSTM model wrappers
│   │   └── pipeline/      # Frame extraction, preprocessing
│   ├── services/          # Business logic (inference, TCA, Groq)
│   ├── utils/             # Constants, file utils, metrics
│   └── main.py            # FastAPI entry point
├── scripts/               # Training, DB init, feature extraction
├── tests/                 # Unit and API tests
├── storage/               # Uploads and model weights
└── requirements.txt
```
