import { useState } from 'react'
import './App.css'
import Navbar from './components/layout/Navbar'
import MainCard from './components/layout/MainCard'
import UploadState from './components/states/UploadState'
import ProcessingState from './components/states/ProcessingState'
import ResultState from './components/states/ResultState'
import ExplanationState from './components/states/ExplanationState'
import ErrorState from './components/states/ErrorState'
import { useToast } from './hooks/useToast.jsx'
import { useVideoUpload } from './hooks/useVideoUpload'
import { APP_STATES } from './utils/constants'

function App() {
    const [currentState, setCurrentState] = useState(APP_STATES.UPLOAD)
    const [uploadedFile, setUploadedFile] = useState(null)
    const [analysisResult, setAnalysisResult] = useState(null)
    const [error, setError] = useState(null)
    const { showToast, ToastContainer } = useToast()
    const { uploadAndAnalyze } = useVideoUpload()

    const handleFileUpload = async (file) => {
        setUploadedFile(file)
        setCurrentState(APP_STATES.PROCESSING)
        showToast('Uploading video...', 'info')
        
        // Call real API
        await uploadAndAnalyze(
            file,
            (result) => {
                setAnalysisResult(result)
                setCurrentState(APP_STATES.RESULT)
                showToast('Analysis completed successfully!', 'success')
            },
            (errorMsg) => {
                setError(errorMsg)
                setCurrentState(APP_STATES.ERROR)
                showToast(errorMsg, 'error')
            }
        )
    }

    const handleViewExplanation = () => {
        setCurrentState(APP_STATES.EXPLANATION)
    }

    const handleError = (errorMessage) => {
        setError(errorMessage)
        setCurrentState(APP_STATES.ERROR)
        showToast(errorMessage, 'error')
    }

    const handleReset = () => {
        setCurrentState(APP_STATES.UPLOAD)
        setUploadedFile(null)
        setAnalysisResult(null)
        setError(null)
    }

    const handleRetry = () => {
        if (uploadedFile) {
            setCurrentState(APP_STATES.PROCESSING)
            setError(null)
        } else {
            handleReset()
        }
    }

    const renderCurrentState = () => {
        switch (currentState) {
            case APP_STATES.UPLOAD:
                return <UploadState onFileUpload={handleFileUpload} />

            case APP_STATES.PROCESSING:
                return (
                    <ProcessingState
                        fileName={uploadedFile?.name}
                        onComplete={() => {}} // Handled by uploadAndAnalyze callback
                        onError={() => {}} // Handled by uploadAndAnalyze callback
                    />
                )

            case APP_STATES.RESULT:
                return (
                    <ResultState
                        result={analysisResult}
                        onViewExplanation={handleViewExplanation}
                        onReset={handleReset}
                    />
                )

            case APP_STATES.EXPLANATION:
                return (
                    <ExplanationState
                        result={analysisResult}
                        onBack={() => setCurrentState(APP_STATES.RESULT)}
                        onReset={handleReset}
                    />
                )

            case APP_STATES.ERROR:
                return (
                    <ErrorState
                        error={error}
                        onRetry={handleRetry}
                        onReset={handleReset}
                    />
                )

            default:
                return <UploadState onFileUpload={handleFileUpload} />
        }
    }

    return (
        <div className="app-container">
            <Navbar />

            <main className="main-content">
                <MainCard>
                    {renderCurrentState()}
                </MainCard>
            </main>

            <ToastContainer />
        </div>
    )
}

export default App
