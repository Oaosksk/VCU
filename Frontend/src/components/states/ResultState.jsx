import { useState, useRef } from 'react'
import { formatTimestamp } from '../../utils/formatters'

const S = {
    // Layout
    root: { display: 'flex', flexDirection: 'column', gap: '32px', animation: 'fadeIn 0.4s ease' },
    header: { textAlign: 'center' },
    title: { fontSize: '1.75rem', fontWeight: 800, color: 'white', margin: '0 0 6px', letterSpacing: '-0.02em' },
    subtitle: { fontSize: '0.85rem', color: 'rgba(148,163,184,0.6)', margin: 0 },

    // Top verdict banner
    verdictBanner: (isAccident) => ({
        display: 'flex', alignItems: 'center', justifyContent: 'space-between', flexWrap: 'wrap', gap: '16px',
        padding: '24px 28px',
        borderRadius: '18px',
        background: isAccident
            ? 'linear-gradient(135deg, rgba(239,68,68,0.12) 0%, rgba(220,38,38,0.06) 100%)'
            : 'linear-gradient(135deg, rgba(16,185,129,0.12) 0%, rgba(5,150,105,0.06) 100%)',
        border: `1px solid ${isAccident ? 'rgba(239,68,68,0.3)' : 'rgba(16,185,129,0.3)'}`,
        boxShadow: `0 0 30px ${isAccident ? 'rgba(239,68,68,0.1)' : 'rgba(16,185,129,0.1)'}`,
    }),
    verdictLeft: { display: 'flex', alignItems: 'center', gap: '16px' },
    verdictIcon: (isAccident) => ({
        width: 52, height: 52, borderRadius: '14px', flexShrink: 0,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: isAccident ? 'rgba(239,68,68,0.2)' : 'rgba(16,185,129,0.2)',
        border: `1px solid ${isAccident ? 'rgba(239,68,68,0.4)' : 'rgba(16,185,129,0.4)'}`,
    }),
    verdictLabel: (isAccident) => ({
        fontSize: '1.35rem', fontWeight: 800, letterSpacing: '-0.02em',
        color: isAccident ? '#f87171' : '#34d399', margin: '0 0 4px',
    }),
    verdictSub: { fontSize: '0.8rem', color: 'rgba(148,163,184,0.7)', margin: 0 },
    severityBadge: (sev) => {
        const map = {
            critical: { bg: 'rgba(239,68,68,0.15)', color: '#f87171', border: 'rgba(239,68,68,0.3)' },
            moderate: { bg: 'rgba(245,158,11,0.15)', color: '#fbbf24', border: 'rgba(245,158,11,0.3)' },
            minor: { bg: 'rgba(251,191,36,0.15)', color: '#fde68a', border: 'rgba(251,191,36,0.3)' },
        }
        const c = map[sev] || { bg: 'rgba(148,163,184,0.1)', color: '#94a3b8', border: 'rgba(148,163,184,0.2)' }
        return {
            padding: '6px 16px', borderRadius: '999px', fontSize: '0.75rem', fontWeight: 700,
            letterSpacing: '0.06em', textTransform: 'uppercase',
            background: c.bg, color: c.color, border: `1px solid ${c.border}`,
        }
    },

    // Grid
    twoCol: {
        display: 'grid',
        gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
        gap: '24px',
    },

    // Section heading
    sectionLabel: {
        fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase',
        color: 'rgba(148,163,184,0.5)', marginBottom: '14px',
    },

    // Confidence panel
    confPanel: {
        background: 'rgba(10, 18, 35, 0.6)',
        border: '1px solid rgba(56, 189, 248, 0.12)',
        borderRadius: '18px', padding: '28px',
    },
    confRingWrap: { display: 'flex', alignItems: 'center', gap: '24px', marginBottom: '20px' },
    confValue: { fontSize: '2.8rem', fontWeight: 900, letterSpacing: '-0.04em', color: 'white', lineHeight: 1 },
    confPct: { fontSize: '1.2rem', color: 'rgba(148,163,184,0.5)' },
    confLevelLabel: { fontSize: '0.78rem', color: 'rgba(148,163,184,0.6)', marginTop: '4px' },
    barTrack: {
        width: '100%', height: '8px', borderRadius: '99px',
        background: 'rgba(30, 41, 59, 0.8)', overflow: 'hidden',
    },

    // Stats grid
    statsGrid: { display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '12px' },
    statBox: {
        background: 'rgba(15, 23, 42, 0.6)',
        border: '1px solid rgba(148, 163, 184, 0.08)',
        borderRadius: '14px', padding: '16px',
        transition: 'border-color 0.2s',
    },
    statBoxLabel: { fontSize: '0.68rem', fontWeight: 600, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'rgba(148,163,184,0.5)', marginBottom: '6px' },
    statBoxVal: { fontSize: '1.15rem', fontWeight: 700, color: 'white' },

    // Reasoning
    reasonBox: {
        background: 'rgba(56, 189, 248, 0.04)',
        border: '1px solid rgba(56, 189, 248, 0.12)',
        borderRadius: '14px', padding: '20px',
    },
    reasonText: { fontSize: '0.88rem', color: '#94a3b8', lineHeight: 1.7, margin: 0 },

    // Video panel
    videoPanel: {
        background: 'rgba(10, 18, 35, 0.6)',
        border: '1px solid rgba(56, 189, 248, 0.12)',
        borderRadius: '18px', padding: '24px',
    },
    videoWrap: {
        background: '#000', borderRadius: '12px', overflow: 'hidden',
        border: '1px solid rgba(148,163,184,0.1)',
        aspectRatio: '16/9', display: 'flex', alignItems: 'center', justifyContent: 'center',
    },

    // Frames
    framesGrid: { display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: '8px', marginTop: '12px' },
    frameWrap: (isImpact) => ({
        position: 'relative', cursor: 'pointer', borderRadius: '8px', overflow: 'hidden',
        border: `2px solid ${isImpact ? '#ef4444' : 'rgba(148,163,184,0.12)'}`,
        transition: 'all 0.2s',
        boxShadow: isImpact ? '0 0 12px rgba(239,68,68,0.3)' : 'none',
    }),
    frameLabel: {
        position: 'absolute', bottom: 4, right: 4,
        background: 'rgba(0,0,0,0.75)', color: 'white',
        fontSize: '0.6rem', fontWeight: 700, padding: '2px 6px', borderRadius: '4px',
    },

    // Meta row
    metaRow: { display: 'flex', alignItems: 'center', gap: '6px', fontSize: '0.75rem', color: 'rgba(148,163,184,0.4)' },

    // Actions
    actions: { display: 'flex', gap: '12px', justifyContent: 'center', flexWrap: 'wrap', paddingTop: '8px' },

    // Modal
    modal: {
        position: 'fixed', inset: 0, zIndex: 100,
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        background: 'rgba(0,0,0,0.92)', backdropFilter: 'blur(8px)',
        padding: '24px',
    },
    modalClose: {
        position: 'absolute', top: 16, right: 16,
        width: 36, height: 36, borderRadius: '50%',
        background: 'rgba(239,68,68,0.8)', border: 'none', color: 'white',
        fontSize: '1.2rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'pointer',
    },
}

