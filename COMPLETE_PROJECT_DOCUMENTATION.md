# Vehicle Accident Detection System - Complete Project Documentation

Generated: 2026-05-21

## 1. Project Overview

The Vehicle Accident Detection System is a full-stack AI/ML web application for analyzing traffic video footage and predicting whether an accident occurred. It combines computer vision, temporal sequence modeling, backend APIs, persistent storage, and a React user interface.

The system workflow is:

1. A user uploads a traffic video through the frontend.
2. The FastAPI backend stores the video and creates a database record.
3. OpenCV extracts sampled frames from the uploaded video.
4. YOLO detects vehicles in each frame.
5. Vehicle detections are converted into numerical temporal features.
6. An LSTM model predicts accident probability from the frame sequence.
7. Temporal Confidence Aggregation and physics-based heuristics refine the decision.
8. If an accident is detected, annotated frames and an accident clip are generated.
9. Results are stored in the database and returned to the frontend.
10. The UI displays verdict, confidence, evidence frames, video preview, and explanation.

This project is best understood as a prototype/full-stack AI application rather than a fully production-validated safety system. The repository currently does not include the training dataset or trained model checkpoint, so model accuracy claims cannot be independently reproduced from this checkout alone.

## 2. Technology Stack

### Backend

- Python 3.11
- FastAPI
- Uvicorn
- SQLAlchemy
- SQLite by default, configurable for MySQL
- Pydantic and Pydantic Settings
- OpenCV
- NumPy
- PyTorch
- Ultralytics YOLO
- Groq API for optional natural-language explanations

### Frontend

- React 19
- Vite
- Axios
- Tailwind CSS utility styling
- Custom React hooks and UI components

### Machine Learning

- YOLO object detection for spatial vehicle detection
- LSTM neural network for temporal accident classification
- Handcrafted physics features for gating and evidence frame selection
- Temporal Confidence Aggregation for smoothing and event-window detection

### Storage

- Local filesystem for uploaded videos, generated frames, generated clips, logs, and model files
- SQL database for metadata, analysis results, and event records

## 3. Repository Structure

```text
O:/VCU
├── Backend/
│   ├── app/
│   │   ├── api/v1/routes/
│   │   ├── api/v1/schemas/
│   │   ├── core/
│   │   ├── db/
│   │   ├── ml/
│   │   ├── services/
│   │   └── utils/
│   ├── scripts/
│   ├── storage/
│   ├── tests/
│   ├── requirements.txt
│   └── pyproject.toml
├── Frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── hooks/
│   │   ├── services/
│   │   └── utils/
│   ├── package.json
│   └── vite.config.js
├── docs/
├── PROJECT_DOCUMENTATION.md
├── COMPLETE_PROJECT_DOCUMENTATION.md
└── debug_report.txt
```

## 4. System Architecture

The project follows a three-layer architecture:

### Presentation Layer

The React frontend handles:

- Video selection and drag-and-drop upload
- Client-side file validation
- Upload and analysis request orchestration
- Processing animation
- Result visualization
- AI explanation rendering
- Error and retry flows

### Application/API Layer

The FastAPI backend handles:

- Upload endpoint
- Analyze endpoint
- Explanation endpoint
- Frame metadata endpoint
- Health check endpoint
- Cleanup endpoint
- Request validation
- Database interaction
- ML inference orchestration

### ML And Storage Layer

The ML/storage layer handles:

- Frame extraction
- Object detection
- Feature engineering
- LSTM inference
- Confidence aggregation
- Accident frame/clip generation
- Result persistence
- Static serving of generated frames and clips

## 5. End-To-End Execution Flow

### Step 1: User Uploads Video

Frontend file:

- `Frontend/src/components/states/UploadState.jsx`
- `Frontend/src/components/ui/FileDropzone.jsx`
- `Frontend/src/hooks/useVideoUpload.js`

The user selects or drops a file. The frontend validates file type and size using `validateVideoFile`.

Allowed extensions:

- `.mp4`
- `.avi`
- `.mov`
- `.mkv`

Maximum file size:

