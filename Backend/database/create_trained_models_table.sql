-- SQL Script to create trained_models table in XAMPP MySQL
-- Database: acvi

USE acvi;

-- Table to store trained model information
CREATE TABLE IF NOT EXISTS trained_models (
    id INT AUTO_INCREMENT PRIMARY KEY,
    model_name VARCHAR(255) NOT NULL,
    model_type VARCHAR(50) NOT NULL COMMENT 'LSTM, YOLO, etc',
    model_path VARCHAR(500) NOT NULL,
    training_date DATETIME NOT NULL,
    total_videos INT NOT NULL,
    accident_videos INT NOT NULL,
    normal_videos INT NOT NULL,
    accuracy FLOAT,
    loss FLOAT,
    epochs INT,
    batch_size INT,
    learning_rate FLOAT,
    feature_shape VARCHAR(100) COMMENT 'e.g., (150, 3)',
    notes TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Insert current trained model data
INSERT INTO trained_models (
    model_name,
    model_type,
    model_path,
    training_date,
    total_videos,
    accident_videos,
    normal_videos,
    accuracy,
    epochs,
    feature_shape,
    notes,
    is_active
) VALUES (
    'lstm_crash_detector.pth',
    'LSTM',
    './storage/models/lstm_crash_detector.pth',
    '2026-02-15 23:45:00',
    12,
    12,
    0,
    1.00,
    50,
    '(12, 150, 3)',
    'WARNING: Trained only on accident videos. Need to retrain with normal driving videos.',
    TRUE
);

-- View the inserted data
SELECT * FROM trained_models;