const BASE_URL = import.meta.env.VITE_API_BASE_URL?.replace('/api', '') || 'http://localhost:8000'

const ConfidenceRing = ({ value, isAccident }) => {
    const r = 44
    const circ = 2 * Math.PI * r
    const offset = circ - (value / 100) * circ
    const color = isAccident ? '#ef4444' : value >= 30 ? '#f59e0b' : '#10b981'
    return (
        <svg width="100" height="100" viewBox="0 0 100 100" style={{ flexShrink: 0 }}>
            <circle cx="50" cy="50" r={r} fill="none" stroke="rgba(148,163,184,0.08)" strokeWidth="8" />
            <circle
                cx="50" cy="50" r={r} fill="none"
                stroke={color} strokeWidth="8"
                strokeDasharray={circ} strokeDashoffset={offset}
                strokeLinecap="round"
                transform="rotate(-90 50 50)"
                style={{ transition: 'stroke-dashoffset 1.2s cubic-bezier(0.4,0,0.2,1)', filter: `drop-shadow(0 0 6px ${color})` }}
            />
            <text x="50" y="54" textAnchor="middle" fill="white" fontSize="18" fontWeight="800" fontFamily="Inter">{value}</text>
            <text x="50" y="66" textAnchor="middle" fill="rgba(148,163,184,0.5)" fontSize="9" fontFamily="Inter">SCORE</text>
        </svg>
    )
}