- 500 MB

### Step 2: Frontend Calls Upload API

Frontend service:

- `Frontend/src/services/api.js`

API request:

```http
POST /api/upload
Content-Type: multipart/form-data
```

Backend route:

- `Backend/app/api/v1/routes/video.py`

The backend:

1. Validates the filename and size.
2. Generates a UUID for the video.
3. Sanitizes the filename.
4. Stores the video in `storage/uploads`.
5. Creates a database row in `videos`.
6. Returns the generated `video_id`.

### Step 3: Frontend Calls Analyze API

API request:

```http
POST /api/analyze
Content-Type: application/json

{
  "video_id": "uuid"
}
```

The backend:

1. Checks whether the video exists in the database.
2. Marks the video as `processing`.
3. Calls `analyze_video_file`.
4. Persists the final analysis result.
5. Marks the video as `completed` or `failed`.
6. Returns the result JSON to the frontend.

### Step 4: Frame Extraction

File:

- `Backend/app/ml/pipeline/frame_extractor.py`

Class:

- `FrameExtractor`

Responsibilities:

- Opens the video using OpenCV.
- Validates FPS, frame count, and duration.
- Samples frames at the configured target FPS.
- Limits extraction to 150 frames to match the LSTM training shape.
- Returns frames as NumPy arrays.

Important configuration:

- `TARGET_FPS`
- `MAX_VIDEO_DURATION`
- `MAX_INFERENCE_FRAMES`

### Step 5: YOLO Vehicle Detection

File:

- `Backend/app/ml/models/yolo_detector.py`

Class:

- `YOLODetector`

Responsibilities:

- Loads the YOLO model lazily.
- Selects GPU when available and enabled.
- Falls back to CPU after GPU out-of-memory errors.
- Detects objects in each extracted frame.
- Returns bounding boxes, confidence, class ID, and class name.

Vehicle classes used by the inference pipeline:

- `car`
- `truck`
- `bus`
- `motorcycle`

### Step 6: Feature Engineering

File:

- `Backend/app/ml/features.py`

Function:

- `normalize_vehicle_features`

For each frame, the system creates three features:

1. Number of detected vehicles.
2. Average YOLO confidence for detected vehicles.
3. Variance of vehicle bounding-box coordinates.

These values are normalized using shared z-score constants. The same normalization utility is used by both training and inference to avoid distribution mismatch.

### Step 7: Physics-Based Gating

File:

- `Backend/app/services/inference_service.py`

The system computes additional heuristic signals:

- Vehicle coverage across frames.
- Average vehicles per frame.
- Bounding-box overlap.
- Sudden overlap spikes.
- Frame-to-frame center movement.
- Bounding-box size change.

Purpose:

- Reject videos that do not appear to contain traffic.
- Avoid running final accident logic on irrelevant inputs.
- Select the most useful frame evidence when an accident is detected.

Risk:

- Hard gates can reject valid edge cases, especially low-light footage, occluded accidents, sparse traffic, unusual camera angles, or weak YOLO detections.

### Step 8: LSTM Accident Classification

File:

- `Backend/app/ml/models/lstm_model.py`

Classes:

- `AccidentLSTM`
- `LSTMDetector`

Architecture:

- Input size: 3
- Hidden size: 64
- LSTM layers: 2
- Dropout: 0.3
- Fully connected layer: 32 units
- Output: sigmoid accident probability

Input shape:

```text
(150, 3)
```

The LSTM returns a probability between 0 and 1.

### Step 9: Temporal Confidence Aggregation

File:

- `Backend/app/services/confidence_service.py`

Class:

- `TemporalConfidenceAggregator`

Responsibilities:

- Filters isolated confidence spikes.
- Computes sliding-window confidence scores.
- Computes temporal stability.
- Groups high-confidence frames into event ranges.
- Produces final temporal metadata.

Important methods:

- `aggregate`
- `_filter_spikes`
- `_sliding_window_aggregate`
- `_check_temporal_consistency`
- `_detect_event_frames`
- `_compute_final_confidence`

### Step 10: Accident Evidence Generation

