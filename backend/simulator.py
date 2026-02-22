"""
simulator.py - Facade orchestrating all OS simulation modules.

Provides a single entry-point class that coordinates process management,
scheduling, metrics computation, memory simulation, and deadlock detection.
"""

from __future__ import annotations

import csv
import io
import logging
from typing import Any, Dict, List, Optional

from config import DEFAULT_TIME_QUANTUM, DEFAULT_MEMORY_FRAMES
from modules.process_manager import ProcessManager, Process
from modules.scheduler import (
    FCFSScheduler,
    SJFScheduler,
    PriorityScheduler,
    RoundRobinScheduler,
    ScheduleResult,
)
from modules.metrics import MetricsCalculator
from modules.memory_manager import (
    FIFOPageReplacer,
    LRUPageReplacer,
    OptimalPageReplacer,
)
from modules.deadlock_detector import ResourceAllocationGraph

logger = logging.getLogger("os_simulator.simulator")

# Map algorithm names to scheduler classes
SCHEDULER_MAP = {
    "fcfs": FCFSScheduler,
    "sjf": SJFScheduler,
    "priority": PriorityScheduler,
    "rr": RoundRobinScheduler,
}

MEMORY_ALGO_MAP = {
    "fifo": FIFOPageReplacer,
    "lru": LRUPageReplacer,
    "optimal": OptimalPageReplacer,
}


