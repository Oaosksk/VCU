# Spatio-Temporal Vehicle Accident Detection System

A full-stack AI/ML web application that detects vehicle accidents in video footage using a hybrid deep learning pipeline combining **YOLOv8** for spatial object detection and **LSTM** for temporal pattern analysis, enhanced by a novel **Temporal Confidence Aggregation (TCA)** algorithm.

---

## System Architecture

```
┌─────────────────────────────────────────┐
│         Frontend  (React 19 + Vite)     │
│  Upload → Processing → Result → Explain │
└──────────────────┬──────────────────────┘
                   │ REST API
┌──────────────────▼──────────────────────┐
│         Backend  (FastAPI + PyTorch)    │
│                                         │
│  Video → Frames → YOLO → Features       │
│       → LSTM → TCA → Decision           │
└──────────────────┬──────────────────────┘
                   │
┌──────────────────▼──────────────────────┐
│     Database  (MySQL via XAMPP)         │
│  videos | analysis_results | events     │
└─────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React 19, Vite, Tailwind CSS, Axios |
| Backend | FastAPI, Python 3.11 |
| Deep Learning | PyTorch 2.2, Ultralytics YOLOv11m |
| Computer Vision | OpenCV 4.9 |
| Database | SQLAlchemy, MySQL (XAMPP) |
| AI Explanation | Groq API (LLaMA 3.3 70B) |

---

## Quick Start

### Prerequisites
- Python 3.11
- Node.js 18+
- XAMPP (MySQL)
- NVIDIA GPU recommended (RTX 3050 or better)

### 1. Database Setup
1. Open XAMPP → Start MySQL
2. Go to `http://localhost/phpmyadmin`
3. Create database named `accident_db`

### 2. Backend
```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
# Edit .env — set DATABASE_URL to MySQL
run.bat
```
Backend runs at: `http://localhost:8000`

### 3. Frontend
```bash
cd Frontend
npm install
npm run dev
```
Frontend runs at: `http://localhost:3000`

---

## Model Training

Before running inference, train the LSTM model:

```bash
cd Backend

# Step 1 — Extract YOLO features from accident videos
python scripts/extract_features.py --mode accident
python scripts/extract_features.py --mode normal
python scripts/extract_features.py --mode merge

# Step 2 — Train LSTM
python scripts/train_lstm.py --features features.pkl --output storage/models/lstm_crash_detector.pth --epochs 100
```

Dataset folder structure required:
```
Backend/dataset/
├── Accident Videos/
└── Non - Accident videos/
```

See `docs/TRAINING_GUIDE.md` for full training instructions.

---

## Novel Contribution — Temporal Confidence Aggregation (TCA)

The TCA algorithm (`app/services/confidence_service.py`) reduces false positives through:

1. **Spike Filtering** — removes single-frame anomalies
2. **Sliding Window Aggregation** — 15-frame weighted smoothing
3. **Temporal Consistency Check** — requires sustained high confidence
4. **Event Detection** — groups high-confidence frames into event windows
5. **Final Decision** — P90 window score (50%) + consistency (30%) + mean (20%)

---

## Documentation

| File | Description |
|------|-------------|
| `docs/API_REFERENCE.md` | All API endpoints with request/response examples |
| `docs/DATABASE_SCHEMA.md` | Database tables and relationships |
| `docs/TRAINING_GUIDE.md` | Step-by-step model training instructions |
| `Backend/README.md` | Backend setup and configuration |

---

## Project Structure

```
VCU/
├── Backend/
│   ├── app/
│   │   ├── api/          — API routes and schemas
│   │   ├── core/         — Config and logging
│   │   ├── db/           — Database models and CRUD
│   │   ├── ml/           — YOLO, LSTM, feature engineering
│   │   ├── services/     — Inference, TCA, Groq, cleanup
│   │   └── utils/        — Constants, file validation
│   ├── scripts/          — Training pipeline scripts
│   ├── storage/          — Uploads, frames, clips, models
│   └── tests/            — Unit tests
├── Frontend/
│   └── src/
│       ├── components/   — Layout, states, UI components
│       ├── hooks/        — useVideoUpload, useToast
│       ├── services/     — Axios API client
│       └── utils/        — Constants, validation, formatters
└── docs/                 — Project documentation
```

---

*College Project — Computer Science and Engineering*