File:

- `Backend/app/services/frame_service.py`

Class:

- `AccidentFrameService`

Responsibilities:

- Finds the collision peak frame.
- Saves a 5-frame accident sequence around the peak.
- Draws annotated bounding boxes.
- Generates a short MP4 accident clip.
- Returns static URLs for frontend display.

Color coding:

- Red: likely colliding vehicles.
- Amber: vehicles around the impact frame.
- Green: surrounding/context vehicles.

### Step 11: Result Persistence

Files:

- `Backend/app/db/models.py`
- `Backend/app/db/crud.py`

Tables:

- `videos`
- `analysis_results`
- `accident_events`

The backend saves:

- Video metadata.
- Accident/no-accident verdict.
- Confidence score.
- Inference time.
- Temporal stability.
- Frame count.
- Vehicle count.
- JSON details.
- Accident frame/event ranges.

### Step 12: Frontend Result Display

File:

- `Frontend/src/components/states/ResultState.jsx`

The frontend displays:

- Accident/no-accident verdict.
- Confidence score.
- Severity.
- Accident type.
- Frame evidence.
- Reasoning text.
- Uploaded video preview.
- Annotated accident frames.
- Processing time.

## 6. API Reference

### Root

```http
GET /
```

Returns basic API metadata.

### Health Check

```http
GET /health
```

Checks:

- Database connectivity.
- Model file availability.
- Disk space.
- GPU availability.

### Upload Video

```http
POST /api/upload
```

Request:

- Multipart form field: `video`

Response:

```json
{
  "video_id": "uuid",
  "message": "Video uploaded successfully",
  "filename": "traffic.mp4",
  "size": 12345678
}
```

### Analyze Video

```http
POST /api/analyze
```

Request:

```json
{
  "video_id": "uuid"
}
```

Response:

```json
{
  "id": "result-uuid",
  "status": "accident",
  "confidence": 96,
  "timestamp": "2026-05-21T12:00:00",
  "inference_time": 12.34,
  "isAccident": true,
  "accidentType": "Vehicle Collision",
  "severity": "moderate",
  "frameEvidence": "frames 42-48",
  "reasoning": "Detected Vehicle Collision with 96% confidence...",
  "details": {
    "frameCount": 150,
    "duration": "15.0 seconds",
    "temporalStability": 0.82,
    "eventFrames": [[42, 48]],
    "totalVehicles": 73,
    "accidentFrameUrls": ["/frames/video-id/frame_0042.jpg"],
    "accidentClipUrl": "/clips/video-id_accident.mp4"
  }
}
```

### Explanation

```http
GET /api/explanation/{result_id}
```

Returns a Groq-generated explanation when configured, otherwise a fallback explanation.

### Frames

```http
GET /api/frames/{video_id}
```

Returns stored accident frame metadata.

### Cleanup

```http
POST /api/cleanup?days=7
```

Deletes old uploaded videos except videos currently marked as processing.

## 7. Database Schema

### videos

Purpose:

- Stores uploaded video metadata and processing status.

Important fields:

- `id`
- `filename`
- `filepath`
- `size`
- `duration`
- `fps`
- `resolution`
- `status`
- `uploaded_at`
- `processed_at`

### analysis_results

Purpose:

- Stores model prediction and analysis metadata.

Important fields:

- `id`
- `video_id`
- `is_accident`
- `confidence`
- `inference_time`
- `temporal_stability`
- `total_frames`
- `total_vehicles`
- `max_confidence`
- `mean_confidence`
- `details`
- `error_message`
- `created_at`

### accident_events

Purpose:

- Stores detected accident event windows and frame proxies.

Important fields:

- `id`
- `video_id`
- `result_id`
- `start_frame`
- `end_frame`
- `start_time`
- `end_time`
- `duration`
- `confidence`
- `severity`

## 8. Backend File Documentation

### `Backend/app/main.py`

Creates the FastAPI application. Configures logging, CORS, routers, static frame/clip serving, database initialization, health checks, and cleanup endpoint.

### `Backend/app/core/config.py`

