import { useState, useCallback } from 'react'
import { validateVideoFile } from '../utils/fileValidation'
import { uploadVideo, analyzeVideo } from '../services/api'

export const useVideoUpload = () => {
    const [isUploading, setIsUploading] = useState(false)
    const [uploadProgress, setUploadProgress] = useState(0)
    const [error, setError] = useState(null)

    const uploadAndAnalyze = useCallback(async (file, onSuccess, onError) => {
        // Validate file
        const validation = validateVideoFile(file)
        if (!validation.valid) {
            setError(validation.error)
            onError?.(validation.error)
            return
        }

        setIsUploading(true)
        setError(null)
        setUploadProgress(0)

        try {
            // Upload video
            const uploadResult = await uploadVideo(file, (progress) => {
                setUploadProgress(progress)
            })

            if (!uploadResult.success) {
                throw new Error(uploadResult.error || 'Upload failed')
            }

            // Analyze video
            const analysisResult = await analyzeVideo(uploadResult.videoId)

            if (!analysisResult.success) {
                throw new Error(analysisResult.error || 'Analysis failed')
            }

            setIsUploading(false)
            setUploadProgress(100)
            onSuccess?.(analysisResult.data)

        } catch (err) {
            setIsUploading(false)
            setError(err.message)
            onError?.(err.message)
        }
    }, [])

    const reset = useCallback(() => {
        setIsUploading(false)
        setUploadProgress(0)
        setError(null)
    }, [])

    return {
        isUploading,
        uploadProgress,
        error,
        uploadAndAnalyze,
        reset
    }
}
