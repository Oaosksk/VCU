import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 60000, // 60 seconds
    headers: {
        'Content-Type': 'application/json',
    },
})

/**
 * Upload video file to server
 * @param {File} file - Video file to upload
 * @param {Function} onProgress - Progress callback
 * @returns {Promise} - Upload result
 */
export const uploadVideo = async (file, onProgress) => {
    try {
        const formData = new FormData()
        formData.append('video', file)

        const response = await api.post('/upload', formData, {
            headers: {
                'Content-Type': 'multipart/form-data',
            },
            onUploadProgress: (progressEvent) => {
                const percentCompleted = Math.round(
                    (progressEvent.loaded * 100) / progressEvent.total
                )
                onProgress?.(percentCompleted)
            },
        })

        return {
            success: true,
            videoId: response.data.video_id,
            message: response.data.message,
        }
    } catch (error) {
        console.error('Upload error:', error)
        return {
            success: false,
            error: error.response?.data?.error || error.message || 'Upload failed',
        }
    }
}

/**
 * Analyze uploaded video
 * @param {string} videoId - ID of uploaded video
 * @returns {Promise} - Analysis result
 */
export const analyzeVideo = async (videoId) => {
    try {
        const response = await api.post('/analyze', { video_id: videoId })

        return {
            success: true,
            data: response.data,
        }
    } catch (error) {
        console.error('Analysis error:', error)
        return {
            success: false,
            error: error.response?.data?.error || error.message || 'Analysis failed',
        }
    }
}

/**
 * Get AI explanation for analysis result
 * @param {string} resultId - ID of analysis result
 * @returns {Promise} - Explanation text
 */
export const getExplanation = async (resultId) => {
    try {
        const response = await api.get(`/explanation/${resultId}`)

        return {
            success: true,
            explanation: response.data.explanation,
        }
    } catch (error) {
        console.error('Explanation error:', error)
        return {
            success: false,
            error: error.response?.data?.error || error.message || 'Failed to get explanation',
        }
    }
}

// Mock data for development/demo purposes
export const getMockAnalysisResult = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                success: true,
                data: {
                    id: 'mock-' + Date.now(),
                    status: 'accident',
                    confidence: 0.87,
                    timestamp: new Date().toISOString(),
                    details: {
                        spatialFeatures: 'Vehicle collision detected with high impact force',
                        temporalFeatures: 'Sudden deceleration and erratic movement patterns',
                        frameCount: 450,
                        duration: '15 seconds',
                    },
                },
            })
        }, 2000)
    })
}

export const getMockExplanation = () => {
    return new Promise((resolve) => {
        setTimeout(() => {
            resolve({
                success: true,
                explanation: `Based on the spatio-temporal analysis of the video, our deep learning model has detected a vehicle accident with high confidence (87%).

Spatial Analysis

The model identified significant spatial anomalies including vehicle collision, impact deformation, and debris dispersion patterns characteristic of traffic accidents.

Temporal Analysis

The temporal feature extraction revealed sudden deceleration patterns, erratic movement trajectories, and post-impact vehicle behavior consistent with accident scenarios.

Model Architecture

Our hybrid CNN-LSTM architecture processes both spatial features (using ResNet-50 backbone) and temporal sequences (using bidirectional LSTM layers) to achieve robust accident detection.

Confidence Score

The 87% confidence score indicates strong evidence of an accident event. This score is derived from the combined spatial and temporal feature analysis, with both components showing high agreement on the accident classification.`,
            })
        }, 1500)
    })
}

export default api
