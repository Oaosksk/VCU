import { FILE_CONFIG } from './constants'

/**
 * Validates if a file is a valid video file
 * @param {File} file - The file to validate
 * @returns {Object} - { valid: boolean, error: string }
 */
export const validateVideoFile = (file) => {
    if (!file) {
        return { valid: false, error: 'No file provided' }
    }

    // Check file type
    const fileType = file.type
    const isValidType = Object.keys(FILE_CONFIG.ALLOWED_TYPES).includes(fileType)

    if (!isValidType) {
        const allowedFormats = FILE_CONFIG.ALLOWED_EXTENSIONS.join(', ')
        return {
            valid: false,
            error: `Invalid file type. Allowed formats: ${allowedFormats}`
        }
    }

    // Check file size
    if (file.size > FILE_CONFIG.MAX_SIZE) {
        const maxSizeMB = FILE_CONFIG.MAX_SIZE / (1024 * 1024)
        return {
            valid: false,
            error: `File size exceeds ${maxSizeMB}MB limit`
        }
    }

    // Check file extension
    const fileName = file.name.toLowerCase()
    const hasValidExtension = FILE_CONFIG.ALLOWED_EXTENSIONS.some(ext =>
        fileName.endsWith(ext)
    )

    if (!hasValidExtension) {
        return {
            valid: false,
            error: 'Invalid file extension'
        }
    }

    return { valid: true, error: null }
}

/**
 * Formats file size to human-readable format
 * @param {number} bytes - File size in bytes
 * @returns {string} - Formatted file size
 */
export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes'

    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))

    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i]
}
