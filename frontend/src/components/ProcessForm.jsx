import React, { useState } from 'react';
import { Plus, Trash2, Database } from 'lucide-react';
import { getSampleData } from '../api';

/**
 * ProcessForm - Dynamic form for adding/editing processes.
 * Supports manual entry and loading sample data.
 */

const emptyProcess = { pid: '', arrival_time: 0, burst_time: 1, priority: 0, memory_required: 0 };

export default function ProcessForm({ processes, setProcesses }) {
    const [error, setError] = useState('');

    const addRow = () => {
        const nextId = `P${processes.length + 1}`;
        setProcesses([...processes, { ...emptyProcess, pid: nextId }]);
    };

    const removeRow = (index) => {
        setProcesses(processes.filter((_, i) => i !== index));
    };

    const updateField = (index, field, value) => {
        const updated = [...processes];
        updated[index] = {
            ...updated[index],
            [field]: field === 'pid' ? value : Number(value),
        };
        setProcesses(updated);
    };

    const loadSample = async () => {
        try {
            const res = await getSampleData();
            setProcesses(res.data.processes);
            setError('');
        } catch {
            setError('Failed to load sample data. Is the backend running?');
        }
    };

    return (
        <div className="card">
            <div className="card-header">
                <span className="card-title">Processes</span>
                <div style={{ display: 'flex', gap: '8px' }}>
                    <button className="btn btn-secondary btn-small" onClick={loadSample}>
                        <Database size={14} /> Sample Data
                    </button>
                    <button className="btn btn-primary btn-small" onClick={addRow}>
                        <Plus size={14} /> Add
                    </button>
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div style={{ overflowX: 'auto' }}>
                <table className="data-table">
                    <thead>
                        <tr>
                            <th>PID</th>
                            <th>Arrival Time</th>
                            <th>Burst Time</th>
                            <th>Priority</th>
                            <th>Memory (KB)</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        {processes.map((p, i) => (
                            <tr key={i}>
                                <td>
                                    <input
                                        value={p.pid}
                                        onChange={(e) => updateField(i, 'pid', e.target.value)}
                                        style={{ width: '60px' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        min="0"
                                        value={p.arrival_time}
                                        onChange={(e) => updateField(i, 'arrival_time', e.target.value)}
                                        style={{ width: '70px' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        min="1"
                                        value={p.burst_time}
                                        onChange={(e) => updateField(i, 'burst_time', e.target.value)}
                                        style={{ width: '70px' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        min="0"
                                        value={p.priority}
                                        onChange={(e) => updateField(i, 'priority', e.target.value)}
                                        style={{ width: '70px' }}
                                    />
                                </td>
                                <td>
                                    <input
                                        type="number"
                                        min="0"
                                        value={p.memory_required}
                                        onChange={(e) => updateField(i, 'memory_required', e.target.value)}
                                        style={{ width: '70px' }}
                                    />
                                </td>
                                <td>
                                    <button
                                        className="btn btn-secondary btn-small"
                                        onClick={() => removeRow(i)}
                                        style={{ padding: '6px 8px' }}
                                    >
                                        <Trash2 size={14} />
                                    </button>
                                </td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>

            {processes.length === 0 && (
                <p style={{ textAlign: 'center', color: 'var(--text-muted)', padding: '20px' }}>
                    No processes. Click "Add" or "Sample Data" to begin.
                </p>
            )}
        </div>
    );
}
