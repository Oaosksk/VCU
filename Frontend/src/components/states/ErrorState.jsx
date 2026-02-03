import Button from '../ui/Button'

const ErrorState = ({ error, onRetry, onReset }) => {
    return (
        <div className="text-center space-y-8">
            {/* Error Icon */}
            <div className="w-20 h-20 mx-auto bg-red-600 rounded-full flex items-center justify-center">
                <svg
                    className="w-10 h-10 text-white"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                >
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
            </div>

            {/* Header */}
            <div className="space-y-3">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Analysis Failed
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                    We encountered an error while processing your video
                </p>
            </div>

            {/* Error Message */}
            <div className="bg-red-900/20 border border-red-800 rounded-xl p-6 max-w-md mx-auto">
                <div className="flex items-start gap-3">
                    <svg
                        className="w-6 h-6 text-red-400 flex-shrink-0 mt-0.5"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
                        />
                    </svg>
                    <div className="flex-1 text-left">
                        <h3 className="font-semibold text-red-200 mb-1">
                            Error Details
                        </h3>
                        <p className="text-sm text-red-300">
                            {error || 'An unexpected error occurred during video analysis'}
                        </p>
                    </div>
                </div>
            </div>

            {/* Troubleshooting Tips */}
            <div className="bg-slate-800/50 rounded-xl p-6 max-w-md mx-auto border border-slate-700">
                <h3 className="font-semibold text-white mb-4 flex items-center gap-2">
                    <svg
                        className="w-5 h-5 text-blue-400"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                        />
                    </svg>
                    Troubleshooting Tips
                </h3>
                <ul className="text-left space-y-2 text-sm text-gray-300">
                    <li className="flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">•</span>
                        <span>Ensure your video is in a supported format (MP4, AVI, MOV)</span>
                    </li>
                    <li className="flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">•</span>
                        <span>Check that the file size is under 100MB</span>
                    </li>
                    <li className="flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">•</span>
                        <span>Make sure you have a stable internet connection</span>
                    </li>
                    <li className="flex items-start gap-2">
                        <span className="text-blue-400 mt-0.5">•</span>
                        <span>Try uploading a different video file</span>
                    </li>
                </ul>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button onClick={onRetry} variant="primary">
                    Try Again
                </Button>
                <Button onClick={onReset} variant="secondary">
                    Upload Different Video
                </Button>
            </div>

            {/* Support */}
            <p className="text-sm text-gray-500 dark:text-gray-500">
                If the problem persists, please contact support
            </p>
        </div>
    )
}

export default ErrorState
