"""
metrics.py - Performance metrics computation for scheduling results.

Computes per-process and aggregate metrics, and provides a comparison
utility that runs multiple algorithms on the same process set.
"""

from __future__ import annotations

from typing import List, Dict, Any


class MetricsCalculator:
    """
    Computes performance metrics from scheduling results.

    Works with the per-process dictionaries returned by any Scheduler.
    """

    @staticmethod
    def calculate(processes: List[dict], timeline: List[dict]) -> Dict[str, Any]:
        """
        Calculate aggregate performance metrics.

        Args:
            processes: List of process dicts with computed timing fields.
            timeline:  Gantt chart entries [{pid, start, end}, …].

        Returns:
            Dictionary with per-process and aggregate metrics.
        """
        valid = [p for p in processes if p.get("completion_time") is not None]
        n = len(valid)
        if n == 0:
            return {
                "per_process": [],
                "avg_waiting_time": 0,
                "avg_turnaround_time": 0,
                "avg_response_time": 0,
                "cpu_utilization": 0,
                "throughput": 0,
            }

        total_wt = sum(p["waiting_time"] for p in valid)
        total_tat = sum(p["turnaround_time"] for p in valid)
        total_rt = sum(p["response_time"] for p in valid)

        # CPU utilization: fraction of total span that was non-idle
        total_span = max(e["end"] for e in timeline) - min(e["start"] for e in timeline)
        busy_time = sum(
            e["end"] - e["start"] for e in timeline if e["pid"] != "IDLE"
        )
        cpu_util = (busy_time / total_span * 100) if total_span > 0 else 0

        # Throughput: processes completed per unit time
        throughput = n / total_span if total_span > 0 else 0

        return {
            "per_process": valid,
            "avg_waiting_time": round(total_wt / n, 2),
            "avg_turnaround_time": round(total_tat / n, 2),
            "avg_response_time": round(total_rt / n, 2),
            "cpu_utilization": round(cpu_util, 2),
            "throughput": round(throughput, 4),
        }

    @staticmethod
    def compare(results: Dict[str, Dict[str, Any]]) -> List[dict]:
        """
        Build a comparison table across multiple algorithm results.

        Args:
            results: {algorithm_name: metrics_dict, …}

        Returns:
            List of dicts suitable for tabular display, one per algorithm.
        """
        comparison = []
        for algo_name, metrics in results.items():
            comparison.append({
                "algorithm": algo_name,
                "avg_waiting_time": metrics["avg_waiting_time"],
                "avg_turnaround_time": metrics["avg_turnaround_time"],
                "avg_response_time": metrics["avg_response_time"],
                "cpu_utilization": metrics["cpu_utilization"],
                "throughput": metrics["throughput"],
            })
        return comparison
