import React, { useState, useEffect } from 'react';
import { Play, BarChart3 } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Cell } from 'recharts';
import MemoryGrid from '../components/MemoryGrid';
import { runMemory, compareMemory } from '../api';

const ALGO_COLORS = { FIFO: '#5b8a72', LRU: '#6b8aaf', OPTIMAL: '#8b7a9e' };

/**
 * MemoryPage - Page replacement simulation with frame visualization and comparison.
 */
export default function MemoryPage() {
    useEffect(() => { document.title = 'OS Simulator | Memory Management'; }, []);
    const [refString, setRefString] = useState('7,0,1,2,0,3,0,4,2,3,0,3,2');
    const [numFrames, setNumFrames] = useState(3);
    const [algorithm, setAlgorithm] = useState('fifo');
    const [result, setResult] = useState(null);
    const [compareResult, setCompareResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const parseRefString = () =>
        refString.split(',').map((s) => parseInt(s.trim())).filter((n) => !isNaN(n));

    const handleRun = async () => {
        const refs = parseRefString();
        if (refs.length === 0) { setError('Enter a valid reference string.'); return; }
        setError('');
        setLoading(true);
        setCompareResult(null);
        try {
            const res = await runMemory(refs, numFrames, algorithm);
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Simulation failed.');
        } finally { setLoading(false); }
    };

    const handleCompare = async () => {
        const refs = parseRefString();
        if (refs.length === 0) { setError('Enter a valid reference string.'); return; }
        setError('');
        setLoading(true);
        setResult(null);
        try {
            const res = await compareMemory(refs, numFrames);
            setCompareResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Comparison failed.');
        } finally { setLoading(false); }
    };

    const compData = compareResult?.map((r) => ({
        algorithm: r.algorithm,
        Faults: r.total_faults,
        'Hit Rate %': +(r.hit_rate * 100).toFixed(1),
    })) || [];

    return (
        <div>
            <div className="page-header">
                <h2>Memory Management</h2>
                <p>Simulate page replacement algorithms (FIFO, LRU, Optimal) and compare page fault rates.</p>
            </div>

            <div className="card">
                <div className="card-header">
                    <span className="card-title">Configuration</span>
                </div>

                <div className="form-group mb-16">
                    <label>Page Reference String (comma-separated)</label>
                    <input
                        value={refString}
                        onChange={(e) => setRefString(e.target.value)}
                        placeholder="7,0,1,2,0,3,0,4,2,3,0,3,2"
                    />
                </div>

                <div className="form-row">
                    <div className="form-group">
                        <label>Number of Frames</label>
                        <input
                            type="number" min="1" max="20"
                            value={numFrames}
                            onChange={(e) => setNumFrames(Number(e.target.value))}
                            style={{ width: '80px' }}
                        />
                    </div>

                    <div className="form-group">
                        <label>Algorithm</label>
                        <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
                            <option value="fifo">FIFO</option>
                            <option value="lru">LRU</option>
                            <option value="optimal">Optimal</option>
                        </select>
                    </div>

                    <button className="btn btn-primary" onClick={handleRun} disabled={loading}>
                        <Play size={16} /> Simulate
                    </button>
                    <button className="btn btn-violet" onClick={handleCompare} disabled={loading}>
                        <BarChart3 size={16} /> Compare All
                    </button>
                </div>
            </div>

            {error && <div className="error-message mt-16">{error}</div>}

            {/* Single Algorithm Result */}
            {result && (
                <>
                    <div className="stats-grid mt-24">
                        <div className="stat-card">
                            <div className="stat-value">{result.total_faults}</div>
                            <div className="stat-label">Page Faults</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{result.total_hits}</div>
                            <div className="stat-label">Page Hits</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{(result.hit_rate * 100).toFixed(1)}%</div>
                            <div className="stat-label">Hit Rate</div>
                        </div>
                    </div>
                    <MemoryGrid history={result.history} numFrames={numFrames} />
                </>
            )}

            {/* Comparison Result */}
            {compareResult && (
                <>
                    <div className="card mt-24">
                        <div className="card-header">
                            <span className="card-title">Page Faults Comparison</span>
                        </div>
                        <ResponsiveContainer width="100%" height={300}>
                            <BarChart data={compData} barCategoryGap="20%">
                                <CartesianGrid strokeDasharray="3 3" stroke="#e8ecf1" />
                                <XAxis dataKey="algorithm" stroke="#5a6580" fontSize={12} />
                                <YAxis stroke="#5a6580" fontSize={12} />
                                <Tooltip
                                    contentStyle={{ background: '#ffffff', border: '1px solid #e8ecf1', borderRadius: '8px', fontSize: '0.82rem' }}
                                    labelStyle={{ color: '#1a1d26' }}
                                />
                                <Bar dataKey="Faults" radius={[4, 4, 0, 0]}>
                                    {compData.map((entry) => (
                                        <Cell key={entry.algorithm} fill={ALGO_COLORS[entry.algorithm] || '#06d6a0'} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>

                    <div className="card mt-16">
                        <div className="card-header">
                            <span className="card-title">Summary Table</span>
                        </div>
                        <table className="data-table">
                            <thead>
                                <tr><th>Algorithm</th><th>Faults</th><th>Hits</th><th>Hit Rate</th></tr>
                            </thead>
                            <tbody>
                                {compareResult.map((r) => (
                                    <tr key={r.algorithm}>
                                        <td style={{ color: ALGO_COLORS[r.algorithm], fontWeight: 600 }}>{r.algorithm}</td>
                                        <td>{r.total_faults}</td>
                                        <td>{r.total_hits}</td>
                                        <td>{(r.hit_rate * 100).toFixed(1)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </>
            )}

            {/* Terminology */}
            <div className="glossary">
                <div className="glossary-title">Terminology</div>
                <div className="glossary-grid">
                    <div className="glossary-item"><span className="abbr">FIFO</span><span className="full">— First In First Out</span></div>
                    <div className="glossary-item"><span className="abbr">LRU</span><span className="full">— Least Recently Used</span></div>
                    <div className="glossary-item"><span className="abbr">Page Fault</span><span className="full">— When a requested page is not in memory</span></div>
                    <div className="glossary-item"><span className="abbr">Page Hit</span><span className="full">— When a requested page is already in memory</span></div>
                    <div className="glossary-item"><span className="abbr">Frame</span><span className="full">— A fixed-size block of physical memory</span></div>
                    <div className="glossary-item"><span className="abbr">Ref String</span><span className="full">— Page Reference String (sequence of page requests)</span></div>
                </div>
            </div>
        </div>
    );
}
