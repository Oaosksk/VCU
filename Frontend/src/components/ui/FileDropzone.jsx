import { useState, useRef } from 'react'
import { formatFileSize } from '../../utils/fileValidation'

const FileDropzone = ({ onFileSelect, accept, maxSize }) => {
    const [isDragging, setIsDragging] = useState(false)
    const [selectedFile, setSelectedFile] = useState(null)
    const fileInputRef = useRef(null)

    const handleDragOver = (e) => { e.preventDefault(); setIsDragging(true) }
    const handleDragLeave = (e) => { e.preventDefault(); setIsDragging(false) }
    const handleDrop = (e) => {
        e.preventDefault(); setIsDragging(false)
        const files = e.dataTransfer.files
        if (files.length > 0) { setSelectedFile(files[0]); onFileSelect(files[0]) }
    }
    const handleFileInput = (e) => {
        const files = e.target.files
        if (files.length > 0) { setSelectedFile(files[0]); onFileSelect(files[0]) }
    }

    return (
        <div
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
            onClick={() => fileInputRef.current?.click()}
            style={{
                border: `2px dashed ${isDragging ? '#38bdf8' : 'rgba(148, 163, 184, 0.18)'}`,
                borderRadius: '20px',
                padding: '56px 32px',
                textAlign: 'center',
                cursor: 'pointer',
                transition: 'all 0.3s ease',
                background: isDragging
                    ? 'rgba(56, 189, 248, 0.06)'
                    : 'rgba(15, 23, 42, 0.4)',
                boxShadow: isDragging ? '0 0 40px rgba(56, 189, 248, 0.12), inset 0 0 40px rgba(56, 189, 248, 0.04)' : 'none',
                position: 'relative',
                overflow: 'hidden',
            }}
        >
            <input ref={fileInputRef} type="file" accept={accept} onChange={handleFileInput} style={{ display: 'none' }} />

            {/* Animated corner accents when dragging */}
            {isDragging && (
                <>
                    {['topLeft', 'topRight', 'bottomLeft', 'bottomRight'].map((pos) => (
                        <div key={pos} style={{
                            position: 'absolute',
                            width: 24, height: 24,
                            borderColor: '#38bdf8',
                            borderStyle: 'solid',
                            borderWidth: 0,
                            ...(pos === 'topLeft' ? { top: 12, left: 12, borderTopWidth: 2, borderLeftWidth: 2, borderTopLeftRadius: 6 } :
                                pos === 'topRight' ? { top: 12, right: 12, borderTopWidth: 2, borderRightWidth: 2, borderTopRightRadius: 6 } :
                                    pos === 'bottomLeft' ? { bottom: 12, left: 12, borderBottomWidth: 2, borderLeftWidth: 2, borderBottomLeftRadius: 6 } :
                                        { bottom: 12, right: 12, borderBottomWidth: 2, borderRightWidth: 2, borderBottomRightRadius: 6 })
                        }} />
                    ))}
                </>
            )}

            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '20px' }}>
                {/* Icon */}
                <div style={{
                    width: 72, height: 72, borderRadius: '20px',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    background: isDragging
                        ? 'linear-gradient(135deg, rgba(56,189,248,0.25), rgba(99,102,241,0.25))'
                        : 'rgba(30, 41, 59, 0.8)',
                    border: `1px solid ${isDragging ? 'rgba(56,189,248,0.4)' : 'rgba(148,163,184,0.1)'}`,
                    transition: 'all 0.3s ease',
                    boxShadow: isDragging ? '0 0 30px rgba(56,189,248,0.2)' : 'none',
                }}>
                    <svg width="34" height="34" viewBox="0 0 24 24" fill="none"
                        stroke={isDragging ? '#38bdf8' : 'rgba(148,163,184,0.6)'}
                        strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"
                        style={{ transition: 'stroke 0.3s' }}>
                        <polyline points="16 16 12 12 8 16" />
                        <line x1="12" y1="12" x2="12" y2="21" />
                        <path d="M20.39 18.39A5 5 0 0018 9h-1.26A8 8 0 103 16.3" />
                    </svg>
                </div>

                {/* Text */}
                <div>
                    <p style={{
                        margin: '0 0 6px', fontSize: '1.05rem', fontWeight: 700,
                        color: isDragging ? '#38bdf8' : 'white',
                        transition: 'color 0.3s',
                    }}>
                        {isDragging ? 'Release to upload' : 'Drop your video here'}
                    </p>
                    <p style={{ margin: 0, fontSize: '0.82rem', color: 'rgba(148,163,184,0.5)' }}>
                        or click to browse files
                    </p>
                </div>

                {/* CTA button */}
                <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: '8px',
                    padding: '10px 24px', borderRadius: '12px',
                    background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
                    color: 'white', fontSize: '0.85rem', fontWeight: 600,
                    boxShadow: '0 0 20px rgba(14,165,233,0.25)',
                    pointerEvents: 'none',
                }}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                        <path d="M21 15v4a2 2 0 01-2 2H5a2 2 0 01-2-2v-4" />
                        <polyline points="17 8 12 3 7 8" /><line x1="12" y1="3" x2="12" y2="15" />
                    </svg>
                    Select Video
                </div>

                {/* Format + size info */}
                <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', justifyContent: 'center' }}>
                    {['MP4', 'AVI', 'MOV', 'MKV'].map(fmt => (
                        <span key={fmt} style={{
                            padding: '3px 10px', borderRadius: '6px', fontSize: '0.7rem', fontWeight: 700,
                            background: 'rgba(56,189,248,0.08)', color: 'rgba(56,189,248,0.6)',
                            border: '1px solid rgba(56,189,248,0.12)', letterSpacing: '0.06em',
                        }}>{fmt}</span>
                    ))}
                    {maxSize && (
                        <span style={{ fontSize: '0.72rem', color: 'rgba(148,163,184,0.35)', alignSelf: 'center' }}>
                            Max {formatFileSize(maxSize)}
                        </span>
                    )}
                </div>
            </div>
        </div>
    )
}

export default FileDropzone
