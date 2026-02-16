import { useState } from 'react'
import Button from '../ui/Button'
import StatusBadge from '../ui/StatusBadge'
import FrameGallery from '../ui/FrameGallery'
import VideoPlayer from '../ui/VideoPlayer'
import { formatTimestamp } from '../../utils/formatters'

const ResultState = ({ result, file, onViewExplanation, onReset }) => {
    const [zoomedImage, setZoomedImage] = useState(null)

    if (!result) {
        return (
            <div className="text-center">
                <p className="text-gray-400">No results available</p>
            </div>
        )
    }

    // Create object URL for the uploaded file if available
    const videoUrl = file ? URL.createObjectURL(file) : null

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
                <h2 className="text-3xl font-bold text-white">
                    Detection Result
                </h2>
            </div>

            {/* Main Results Card with Split Layout */}
            <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                    {/* LEFT COLUMN: Stats & Details */}
                    <div className="space-y-6">
                        {/* Status */}
                        <div>
                            <h3 className="text-sm font-medium text-gray-400 mb-2">
                                Detection Result
                            </h3>
                            <StatusBadge status={result.status} confidence={result.confidence} />
                        </div>

                        {/* Confidence Score */}
                        <div>
                            <h3 className="text-sm font-medium text-gray-400 mb-3">
                                Confidence Score
                            </h3>
                            <div className="relative pt-1">
                                <div className="flex items-center justify-between mb-2">
                                    <span className="text-2xl font-bold text-white">
                                        {(result.confidence * 100).toFixed(1)}%
                                    </span>
                                    <span className="text-sm text-gray-400">
                                        {result.confidence >= 0.8 ? 'High' : result.confidence >= 0.5 ? 'Medium' : 'Low'}
                                    </span>
                                </div>
                                <div className="w-full bg-gray-700 rounded-full h-3">
                                    <div
                                        className={`h-full rounded-full transition-all duration-500 ${result.confidence >= 0.8
                                            ? 'bg-gradient-to-r from-green-400 to-green-600'
                                            : result.confidence >= 0.5
                                                ? 'bg-gradient-to-r from-yellow-400 to-yellow-600'
                                                : 'bg-gradient-to-r from-red-400 to-red-600'
                                            }`}
                                        style={{ width: `${result.confidence * 100}%` }}
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Details Grid */}
                        {result.details && (
                            <div className="grid grid-cols-2 gap-4 pt-4 border-t border-slate-600">
                                <DetailItem
                                    label="Spatial Features"
                                    value={result.details.spatialFeatures}
                                />
                                <DetailItem
                                    label="Temporal Features"
                                    value={result.details.temporalFeatures}
                                />
                                <DetailItem
                                    label="Frame Count"
                                    value={result.details.frameCount}
                                />
                                <DetailItem
                                    label="Duration"
                                    value={result.details.duration}
                                />
                            </div>
                        )}

                        {/* Timestamp */}
                        <div className="pt-4 border-t border-slate-600">
                            <p className="text-xs text-gray-500">
                                Analyzed at: {formatTimestamp(result.timestamp)}
                            </p>
                        </div>
                    </div>

                    {/* RIGHT COLUMN: Visuals (Video + Frames) */}
                    <div className="space-y-6">
                        {/* Uploaded Video */}
                        <div className="space-y-2">
                            <h3 className="text-sm font-medium text-gray-400">Uploaded Video</h3>
                            <div className="relative bg-black rounded-lg overflow-hidden border border-slate-700 w-full h-48 flex items-center justify-center">
                                {videoUrl ? (
                                    <video
                                        src={videoUrl}
                                        controls
                                        className="w-full h-full object-cover"
                                    >
                                        Your browser does not support the video tag.
                                    </video>
                                ) : (
                                    <div className="text-gray-500 text-sm">
                                        Video preview unavailable
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* Accident Frames Sequence */}
                        {result.status === 'accident' && result.details?.accidentFrameUrls?.length > 0 && (
                            <div className="space-y-2">
                                <h3 className="text-sm font-medium text-gray-400">Accident Sequence</h3>
                                <div className="grid grid-cols-5 gap-2">
                                    {result.details.accidentFrameUrls.map((url, idx) => (
                                        <div key={idx} className="relative cursor-pointer" onClick={() => setZoomedImage(`${import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'}${url}`)}>
                                            <img 
                                                src={`${import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'}${url}`}
                                                alt={`Frame ${idx + 1}`}
                                                className={`w-full h-auto rounded border-2 hover:opacity-80 transition-opacity ${
                                                    idx === 2 ? 'border-red-500' : 'border-slate-600'
                                                }`}
                                            />
                                            <span className="absolute bottom-1 right-1 bg-black/70 text-white text-xs px-1 rounded">
                                                {idx === 0 ? '-2' : idx === 1 ? '-1' : idx === 2 ? 'Impact' : idx === 3 ? '+1' : '+2'}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}
                    </div>
                </div>
            </div>

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button onClick={onViewExplanation} variant="primary">
                    View AI Explanation
                </Button>
                <Button onClick={onReset} variant="secondary">
                    Analyze Another Video
                </Button>
            </div>

            {/* Zoom Modal */}
            {zoomedImage && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/90 p-4" onClick={() => setZoomedImage(null)}>
                    <div className="relative max-w-7xl max-h-full">
                        <img src={zoomedImage} alt="Zoomed frame" className="max-w-full max-h-[90vh] object-contain" />
                        <button className="absolute top-4 right-4 text-white bg-red-600 hover:bg-red-700 rounded-full w-10 h-10 flex items-center justify-center text-xl font-bold" onClick={() => setZoomedImage(null)}>
                            ×
                        </button>
                    </div>
                </div>
            )}
        </div>
    )
}

const DetailItem = ({ label, value }) => (
    <div>
        <p className="text-xs font-medium text-gray-400 mb-1">
            {label}
        </p>
        <p className="text-sm text-white font-medium">
            {value}
        </p>
    </div>
)

export default ResultState
