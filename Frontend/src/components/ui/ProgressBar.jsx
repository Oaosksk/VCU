const ProgressBar = ({ progress, label, showPercentage = true }) => {
    return (
        <div className="w-full">
            {label && (
                <div className="flex justify-between items-center mb-2">
                    <span className="text-sm font-medium text-gray-300">
                        {label}
                    </span>
                    {showPercentage && (
                        <span className="text-sm font-semibold text-blue-400">
                            {progress}%
                        </span>
                    )}
                </div>
            )}
            <div className="w-full bg-slate-700 rounded-full h-2.5 overflow-hidden">
                <div
                    className="bg-gradient-to-r from-blue-500 to-blue-600 h-full rounded-full transition-all duration-300 ease-out"
                    style={{ width: `${progress}%` }}
                />
            </div>
        </div>
    )
}

export default ProgressBar
