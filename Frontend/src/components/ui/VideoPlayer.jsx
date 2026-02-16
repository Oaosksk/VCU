import { useRef, useState } from 'react'

const VideoPlayer = ({ clipUrl, baseUrl }) => {
    const videoRef = useRef(null)
    const [isPlaying, setIsPlaying] = useState(false)

    if (!clipUrl) {
        return null
    }

    const fullUrl = `${baseUrl}${clipUrl}`

    const togglePlay = () => {
        if (videoRef.current) {
            if (isPlaying) {
                videoRef.current.pause()
            } else {
                videoRef.current.play()
            }
            setIsPlaying(!isPlaying)
        }
    }

    const handleVideoEnd = () => {
        setIsPlaying(false)
    }

    return (
        <div className="space-y-3">
            {/* Header */}
            <h3 className="text-lg font-semibold text-white flex items-center gap-2">
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
                        d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
                    />
                    <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
                    />
                </svg>
                Accident Clip
            </h3>

            {/* Video Player */}
            <div className="relative bg-black rounded-lg overflow-hidden border border-slate-700">
                <video
                    ref={videoRef}
                    src={fullUrl}
                    className="w-full h-auto"
                    onEnded={handleVideoEnd}
                    onClick={togglePlay}
                    controls
                >
                    Your browser does not support the video tag.
                </video>

                {/* Play overlay (visible when paused) */}
                {!isPlaying && (
                    <div
                        className="absolute inset-0 flex items-center justify-center bg-black/30 cursor-pointer"
                        onClick={togglePlay}
                    >
                        <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center hover:bg-blue-700 transition-colors">
                            <svg
                                className="w-8 h-8 text-white ml-1"
                                fill="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path d="M8 5v14l11-7z" />
                            </svg>
                        </div>
                    </div>
                )}
            </div>

            {/* Info */}
            <p className="text-xs text-gray-500">
                This clip contains only the detected accident frames
            </p>
        </div>
    )
}

export default VideoPlayer
