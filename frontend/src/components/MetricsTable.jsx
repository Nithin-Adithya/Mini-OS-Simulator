import React from 'react';

/**
 * MetricsTable - Renders per-process scheduling metrics in a styled table.
 */
export default function MetricsTable({ metrics }) {
    if (!metrics || metrics.length === 0) return null;

    return (
        <div className="card mt-16">
            <div className="card-header">
                <span className="card-title">Per-Process Metrics</span>
            </div>
            <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Arrival</th>
                            <th>Burst</th>
                            <th>Start</th>
                            <th>Completion</th>
                            <th>Waiting</th>
                            <th>Turnaround</th>
                            <th>Response</th>
                        </tr>
                    </thead>
                    <tbody>
                        {metrics.map((p) => (
                            <tr key={p.pid}>
                                <td style={{ color: 'var(--cyan)', fontWeight: 600 }}>{p.pid}</td>
                                <td>{p.arrival_time}</td>
                                <td>{p.burst_time}</td>
                                <td>{p.start_time}</td>
                                <td>{p.completion_time}</td>
                                <td>{p.waiting_time}</td>
                                <td>{p.turnaround_time}</td>
                                <td>{p.response_time}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