class Simulator:
    """
    Top-level facade for the Mini OS Simulator.

    Usage:
        sim = Simulator()
        sim.load_processes([...])
        result = sim.run_scheduling("fcfs")
        comparison = sim.run_comparison()
    """

    def __init__(self):
        self.pm = ProcessManager()

    # ── Process Loading ──────────────────────────────────

    def load_processes(self, data: List[dict]) -> None:
        """Load processes from a list of dicts."""
        self.pm.load_from_dicts(data)
        errors = self.pm.validate()
        if errors:
            raise ValueError(f"Invalid process data: {'; '.join(errors)}")
        logger.info("Loaded %d processes", len(self.pm))

    def load_processes_from_csv(self, filepath: str) -> None:
        """Load processes from a CSV file."""
        self.pm.load_from_csv(filepath)
        errors = self.pm.validate()
        if errors:
            raise ValueError(f"Invalid process data: {'; '.join(errors)}")
        logger.info("Loaded %d processes from %s", len(self.pm), filepath)

    # ── Scheduling ───────────────────────────────────────

    def run_scheduling(
        self, algorithm: str, quantum: int = DEFAULT_TIME_QUANTUM
    ) -> Dict[str, Any]:
        """
        Run a single scheduling algorithm.

        Args:
            algorithm: One of 'fcfs', 'sjf', 'priority', 'rr'.
            quantum:   Time quantum (only used for Round Robin).

        Returns:
            {timeline, metrics, aggregates, log}
        """
        algo = algorithm.lower()
        if algo not in SCHEDULER_MAP:
            raise ValueError(f"Unknown algorithm '{algorithm}'. Choose from: {list(SCHEDULER_MAP)}")

        self.pm.reset()
        processes = self.pm.get_all()

        if algo == "rr":
            scheduler = RoundRobinScheduler(quantum=quantum)
        else:
            scheduler = SCHEDULER_MAP[algo]()

        result: ScheduleResult = scheduler.run(processes)
        metrics = MetricsCalculator.calculate(result.processes, result.timeline)

        logger.info("Scheduling [%s] complete — avg WT=%.2f, avg TAT=%.2f",
                     algo.upper(), metrics["avg_waiting_time"], metrics["avg_turnaround_time"])

        return {
            "algorithm": algo.upper(),
            "timeline": result.timeline,
            "metrics": metrics["per_process"],
            "aggregates": {
                "avg_waiting_time": metrics["avg_waiting_time"],
                "avg_turnaround_time": metrics["avg_turnaround_time"],
                "avg_response_time": metrics["avg_response_time"],
                "cpu_utilization": metrics["cpu_utilization"],
                "throughput": metrics["throughput"],
            },
            "log": result.log,
        }

    def run_comparison(self, quantum: int = DEFAULT_TIME_QUANTUM) -> Dict[str, Any]:
        """
        Run all four scheduling algorithms and return a comparison.

        Returns:
            {results: [{algorithm, timeline, metrics, aggregates, log}, …],
             comparison: [{algorithm, avg_wt, avg_tat, …}, …]}
        """
        all_results = {}
        all_metrics = {}
        for algo in SCHEDULER_MAP:
            res = self.run_scheduling(algo, quantum=quantum)
            all_results[algo.upper()] = res
            all_metrics[algo.upper()] = res["aggregates"]

        comparison = MetricsCalculator.compare(
            {k: {**v, "per_process": all_results[k]["metrics"]}
             for k, v in all_metrics.items()}
        )

        return {
            "results": list(all_results.values()),
            "comparison": comparison,
        }

    # ── Memory Management ────────────────────────────────

    def run_memory_simulation(
        self,
        reference_string: List[int],
        num_frames: int = DEFAULT_MEMORY_FRAMES,
        algorithm: str = "fifo",
    ) -> Dict[str, Any]:
        """
        Run a page replacement simulation.

        Args:
            reference_string: Sequence of page numbers.
            num_frames:       Number of page frames available.
            algorithm:        One of 'fifo', 'lru', 'optimal'.

        Returns:
            {algorithm, total_faults, total_hits, hit_rate, history}
        """
        algo = algorithm.lower()
        if algo not in MEMORY_ALGO_MAP:
            raise ValueError(f"Unknown memory algorithm '{algorithm}'. Choose from: {list(MEMORY_ALGO_MAP)}")

        replacer = MEMORY_ALGO_MAP[algo]()
        result = replacer.simulate(reference_string, num_frames)

        logger.info("Memory [%s] — %d faults, hit_rate=%.2f%%",
                     algo.upper(), result.total_faults, result.hit_rate * 100)

        return {"algorithm": algo.upper(), **result.to_dict()}

    def run_memory_comparison(
        self,
        reference_string: List[int],
        num_frames: int = DEFAULT_MEMORY_FRAMES,
    ) -> List[Dict[str, Any]]:
        """Run all three page replacement algorithms and return comparison."""
        results = []
        for algo in MEMORY_ALGO_MAP:
            res = self.run_memory_simulation(reference_string, num_frames, algo)
            results.append(res)
        return results

    # ── Deadlock Detection ───────────────────────────────

    def run_deadlock_detection(self, graph_data: Dict) -> Dict[str, Any]:
        """
        Detect deadlock from a RAG specification.

        Args:
            graph_data: {
                processes: [pid, …],
                resources: [{id, instances}, …],
                requests: [{process, resource}, …],
                assignments: [{resource, process}, …]
            }

        Returns:
            {deadlocked, cycle, graph}
        """
        rag = ResourceAllocationGraph()

        for pid in graph_data.get("processes", []):
            rag.add_process(pid)
        for res in graph_data.get("resources", []):
            rag.add_resource(res["id"], res.get("instances", 1))
        for req in graph_data.get("requests", []):
            rag.add_request(req["process"], req["resource"])
        for asn in graph_data.get("assignments", []):
            rag.add_assignment(asn["resource"], asn["process"])

        detection = rag.detect_deadlock()
        graph_viz = rag.get_graph_data()

        logger.info("Deadlock detection: %s", "DEADLOCKED" if detection["deadlocked"] else "SAFE")

        return {**detection, "graph": graph_viz}

    # ── Export ────────────────────────────────────────────

    @staticmethod
    def export_csv(data: List[dict]) -> str:
        """Export a list of dicts as a CSV string."""
        if not data:
            return ""
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=data[0].keys())
        writer.writeheader()
        writer.writerows(data)
        return output.getvalue()
