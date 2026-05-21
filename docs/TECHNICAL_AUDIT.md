# Vehicle Accident Detection System - Technical Audit

Generated: 2026-05-21

## Executive Summary

This project is a full-stack accident-detection prototype with a React/Vite frontend and a FastAPI backend. The backend uploads traffic videos, extracts frames with OpenCV, detects vehicles with Ultralytics YOLO, converts detections into compact per-frame features, classifies the sequence with a PyTorch LSTM, applies temporal confidence aggregation, stores results in SQLAlchemy-backed storage, and serves annotated accident frames/clips to the UI.

The codebase is coherent and testable, but it is not yet production ready from this checkout alone. The dataset directory is absent, `Backend/storage/models` contains no trained LSTM/YOLO checkpoint, and the published accuracy claims cannot be reproduced without the original data, feature pickle, checkpoints, and evaluation logs.

## Architecture

Frontend flow:
1. `Frontend/src/App.jsx` owns the UI state machine: upload, processing, result, explanation, and error.
2. `UploadState` and `FileDropzone` collect a local video file.
3. `useVideoUpload` validates the file, calls `uploadVideo`, then calls `analyzeVideo`.
4. `ResultState` displays the returned verdict, confidence, frame evidence, local video preview, and annotated frame URLs.
5. `ExplanationState` requests `/api/explanation/{result_id}` and renders the Groq or fallback explanation.

Backend flow:
1. `POST /api/upload` validates extension/size, sanitizes the filename, stores the video by UUID, and creates a `videos` row.
2. `POST /api/analyze` verifies the video row, marks it processing, and calls `analyze_video_file`.
3. `FrameExtractor` samples up to 150 frames at the configured target FPS.
4. `YOLODetector` detects vehicles per frame.
5. `normalize_vehicle_features` converts vehicle count, average vehicle confidence, and bounding-box variance into the LSTM feature vector.
6. Physics heuristics gate obviously irrelevant videos and select visual evidence frames.
7. `LSTMDetector` loads `lstm_crash_detector.pth` and returns an accident probability for the sequence.
8. `TemporalConfidenceAggregator` summarizes confidence, stability, and event windows.
9. `AccidentFrameService` saves annotated JPG evidence and an MP4 clip when an accident is detected.
10. CRUD helpers persist `analysis_results` and event/frame metadata.

## Dataset And Training

Expected dataset paths in `scripts/extract_features.py`:
- `Backend/dataset/Accident Videos`
- `Backend/dataset/Non - Accident videos`

Observed state:
- `Backend/dataset` is not present in this checkout.
- `Backend/storage/models` contains no model checkpoint.
- No `features.pkl`, `features_accident.pkl`, or `features_normal.pkl` is present.

Feature engineering:
- Per frame: `[vehicle_count, average_vehicle_confidence, bbox_coordinate_variance]`.
- The project uses z-score normalization before LSTM inference.
- Normalization is now centralized in `Backend/app/ml/features.py` to prevent training/inference drift.

Training:
- `scripts/extract_features.py` extracts fixed-length `(150, 3)` sequences using YOLO.
- `scripts/train_lstm.py` trains `AccidentLSTM` with weighted sampling, focal BCE, AdamW, cosine annealing, gradient clipping, and early stopping.
- Validation is a small stratified holdout, not a rigorous dataset split protocol.

## Model Behavior

Model stack:
- YOLO is used only as a vehicle/object feature extractor and evidence renderer.
- LSTM is a 2-layer recurrent binary classifier with hidden size 64, dropout 0.3, FC layer 32, and sigmoid output.
- TCA filters isolated confidence spikes, computes sliding-window confidence, temporal stability, and event frame spans.

Current limitations:
- With no shipped checkpoint, inference will fail until `settings.LSTM_MODEL_PATH` points to a real model.
- YOLO auto-download fallback requires network access and may fail in offline production.
- The current confidence rescaling deliberately hides midrange uncertainty: accident results become 91-100 and non-accident results become 0-49.
- The physics gate can reject edge cases with sparse vehicle detections, night footage, occlusion, unusual camera angles, or single-frame crashes.

## File And Function Map

