import { useState, useEffect } from 'react'
import ProgressBar from '../ui/ProgressBar'
import { PROCESSING_STAGES } from '../../utils/constants'
import { useVideoUpload } from '../../hooks/useVideoUpload'

const ProcessingState = ({ fileName, onComplete, onError }) => {
    const [currentStage, setCurrentStage] = useState(0)
    const [progress, setProgress] = useState(0)
    const { uploadAndAnalyze, uploadProgress } = useVideoUpload()

    useEffect(() => {
        let stageIndex = 0

        const processStages = async () => {
            for (const stage of PROCESSING_STAGES) {
                setCurrentStage(stageIndex)

                // Animate progress for this stage
                const startProgress = (stageIndex / PROCESSING_STAGES.length) * 100
                const endProgress = ((stageIndex + 1) / PROCESSING_STAGES.length) * 100

                await animateProgress(startProgress, endProgress, stage.duration)
                stageIndex++
            }

            // Complete processing - trigger callback
            setProgress(100)
        }

        processStages()
    }, [onComplete, onError])

    const animateProgress = (start, end, duration) => {
        return new Promise((resolve) => {
            const startTime = Date.now()
            const range = end - start

            const updateProgress = () => {
                const elapsed = Date.now() - startTime
                const progress = Math.min(elapsed / duration, 1)
                const currentProgress = start + (range * progress)

                setProgress(currentProgress)

                if (progress < 1) {
                    requestAnimationFrame(updateProgress)
                } else {
                    resolve()
                }
            }

            updateProgress()
        })
    }

    return (
        <div className="text-center space-y-8">
            {/* Header */}
            <div className="space-y-3">
                <div className="w-20 h-20 mx-auto bg-blue-600 rounded-full flex items-center justify-center pulse-ring">
                    <svg
                        className="w-10 h-10 text-white spinner"
                        fill="none"
                        stroke="currentColor"
                        viewBox="0 0 24 24"
                    >
                        <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
                        />
                    </svg>
                </div>

                <h2 className="text-3xl font-bold text-white">
                    Analyzing Video
                </h2>
                <p className="text-gray-400">
                    Processing: <span className="font-semibold">{fileName}</span>
                </p>
            </div>

            {/* Progress Bar */}
            <div className="max-w-md mx-auto">
                <ProgressBar progress={Math.round(progress)} />
            </div>

            {/* Current Stage */}
            <div className="space-y-4">
                <p className="text-lg font-semibold text-blue-400">
                    {PROCESSING_STAGES[currentStage]?.name}
                </p>

                {/* Stage Timeline - Horizontal */}
                <div className="max-w-4xl mx-auto px-8">
                    <div className="flex items-start justify-center gap-8 relative">
                        {PROCESSING_STAGES.map((stage, index) => (
                            <div key={stage.id} className="flex flex-col items-center relative">
                                {/* Stage item */}
                                <div className="relative z-10">
                                    {/* Stage number/icon */}
                                    <div className={`
                                        w-12 h-12 rounded-full flex items-center justify-center text-sm font-bold transition-all duration-300
                                        ${index === currentStage
                                            ? 'bg-blue-600 text-white ring-4 ring-blue-500/30 scale-110'
                                            : index < currentStage
                                                ? 'bg-green-500 text-white'
                                                : 'bg-slate-700 text-gray-400'
                                        }
                                    `}>
                                        {index < currentStage ? (
                                            <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                                                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                                            </svg>
                                        ) : (
                                            index + 1
                                        )}
                                    </div>
                                </div>

                                {/* Stage name */}
                                <span className={`
                                    mt-3 text-xs font-medium text-center transition-colors duration-300 max-w-[100px]
                                    ${index === currentStage
                                        ? 'text-blue-400 font-semibold'
                                        : index < currentStage
                                            ? 'text-green-400'
                                            : 'text-gray-500'
                                    }
                                `}>
                                    {stage.name}
                                </span>

                                {/* Timeline connector line - only between stages */}
                                {index < PROCESSING_STAGES.length - 1 && (
                                    <div
                                        className={`absolute top-6 left-full h-0.5 w-8 border-t-2 border-dashed transition-colors duration-300 ${index < currentStage
                                            ? 'border-green-500'
                                            : 'border-slate-600'
                                            }`}
                                        style={{ transform: 'translateY(-50%)' }}
                                    />
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>

            {/* Info */}
            <p className="text-sm text-gray-500">
                This may take a few moments. Please do not close this window.
            </p>
        </div>
    )
}

export default ProcessingState
