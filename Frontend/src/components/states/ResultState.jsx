import Button from '../ui/Button'
import StatusBadge from '../ui/StatusBadge'
import { formatTimestamp } from '../../utils/formatters'

const ResultState = ({ result, onViewExplanation, onReset }) => {
    if (!result) {
        return (
            <div className="text-center">
                <p className="text-gray-600 dark:text-gray-400">No results available</p>
            </div>
        )
    }

    return (
        <div className="space-y-8">
            {/* Header */}
            <div className="text-center space-y-4">
                <h2 className="text-3xl font-bold text-gray-900 dark:text-white">
                    Analysis Complete
                </h2>
            </div>

            {/* Results Card */}
            <div className="bg-slate-800/50 rounded-xl p-8 border border-slate-700">
                <div className="space-y-6">
                    {/* Status */}
                    <div>
                        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
                            Detection Result
                        </h3>
                        <StatusBadge status={result.status} confidence={result.confidence} />
                    </div>

                    {/* Confidence Score */}
                    <div>
                        <h3 className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-3">
                            Confidence Score
                        </h3>
                        <div className="relative pt-1">
                            <div className="flex items-center justify-between mb-2">
                                <span className="text-2xl font-bold text-gray-900 dark:text-white">
                                    {(result.confidence * 100).toFixed(1)}%
                                </span>
                                <span className="text-sm text-gray-500 dark:text-gray-400">
                                    {result.confidence >= 0.8 ? 'High' : result.confidence >= 0.5 ? 'Medium' : 'Low'}
                                </span>
                            </div>
                            <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-3">
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

                    {/* Details */}
                    {result.details && (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-4 border-t border-slate-600">
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
                        <p className="text-xs text-gray-500 dark:text-gray-500">
                            Analyzed at: {formatTimestamp(result.timestamp)}
                        </p>
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
        </div>
    )
}

const DetailItem = ({ label, value }) => (
    <div>
        <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
            {label}
        </p>
        <p className="text-sm text-gray-900 dark:text-white font-medium">
            {value}
        </p>
    </div>
)

export default ResultState
