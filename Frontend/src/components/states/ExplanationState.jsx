import { useState, useEffect } from 'react'
import { getExplanation } from '../../services/api'

const ExplanationState = ({ result, onBack, onReset }) => {
    const [explanation, setExplanation] = useState('')
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        if (!result?.id) return
        setIsLoading(true)
        getExplanation(result.id)
            .then(r => setExplanation(r.success ? r.explanation : 'Failed to load explanation.'))
            .catch(() => setExplanation('Failed to load explanation.'))
            .finally(() => setIsLoading(false))
    }, [result])

    const isAccident = result?.status === 'accident'

    // Parse markdown-ish sections
    const sections = explanation.split('\n\n').filter(Boolean)

    return (
        <div style={{ display: 'flex', flexDirection: 'column', gap: '28px', animation: 'fadeIn 0.4s ease' }}>
            {/* Header */}
            <div style={{ textAlign: 'center' }}>
                <div style={{
                    display: 'inline-flex', alignItems: 'center', gap: '8px',
                    padding: '6px 16px', marginBottom: '16px',
                    background: 'rgba(99, 102, 241, 0.1)',
                    border: '1px solid rgba(99, 102, 241, 0.25)',
                    borderRadius: '999px',
                    fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.1em',
                    textTransform: 'uppercase', color: '#818cf8',
                }}>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><path d="M12 2L2 7l10 5 10-5-10-5z" /><path d="M2 17l10 5 10-5" /><path d="M2 12l10 5 10-5" /></svg>
                    AI Analysis
                </div>
                <h2 style={{ fontSize: '1.75rem', fontWeight: 800, color: 'white', margin: '0 0 8px', letterSpacing: '-0.02em' }}>
                    AI Explanation
                </h2>
                <p style={{ margin: 0, color: 'rgba(148,163,184,0.6)', fontSize: '0.85rem' }}>
                    Deep analysis powered by Groq LLaMA 3.3-70B
                </p>
            </div>

            {/* Result summary strip */}
            <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '12px',
                padding: '16px 24px',
                background: isAccident ? 'rgba(239,68,68,0.06)' : 'rgba(16,185,129,0.06)',
                border: `1px solid ${isAccident ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)'}`,
                borderRadius: '14px',
            }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <div style={{
                        width: 10, height: 10, borderRadius: '50%',
                        background: isAccident ? '#ef4444' : '#10b981',
                        boxShadow: `0 0 8px ${isAccident ? '#ef4444' : '#10b981'}`,
                    }} />
                    <span style={{ fontWeight: 700, color: isAccident ? '#f87171' : '#34d399', fontSize: '0.9rem' }}>
                        {isAccident ? 'Accident Detected' : 'No Accident'}
                    </span>
                    <span style={{ color: 'rgba(148,163,184,0.5)', fontSize: '0.85rem' }}>
                        · {result?.confidence}% confidence
                    </span>
                </div>
                <span style={{
                    fontSize: '0.72rem', color: 'rgba(148,163,184,0.4)',
                    fontFamily: "'JetBrains Mono', monospace",
                }}>
                    {result?.id}
                </span>
            </div>

            {/* Explanation body */}
            <div style={{
                background: 'rgba(10, 18, 35, 0.7)',
                border: '1px solid rgba(148,163,184,0.08)',
                borderRadius: '18px',
                padding: '36px',
                minHeight: '280px',
            }}>
                {isLoading ? (
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: '16px', minHeight: '200px' }}>
                        <div style={{
                            width: 48, height: 48,
                            border: '3px solid rgba(99,102,241,0.2)',
                            borderTopColor: '#6366f1',
                            borderRadius: '50%',
                            animation: 'spin 0.9s linear infinite',
                        }} />
                        <p style={{ color: 'rgba(148,163,184,0.5)', margin: 0, fontSize: '0.85rem' }}>
                            Generating AI explanation...
                        </p>
                    </div>
                ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                        {sections.map((section, i) => {
                            const lines = section.split('\n')
                            const firstLine = lines[0]
                            const isHeading = firstLine.startsWith('##') || firstLine.startsWith('#')
                            const isBullet = lines.some(l => l.trim().startsWith('-') || l.trim().startsWith('*'))

                            if (isHeading) {
                                const headingText = firstLine.replace(/^#+\s*/, '')
                                const rest = lines.slice(1).join('\n')
                                return (
                                    <div key={i}>
                                        <h3 style={{
                                            fontSize: '1rem', fontWeight: 700, color: 'white',
                                            margin: '0 0 10px', display: 'flex', alignItems: 'center', gap: '8px',
                                        }}>
                                            <span style={{ width: 3, height: 16, background: 'linear-gradient(180deg,#0ea5e9,#6366f1)', borderRadius: '2px', display: 'inline-block' }} />
                                            {headingText}
                                        </h3>
                                        {rest && <p style={{ margin: 0, color: '#94a3b8', lineHeight: 1.75, fontSize: '0.88rem' }}>{rest}</p>}
                                    </div>
                                )
                            }
                            return (
                                <p key={i} style={{ margin: 0, color: '#94a3b8', lineHeight: 1.75, fontSize: '0.88rem' }}>
                                    {section}
                                </p>
                            )
                        })}
                    </div>
                )}
            </div>

            {/* Technical detail chips */}
            {!isLoading && result?.details && (
                <div style={{
                    display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))', gap: '12px',
                }}>
                    {[
                        { label: 'Architecture', val: 'YOLOv8 + LSTM' },
                        { label: 'Method', val: 'Spatio-Temporal' },
                        { label: 'Frames', val: result.details.frameCount },
                        { label: 'Processing', val: result.details.duration },
                    ].map(({ label, val }) => (
                        <div key={label} style={{
                            padding: '14px 18px', borderRadius: '12px',
                            background: 'rgba(15,23,42,0.6)',
                            border: '1px solid rgba(148,163,184,0.08)',
                        }}>
                            <p style={{ margin: '0 0 4px', fontSize: '0.65rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', color: 'rgba(148,163,184,0.4)' }}>{label}</p>
                            <p style={{ margin: 0, fontSize: '0.9rem', fontWeight: 600, color: 'white' }}>{val}</p>
                        </div>
                    ))}
                </div>
            )}

            {/* Actions */}
            <div style={{ display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap' }}>
                <button className="btn-secondary" onClick={onBack}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="15 18 9 12 15 6" /></svg>
                    Back to Results
                </button>
                <button className="btn-primary" onClick={onReset}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 102.13-9.36L1 10" /></svg>
                    Analyze Another Video
                </button>
            </div>
        </div>
    )
}

export default ExplanationState