const ResultState = ({ result, file, onViewExplanation, onReset }) => {
    const [zoomedImage, setZoomedImage] = useState(null)
    const videoRef = useRef(null)

    if (!result) return (
        <div style={{ textAlign: 'center', color: 'rgba(148,163,184,0.5)' }}>No results available</div>
    )

    const isAccident = result.status === 'accident'
    const videoUrl = file ? URL.createObjectURL(file) : null
    const conf = result.confidence ?? 0
    const confColor = isAccident ? '#ef4444' : conf >= 30 ? '#f59e0b' : '#10b981'
    const confLabel = conf >= 91 ? 'High Confidence' : conf >= 30 ? 'Medium Confidence' : 'Low Confidence'
    const frameLabels = ['-2s', '-1s', 'Impact', '+1s', '+2s']

    return (
        <div style={S.root}>
            {/* Header */}
            <div style={S.header}>
                <h2 style={S.title}>Analysis Complete</h2>
                <p style={S.subtitle}>Spatio-temporal accident detection result</p>
            </div>

            {/* Verdict Banner */}
            <div style={S.verdictBanner(isAccident)}>
                <div style={S.verdictLeft}>
                    <div style={S.verdictIcon(isAccident)}>
                        {isAccident ? (
                            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#f87171" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" />
                                <line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />
                            </svg>
                        ) : (
                            <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2.2" strokeLinecap="round" strokeLinejoin="round">
                                <path d="M22 11.08V12a10 10 0 11-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />
                            </svg>
                        )}
                    </div>
                    <div>
                        <p style={S.verdictLabel(isAccident)}>
                            {isAccident ? '🚨 Accident Detected' : '✅ No Accident'}
                        </p>
                        <p style={S.verdictSub}>
                            {isAccident
                                ? `${result.accidentType || 'Collision event'} • ${(result.severity || 'unknown').toUpperCase()} severity`
                                : 'Normal driving patterns observed — no collision detected'}
                        </p>
                    </div>
                </div>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center', flexWrap: 'wrap' }}>
                    {result.severity && result.severity !== 'none' && (
                        <span style={S.severityBadge(result.severity)}>{result.severity}</span>
                    )}
                    <span style={{
                        fontSize: '0.8rem', color: 'rgba(148,163,184,0.5)',
                        background: 'rgba(15,23,42,0.6)', border: '1px solid rgba(148,163,184,0.1)',
                        padding: '5px 14px', borderRadius: '999px', fontFamily: "'JetBrains Mono', monospace",
                    }}>
                        ID: {result.id?.slice(-8)}
                    </span>
                </div>
            </div>

            {/* Main two-column area */}
            <div style={S.twoCol}>
                {/* LEFT: Confidence + Stats + Reasoning */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>

                    {/* Confidence panel */}
                    <div style={S.confPanel}>
                        <p style={S.sectionLabel}>Confidence Score</p>
                        <div style={S.confRingWrap}>
                            <ConfidenceRing value={conf} isAccident={isAccident} />
                            <div>
                                <div style={{ display: 'flex', alignItems: 'baseline', gap: '3px' }}>
                                    <span style={{ ...S.confValue, color: confColor }}>{conf}</span>
                                    <span style={S.confPct}>%</span>
                                </div>
                                <p style={{ ...S.confLevelLabel, color: confColor }}>{confLabel}</p>
                            </div>
                        </div>
                        {/* Bar */}
                        <div style={S.barTrack}>
                            <div style={{
                                height: '100%', borderRadius: '99px', width: `${conf}%`,
                                background: isAccident
                                    ? 'linear-gradient(90deg, #ef4444, #dc2626)'
                                    : conf >= 30
                                        ? 'linear-gradient(90deg, #f59e0b, #d97706)'
                                        : 'linear-gradient(90deg, #10b981, #059669)',
                                boxShadow: `0 0 10px ${confColor}50`,
                                transition: 'width 1s cubic-bezier(0.4,0,0.2,1)',
                            }} />
                        </div>
                    </div>

                    {/* Stats grid */}
                    <div>
                        <p style={S.sectionLabel}>Detection Metrics</p>
                        <div style={S.statsGrid}>
                            {[
                                { label: 'Frames Analyzed', val: result.details?.frameCount ?? '—' },
                                { label: 'Duration', val: result.details?.duration ?? '—' },
                                { label: 'Spatial Features', val: result.details?.spatialFeatures ?? '—' },
                                { label: 'Temporal Stability', val: result.details?.temporalFeatures ?? '—' },
                            ].map(({ label, val }) => (
                                <div key={label} style={S.statBox}>
                                    <p style={S.statBoxLabel}>{label}</p>
                                    <p style={S.statBoxVal}>{val}</p>
                                </div>
                            ))}
                        </div>
                    </div>

                    {/* Forensic reasoning */}
                    {result.reasoning && (
                        <div>
                            <p style={S.sectionLabel}>Forensic Reasoning</p>
                            <div style={S.reasonBox}>
                                <p style={S.reasonText}>{result.reasoning}</p>
                            </div>
                        </div>
                    )}

                    {/* Timestamp */}
                    <div style={S.metaRow}>
                        <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
                        Analyzed {formatTimestamp(result.timestamp)}
                    </div>
                </div>

                {/* RIGHT: Video + Frames */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={S.videoPanel}>
                        <p style={S.sectionLabel}>Uploaded Video</p>
                        <div style={S.videoWrap}>
                            {videoUrl ? (
                                <video
                                    ref={videoRef}
                                    src={videoUrl}
                                    controls
                                    style={{ width: '100%', height: '100%', objectFit: 'contain' }}
                                >
                                    Your browser does not support video.
                                </video>
                            ) : (
                                <div style={{ color: 'rgba(148,163,184,0.3)', fontSize: '0.85rem' }}>
                                    Video preview unavailable
                                </div>
                            )}
                        </div>

                        {/* Accident frames */}
                        {isAccident && result.details?.accidentFrameUrls?.length > 0 && (
                            <div style={{ marginTop: '20px' }}>
                                <p style={S.sectionLabel}>Accident Sequence Frames</p>
                                <div style={S.framesGrid}>
                                    {result.details.accidentFrameUrls.map((url, idx) => (
                                        <div
                                            key={idx}
                                            style={S.frameWrap(idx === 2)}
                                            onClick={() => setZoomedImage(`${BASE_URL}${url}`)}
                                        >
                                            <img
                                                src={`${BASE_URL}${url}`}
                                                alt={`Frame ${frameLabels[idx]}`}
                                                style={{ width: '100%', display: 'block' }}
                                            />
                                            <span style={S.frameLabel}>{frameLabels[idx] ?? `+${idx}`}</span>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        )}

                        {/* No accident message */}
                        {!isAccident && (
                            <div style={{
                                marginTop: '16px', padding: '14px 18px', borderRadius: '12px',
                                background: 'rgba(16, 185, 129, 0.06)',
                                border: '1px solid rgba(16, 185, 129, 0.15)',
                                display: 'flex', alignItems: 'center', gap: '10px',
                            }}>
                                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="#34d399" strokeWidth="2"><path d="M22 11.08V12a10 10 0 11-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" /></svg>
                                <p style={{ margin: 0, fontSize: '0.8rem', color: '#34d399' }}>
                                    No accident frames detected — footage appears safe
                                </p>
                            </div>
                        )}
                    </div>

                    {/* Inference time badge */}
                    {result.inference_time && (
                        <div style={{
                            display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px',
                            padding: '10px 16px', borderRadius: '12px',
                            background: 'rgba(15, 23, 42, 0.5)', border: '1px solid rgba(148,163,184,0.08)',
                        }}>
                            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="rgba(148,163,184,0.5)" strokeWidth="2"><circle cx="12" cy="12" r="10" /><polyline points="12 6 12 12 16 14" /></svg>
                            <span style={{ fontSize: '0.78rem', color: 'rgba(148,163,184,0.5)' }}>
                                Processing time: <strong style={{ color: '#94a3b8', fontFamily: "'JetBrains Mono', monospace" }}>{result.inference_time.toFixed(2)}s</strong>
                            </span>
                        </div>
                    )}
                </div>
            </div>

            {/* Actions */}
            <div style={S.actions}>
                <button className="btn-primary" onClick={onViewExplanation}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 015.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" /></svg>
                    View AI Explanation
                </button>
                <button className="btn-secondary" onClick={onReset}>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><polyline points="1 4 1 10 7 10" /><path d="M3.51 15a9 9 0 102.13-9.36L1 10" /></svg>
                    Analyze Another Video
                </button>
            </div>

            {/* Zoom Modal */}
            {zoomedImage && (
                <div style={S.modal} onClick={() => setZoomedImage(null)}>
                    <div style={{ position: 'relative', maxWidth: '90vw', maxHeight: '90vh' }}>
                        <img src={zoomedImage} alt="Zoomed frame" style={{ maxWidth: '100%', maxHeight: '90vh', objectFit: 'contain', borderRadius: '12px' }} />
                        <button style={S.modalClose} onClick={() => setZoomedImage(null)}>×</button>
                    </div>
                </div>
            )}
        </div>
    )
}

export default ResultState
