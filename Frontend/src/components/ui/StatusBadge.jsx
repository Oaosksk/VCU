import { STATUS_TYPES } from '../../utils/constants'

const StatusBadge = ({ status, confidence }) => {
    const getStatusConfig = () => {
        switch (status) {
            case STATUS_TYPES.ACCIDENT:
                return {
                    label: 'Accident Detected',
                    className: 'badge badge-danger',
                    icon: (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                        </svg>
                    )
                }
            case STATUS_TYPES.NO_ACCIDENT:
                return {
                    label: 'No Accident',
                    className: 'badge badge-success',
                    icon: (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M5 13l4 4L19 7" />
                        </svg>
                    )
                }
            case STATUS_TYPES.UNCERTAIN:
                return {
                    label: 'Uncertain',
                    className: 'badge badge-warning',
                    icon: (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" strokeWidth={1.5} />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 8v4m0 4h.01" />
                        </svg>
                    )
                }
            default:
                return {
                    label: 'Unknown',
                    className: 'badge badge-info',
                    icon: (
                        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <circle cx="12" cy="12" r="10" strokeWidth={1.5} />
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 11v5m0-8h.01" />
                        </svg>
                    )
                }
        }
    }

    const config = getStatusConfig()

    return (
        <div className="flex items-center gap-3">
            <span className={config.className}>
                <span className="mr-1">{config.icon}</span>
                {config.label}
            </span>
            {confidence !== undefined && (
                <span className="text-sm text-gray-400">
                    {(confidence * 100).toFixed(1)}% confidence
                </span>
            )}
        </div>
    )
}

export default StatusBadge
