"""
OS Simulator Core Modules
─────────────────────────
Exports the main classes used by the simulator facade and API layer.
"""

from .process_manager import Process, ProcessState, ProcessManager
from .scheduler import (
    FCFSScheduler,
    RoundRobinScheduler,
    SJFScheduler,
    PriorityScheduler,
)
from .metrics import MetricsCalculator
from .memory_manager import FIFOPageReplacer, LRUPageReplacer, OptimalPageReplacer
from .deadlock_detector import ResourceAllocationGraph

__all__ = [
    "Process",
    "ProcessState",
    "ProcessManager",
    "FCFSScheduler",
    "RoundRobinScheduler",
    "SJFScheduler",
    "PriorityScheduler",
    "MetricsCalculator",
    "FIFOPageReplacer",
    "LRUPageReplacer",
    "OptimalPageReplacer",
    "ResourceAllocationGraph",
]
