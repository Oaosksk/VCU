import FileDropzone from '../ui/FileDropzone'
import { validateVideoFile } from '../../utils/fileValidation'
import { FILE_CONFIG } from '../../utils/constants'

const UploadState = ({ onFileUpload, showToast }) => {
    const handleFileSelect = (file) => {
        const validation = validateVideoFile(file)

        if (!validation.valid) {
            // Use toast notification instead of alert
            if (showToast) {
                showToast(validation.error, 'error')
            } else {
                alert(validation.error)
            }
            return
        }

        onFileUpload(file)
    }

    return (
        <div className="text-center space-y-8">
            {/* Header */}
            <div className="space-y-3">
                <h2 className="text-3xl font-bold text-white">
                    Upload Video for Analysis
                </h2>
                <p className="text-gray-400 max-w-2xl mx-auto">
                    Upload a traffic video to detect potential accidents using our advanced
                    spatio-temporal deep learning model
                </p>
            </div>

            {/* Dropzone */}
            <FileDropzone
                onFileSelect={handleFileSelect}
                accept="video/mp4,video/avi,video/quicktime"
                maxSize={FILE_CONFIG.MAX_SIZE}
            />
        </div>
    )
}

export default UploadState
