import React, { useState, useEffect } from 'react';
import { Play } from 'lucide-react';
import ProcessForm from '../components/ProcessForm';
import GanttChart from '../components/GanttChart';
import MetricsTable from '../components/MetricsTable';
import { runScheduling } from '../api';

/**
 * SchedulingPage - Process input, algorithm selection, Gantt chart + metrics.
 */
export default function SchedulingPage() {
    useEffect(() => { document.title = 'OS Simulator | CPU Scheduling'; }, []);
    const [processes, setProcesses] = useState([]);
    const [algorithm, setAlgorithm] = useState('fcfs');
    const [quantum, setQuantum] = useState(2);
    const [result, setResult] = useState(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');

    const handleRun = async () => {
        if (processes.length === 0) {
            setError('Add at least one process.');
            return;
        }
        setError('');
        setLoading(true);
        try {
            const res = await runScheduling(processes, algorithm, quantum);
            setResult(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Simulation failed. Is the backend running?');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2>CPU Scheduling</h2>
                <p>Configure processes and run a scheduling algorithm to see the Gantt chart and metrics.</p>
            </div>

            <ProcessForm processes={processes} setProcesses={setProcesses} />

            <div className="card mt-16">
                <div className="form-row">
                    <div className="form-group">
                        <label>Algorithm</label>
                        <select value={algorithm} onChange={(e) => setAlgorithm(e.target.value)}>
                            <option value="fcfs">First Come First Serve</option>
                            <option value="sjf">Shortest Job First</option>
                            <option value="priority">Priority Scheduling</option>
                            <option value="rr">Round Robin</option>
                        </select>
                    </div>

                    {algorithm === 'rr' && (
                        <div className="form-group">
                            <label>Time Quantum</label>
                            <input
                                type="number"
                                min="1"
                                value={quantum}
                                onChange={(e) => setQuantum(Number(e.target.value))}
                                style={{ width: '80px' }}
                            />
                        </div>
                    )}

                    <button className="btn btn-primary" onClick={handleRun} disabled={loading}>
                        <Play size={16} /> {loading ? 'Running...' : 'Simulate'}
                    </button>
                </div>
            </div>

            {error && <div className="error-message mt-16">{error}</div>}

            {result && (
                <>
                    {/* Aggregate Stats */}
                    <div className="stats-grid mt-24">
                        <div className="stat-card">
                            <div className="stat-value">{result.aggregates.avg_waiting_time}</div>
                            <div className="stat-label">Avg Waiting Time</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{result.aggregates.avg_turnaround_time}</div>
                            <div className="stat-label">Avg Turnaround Time</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{result.aggregates.avg_response_time}</div>
                            <div className="stat-label">Avg Response Time</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{result.aggregates.cpu_utilization}%</div>
                            <div className="stat-label">CPU Utilization</div>
                        </div>
                        <div className="stat-card">
                            <div className="stat-value">{result.aggregates.throughput}</div>
                            <div className="stat-label">Throughput</div>
                        </div>
                    </div>

                    <GanttChart timeline={result.timeline} />
                    <MetricsTable metrics={result.metrics} />

                    {/* Simulation Log */}
                    {result.log && result.log.length > 0 && (
                        <div className="card mt-16">
                            <div className="card-header">
                                <span className="card-title">Simulation Log</span>
                            </div>
                            <div className="step-log">
                                {result.log.map((line, i) => (
                                    <div key={i} className="log-line">{line}</div>
                                ))}
                            </div>
                        </div>
                    )}
                </>
            )}

            {/* Terminology */}
            <div className="glossary">
                <div className="glossary-title">Terminology</div>
                <div className="glossary-grid">
                    <div className="glossary-item"><span className="abbr">CPU</span><span className="full">— Central Processing Unit</span></div>
                    <div className="glossary-item"><span className="abbr">FCFS</span><span className="full">— First Come First Serve</span></div>
                    <div className="glossary-item"><span className="abbr">SJF</span><span className="full">— Shortest Job First</span></div>
                    <div className="glossary-item"><span className="abbr">RR</span><span className="full">— Round Robin</span></div>
                    <div className="glossary-item"><span className="abbr">WT</span><span className="full">— Waiting Time</span></div>
                    <div className="glossary-item"><span className="abbr">TAT</span><span className="full">— Turnaround Time</span></div>
                    <div className="glossary-item"><span className="abbr">RT</span><span className="full">— Response Time</span></div>
                    <div className="glossary-item"><span className="abbr">PID</span><span className="full">— Process Identifier</span></div>
                </div>
            </div>
        </div>
    );
}
