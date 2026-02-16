import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

// Create axios instance
const api = axios.create({
    baseURL: API_BASE_URL,
    timeout: 300000, // 5 minutes (matches backend keep-alive)
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
            error: error.response?.data?.detail || error.message || 'Upload failed',
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
            error: error.response?.data?.detail || error.message || 'Analysis failed',
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
            error: error.response?.data?.detail || error.message || 'Failed to get explanation',
        }
    }
}

export default api
