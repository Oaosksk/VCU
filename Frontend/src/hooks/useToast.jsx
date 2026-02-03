import { useState, useCallback } from 'react'
import { TOAST_TYPES } from '../utils/constants'

export const useToast = () => {
    const [toasts, setToasts] = useState([])

    const showToast = useCallback((message, type = TOAST_TYPES.INFO, duration = 3000) => {
        const id = Date.now()
        const toast = { id, message, type }

        setToasts(prev => [...prev, toast])

        setTimeout(() => {
            setToasts(prev => prev.filter(t => t.id !== id))
        }, duration)
    }, [])

    const removeToast = useCallback((id) => {
        setToasts(prev => prev.filter(t => t.id !== id))
    }, [])

    const ToastContainer = () => (
        <div className="fixed top-4 right-4 z-50 space-y-2">
            {toasts.map(toast => (
                <Toast
                    key={toast.id}
                    message={toast.message}
                    type={toast.type}
                    onClose={() => removeToast(toast.id)}
                />
            ))}
        </div>
    )

    return { showToast, ToastContainer }
}

const Toast = ({ message, type, onClose }) => {
    const getToastStyles = () => {
        switch (type) {
            case TOAST_TYPES.SUCCESS:
                return 'bg-green-500 text-white'
            case TOAST_TYPES.ERROR:
                return 'bg-red-500 text-white'
            case TOAST_TYPES.WARNING:
                return 'bg-yellow-500 text-white'
            default:
                return 'bg-blue-500 text-white'
        }
    }

    const getIcon = () => {
        switch (type) {
            case TOAST_TYPES.SUCCESS:
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                )
            case TOAST_TYPES.ERROR:
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                )
            case TOAST_TYPES.WARNING:
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                )
            default:
                return (
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                )
        }
    }

    return (
        <div className={`${getToastStyles()} px-6 py-4 rounded-lg shadow-lg flex items-center gap-3 min-w-[300px] animate-slide-up`}>
            <span className="flex-shrink-0">{getIcon()}</span>
            <p className="flex-1 font-medium">{message}</p>
            <button
                onClick={onClose}
                className="text-white hover:text-gray-200 transition-colors flex-shrink-0"
                aria-label="Close notification"
            >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
            </button>
        </div>
    )
}
