"""
scheduler.py - CPU scheduling algorithm implementations.

Provides four classic scheduling algorithms:
  • FCFS  (First Come First Serve)   — non-preemptive
  • SJF   (Shortest Job First)       — non-preemptive
  • Priority Scheduling              — non-preemptive, lower number = higher priority
  • Round Robin                      — preemptive, configurable time quantum

Each scheduler returns a ScheduleResult containing the Gantt chart
timeline, per-process metrics, and a step-by-step simulation log.
"""

from __future__ import annotations

import copy
from dataclasses import dataclass, field
from typing import List, Optional

from .process_manager import Process, ProcessState


# ── Result Container ────────────────────────────────────


@dataclass
class ScheduleResult:
    """
    Output of a scheduling simulation.

    Attributes:
        timeline:   Gantt chart entries [{pid, start, end}, …].
        processes:  Per-process dicts with computed timing fields.
        log:        Human-readable step-by-step log lines.
    """
    timeline: List[dict] = field(default_factory=list)
    processes: List[dict] = field(default_factory=list)
    log: List[str] = field(default_factory=list)


# ── Helper ──────────────────────────────────────────────


def _deep_copy_processes(processes: List[Process]) -> List[Process]:
    """Return independent copies so the originals are untouched."""
    return copy.deepcopy(processes)


def _finalize(procs: List[Process], timeline: List[dict], log: List[str]) -> ScheduleResult:
    """Compute per-process metrics and package the result."""
    proc_dicts = []
    for p in procs:
        if p.completion_time is not None and p.start_time is not None:
            p.turnaround_time = p.completion_time - p.arrival_time
            p.waiting_time = p.turnaround_time - p.burst_time
            p.response_time = p.start_time - p.arrival_time
        proc_dicts.append(p.to_dict())
    return ScheduleResult(timeline=timeline, processes=proc_dicts, log=log)


# ══════════════════════════════════════════════════════════
#  1. FCFS — First Come First Serve
# ══════════════════════════════════════════════════════════


class FCFSScheduler:
    """
    Non-preemptive scheduler that executes processes in order
    of their arrival time.
    """

    def run(self, processes: List[Process]) -> ScheduleResult:
        procs = _deep_copy_processes(processes)
        procs.sort(key=lambda p: p.arrival_time)

        current_time = 0
        timeline: List[dict] = []
        log: List[str] = []

        for p in procs:
            # Handle idle gap
            if current_time < p.arrival_time:
                log.append(f"t={current_time}: CPU idle until t={p.arrival_time}")
                timeline.append({"pid": "IDLE", "start": current_time, "end": p.arrival_time})
                current_time = p.arrival_time

            p.start_time = current_time
            p.state = ProcessState.RUNNING
            log.append(f"t={current_time}: {p.pid} starts (burst={p.burst_time})")

            end_time = current_time + p.burst_time
            timeline.append({"pid": p.pid, "start": current_time, "end": end_time})

            current_time = end_time
            p.completion_time = current_time
            p.remaining_time = 0
            p.state = ProcessState.COMPLETED
            log.append(f"t={current_time}: {p.pid} completed")

        return _finalize(procs, timeline, log)


# ══════════════════════════════════════════════════════════
#  2. SJF — Shortest Job First (non-preemptive)
# ══════════════════════════════════════════════════════════


class SJFScheduler:
    """
    Non-preemptive scheduler that always picks the ready process
    with the shortest burst time.  Ties broken by arrival time.
    """

    def run(self, processes: List[Process]) -> ScheduleResult:
        procs = _deep_copy_processes(processes)
        n = len(procs)
        completed = 0
        current_time = 0
        visited = [False] * n
        timeline: List[dict] = []
        log: List[str] = []

        while completed < n:
            # Find ready processes
            ready = [
                (i, p) for i, p in enumerate(procs)
                if not visited[i] and p.arrival_time <= current_time
            ]
            if not ready:
                # Jump to next arrival
                next_arrival = min(p.arrival_time for i, p in enumerate(procs) if not visited[i])
                log.append(f"t={current_time}: CPU idle until t={next_arrival}")
                timeline.append({"pid": "IDLE", "start": current_time, "end": next_arrival})
                current_time = next_arrival
                continue

            # Pick shortest burst; tie-break by arrival
            ready.sort(key=lambda x: (x[1].burst_time, x[1].arrival_time))
            idx, p = ready[0]
            visited[idx] = True

            p.start_time = current_time
            p.state = ProcessState.RUNNING
            log.append(f"t={current_time}: {p.pid} starts (burst={p.burst_time})")

            end_time = current_time + p.burst_time
            timeline.append({"pid": p.pid, "start": current_time, "end": end_time})

            current_time = end_time
            p.completion_time = current_time
            p.remaining_time = 0
            p.state = ProcessState.COMPLETED
            log.append(f"t={current_time}: {p.pid} completed")
            completed += 1

        return _finalize(procs, timeline, log)