Defines application settings using environment variables. Controls database URL, model paths, upload directory, CORS origins, inference limits, GPU usage, and Groq key.

### `Backend/app/core/logging_config.py`

Configures structured application logging to console and files.

### `Backend/app/api/v1/routes/video.py`

Defines all video-related API routes:

- `upload_video`
- `analyze_video`
- `get_explanation`
- `get_video_frames`

It connects request handling, file storage, inference, database persistence, and response formatting.

### `Backend/app/api/v1/schemas/video.py`

Pydantic schemas for upload and analysis request/response validation.

### `Backend/app/api/v1/schemas/response.py`

Common API response schemas for errors, success, and explanations.

### `Backend/app/db/models.py`

SQLAlchemy ORM models for database tables.

### `Backend/app/db/database.py`

Creates SQLAlchemy engine, session factory, database initialization, and dependency-injected sessions.

### `Backend/app/db/crud.py`

Database operations for:

- Creating videos.
- Updating video status.
- Saving analysis results.
- Saving accident events.
- Reading results and frame metadata.

### `Backend/app/ml/models/lstm_model.py`

Defines the LSTM neural network and inference wrapper. Handles model loading, CPU/GPU placement, prediction, sequence prediction, and GPU out-of-memory fallback.

### `Backend/app/ml/models/yolo_detector.py`

Wraps Ultralytics YOLO loading and detection. Handles model path resolution, optional download fallback, GPU/CPU selection, and detection formatting.

### `Backend/app/ml/features.py`

Centralized feature-normalization module used by both training and inference.

### `Backend/app/ml/pipeline/frame_extractor.py`

Extracts frames from video files with validation and duration limits.

### `Backend/app/services/inference_service.py`

Main ML orchestration service. This is the most important backend file. It performs:

- Video lookup.
- Frame extraction.
- YOLO detection.
- LSTM feature generation.
- Physics scoring.
- LSTM prediction.
- Temporal aggregation.
- Accident frame generation.
- Confidence rescaling.
- Severity/type reasoning.
- Final response construction.

### `Backend/app/services/confidence_service.py`

Implements Temporal Confidence Aggregation for smoothing frame confidence signals and identifying event windows.

### `Backend/app/services/frame_service.py`

Generates annotated evidence frames and accident clips.

### `Backend/app/services/video_service.py`

Sanitizes uploaded filenames, saves uploaded videos, and retrieves videos by UUID.

### `Backend/app/services/groq_service.py`

Generates natural-language explanations using Groq. Falls back to local explanation text if no API key is configured or the API fails.

### `Backend/app/services/cleanup_service.py`

Deletes old uploaded files and reports storage usage.

### `Backend/app/utils/constants.py`

Shared backend constants for file validation, video processing, ML thresholds, and statuses.

### `Backend/app/utils/file_utils.py`

Validates video filename extension and upload size.

### `Backend/app/utils/metrics.py`

Provides accuracy, precision, recall, F1, inference-time, and confusion-matrix utilities.

### `Backend/app/utils/time_utils.py`

Formatting helpers for timestamps and durations.

## 9. Frontend File Documentation

### `Frontend/src/App.jsx`

Root React component and state machine for the whole UI.

States:

- upload
- processing
- result
- explanation
- error

### `Frontend/src/services/api.js`

Axios API client and functions:

- `uploadVideo`
- `analyzeVideo`
- `getExplanation`

### `Frontend/src/hooks/useVideoUpload.js`

Coordinates frontend validation, upload, analysis, success callback, and error callback.

### `Frontend/src/hooks/useToast.jsx`

Implements toast notifications.

### `Frontend/src/components/states/UploadState.jsx`

Upload screen containing title text, feature chips, and file dropzone.

### `Frontend/src/components/states/ProcessingState.jsx`

Animated processing screen that shows staged progress while the backend request is running.

Current limitation:

- Progress is simulated rather than streamed from the backend.

### `Frontend/src/components/states/ResultState.jsx`

Displays final prediction, confidence, severity, reasoning, metrics, uploaded video, generated frames, and action buttons.

