// Application States
export const APP_STATES = {
    UPLOAD: 'upload',
    PROCESSING: 'processing',
    RESULT: 'result',
    EXPLANATION: 'explanation',
    ERROR: 'error'
}

// File Upload Configuration
export const FILE_CONFIG = {
    MAX_SIZE: 100 * 1024 * 1024, // 100MB in bytes
    ALLOWED_TYPES: {
        'video/mp4': ['.mp4'],
        'video/avi': ['.avi'],
        'video/quicktime': ['.mov'],
    },
    ALLOWED_EXTENSIONS: ['.mp4', '.avi', '.mov']
}

// API Endpoints
export const API_ENDPOINTS = {
    UPLOAD: '/upload',
    ANALYZE: '/analyze',
    EXPLANATION: '/explanation'
}

// Status Types
export const STATUS_TYPES = {
    ACCIDENT: 'accident',
    NO_ACCIDENT: 'no_accident',
    UNCERTAIN: 'uncertain'
}

// Confidence Thresholds
export const CONFIDENCE_THRESHOLDS = {
    HIGH: 0.8,
    MEDIUM: 0.5,
    LOW: 0.3
}

// Toast Types
export const TOAST_TYPES = {
    SUCCESS: 'success',
    ERROR: 'error',
    INFO: 'info',
    WARNING: 'warning'
}

// Processing Stages
export const PROCESSING_STAGES = [
    { id: 1, name: 'Uploading Video', duration: 2000 },
    { id: 2, name: 'Extracting Frames', duration: 3000 },
    { id: 3, name: 'Analyzing Spatial Features', duration: 4000 },
    { id: 4, name: 'Analyzing Temporal Features', duration: 4000 },
    { id: 5, name: 'Generating Results', duration: 2000 }
]
