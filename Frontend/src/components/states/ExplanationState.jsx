import { useState, useEffect } from 'react'
import Button from '../ui/Button'
import StatusBadge from '../ui/StatusBadge'
import { getMockExplanation } from '../../services/api'

const ExplanationState = ({ result, onBack, onReset }) => {
    const [explanation, setExplanation] = useState('')
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        const fetchExplanation = async () => {
            setIsLoading(true)
            try {
                const response = await getMockExplanation()
                if (response.success) {
                    setExplanation(response.explanation)
                }
            } catch (error) {
                console.error('Failed to fetch explanation:', error)
                setExplanation('Failed to load explanation. Please try again.')
            } finally {
                setIsLoading(false)
            }
        }

        fetchExplanation()
    }, [result])

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                    AI Explanation
                </h2>
                <p className="text-gray-600 dark:text-gray-400">
                    Understanding the analysis results
                </p>
            </div>

            {/* Result Summary */}
            <div className="bg-slate-800/50 rounded-lg p-6 border border-slate-700">
                <div className="flex items-center justify-between">
                    <StatusBadge status={result?.status} confidence={result?.confidence} />
                    <span className="text-sm text-gray-500 dark:text-gray-400">
                        Result ID: {result?.id}
                    </span>
                </div>
            </div>

            {/* Explanation Content */}
            <div className="bg-slate-800 rounded-xl p-8 border border-slate-700 shadow-sm">
                {isLoading ? (
                    <div className="text-center py-12">
                        <div className="inline-block w-12 h-12 border-4 border-blue-500 border-t-transparent rounded-full spinner mb-4" />
                        <p className="text-gray-600 dark:text-gray-400">
                            Generating AI explanation...
                        </p>
                    </div>
                ) : (
                    <div className="space-y-6 text-gray-300 leading-relaxed">
                        {explanation.split('\n\n').map((section, index) => {
                            const lines = section.split('\n')
                            const title = lines[0]
                            const content = lines.slice(1).join(' ')
                            
                            if (index === 0) {
                                return <p key={index} className="text-base">{section}</p>
                            }
                            
                            return (
                                <div key={index}>
                                    <h4 className="text-lg font-semibold text-white mb-2">{title}</h4>
                                    <p className="text-base">{content}</p>
                                </div>
                            )
                        })}
                    </div>
                )}
            </div>

            {/* Technical Details */}
            {!isLoading && result?.details && (
                <div className="bg-slate-800/50 rounded-xl p-6 border border-slate-700">
                    <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
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
                        Technical Details
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <TechnicalDetail
                            label="Model Architecture"
                            value="Hybrid CNN-LSTM"
                        />
                        <TechnicalDetail
                            label="Backbone"
                            value="ResNet-50"
                        />
                        <TechnicalDetail
                            label="Frames Analyzed"
                            value={result.details.frameCount}
                        />
                        <TechnicalDetail
                            label="Processing Time"
                            value={result.details.duration}
                        />
                    </div>
                </div>
            )}

            {/* Actions */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
                <Button onClick={onBack} variant="secondary">
                    ← Back to Results
                </Button>
                <Button onClick={onReset} variant="primary">
                    Analyze Another Video
                </Button>
            </div>
        </div>
    )
}

const TechnicalDetail = ({ label, value }) => (
    <div className="flex items-center gap-3">
        <div className="w-2 h-2 bg-blue-500 rounded-full" />
        <div>
            <p className="text-xs text-gray-400">{label}</p>
            <p className="text-sm font-semibold text-white">{value}</p>
        </div>
    </div>
)

export default ExplanationState
