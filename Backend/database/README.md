# Database Schema - Accident Detection System

## Overview
Clean, optimized database schema with 3 tables for accident detection.

## Tables

### 1. videos
Stores uploaded video metadata
- **Primary Key**: id (UUID)
- **Indexes**: status, uploaded_at
- **Fields**: filename, filepath, size, duration, fps, resolution, status, uploaded_at, processed_at

### 2. analysis_results
Stores accident detection results
- **Primary Key**: id (result-{video_id})
- **Indexes**: video_id, is_accident, confidence
- **Fields**: 
  - Detection: is_accident (0/1), confidence
  - Metrics: inference_time, temporal_stability
  - Stats: total_frames, total_vehicles, max_confidence, mean_confidence
  - Data: details (JSON), error_message

### 3. accident_events
Stores detected accident timeframes
- **Primary Key**: id (auto-increment)
- **Indexes**: video_id, result_id
- **Fields**: start_frame, end_frame, start_time, end_time, duration, confidence, severity

## Setup

1. **Create database:**
```sql
CREATE DATABASE accident_detection;
```

2. **Initialize tables:**
```bash
cd Backend
python scripts/init_db.py
```

3. **Restart backend**

## Key Changes from Old Schema
- Removed `AccidentFrame` table (unused)
- Renamed `Event` → `AccidentEvent` (clearer naming)
- Changed `status` field → `is_accident` (0/1 instead of string)
- Added video metadata fields (duration, fps, resolution)
- Added severity levels for events (low/medium/high)
- Added proper indexes for performance
- Added comments for all fields
