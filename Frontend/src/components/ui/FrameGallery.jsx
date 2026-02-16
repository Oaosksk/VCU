import { useState } from 'react'

const FrameGallery = ({ frameUrls, totalCount, baseUrl, compact = false }) => {
    const [selectedFrame, setSelectedFrame] = useState(null)

    if (!frameUrls || frameUrls.length === 0) {
        return null
    }

    const fullUrls = frameUrls.map(url => `${baseUrl}${url}`)

    return (
        <div className={compact ? "space-y-2" : "space-y-4"}>
            {/* Header - Only hide if compact is true */}
            {!compact && (
                <div className="flex items-center justify-between">
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
                                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
                            />
                        </svg>
                        Accident Frames
                    </h3>
                    <span className="text-sm text-gray-400">
                        Showing {frameUrls.length} of {totalCount} frames
                    </span>
                </div>
            )}

            {/* Frame Grid */}
            <div className={`grid gap-2 ${compact ? 'grid-cols-5' : 'grid-cols-2 sm:grid-cols-3 md:grid-cols-5'}`}>
                {fullUrls.map((url, index) => (
                    <div
                        key={index}
                        className="relative aspect-video bg-slate-800 rounded-lg overflow-hidden border-2 border-slate-700 hover:border-blue-500 transition-all cursor-pointer group"
                        onClick={() => setSelectedFrame(url)}
                    >
                        <img
                            src={url}
                            alt={`Accident frame ${index + 1}`}
                            className="w-full h-full object-cover group-hover:scale-105 transition-transform"
                            loading="lazy"
                        />
                        <div className="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                            <svg
                                className="w-8 h-8 text-white"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0zM10 7v3m0 0v3m0-3h3m-3 0H7"
                                />
                            </svg>
                        </div>
                        <div className="absolute bottom-1 right-1 bg-black/70 text-white text-xs px-2 py-0.5 rounded">
                            #{index + 1}
                        </div>
                    </div>
                ))}
            </div>

            {/* Lightbox Modal */}
            {selectedFrame && (
                <div
                    className="fixed inset-0 bg-black/90 z-50 flex items-center justify-center p-4"
                    onClick={() => setSelectedFrame(null)}
                >
                    <div className="relative max-w-5xl w-full">
                        {/* Close button */}
                        <button
                            className="absolute top-4 right-4 text-white hover:text-gray-300 bg-black/50 rounded-full p-2"
                            onClick={() => setSelectedFrame(null)}
                        >
                            <svg
                                className="w-6 h-6"
                                fill="none"
                                stroke="currentColor"
                                viewBox="0 0 24 24"
                            >
                                <path
                                    strokeLinecap="round"
                                    strokeLinejoin="round"
                                    strokeWidth={2}
                                    d="M6 18L18 6M6 6l12 12"
                                />
                            </svg>
                        </button>

                        {/* Image */}
                        <img
                            src={selectedFrame}
                            alt="Accident frame enlarged"
                            className="w-full h-auto rounded-lg"
                            onClick={(e) => e.stopPropagation()}
                        />
                    </div>
                </div>
            )}
        </div>
    )
}

export default FrameGallery
