const Navbar = () => {
    return (
        <nav style={{
            background: 'rgba(6, 11, 20, 0.85)',
            borderBottom: '1px solid rgba(56, 189, 248, 0.1)',
            backdropFilter: 'blur(20px)',
            WebkitBackdropFilter: 'blur(20px)',
            position: 'sticky',
            top: 0,
            zIndex: 50,
        }}>
            <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '0 24px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', height: '64px' }}>
                    {/* Logo */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '14px' }}>
                        <div style={{
                            width: '40px', height: '40px',
                            background: 'linear-gradient(135deg, #0ea5e9, #6366f1)',
                            borderRadius: '12px',
                            display: 'flex', alignItems: 'center', justifyContent: 'center',
                            boxShadow: '0 0 20px rgba(14, 165, 233, 0.35)',
                        }}>
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M22.54 6.42a2.78 2.78 0 0 0-1.95-1.96C18.88 4 12 4 12 4s-6.88 0-8.59.46A2.78 2.78 0 0 0 1.46 6.42 29 29 0 0 0 1 12a29 29 0 0 0 .46 5.58 2.78 2.78 0 0 0 1.95 1.96C5.12 20 12 20 12 20s6.88 0 8.59-.46a2.78 2.78 0 0 0 1.95-1.96A29 29 0 0 0 23 12a29 29 0 0 0-.46-5.58z" />
                                <polygon points="9.75 15.02 15.5 12 9.75 8.98 9.75 15.02" fill="white" stroke="none" />
                            </svg>
                        </div>
                        <div>
                            <h1 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'white', margin: 0, lineHeight: 1.2 }}>
                                AccidentSense
                            </h1>
                            <p style={{ fontSize: '0.7rem', color: 'rgba(148,163,184,0.7)', margin: 0, letterSpacing: '0.06em', textTransform: 'uppercase' }}>
                                Spatio-Temporal Detection
                            </p>
                        </div>
                    </div>

                    {/* Right — live indicator */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                        <span style={{
                            display: 'inline-flex', alignItems: 'center', gap: '6px',
                            padding: '5px 12px',
                            background: 'rgba(16, 185, 129, 0.1)',
                            border: '1px solid rgba(16, 185, 129, 0.25)',
                            borderRadius: '999px',
                            fontSize: '0.72rem', fontWeight: 600, color: '#34d399',
                            letterSpacing: '0.05em',
                        }}>
                            <span style={{
                                width: 7, height: 7,
                                borderRadius: '50%',
                                background: '#34d399',
                                boxShadow: '0 0 6px #34d399',
                                animation: 'pulse-glow 2s ease infinite',
                            }} />
                            SYSTEM ONLINE
                        </span>
                    </div>
                </div>
            </div>
        </nav>
    )
}

export default Navbar
