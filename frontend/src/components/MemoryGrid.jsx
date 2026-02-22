import React from 'react';

/**
 * MemoryGrid - Visualizes page frame state at each step.
 * Highlights page faults in red.
 */
export default function MemoryGrid({ history, numFrames }) {
    if (!history || history.length === 0) return null;

    return (
        <div className="card mt-16">
            <div className="card-header">
                <span className="card-title">Frame-by-Frame Memory State</span>
            </div>
            <div className="memory-grid">
                {/* Header column */}
                <div className="memory-col" style={{ minWidth: '60px' }}>
                    <div className="step-label">Page</div>
                    {Array.from({ length: numFrames }).map((_, i) => (
                        <div key={i} className="memory-cell" style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '0.7rem' }}>
                            F{i}
                        </div>
                    ))}
                    <div className="step-label" style={{ marginTop: '4px' }}>Status</div>
                </div>

                {history.map((step) => (
                    <div key={step.step} className="memory-col">
                        <div className="step-label" style={{ color: step.fault ? 'var(--red)' : 'var(--cyan)', fontWeight: 600 }}>
                            {step.page}
                        </div>
                        {Array.from({ length: numFrames }).map((_, i) => (
                            <div
                                key={i}
                                className={`memory-cell ${step.fault && i === step.frames.length - 1 ? 'fault' : ''} ${i >= step.frames.length ? 'empty' : ''}`}
                            >
                                {step.frames[i] !== undefined ? step.frames[i] : '—'}
                            </div>
                        ))}
                        <span className={`badge ${step.fault ? 'badge-fault' : 'badge-hit'}`} style={{ marginTop: '4px' }}>
                            {step.fault ? 'F' : 'H'}
                        </span>
                    </div>
                ))}
            </div>
        </div>
    );
}