### `Frontend/src/components/states/ExplanationState.jsx`

Fetches and displays AI-generated or fallback explanation.

### `Frontend/src/components/states/ErrorState.jsx`

Shows upload/analysis errors and retry/reset actions.

### `Frontend/src/components/ui/*`

Reusable UI components:

- Button
- FileDropzone
- FrameGallery
- ProgressBar
- StatusBadge
- VideoPlayer

### `Frontend/src/utils/constants.js`

Frontend application constants, upload limits, allowed MIME types, status labels, thresholds, and processing stages.

### `Frontend/src/utils/fileValidation.js`

Client-side file type, extension, and size validation.

### `Frontend/src/utils/formatters.js`

Display formatting helpers for confidence, timestamp, duration, and text truncation.

## 10. Training Pipeline

### Feature Extraction

Script:

```bash
cd Backend
python scripts/extract_features.py --mode accident
python scripts/extract_features.py --mode normal
python scripts/extract_features.py --mode merge
```

Expected input folders:

```text
Backend/dataset/Accident Videos
Backend/dataset/Non - Accident videos
```

Output:

```text
features_accident.pkl
features_normal.pkl
features.pkl
```

### LSTM Training

Script:

```bash
cd Backend
python scripts/train_lstm.py --features features.pkl --output storage/models/lstm_crash_detector.pth --epochs 100
```

Training features:

- WeightedRandomSampler
- Focal BCE loss
- AdamW optimizer
- CosineAnnealingLR scheduler
- Gradient clipping
- Early stopping
- Basic validation metrics
- Sanity-check predictions

## 11. Environment Setup

### Backend

