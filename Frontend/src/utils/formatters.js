/**
 * Formats a confidence score to percentage
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} - Formatted percentage
 */
export const formatConfidence = (confidence) => {
    return `${(confidence * 100).toFixed(1)}%`
}

/**
 * Formats a timestamp to readable format
 * @param {Date|string} timestamp - Timestamp to format
 * @returns {string} - Formatted timestamp
 */
export const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp)
    return date.toLocaleString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    })
}

/**
 * Formats duration in milliseconds to readable format
 * @param {number} ms - Duration in milliseconds
 * @returns {string} - Formatted duration
 */
export const formatDuration = (ms) => {
    const seconds = Math.floor(ms / 1000)
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60

    if (minutes > 0) {
        return `${minutes}m ${remainingSeconds}s`
    }
    return `${seconds}s`
}

/**
 * Truncates text to specified length
 * @param {string} text - Text to truncate
 * @param {number} maxLength - Maximum length
 * @returns {string} - Truncated text
 */
export const truncateText = (text, maxLength = 50) => {
    if (text.length <= maxLength) return text
    return text.substring(0, maxLength) + '...'
}

/**
 * Gets confidence level label
 * @param {number} confidence - Confidence score (0-1)
 * @returns {string} - Confidence level label
 */
export const getConfidenceLevel = (confidence) => {
    if (confidence >= 0.8) return 'High'
    if (confidence >= 0.5) return 'Medium'
    return 'Low'
}
