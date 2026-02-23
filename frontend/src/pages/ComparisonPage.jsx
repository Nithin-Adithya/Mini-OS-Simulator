import React, { useState, useEffect } from 'react';
import { BarChart3, Play } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer, CartesianGrid } from 'recharts';
import ProcessForm from '../components/ProcessForm';
import { compareAlgorithms } from '../api';

const COLORS = { 'avg_waiting_time': '#06d6a0', 'avg_turnaround_time': '#7c5cfc', 'avg_response_time': '#3b82f6' };
const LABELS = { 'avg_waiting_time': 'Avg WT', 'avg_turnaround_time': 'Avg TAT', 'avg_response_time': 'Avg RT' };

/**
 * ComparisonPage - Runs all 4 scheduling algorithms and shows grouped bar charts.
 */
export default function ComparisonPage() {
    useEffect(() => { document.title = 'OS Simulator | Comparison'; }, []);
    const [processes, setProcesses] = useState([]);
    const [quantum, setQuantum] = useState(2);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleCompare = async () => {
        if (processes.length === 0) {
            setError('Add at least one process.');
            return;
        }
        setError('');
        setLoading(true);
        try {
            const res = await compareAlgorithms(processes, quantum);
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Comparison failed. Is the backend running?');
        } finally {
            setLoading(false);
        }
    };

    const comparisonData = result?.comparison?.map((c) => ({
        algorithm: c.algorithm,
        'Avg WT': c.avg_waiting_time,
        'Avg TAT': c.avg_turnaround_time,
        'Avg RT': c.avg_response_time,
    })) || [];

    const utilizationData = result?.comparison?.map((c) => ({
        algorithm: c.algorithm,
        'CPU Util %': c.cpu_utilization,
        Throughput: +(c.throughput * 100).toFixed(2),
    })) || [];

    // Find best algorithm based on avg WT
    const best = result?.comparison?.reduce((a, b) =>
        a.avg_waiting_time < b.avg_waiting_time ? a : b, result.comparison[0]
    );

    return (
        <div>
            <div className="page-header">
                <h2>Algorithm Comparison</h2>
                <p>Run all four scheduling algorithms on the same process set and compare performance.</p>
            </div>

            <ProcessForm processes={processes} setProcesses={setProcesses} />

            <div className="card mt-16">
                <div className="form-row">
                    <div className="form-group">
                        <label>Time Quantum (for RR)</label>
                        <input
                            type="number"
                            min="1"
                            value={quantum}
                            onChange={(e) => setQuantum(Number(e.target.value))}
                            style={{ width: '80px' }}
                        />
                    </div>

                    <button className="btn btn-violet" onClick={handleCompare} disabled={loading}>
                        <BarChart3 size={16} /> {loading ? 'Running...' : 'Compare All'}
                    </button>
                </div>
            </div>

            {error && <div className="error-message mt-16">{error}</div>}

            {result && (
                <>
                    {best && (
                        <div className="result-banner safe mt-16">
                            <BarChart3 size={20} />
                            Best algorithm by average waiting time: <strong style={{ marginLeft: '4px' }}>{best.algorithm}</strong>
                            &nbsp;(WT = {best.avg_waiting_time})
                        </div>
                    )}

                    {/* Timing Metrics Chart */}
                    <div className="card mt-16">
                        <div className="card-header">
                            <span className="card-title">Timing Metrics Comparison</span>
                        </div>
                        <ResponsiveContainer width="100%" height={320}>
                            <BarChart data={comparisonData} barCategoryGap="20%">
                                <CartesianGrid strokeDasharray="3 3" stroke="#e8ecf1" />
                                <XAxis dataKey="algorithm" stroke="#5a6580" fontSize={12} />
                                <YAxis stroke="#5a6580" fontSize={12} />
                                <Tooltip
                                    contentStyle={{ background: '#ffffff', border: '1px solid #e8ecf1', borderRadius: '8px', fontSize: '0.82rem' }}
                                    labelStyle={{ color: '#1a1d26' }}
                                />
                                <Legend wrapperStyle={{ fontSize: '0.82rem' }} />
                                <Bar dataKey="Avg WT" fill="#5b8a72" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="Avg TAT" fill="#6b8aaf" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="Avg RT" fill="#8b7a9e" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Utilization Chart */}
                    <div className="card mt-16">
                        <div className="card-header">
                            <span className="card-title">CPU Utilization & Throughput</span>
                        </div>
                        <ResponsiveContainer width="100%" height={280}>
                            <BarChart data={utilizationData} barCategoryGap="20%">
                                <CartesianGrid strokeDasharray="3 3" stroke="#e8ecf1" />
                                <XAxis dataKey="algorithm" stroke="#5a6580" fontSize={12} />
                                <YAxis stroke="#5a6580" fontSize={12} />
                                <Tooltip
                                    contentStyle={{ background: '#ffffff', border: '1px solid #e8ecf1', borderRadius: '8px', fontSize: '0.82rem' }}
                                    labelStyle={{ color: '#1a1d26' }}
                                />
                                <Legend wrapperStyle={{ fontSize: '0.82rem' }} />
                                <Bar dataKey="CPU Util %" fill="#c4956a" radius={[4, 4, 0, 0]} />
                                <Bar dataKey="Throughput" fill="#b87a8a" radius={[4, 4, 0, 0]} />
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Comparison Table */}
                    <div className="card mt-16">
                        <div className="card-header">
                            <span className="card-title">Summary Table</span>
                        </div>
                        <div style={{ overflowX: 'auto' }}>
                            <table className="data-table">
                                <thead>
                                    <tr>
                                        <th>Algorithm</th>
                                        <th>Avg WT</th>
                                        <th>Avg TAT</th>
                                        <th>Avg RT</th>
                                        <th>CPU Util %</th>
                                        <th>Throughput</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {result.comparison.map((c) => (
                                        <tr key={c.algorithm} style={c.algorithm === best?.algorithm ? { background: 'var(--cyan-dim)' } : {}}>
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
                    </div>
                </>
            )}

            {/* Terminology */}
            <div className="glossary">
                <div className="glossary-title">Terminology</div>
                <div className="glossary-grid">
                    <div className="glossary-item"><span className="abbr">FCFS</span><span className="full">— First Come First Serve</span></div>
                    <div className="glossary-item"><span className="abbr">SJF</span><span className="full">— Shortest Job First</span></div>
                    <div className="glossary-item"><span className="abbr">RR</span><span className="full">— Round Robin</span></div>
                    <div className="glossary-item"><span className="abbr">WT</span><span className="full">— Waiting Time</span></div>
                    <div className="glossary-item"><span className="abbr">TAT</span><span className="full">— Turnaround Time</span></div>
                    <div className="glossary-item"><span className="abbr">RT</span><span className="full">— Response Time</span></div>
                    <div className="glossary-item"><span className="abbr">CPU</span><span className="full">— Central Processing Unit</span></div>
                </div>
            </div>
        </div>
    );
}
