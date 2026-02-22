import React from 'react';

/**
 * GanttChart - Renders a horizontal Gantt chart from a scheduling timeline.
 * Each bar is color-coded by PID with duration labels.
 */

const COLORS = [
    '#5b8a72', '#6b8aaf', '#8b7a9e', '#c4956a', '#7a9e8b',
    '#9e8b7a', '#7a8b9e', '#a08b7a', '#6a9e8b', '#8a7a6b',
];

export default function GanttChart({ timeline }) {
    if (!timeline || timeline.length === 0) return null;

    const maxEnd = Math.max(...timeline.map((t) => t.end));
    const pidColors = {};
    let colorIdx = 0;

    timeline.forEach((t) => {
        if (!(t.pid in pidColors)) {
            pidColors[t.pid] = t.pid === 'IDLE' ? '#e8ecf1' : COLORS[colorIdx++ % COLORS.length];
        }
    });

    return (
        <div className="card mt-16">
            <div className="card-header">
                <span className="card-title">Gantt Chart</span>
            </div>

            {/* Legend */}
            <div style={{ display: 'flex', gap: '16px', flexWrap: 'wrap', marginBottom: '16px' }}>
                {Object.entries(pidColors)
                    .filter(([pid]) => pid !== 'IDLE')
                    .map(([pid, color]) => (
                        <div key={pid} style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                            <div style={{
                                width: '12px', height: '12px', borderRadius: '3px',
                                background: color
                            }} />
                            <span style={{ fontSize: '0.78rem', color: 'var(--text-secondary)' }}>{pid}</span>
                        </div>
                    ))}
            </div>

            {/* Chart */}
            <div style={{ overflowX: 'auto' }}>
                <div style={{ display: 'flex', minWidth: `${maxEnd * 30}px`, height: '48px', gap: '2px' }}>
                    {timeline.map((t, i) => {
                        const width = (t.end - t.start) * 30;
                        return (
                            <div
                                key={i}
                                style={{
                                    width: `${width}px`,
                                    background: pidColors[t.pid],
                                    borderRadius: '6px',
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    color: t.pid === 'IDLE' ? 'var(--text-muted)' : '#ffffff',
                                    fontWeight: 600,
                                    fontSize: '0.78rem',
                                    fontFamily: 'var(--font-mono)',
                                    position: 'relative',
                                    transition: 'opacity 0.15s ease',
                                    cursor: 'default',
                                    opacity: t.pid === 'IDLE' ? 0.5 : 1,
                                }}
                                title={`${t.pid}: ${t.start}–${t.end}`}
                            >
                                {width > 30 && t.pid}
                            </div>
                        );
                    })}
                </div>

                {/* Time axis */}
                <div style={{ display: 'flex', minWidth: `${maxEnd * 30}px`, marginTop: '4px' }}>
                    {timeline.map((t, i) => {
                        const width = (t.end - t.start) * 30;
                        return (
                            <div key={i} style={{ width: `${width + 2}px`, fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                                {t.start}
                            </div>
                        );
                    })}
                    <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                        {timeline[timeline.length - 1]?.end}
                    </span>
                </div>
            </div>
        </div>
    );
}