# ══════════════════════════════════════════════════════════
#  3. Priority Scheduling (non-preemptive)
# ══════════════════════════════════════════════════════════


class PriorityScheduler:
    """
    Non-preemptive scheduler using priority values.
    Lower priority number = higher priority.
    Ties broken by arrival time.
    """

    def run(self, processes: List[Process]) -> ScheduleResult:
        procs = _deep_copy_processes(processes)
        n = len(procs)
        completed = 0
        current_time = 0
        visited = [False] * n
        timeline: List[dict] = []
        log: List[str] = []

        while completed < n:
            ready = [
                (i, p) for i, p in enumerate(procs)
                if not visited[i] and p.arrival_time <= current_time
            ]
            if not ready:
                next_arrival = min(p.arrival_time for i, p in enumerate(procs) if not visited[i])
                log.append(f"t={current_time}: CPU idle until t={next_arrival}")
                timeline.append({"pid": "IDLE", "start": current_time, "end": next_arrival})
                current_time = next_arrival
                continue

            # Pick highest priority (lowest number); tie-break by arrival
            ready.sort(key=lambda x: (x[1].priority, x[1].arrival_time))
            idx, p = ready[0]
            visited[idx] = True

            p.start_time = current_time
            p.state = ProcessState.RUNNING
            log.append(f"t={current_time}: {p.pid} starts (priority={p.priority}, burst={p.burst_time})")

            end_time = current_time + p.burst_time
            timeline.append({"pid": p.pid, "start": current_time, "end": end_time})

            current_time = end_time
            p.completion_time = current_time
            p.remaining_time = 0
            p.state = ProcessState.COMPLETED
            log.append(f"t={current_time}: {p.pid} completed")
            completed += 1

        return _finalize(procs, timeline, log)


# ══════════════════════════════════════════════════════════
#  4. Round Robin (preemptive)
# ══════════════════════════════════════════════════════════


class RoundRobinScheduler:
    """
    Preemptive scheduler with a configurable time quantum.
    Processes rotate through the ready queue, each running
    for at most `quantum` time units before being preempted.
    """

    def __init__(self, quantum: int = 2):
        if quantum <= 0:
            raise ValueError("Time quantum must be a positive integer.")
        self.quantum = quantum

    def run(self, processes: List[Process]) -> ScheduleResult:
        procs = _deep_copy_processes(processes)
        procs.sort(key=lambda p: p.arrival_time)

        current_time = 0
        timeline: List[dict] = []
        log: List[str] = []

        from collections import deque
        ready_queue: deque = deque()
        remaining = {p.pid: p for p in procs}
        arrived = set()
        completed_count = 0
        n = len(procs)

        # Seed with processes arriving at time 0
        for p in procs:
            if p.arrival_time <= current_time:
                ready_queue.append(p)
                arrived.add(p.pid)

        while completed_count < n:
            if not ready_queue:
                # Jump to next arrival
                future = [p for p in procs if p.pid not in arrived]
                if not future:
                    break
                next_arrival = min(p.arrival_time for p in future)
                log.append(f"t={current_time}: CPU idle until t={next_arrival}")
                timeline.append({"pid": "IDLE", "start": current_time, "end": next_arrival})
                current_time = next_arrival
                for p in procs:
                    if p.pid not in arrived and p.arrival_time <= current_time:
                        ready_queue.append(p)
                        arrived.add(p.pid)
                continue

            p = ready_queue.popleft()

            # Record first start time
            if p.start_time is None:
                p.start_time = current_time

            run_time = min(self.quantum, p.remaining_time)
            p.state = ProcessState.RUNNING
            log.append(
                f"t={current_time}: {p.pid} runs for {run_time} "
                f"(remaining={p.remaining_time}→{p.remaining_time - run_time})"
            )

            start = current_time
            current_time += run_time
            p.remaining_time -= run_time
            timeline.append({"pid": p.pid, "start": start, "end": current_time})

            # Enqueue newly arrived processes BEFORE re-enqueuing current
            for proc in procs:
                if proc.pid not in arrived and proc.arrival_time <= current_time:
                    ready_queue.append(proc)
                    arrived.add(proc.pid)

            if p.remaining_time == 0:
                p.completion_time = current_time
                p.state = ProcessState.COMPLETED
                completed_count += 1
                log.append(f"t={current_time}: {p.pid} completed")
            else:
                p.state = ProcessState.READY
                ready_queue.append(p)

        return _finalize(procs, timeline, log)
