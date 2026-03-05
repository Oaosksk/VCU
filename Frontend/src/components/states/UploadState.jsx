import FileDropzone from '../ui/FileDropzone'
import { validateVideoFile } from '../../utils/fileValidation'
import { FILE_CONFIG } from '../../utils/constants'

const UploadState = ({ onFileUpload, showToast }) => {
    const handleFileSelect = (file) => {
        const validation = validateVideoFile(file)
        if (!validation.valid) {
            showToast ? showToast(validation.error, 'error') : alert(validation.error)
            return
        }
        onFileUpload(file)
    }

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '40px', animation: 'fadeIn 0.4s ease' }}>
            {/* Header */}
            <div style={{ textAlign: 'center' }}>
                <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: '8px',
                    padding: '6px 16px', marginBottom: '20px',
                    background: 'rgba(56, 189, 248, 0.08)',
                    border: '1px solid rgba(56, 189, 248, 0.2)',
                    borderRadius: '999px',
                    fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.1em',
                    textTransform: 'uppercase', color: '#38bdf8',
                }}>
                    <span style={{ width: 6, height: 6, borderRadius: '50%', background: '#38bdf8', boxShadow: '0 0 8px #38bdf8' }} />
                    AI-Powered Detection
                </div>
                <h2 style={{
                    fontSize: '2.2rem', fontWeight: 900, color: 'white', margin: '0 0 12px',
                    letterSpacing: '-0.03em',
                    backgroundImage: 'linear-gradient(135deg, #ffffff 0%, rgba(56,189,248,0.9) 100%)',
                    WebkitBackgroundClip: 'text', backgroundClip: 'text', WebkitTextFillColor: 'transparent',
                }}>
                    Upload Traffic Video
                </h2>
                <p style={{ margin: 0, color: 'rgba(148, 163, 184, 0.7)', maxWidth: '520px', marginInline: 'auto', lineHeight: 1.6, fontSize: '0.92rem' }}>
                    Detect accidents instantly using our YOLOv8 + LSTM spatio-temporal deep learning pipeline
                </p>
            </div>

            {/* Dropzone */}
            <FileDropzone
                onFileSelect={handleFileSelect}
                accept="video/mp4,video/avi,video/quicktime,video/x-matroska"
                maxSize={FILE_CONFIG.MAX_SIZE}
            />

            {/* Feature chips */}
            <div style={{ display: 'flex', justifyContent: 'center', flexWrap: 'wrap', gap: '10px' }}>
                {[
                    { icon: '⚡', label: 'Real-time Analysis' },
                    { icon: '🎯', label: 'YOLOv8 + LSTM' },
                    { icon: '🔒', label: 'Secure Processing' },
                    { icon: '🧠', label: 'AI Explanation' },
                ].map(({ icon, label }) => (
                    <span key={label} style={{
                        display: 'inline-flex', alignItems: 'center', gap: '6px',
                        padding: '7px 16px', borderRadius: '999px', fontSize: '0.78rem', fontWeight: 500,
                        background: 'rgba(15, 23, 42, 0.6)',
                        border: '1px solid rgba(148, 163, 184, 0.1)',
                        color: 'rgba(148, 163, 184, 0.7)',
                    }}>
                        <span>{icon}</span> {label}
                    </span>
                ))}
            </div>
        </div>
    )
}

export default UploadState
