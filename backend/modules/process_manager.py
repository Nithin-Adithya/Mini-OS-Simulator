"""
process_manager.py - Process creation, state tracking, and validation.

Provides the Process dataclass representing a single OS process with
scheduling attributes and timing fields, plus a ProcessManager for
bulk operations (create, load, validate, reset).
"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class ProcessState(str, Enum):
    """Possible lifecycle states of a process."""
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    COMPLETED = "COMPLETED"


@dataclass
class Process:
    """
    Represents a single process in the simulator.

    Attributes:
        pid:              Unique process identifier (e.g. "P1").
        arrival_time:     Time at which the process enters the ready queue.
        burst_time:       Total CPU burst time required.
        priority:         Priority level (lower number = higher priority).
        memory_required:  Memory needed in KB.
        state:            Current lifecycle state.
        remaining_time:   CPU time still needed (decremented during execution).
        start_time:       Time the process first gets the CPU (None until scheduled).
        completion_time:  Time the process finishes execution (None until done).
        waiting_time:     Computed after simulation.
        turnaround_time:  Computed after simulation.
        response_time:    Computed after simulation.
    """
    pid: str
    arrival_time: int
    burst_time: int
    priority: int = 0
    memory_required: int = 0
    state: ProcessState = ProcessState.READY
    remaining_time: Optional[int] = None
    start_time: Optional[int] = None
    completion_time: Optional[int] = None
    waiting_time: Optional[int] = None
    turnaround_time: Optional[int] = None
    response_time: Optional[int] = None

    def __post_init__(self):
        if self.remaining_time is None:
            self.remaining_time = self.burst_time

    def reset(self) -> None:
        """Reset process to initial state for re-simulation."""
        self.state = ProcessState.READY
        self.remaining_time = self.burst_time
        self.start_time = None
        self.completion_time = None
        self.waiting_time = None
        self.turnaround_time = None
        self.response_time = None

    def to_dict(self) -> dict:
        """Serialize process to a plain dictionary."""
        return {
            "pid": self.pid,
            "arrival_time": self.arrival_time,
            "burst_time": self.burst_time,
            "priority": self.priority,
            "memory_required": self.memory_required,
            "state": self.state.value,
            "remaining_time": self.remaining_time,
            "start_time": self.start_time,
            "completion_time": self.completion_time,
            "waiting_time": self.waiting_time,
            "turnaround_time": self.turnaround_time,
            "response_time": self.response_time,
        }


class ProcessManager:
    """
    Manages a collection of processes for the simulator.

    Supports creating individual processes, bulk-loading from
    dictionaries or CSV files, validation, and resetting state.
    """

    def __init__(self):
        self._processes: List[Process] = []

    # ── Creation ─────────────────────────────────────────

    def add_process(
        self,
        pid: str,
        arrival_time: int,
        burst_time: int,
        priority: int = 0,
        memory_required: int = 0,
    ) -> Process:
        """Create and register a new process."""
        proc = Process(
            pid=pid,
            arrival_time=arrival_time,
            burst_time=burst_time,
            priority=priority,
            memory_required=memory_required,
        )
        self._processes.append(proc)
        return proc

    def load_from_dicts(self, data: List[dict]) -> List[Process]:
        """
        Bulk-load processes from a list of dictionaries.

        Each dict must contain keys: pid, arrival_time, burst_time.
        Optional keys: priority, memory_required.
        """
        self._processes.clear()
        for entry in data:
            self.add_process(
                pid=str(entry["pid"]),
                arrival_time=int(entry["arrival_time"]),
                burst_time=int(entry["burst_time"]),
                priority=int(entry.get("priority", 0)),
                memory_required=int(entry.get("memory_required", 0)),
            )
        return self._processes

    def load_from_csv(self, filepath: str) -> List[Process]:
        """Load processes from a CSV file."""
        with open(filepath, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)
        return self.load_from_dicts(rows)

    # ── Access ───────────────────────────────────────────

    def get_all(self) -> List[Process]:
        """Return a copy of all registered processes."""
        return list(self._processes)

    def get_by_pid(self, pid: str) -> Optional[Process]:
        """Find a process by its PID."""
        for p in self._processes:
            if p.pid == pid:
                return p
        return None

    # ── Utilities ────────────────────────────────────────

    def reset(self) -> None:
        """Reset all processes to their initial state."""
        for p in self._processes:
            p.reset()

    def clear(self) -> None:
        """Remove all processes."""
        self._processes.clear()

    def validate(self) -> List[str]:
        """
        Validate all processes and return a list of error messages.
        An empty list means all processes are valid.
        """
        errors: List[str] = []
        seen_pids: set = set()
        for p in self._processes:
            if p.pid in seen_pids:
                errors.append(f"Duplicate PID: {p.pid}")
            seen_pids.add(p.pid)
            if p.arrival_time < 0:
                errors.append(f"{p.pid}: arrival_time cannot be negative")
            if p.burst_time <= 0:
                errors.append(f"{p.pid}: burst_time must be positive")
            if p.priority < 0:
                errors.append(f"{p.pid}: priority cannot be negative")
            if p.memory_required < 0:
                errors.append(f"{p.pid}: memory_required cannot be negative")
        return errors

    def __len__(self) -> int:
        return len(self._processes)

    def __repr__(self) -> str:
        return f"ProcessManager(count={len(self._processes)})"
