import { useState, useRef } from 'react'
import { formatFileSize } from '../../utils/fileValidation'

const FileDropzone = ({ onFileSelect, accept, maxSize }) => {
    const [isDragging, setIsDragging] = useState(false)
    const fileInputRef = useRef(null)

    const handleDragOver = (e) => {
        e.preventDefault()
        setIsDragging(true)
    }

    const handleDragLeave = (e) => {
        e.preventDefault()
        setIsDragging(false)
    }

    const handleDrop = (e) => {
        e.preventDefault()
        setIsDragging(false)

        const files = e.dataTransfer.files
        if (files.length > 0) {
            onFileSelect(files[0])
        }
    }

    const handleFileInput = (e) => {
        const files = e.target.files
        if (files.length > 0) {
            onFileSelect(files[0])
        }
    }

    const handleClick = () => {
        fileInputRef.current?.click()
    }

    return (
        <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={handleClick}
            className={`
        border-2 border-dashed rounded-xl p-12 text-center cursor-pointer
        transition-all duration-300
        ${isDragging
                    ? 'border-blue-500 bg-blue-500/10'
                    : 'border-slate-600 hover:border-blue-500 hover:bg-slate-800/50'
                }
      `}
        >
            <input
                ref={fileInputRef}
                type="file"
                accept={accept}
                onChange={handleFileInput}
                className="hidden"
            />

            <div className="flex flex-col items-center gap-4">
                {/* Upload Icon */}
                <div className={`
          w-16 h-16 rounded-full flex items-center justify-center
          ${isDragging
                        ? 'bg-blue-600 text-white'
                        : 'bg-slate-800 text-gray-400'
                    }
          transition-all duration-300
        `}>
                    <svg
                        className="w-8 h-8"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12"
                        />
                    </svg>
                </div>

                {/* Text */}
                <div>
                    <p className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                        {isDragging ? 'Drop video here' : 'Drop video here or click to browse'}
                    </p>
                    <p className="text-sm text-gray-500 dark:text-gray-400">
                        Supported formats: MP4, AVI, MOV
                    </p>
                    {maxSize && (
                        <p className="text-xs text-gray-400 dark:text-gray-500 mt-1">
                            Maximum file size: {formatFileSize(maxSize)}
                        </p>
                    )}
                </div>

                {/* Upload Button Visual */}
                <div className="mt-2">
                    <span className="inline-flex items-center px-4 py-2 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors">
                        <svg
                            className="w-5 h-5 mr-2"
                            fill="none"
                            stroke="currentColor"
                            viewBox="0 0 24 24"
                        >
                            <path
                                strokeLinecap="round"
                                strokeLinejoin="round"
                                strokeWidth={2}
                                d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
                            />
                        </svg>
                        Select Video
                    </span>
                </div>
            </div>
        </div>
    )
}

export default FileDropzone
