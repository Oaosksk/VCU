# Backend — Accident Detection API

FastAPI backend for the Spatio-Temporal Vehicle Accident Detection System.

---

## Setup

```bash
# 1. Create and activate virtual environment
python -m venv .venv
.venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
# Edit .env — set DATABASE_URL, GROQ_API_KEY if needed

# 4. Start server
run.bat
# or manually:
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API runs at: `http://localhost:8000`
Interactive docs at: `http://localhost:8000/docs`

---

## Environment Variables (.env)

| Variable | Description |
|----------|-------------|
| `DATABASE_URL` | MySQL: `mysql+pymysql://root:@localhost:3306/accident_db` |
| `YOLO_MODEL_PATH` | Path to YOLO weights (auto-downloads if missing) |
| `LSTM_MODEL_PATH` | Path to trained LSTM: `./storage/models/lstm_crash_detector.pth` |
| `USE_GPU` | `True` for NVIDIA GPU, `False` for CPU only |
| `GROQ_API_KEY` | Optional — leave empty for fallback explanations |
| `TARGET_FPS` | Frame extraction rate (default: 10) |

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/health` | System health check |
| POST | `/api/upload` | Upload video file |
| POST | `/api/analyze` | Run ML analysis on uploaded video |
| GET | `/api/explanation/{result_id}` | Get AI explanation |
| GET | `/api/frames/{video_id}` | Get accident frames |
| POST | `/api/cleanup` | Delete old uploaded files |

See `docs/API_REFERENCE.md` for full request/response details.

---

## Training the Model

```bash
# Step 1 — Extract features
python scripts/extract_features.py --mode accident
python scripts/extract_features.py --mode normal
python scripts/extract_features.py --mode merge

# Step 2 — Train LSTM
python scripts/train_lstm.py --features features.pkl --output storage/models/lstm_crash_detector.pth --epochs 100
```

See `docs/TRAINING_GUIDE.md` for full instructions.

---

## Running Tests

```bash
pytest tests/ -v
```

---

## Project Structure

```
Backend/
├── app/
│   ├── api/v1/         — Routes and Pydantic schemas
│   ├── core/           — Config (settings.py) and logging
│   ├── db/             — SQLAlchemy models, database, CRUD
│   ├── ml/
│   │   ├── models/     — YOLODetector, LSTMDetector
│   │   ├── pipeline/   — FrameExtractor
│   │   └── features.py — Shared normalization constants
│   ├── services/       — inference, confidence (TCA), frame, groq, video, cleanup
│   └── utils/          — constants, file_utils
├── scripts/            — extract_features, train_lstm, create_normal_clips, download_models
├── storage/
│   ├── uploads/        — Uploaded videos (auto-managed)
│   ├── frames/         — Accident evidence frames
│   ├── clips/          — Accident video clips
│   ├── models/         — Place lstm_crash_detector.pth here
│   └── logs/           — app.log, error.log
└── tests/              — Unit tests for all modules
```
