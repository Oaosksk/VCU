const MainCard = ({ children }) => {
    return (
        <div style={{ width: '100%', maxWidth: '1100px', margin: '0 auto', padding: '32px 24px' }}>
            <div style={{
                background: 'rgba(10, 18, 35, 0.85)',
                border: '1px solid rgba(56, 189, 248, 0.1)',
                borderRadius: '24px',
                backdropFilter: 'blur(24px)',
                WebkitBackdropFilter: 'blur(24px)',
                padding: '48px',
                boxShadow: '0 0 0 1px rgba(56,189,248,0.04), 0 24px 80px rgba(0,0,0,0.6), inset 0 1px 0 rgba(255,255,255,0.04)',
                animation: 'fadeIn 0.4s ease forwards',
            }}>
                {children}
            </div>
        </div>
    )
}

export default MainCard
