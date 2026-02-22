import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import SchedulingPage from './pages/SchedulingPage';
import ComparisonPage from './pages/ComparisonPage';
import MemoryPage from './pages/MemoryPage';
import DeadlockPage from './pages/DeadlockPage';
import ReportsPage from './pages/ReportsPage';

export default function App() {
  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<Navigate to="/scheduling" replace />} />
            <Route path="/scheduling" element={<SchedulingPage />} />
            <Route path="/comparison" element={<ComparisonPage />} />
            <Route path="/memory" element={<MemoryPage />} />
            <Route path="/deadlock" element={<DeadlockPage />} />
            <Route path="/reports" element={<ReportsPage />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
