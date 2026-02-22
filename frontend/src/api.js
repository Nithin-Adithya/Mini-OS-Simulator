/**
 * api.js - Axios wrapper for all backend API endpoints.
 */
import axios from 'axios';

const api = axios.create({
    baseURL: '/api',
    headers: { 'Content-Type': 'application/json' },
});

/** Run a single scheduling algorithm */
export const runScheduling = (processes, algorithm, quantum = 2) =>
    api.post('/schedule', { processes, algorithm, quantum });

/** Compare all scheduling algorithms */
export const compareAlgorithms = (processes, quantum = 2) =>
    api.post('/compare', { processes, quantum });

/** Run page replacement simulation */
export const runMemory = (referenceString, numFrames, algorithm) =>
    api.post('/memory', { reference_string: referenceString, num_frames: numFrames, algorithm });

/** Compare all page replacement algorithms */
export const compareMemory = (referenceString, numFrames) =>
    api.post('/memory/compare', { reference_string: referenceString, num_frames: numFrames });

/** Detect deadlock from RAG data */
export const detectDeadlock = (graphData) =>
    api.post('/deadlock', graphData);

/** Get sample data */
export const getSampleData = () => api.get('/sample-data');

/** Export data as CSV */
export const exportCSV = (data) =>
    api.post('/export', data, { responseType: 'blob' });

export default api;