Backend application:
- `app/main.py`: creates the FastAPI app, configures CORS/static mounts, initializes DB tables, exposes `/`, `/health`, and `/api/cleanup`.
- `app/core/config.py`: Pydantic settings for DB, storage, model paths, upload limits, CORS, Groq, and GPU use.
- `app/core/logging_config.py`: structured console/file logging.
- `app/api/v1/routes/video.py`: upload, analyze, explanation, and frame endpoints.
- `app/api/v1/schemas/*.py`: Pydantic request/response contracts.
- `app/db/models.py`: SQLAlchemy tables for videos, analysis results, and accident events.
- `app/db/database.py`: SQLAlchemy engine/session lifecycle.
- `app/db/crud.py`: persistence operations for videos, results, events, and frame proxies.
- `app/ml/models/lstm_model.py`: `AccidentLSTM` architecture and `LSTMDetector` inference wrapper.
- `app/ml/models/yolo_detector.py`: lazy YOLO loader, device selection, detection wrapper, and GPU fallback.
- `app/ml/features.py`: shared YOLO-to-LSTM normalization utility.
- `app/ml/pipeline/frame_extractor.py`: OpenCV frame sampling and metadata extraction.
- `app/services/inference_service.py`: full inference orchestration and final response construction.
- `app/services/confidence_service.py`: temporal aggregation, spike filtering, consistency scoring, and event grouping.
- `app/services/frame_service.py`: collision-peak selection, bounding-box drawing, evidence frame saving, and clip generation.
- `app/services/video_service.py`: filename sanitization, upload storage, and lookup by UUID.
- `app/services/groq_service.py`: Groq explanation generation with deterministic fallback text.
- `app/services/cleanup_service.py`: retention-based cleanup and storage usage reporting.
- `app/utils/constants.py`: backend file/video/ML constants.
- `app/utils/file_utils.py`: extension and size validation.
- `app/utils/metrics.py`: accuracy, precision, recall, F1, confusion matrix, and inference-time metrics.
- `app/utils/time_utils.py`: timestamp and duration formatting helpers.

Scripts:
- `scripts/extract_features.py`: feature extraction for accident/normal videos and pickle merge.
- `scripts/train_lstm.py`: LSTM training and sanity checks.
- `scripts/download_models.py`: model download helper.
- `scripts/create_normal_clips.py`: derives non-accident clips from source videos.
- `scripts/db_utils.py`, `inference_from_db.py`, `yolo_db_register.py`: database-oriented model registration/inference utilities.
- `scripts/init_db.py`: database initialization helper.
- `scripts/check_gpu.py`, `visualize_frames.py`: diagnostics and manual inspection.

Frontend:
- `src/App.jsx`: app state orchestration.
- `src/services/api.js`: Axios API client.
- `src/hooks/useVideoUpload.js`: upload/analyze workflow hook.
- `src/hooks/useToast.jsx`: toast state and component.
- `src/components/states/*.jsx`: upload, processing, result, explanation, and error screens.
- `src/components/ui/*.jsx`: buttons, dropzone, progress, badges, frame gallery, video player.
- `src/utils/constants.js`: frontend states, file limits, endpoint names, thresholds, and stage labels.
- `src/utils/fileValidation.js`: client-side upload validation.
- `src/utils/formatters.js`: display formatting.

## Weak Areas And Failure Modes

- Reproducibility: missing dataset, checkpoints, feature pickles, and evaluation artifacts.
- Production serving: synchronous long-running analysis blocks request workers; background jobs or a queue are needed.
- Security: upload validation is extension/size based; stronger content sniffing and antivirus scanning are needed before public deployment.
- Database design: accident frames are represented as event proxies rather than a dedicated frame table, which can duplicate event semantics.
- Scalability: local filesystem storage and SQLite defaults are not suitable for multi-instance deployment.
- Observability: no request IDs, model version stamps in result rows, GPU memory telemetry, or structured inference trace.
- ML quality: no calibration curves, ROC/PR curves, held-out test manifest, confusion matrix artifact, or drift monitoring.
- Frontend UX: progress is simulated rather than driven by backend processing status.

## Improvements Implemented In This Pass

- Added `app/ml/features.py` and reused it from training and inference so feature normalization cannot diverge silently.
- Fixed fallback event frames so accident evidence selected after LSTM detection is included in API `details.eventFrames`.
- Made backend upload validation robust when `UploadFile.size` is unavailable and persisted the actual saved file size.
- Added `video/x-msvideo` to frontend AVI validation to match common browser MIME reporting.
- Removed unused processing-state hook initialization.
- Revoked local preview object URLs in `ResultState` to avoid browser memory leaks.
- Added tests for shared feature normalization and upload validation without a reported size.

## Production Readiness Checklist

Required before real-world deployment:
- Provide model artifacts and pin their hashes.
- Add a dataset manifest and reproducible train/eval command with metrics artifacts.
- Move analysis to a job queue with status polling or WebSockets.
- Store uploads/evidence in object storage and keep DB metadata only in SQL.
- Add MIME/content validation, malware scanning, auth/rate limits, and retention policies.
- Containerize backend/frontend and use environment-specific settings.
- Add model version, feature version, threshold version, and calibration metadata to every result.
- Add integration tests using tiny fixture videos and mocked YOLO/LSTM outputs.