```bash
cd Backend
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Example `.env`:

```env
DATABASE_URL=sqlite:///./accident_detection.db
YOLO_MODEL_PATH=./storage/models/yolov8s.pt
LSTM_MODEL_PATH=./storage/models/lstm_crash_detector.pth
GROQ_API_KEY=
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:5173
USE_GPU=True
```

### Frontend

```bash
cd Frontend
npm install
npm run dev
```

Default frontend URL:

```text
http://localhost:3000
```

Default backend URL:

```text
http://localhost:8000
```

## 12. Configuration

Main backend settings:

- `DATABASE_URL`
- `UPLOAD_DIR`
- `MODEL_DIR`
- `FRAMES_DIR`
- `CLIPS_DIR`
- `MAX_UPLOAD_SIZE`
- `YOLO_MODEL_PATH`
- `LSTM_MODEL_PATH`
- `CONFIDENCE_WINDOW_SIZE`
- `CONFIDENCE_THRESHOLD`
- `INFERENCE_TIMEOUT`
- `LSTM_WINDOW_SIZE`
- `MAX_INFERENCE_FRAMES`
- `TARGET_FPS`
- `MAX_VIDEO_DURATION`
- `ALLOWED_ORIGINS`
- `GROQ_API_KEY`
- `USE_GPU`

## 13. Testing

Backend tests are located in:

```text
Backend/tests
```

They cover:

- API routes
- File validation
- Metrics
- Confidence aggregation
- CRUD behavior
- Frame extraction
- LSTM model behavior
- YOLO wrapper behavior
- Shared feature normalization

Frontend verification:

```bash
cd Frontend
npm run build
```

Current verification status:

- Frontend production build passed.
- Python tests could not be run in the current environment because no usable Python executable is available and the checked-in virtual environment points to a missing local Python installation.

## 14. Security Review

Implemented:

- Filename sanitization.
- Extension validation.
- Upload size validation.
- CORS allowlist.
- Local static frame/clip serving.

Still needed for production:

- MIME/content sniffing.
- Malware scanning.
- Authentication and authorization.
- Rate limiting.
- Request body limits at reverse proxy level.
- Secure object storage instead of local filesystem.
- Secrets management.
- Audit logging.
- HTTPS termination.
- API abuse protection.

## 15. Performance Review

Current strengths:

- Frame limit prevents unbounded inference.
- GPU use is supported.
- CPU fallback exists.
- OpenCV extraction is straightforward.
- YOLO loading is lazy.

Current bottlenecks:

- Analysis runs synchronously inside the request-response cycle.
- No background job queue.
- No streaming progress updates.
- YOLO is run frame-by-frame rather than batched.
- Local storage does not scale across replicas.
- LSTM and YOLO are re-instantiated per analysis path rather than managed as application-level model services.

Recommended improvements:

- Use Celery/RQ/FastAPI background workers for analysis jobs.
- Add WebSocket or polling progress updates.
- Batch YOLO inference where supported.
- Keep model instances warm in application state.
- Add GPU memory telemetry.
- Add request-level timeout and cancellation.
- Use object storage for uploads and generated artifacts.

## 16. ML Quality Review

Strengths:

- Clear separation of spatial detection and temporal classification.
- Feature extraction is simple and explainable.
- Temporal aggregation helps reduce isolated false positives.
- Evidence frame generation improves interpretability.

Weaknesses:

- Dataset is not included.
- Model checkpoint is not included.
- Accuracy cannot be reproduced from the repository.
- Feature vector is very small and may miss critical accident signals.
- Bounding-box variance is a crude proxy for crash behavior.
- The system may fail under occlusion, low light, camera shake, unusual angles, or crowded traffic.
- Confidence rescaling hides uncertainty by forcing outputs into 0-49 or 91-100.

Recommended ML improvements:

- Add dataset manifest with train/validation/test split.
- Store model version and feature version in each result.
- Add ROC, PR curve, confusion matrix, calibration curve, and threshold report.
- Evaluate on external datasets.
- Add temporal augmentations.
- Consider optical flow, tracked object trajectories, or video transformer features.
- Calibrate confidence with Platt scaling or isotonic regression.
- Add model drift monitoring.

## 17. Production Readiness Checklist

Before deploying for real-world use:

- Add trained model files or reliable model download process.
- Add dataset and evaluation artifacts.
- Replace synchronous inference with background jobs.
- Add progress API or WebSockets.
- Use PostgreSQL/MySQL in production.
- Use object storage for uploads, frames, and clips.
- Add authentication.
- Add rate limits.
- Add MIME sniffing and malware scanning.
- Add Dockerfiles and deployment manifests.
- Add CI for tests and builds.
- Add model/version metadata to results.
- Add observability dashboards.
- Add monitoring and alerting.
- Add retention and cleanup automation.

## 18. Known Limitations In Current Checkout

- No dataset folder is present.
- No trained LSTM checkpoint is present in `Backend/storage/models`.
- No YOLO checkpoint is present in `Backend/storage/models`.
- Backend inference will fail unless model files are supplied or downloaded.
- Frontend progress is simulated.
- Python tests cannot be executed in the current sandbox because Python is unavailable.
- Existing documentation claiming production readiness and perfect accuracy is not reproducible from the current repository state.

## 19. Recent Improvements Made

The following improvements were added during the latest audit/refactor pass:

- Centralized feature normalization in `Backend/app/ml/features.py`.
- Updated inference to use the shared normalization function.
- Updated training feature extraction to use the shared normalization function.
- Fixed fallback accident event frames so API results include generated event windows.
- Made upload size handling robust when `UploadFile.size` is missing.
- Added frontend support for `video/x-msvideo` AVI MIME type.
- Removed unused hook initialization from the processing screen.
- Added object URL cleanup in the result screen to prevent browser memory leaks.
- Added tests for feature normalization and missing upload size handling.
- Added `docs/TECHNICAL_AUDIT.md`.

## 20. Conclusion

This project has a solid full-stack structure and a clear AI/ML inference pipeline. It demonstrates how a React frontend, FastAPI backend, YOLO object detection, LSTM temporal modeling, SQL persistence, and visual evidence generation can work together in a vehicle accident detection application.

However, it should not be considered production ready until the missing model artifacts, dataset, reproducible evaluation, asynchronous processing, stronger security controls, and deployment infrastructure are added. The next most valuable engineering step is to make the ML pipeline reproducible by adding model files, dataset manifests, evaluation scripts, and versioned metrics.
