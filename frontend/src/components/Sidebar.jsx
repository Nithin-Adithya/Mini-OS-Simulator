import React from 'react';
import { NavLink } from 'react-router-dom';
import { Cpu, BarChart3, HardDrive, AlertTriangle, FileDown } from 'lucide-react';

const links = [
    { to: '/scheduling', icon: Cpu, label: 'Scheduling' },
    { to: '/comparison', icon: BarChart3, label: 'Comparison' },
    { to: '/memory', icon: HardDrive, label: 'Memory' },
    { to: '/deadlock', icon: AlertTriangle, label: 'Deadlock' },
    { to: '/reports', icon: FileDown, label: 'Reports' },
];

export default function Sidebar() {
    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <h1>OS Simulator</h1>
                <span>Learning Tool</span>
            </div>
            <nav className="sidebar-nav">
                {links.map(({ to, icon: Icon, label }) => (
                    <NavLink
                        key={to}
                        to={to}
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        <Icon />
                        <span>{label}</span>
                    </NavLink>
                ))}
            </nav>
        </aside>
    );
}
