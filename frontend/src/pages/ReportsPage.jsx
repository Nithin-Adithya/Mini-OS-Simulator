import React, { useState } from 'react';
import { Download, Play, BarChart3 } from 'lucide-react';
import ProcessForm from '../components/ProcessForm';
import { compareAlgorithms, compareMemory } from '../api';

/**
 * ReportsPage - Export simulation results as CSV and view logs.
 */
export default function ReportsPage() {
    const [processes, setProcesses] = useState([]);
    const [quantum, setQuantum] = useState(2);
    const [schedResult, setSchedResult] = useState(null);
    const [memResult, setMemResult] = useState(null);
    const [refString, setRefString] = useState('7,0,1,2,0,3,0,4,2,3,0,3,2');
    const [frames, setFrames] = useState(3);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleGenerateAll = async () => {
        setError('');
        setLoading(true);
        try {
            if (processes.length > 0) {
                const schedRes = await compareAlgorithms(processes, quantum);
                setSchedResult(schedRes.data);
            }
            const refs = refString.split(',').map(s => parseInt(s.trim())).filter(n => !isNaN(n));
            if (refs.length > 0) {
                const memRes = await compareMemory(refs, frames);
                setMemResult(memRes.data);
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Report generation failed.');
        } finally { setLoading(false); }
    };

    const downloadCSV = (data, filename) => {
        if (!data || data.length === 0) return;
        const headers = Object.keys(data[0]);
        const csv = [
            headers.join(','),
            ...data.map(row => headers.map(h => JSON.stringify(row[h] ?? '')).join(','))
        ].join('\n');
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
    };

    return (
        <div>
            <div className="page-header">
                <h2>Reports & Export</h2>
                <p>Generate comprehensive reports and download results as CSV files.</p>
            </div>

            <ProcessForm processes={processes} setProcesses={setProcesses} />

            <div className="card mt-16">
                <div className="card-header">
                    <span className="card-title">Memory Configuration</span>
                </div>
                <div className="form-row">
                    <div className="form-group" style={{ flex: 2 }}>
                        <label>Reference String</label>
                        <input value={refString} onChange={(e) => setRefString(e.target.value)} />
                    </div>
                    <div className="form-group">
                        <label>Frames</label>
                        <input type="number" min="1" max="20" value={frames} onChange={(e) => setFrames(Number(e.target.value))} style={{ width: '70px' }} />
                    </div>
                    <div className="form-group">
                        <label>Quantum (RR)</label>
                        <input type="number" min="1" value={quantum} onChange={(e) => setQuantum(Number(e.target.value))} style={{ width: '70px' }} />
                    </div>
                </div>
            </div>

            <div style={{ marginTop: '16px' }}>
                <button className="btn btn-violet" onClick={handleGenerateAll} disabled={loading}>
                    <BarChart3 size={16} /> {loading ? 'Generating...' : 'Generate Report'}
                </button>
            </div>

            {error && <div className="error-message mt-16">{error}</div>}

            {/* Scheduling Report */}
            {schedResult && (
                <div className="card mt-24">
                    <div className="card-header">
                        <span className="card-title">Scheduling Comparison Report</span>
                        <button className="btn btn-secondary btn-small" onClick={() => downloadCSV(schedResult.comparison, 'scheduling_comparison.csv')}>
                            <Download size={14} /> Download CSV
                        </button>
                    </div>
                    <table className="data-table">
                        <thead>
                            <tr><th>Algorithm</th><th>Avg WT</th><th>Avg TAT</th><th>Avg RT</th><th>CPU Util %</th><th>Throughput</th></tr>
                        </thead>
                        <tbody>
                            {schedResult.comparison.map((c) => (
                                <tr key={c.algorithm}>
                                    <td style={{ color: 'var(--cyan)', fontWeight: 600 }}>{c.algorithm}</td>
                                    <td>{c.avg_waiting_time}</td>
                                    <td>{c.avg_turnaround_time}</td>
                                    <td>{c.avg_response_time}</td>
                                    <td>{c.cpu_utilization}</td>
                                    <td>{c.throughput}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Memory Report */}
            {memResult && (
                <div className="card mt-16">
                    <div className="card-header">
                        <span className="card-title">Memory Comparison Report</span>
                        <button className="btn btn-secondary btn-small" onClick={() => downloadCSV(
                            memResult.map(r => ({ algorithm: r.algorithm, faults: r.total_faults, hits: r.total_hits, hit_rate: (r.hit_rate * 100).toFixed(1) + '%' })),
                            'memory_comparison.csv'
                        )}>
                            <Download size={14} /> Download CSV
                        </button>
                    </div>
                    <table className="data-table">
                        <thead>
                            <tr><th>Algorithm</th><th>Faults</th><th>Hits</th><th>Hit Rate</th></tr>
                        </thead>
                        <tbody>
                            {memResult.map((r) => (
                                <tr key={r.algorithm}>
                                    <td style={{ color: 'var(--violet)', fontWeight: 600 }}>{r.algorithm}</td>
                                    <td>{r.total_faults}</td>
                                    <td>{r.total_hits}</td>
                                    <td>{(r.hit_rate * 100).toFixed(1)}%</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}

            {/* Terminology */}
            <div className="glossary">
                <div className="glossary-title">Terminology</div>
                <div className="glossary-grid">
                    <div className="glossary-item"><span className="abbr">CSV</span><span className="full">— Comma-Separated Values</span></div>
                    <div className="glossary-item"><span className="abbr">FCFS</span><span className="full">— First Come First Serve</span></div>
                    <div className="glossary-item"><span className="abbr">SJF</span><span className="full">— Shortest Job First</span></div>
                    <div className="glossary-item"><span className="abbr">RR</span><span className="full">— Round Robin</span></div>
                    <div className="glossary-item"><span className="abbr">WT</span><span className="full">— Waiting Time</span></div>
                    <div className="glossary-item"><span className="abbr">TAT</span><span className="full">— Turnaround Time</span></div>
                    <div className="glossary-item"><span className="abbr">RT</span><span className="full">— Response Time</span></div>
                    <div className="glossary-item"><span className="abbr">FIFO</span><span className="full">— First In First Out</span></div>
                    <div className="glossary-item"><span className="abbr">LRU</span><span className="full">— Least Recently Used</span></div>
                    <div className="glossary-item"><span className="abbr">CPU</span><span className="full">— Central Processing Unit</span></div>
                </div>
            </div>
        </div>
    );
}
