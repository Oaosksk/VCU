const Button = ({
    children,
    onClick,
    variant = 'primary',
    disabled = false,
    className = '',
    ...props
}) => {
    const baseStyles = 'font-medium px-6 py-3 rounded-lg transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed'

    const variants = {
        primary: 'btn-primary',
        secondary: 'btn-secondary',
        outline: 'border-2 border-accent-primary text-accent-primary hover:bg-accent-primary hover:text-white',
        danger: 'bg-red-500 hover:bg-red-600 text-white',
    }

    return (
        <button
            onClick={onClick}
            disabled={disabled}
            className={`${baseStyles} ${variants[variant]} ${className}`}
            {...props}
        >
            {children}
        </button>
    )
}

export default Button
