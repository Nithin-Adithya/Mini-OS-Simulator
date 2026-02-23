import React, { useState, useEffect } from 'react';
import { Plus, Trash2, Search, AlertTriangle, ShieldCheck } from 'lucide-react';
import { detectDeadlock } from '../api';

/**
 * DeadlockPage - Interactive RAG builder with cycle detection.
 */
export default function DeadlockPage() {
    useEffect(() => { document.title = 'OS Simulator | Deadlock Detection'; }, []);
    const [processes, setProcesses] = useState(['P1', 'P2', 'P3']);
    const [resources, setResources] = useState([{ id: 'R1', instances: 1 }, { id: 'R2', instances: 1 }]);
    const [requests, setRequests] = useState([]);
    const [assignments, setAssignments] = useState([]);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const loadScenario = (type) => {
        if (type === 'deadlock') {
            setProcesses(['P1', 'P2', 'P3']);
            setResources([{ id: 'R1', instances: 1 }, { id: 'R2', instances: 1 }, { id: 'R3', instances: 1 }]);
            setRequests([
                { process: 'P1', resource: 'R2' },
                { process: 'P2', resource: 'R3' },
                { process: 'P3', resource: 'R1' },
            ]);
            setAssignments([
                { resource: 'R1', process: 'P1' },
                { resource: 'R2', process: 'P2' },
                { resource: 'R3', process: 'P3' },
            ]);
        } else {
            setProcesses(['P1', 'P2']);
            setResources([{ id: 'R1', instances: 1 }, { id: 'R2', instances: 1 }]);
            setRequests([{ process: 'P1', resource: 'R2' }]);
            setAssignments([
                { resource: 'R1', process: 'P1' },
                { resource: 'R2', process: 'P2' },
            ]);
        }
        setResult(null);
    };

    const handleDetect = async () => {
        setError('');
        setLoading(true);
        try {
            const res = await detectDeadlock({ processes, resources, requests, assignments });
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Detection failed.');
        } finally { setLoading(false); }
    };

    return (
        <div>
            <div className="page-header">
                <h2>Deadlock Detection</h2>
                <p>Build a Resource Allocation Graph and detect circular wait conditions.</p>
            </div>

            {/* Quick Scenarios */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '16px' }}>
                <button className="btn btn-secondary btn-small" onClick={() => loadScenario('deadlock')}>
                    <AlertTriangle size={14} /> Load Deadlock Scenario
                </button>
                <button className="btn btn-secondary btn-small" onClick={() => loadScenario('safe')}>
                    <ShieldCheck size={14} /> Load Safe Scenario
                </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                {/* Processes */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Processes</span>
                        <button className="btn btn-primary btn-small" onClick={() => setProcesses([...processes, `P${processes.length + 1}`])}>
                            <Plus size={14} />
                        </button>
                    </div>
                    {processes.map((p, i) => (
                        <div key={i} className="form-row mb-16" style={{ alignItems: 'center' }}>
                            <input value={p} onChange={(e) => {
                                const u = [...processes]; u[i] = e.target.value; setProcesses(u);
                            }} style={{ flex: 1 }} />
                            <button className="btn btn-secondary btn-small" onClick={() => setProcesses(processes.filter((_, j) => j !== i))}>
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Resources */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Resources</span>
                        <button className="btn btn-primary btn-small" onClick={() => setResources([...resources, { id: `R${resources.length + 1}`, instances: 1 }])}>
                            <Plus size={14} />
                        </button>
                    </div>
                    {resources.map((r, i) => (
                        <div key={i} className="form-row mb-16" style={{ alignItems: 'center' }}>
                            <input value={r.id} onChange={(e) => {
                                const u = [...resources]; u[i] = { ...u[i], id: e.target.value }; setResources(u);
                            }} style={{ flex: 1 }} placeholder="ID" />
                            <input type="number" value={r.instances} min="1" onChange={(e) => {
                                const u = [...resources]; u[i] = { ...u[i], instances: Number(e.target.value) }; setResources(u);
                            }} style={{ width: '60px' }} />
                            <button className="btn btn-secondary btn-small" onClick={() => setResources(resources.filter((_, j) => j !== i))}>
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginTop: '16px' }}>
                {/* Request edges */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Request Edges (P → R)</span>
                        <button className="btn btn-primary btn-small" onClick={() => setRequests([...requests, { process: processes[0] || '', resource: resources[0]?.id || '' }])}>
                            <Plus size={14} />
                        </button>
                    </div>
                    {requests.map((e, i) => (
                        <div key={i} className="form-row mb-16" style={{ alignItems: 'center' }}>
                            <select value={e.process} onChange={(ev) => {
                                const u = [...requests]; u[i] = { ...u[i], process: ev.target.value }; setRequests(u);
                            }}>
                                {processes.map((p) => <option key={p} value={p}>{p}</option>)}
                            </select>
                            <span style={{ color: 'var(--text-muted)' }}>→</span>
                            <select value={e.resource} onChange={(ev) => {
                                const u = [...requests]; u[i] = { ...u[i], resource: ev.target.value }; setRequests(u);
                            }}>
                                {resources.map((r) => <option key={r.id} value={r.id}>{r.id}</option>)}
                            </select>
                            <button className="btn btn-secondary btn-small" onClick={() => setRequests(requests.filter((_, j) => j !== i))}>
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>

                {/* Assignment edges */}
                <div className="card">
                    <div className="card-header">
                        <span className="card-title">Assignment Edges (R → P)</span>
                        <button className="btn btn-primary btn-small" onClick={() => setAssignments([...assignments, { resource: resources[0]?.id || '', process: processes[0] || '' }])}>
                            <Plus size={14} />
                        </button>
                    </div>
                    {assignments.map((e, i) => (
                        <div key={i} className="form-row mb-16" style={{ alignItems: 'center' }}>
                            <select value={e.resource} onChange={(ev) => {
                                const u = [...assignments]; u[i] = { ...u[i], resource: ev.target.value }; setAssignments(u);
                            }}>
                                {resources.map((r) => <option key={r.id} value={r.id}>{r.id}</option>)}
                            </select>
                            <span style={{ color: 'var(--text-muted)' }}>→</span>
                            <select value={e.process} onChange={(ev) => {
                                const u = [...assignments]; u[i] = { ...u[i], process: ev.target.value }; setAssignments(u);
                            }}>
                                {processes.map((p) => <option key={p} value={p}>{p}</option>)}
                            </select>
                            <button className="btn btn-secondary btn-small" onClick={() => setAssignments(assignments.filter((_, j) => j !== i))}>
                                <Trash2 size={14} />
                            </button>
                        </div>
                    ))}
                </div>
            </div>

            <div style={{ marginTop: '16px' }}>
                <button className="btn btn-primary" onClick={handleDetect} disabled={loading}>
                    <Search size={16} /> {loading ? 'Detecting...' : 'Detect Deadlock'}
                </button>
            </div>

            {error && <div className="error-message mt-16">{error}</div>}

            {result && (
                <div className={`result-banner mt-16 ${result.deadlocked ? 'deadlocked' : 'safe'}`}>
                    {result.deadlocked ? <AlertTriangle size={22} /> : <ShieldCheck size={22} />}
                    <div>
                        <strong>{result.deadlocked ? 'DEADLOCK DETECTED' : 'SYSTEM IS SAFE'}</strong>
                        {result.deadlocked && result.cycle && (
                            <div style={{ fontSize: '0.85rem', marginTop: '4px', fontWeight: 400 }}>
                                Cycle: {result.cycle.join(' → ')} → {result.cycle[0]}
                            </div>
                        )}
                    </div>
                </div>
            )}

            {/* Visual Graph */}
            {result?.graph && (
                <div className="card mt-16">
                    <div className="card-header">
                        <span className="card-title">Resource Allocation Graph</span>
                    </div>
                    <div style={{ display: 'flex', gap: '24px', flexWrap: 'wrap', justifyContent: 'center', padding: '20px 0' }}>
                        {result.graph.nodes.map((n) => (
                            <div key={n.id} style={{
                                width: n.type === 'process' ? '60px' : '60px',
                                height: n.type === 'process' ? '60px' : '60px',
                                borderRadius: n.type === 'process' ? '50%' : '8px',
                                background: n.type === 'process' ? 'var(--cyan-dim)' : 'var(--violet-dim)',
                                border: `2px solid ${n.type === 'process' ? 'var(--cyan)' : 'var(--violet)'}`,
                                display: 'flex', alignItems: 'center', justifyContent: 'center',
                                fontWeight: 600, fontSize: '0.85rem',
                                color: n.type === 'process' ? 'var(--cyan)' : 'var(--violet)',
                            }}>
                                {n.id}
                            </div>
                        ))}
                    </div>
                    <div style={{ textAlign: 'center', padding: '8px 0' }}>
                        <div style={{ display: 'flex', gap: '24px', justifyContent: 'center', flexWrap: 'wrap' }}>
                            {result.graph.edges.map((e, i) => (
                                <span key={i} style={{ fontSize: '0.8rem', color: e.type === 'request' ? 'var(--orange)' : 'var(--green)', fontFamily: 'var(--font-mono)' }}>
                                    {e.from} → {e.to} ({e.type})
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Terminology */}
            <div className="glossary">
                <div className="glossary-title">Terminology</div>
                <div className="glossary-grid">
                    <div className="glossary-item"><span className="abbr">RAG</span><span className="full">— Resource Allocation Graph</span></div>
                    <div className="glossary-item"><span className="abbr">DFS</span><span className="full">— Depth-First Search</span></div>
                    <div className="glossary-item"><span className="abbr">P → R</span><span className="full">— Process requests a Resource (Request Edge)</span></div>
                    <div className="glossary-item"><span className="abbr">R → P</span><span className="full">— Resource assigned to a Process (Assignment Edge)</span></div>
                    <div className="glossary-item"><span className="abbr">Deadlock</span><span className="full">— Circular wait where processes block each other</span></div>
                    <div className="glossary-item"><span className="abbr">Cycle</span><span className="full">— A closed path in the graph indicating deadlock</span></div>
                </div>
            </div>
        </div>
    );
}
