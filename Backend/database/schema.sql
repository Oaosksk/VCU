-- Accident Detection System Database Schema
-- Database: accident_detection (SQLite)
-- Created: 2026-03-03
-- Updated: 2026-03-05 (converted to SQLite-compatible syntax)

-- ============================================
-- Table: videos
-- Purpose: Store uploaded video metadata
-- ============================================
CREATE TABLE IF NOT EXISTS videos (
    id VARCHAR(36) PRIMARY KEY,                          -- UUID
    filename VARCHAR(255) NOT NULL,                      -- Original filename
    filepath VARCHAR(500) NOT NULL,                      -- Storage path
    size INTEGER NOT NULL,                               -- File size in bytes
    duration REAL DEFAULT NULL,                          -- Video duration in seconds
    fps REAL DEFAULT NULL,                               -- Frames per second
    resolution VARCHAR(20) DEFAULT NULL,                 -- Video resolution (e.g., 1920x1080)
    status VARCHAR(20) NOT NULL DEFAULT 'pending',       -- pending|processing|completed|failed
    uploaded_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    processed_at DATETIME DEFAULT NULL                   -- When analysis completed
);

CREATE INDEX IF NOT EXISTS idx_videos_status ON videos(status);
CREATE INDEX IF NOT EXISTS idx_videos_uploaded_at ON videos(uploaded_at);


-- ============================================
-- Table: analysis_results
-- Purpose: Store accident detection results
-- ============================================
CREATE TABLE IF NOT EXISTS analysis_results (
    id VARCHAR(50) PRIMARY KEY,                          -- result-{video_id}
    video_id VARCHAR(36) NOT NULL REFERENCES videos(id), -- Foreign key to videos.id

    -- Detection result
    is_accident INTEGER NOT NULL,                        -- 1=accident, 0=no_accident
    confidence REAL NOT NULL,                            -- Model confidence (0-100 integer, enforced ranges: 91-100 or 0-49)

    -- Performance metrics
    inference_time REAL DEFAULT NULL,                    -- Processing time in seconds
    temporal_stability REAL DEFAULT NULL,                -- TCA stability score (0.0-1.0)

    -- Detection details
    total_frames INTEGER DEFAULT NULL,                   -- Total frames processed
    total_vehicles INTEGER DEFAULT NULL,                 -- Total vehicles detected
    max_confidence REAL DEFAULT NULL,                    -- Peak confidence score
    mean_confidence REAL DEFAULT NULL,                   -- Average confidence score

    -- Additional data
    details TEXT DEFAULT NULL,                           -- Full analysis details (JSON)
    error_message TEXT DEFAULT NULL,                     -- Error message if failed

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_results_video_id ON analysis_results(video_id);
CREATE INDEX IF NOT EXISTS idx_results_is_accident ON analysis_results(is_accident);
CREATE INDEX IF NOT EXISTS idx_results_confidence ON analysis_results(confidence);


-- ============================================
-- Table: accident_events
-- Purpose: Store detected accident timeframes
-- ============================================
CREATE TABLE IF NOT EXISTS accident_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    video_id VARCHAR(36) NOT NULL REFERENCES videos(id),
    result_id VARCHAR(50) NOT NULL REFERENCES analysis_results(id),

    -- Event timeframe
    start_frame INTEGER NOT NULL,                        -- Event start frame number
    end_frame INTEGER NOT NULL,                          -- Event end frame number
    start_time REAL NOT NULL,                            -- Event start time (seconds)
    end_time REAL NOT NULL,                              -- Event end time (seconds)
    duration REAL NOT NULL,                              -- Event duration (seconds)

    -- Event confidence
    confidence REAL NOT NULL,                            -- Event confidence score
    severity VARCHAR(20) DEFAULT NULL,                   -- low|medium|high

    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_events_video_id ON accident_events(video_id);
CREATE INDEX IF NOT EXISTS idx_events_result_id ON accident_events(result_id);


-- ============================================
-- Sample Queries
-- ============================================

-- Get all videos with their analysis results
-- SELECT v.*, ar.is_accident, ar.confidence
-- FROM videos v
-- LEFT JOIN analysis_results ar ON v.id = ar.video_id
-- ORDER BY v.uploaded_at DESC;

-- Get accident videos only
-- SELECT v.*, ar.confidence, ar.temporal_stability
-- FROM videos v
-- JOIN analysis_results ar ON v.id = ar.video_id
-- WHERE ar.is_accident = 1
-- ORDER BY ar.confidence DESC;

-- Get accident events for a video
-- SELECT * FROM accident_events
-- WHERE video_id = 'your-video-id'
-- ORDER BY start_time;

-- Statistics
-- SELECT
--     COUNT(*) as total_videos,
--     SUM(ar.is_accident) as accidents,
--     AVG(ar.confidence) as avg_confidence,
--     AVG(ar.inference_time) as avg_processing_time
-- FROM videos v
-- LEFT JOIN analysis_results ar ON v.id = ar.video_id
-- WHERE v.status = 'completed';
