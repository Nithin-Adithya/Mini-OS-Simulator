"""
test_scheduler.py - Unit tests for CPU scheduling algorithms.

Verifies correctness of FCFS, SJF, Priority, and Round Robin schedulers
against hand-calculated expected values.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.process_manager import Process
from modules.scheduler import (
    FCFSScheduler,
    SJFScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
)


def make_processes():
    """Standard 3-process test set."""
    return [
        Process(pid="P1", arrival_time=0, burst_time=6),
        Process(pid="P2", arrival_time=1, burst_time=4),
        Process(pid="P3", arrival_time=2, burst_time=2),
    ]


# ── FCFS ─────────────────────────────────────────────────

def test_fcfs_order():
    """FCFS should execute in arrival order."""
    result = FCFSScheduler().run(make_processes())
    pids = [e["pid"] for e in result.timeline if e["pid"] != "IDLE"]
    assert pids == ["P1", "P2", "P3"]


def test_fcfs_metrics():
    """FCFS waiting times: P1=0, P2=5, P3=8  →  avg=4.33"""
    result = FCFSScheduler().run(make_processes())
    wt = {p["pid"]: p["waiting_time"] for p in result.processes}
    assert wt["P1"] == 0
    assert wt["P2"] == 5   # start=6, arrival=1 → WT=6-1-4=5? Actually WT = TAT - BT
    # P1: completes at 6, TAT=6, WT=0
    # P2: completes at 10, TAT=9, WT=5
    # P3: completes at 12, TAT=10, WT=8
    assert wt["P3"] == 8


def test_fcfs_completion_times():
    result = FCFSScheduler().run(make_processes())
    ct = {p["pid"]: p["completion_time"] for p in result.processes}
    assert ct["P1"] == 6
    assert ct["P2"] == 10
    assert ct["P3"] == 12


# ── SJF ──────────────────────────────────────────────────

def test_sjf_picks_shortest():
    """SJF should pick P3 (burst=2) over P2 (burst=4) when both are ready."""
    result = SJFScheduler().run(make_processes())
    # P1 runs first (only one at t=0). At t=6, P2 and P3 are ready.
    # SJF picks P3 (burst=2), then P2 (burst=4).
    timeline_pids = [e["pid"] for e in result.timeline if e["pid"] != "IDLE"]
    assert timeline_pids == ["P1", "P3", "P2"]


def test_sjf_metrics():
    result = SJFScheduler().run(make_processes())
    wt = {p["pid"]: p["waiting_time"] for p in result.processes}
    # P1: 0→6, WT=0
    # P3: 6→8, WT=6-2=4   (TAT=8-2=6, WT=6-2=4)
    # P2: 8→12, WT=8-1-4=7? (TAT=12-1=11, WT=11-4=7)
    assert wt["P1"] == 0
    assert wt["P3"] == 4
    assert wt["P2"] == 7


# ── Priority ─────────────────────────────────────────────

def test_priority_order():
    """Lower priority number = higher priority."""
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=4, priority=3),
        Process(pid="P2", arrival_time=0, burst_time=3, priority=1),
        Process(pid="P3", arrival_time=0, burst_time=5, priority=2),
    ]
    result = PriorityScheduler().run(procs)
    pids = [e["pid"] for e in result.timeline if e["pid"] != "IDLE"]
    assert pids == ["P2", "P3", "P1"]


# ── Round Robin ──────────────────────────────────────────

def test_rr_preemption():
    """RR(q=2) should preempt processes after 2 time units."""
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=0, burst_time=3),
    ]
    result = RoundRobinScheduler(quantum=2).run(procs)
    pids = [e["pid"] for e in result.timeline]
    # Expected: P1(2), P2(2), P1(2), P2(1), P1(1)
    assert pids == ["P1", "P2", "P1", "P2", "P1"]


def test_rr_completion():
    """RR(q=2): P1(burst=5), P2(burst=3) — verify completion times."""
    procs = [
        Process(pid="P1", arrival_time=0, burst_time=5),
        Process(pid="P2", arrival_time=0, burst_time=3),
    ]
    result = RoundRobinScheduler(quantum=2).run(procs)
    ct = {p["pid"]: p["completion_time"] for p in result.processes}
    assert ct["P2"] == 7   # P2 runs at [2-4] and [6-7]
    assert ct["P1"] == 8   # P1 runs at [0-2], [4-6], [7-8]


def test_rr_quantum_validation():
    """Quantum must be positive."""
    try:
        RoundRobinScheduler(quantum=0)
        assert False, "Should have raised ValueError"
    except ValueError:
        pass


if __name__ == "__main__":
    tests = [v for k, v in globals().items() if k.startswith("test_")]
    passed = 0
    for t in tests:
        try:
            t()
            print(f"  ✓ {t.__name__}")
            passed += 1
        except AssertionError as e:
            print(f"  ✗ {t.__name__}: {e}")
        except Exception as e:
            print(f"  ✗ {t.__name__}: {e}")
    print(f"\n{passed}/{len(tests)} tests passed")
