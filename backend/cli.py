"""
cli.py - Command-line interface for the Mini OS Simulator.

Supports three subcommands:
  schedule  — run a single scheduling algorithm
  compare   — run all four algorithms and show comparison
  memory    — run page replacement simulation

Examples:
  python cli.py schedule --algorithm fcfs --file ../data/sample_processes.csv
  python cli.py compare --file ../data/sample_processes.csv --quantum 3
  python cli.py memory --algorithm lru --frames 3 --ref-string 7,0,1,2,0,3,0,4,2,3,0,3,2
"""

from __future__ import annotations

import argparse
import csv
import sys
from typing import List

from config import setup_logging
from simulator import Simulator


def print_table(headers: List[str], rows: List[List[str]], title: str = "") -> None:
    """Pretty-print a table to the console."""
    if title:
        print(f"\n{'═' * 60}")
        print(f"  {title}")
        print(f"{'═' * 60}")

    col_widths = [len(h) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    header_line = " │ ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers))
    separator = "─┼─".join("─" * w for w in col_widths)
    print(f" {header_line}")
    print(f" {separator}")
    for row in rows:
        line = " │ ".join(str(cell).ljust(col_widths[i]) for i, cell in enumerate(row))
        print(f" {line}")
    print()


def cmd_schedule(args):
    """Handle the 'schedule' subcommand."""
    sim = Simulator()
    sim.load_processes_from_csv(args.file)
    result = sim.run_scheduling(args.algorithm, quantum=args.quantum)

    # Gantt timeline
    print_table(
        ["PID", "Start", "End"],
        [[e["pid"], e["start"], e["end"]] for e in result["timeline"]],
        title=f"Gantt Chart — {result['algorithm']}",
    )

    # Per-process metrics
    print_table(
        ["PID", "Arrival", "Burst", "Start", "Completion", "Waiting", "Turnaround", "Response"],
        [
            [p["pid"], p["arrival_time"], p["burst_time"],
             p["start_time"], p["completion_time"],
             p["waiting_time"], p["turnaround_time"], p["response_time"]]
            for p in result["metrics"]
        ],
        title="Per-Process Metrics",
    )

    # Aggregates
    agg = result["aggregates"]
    print(f"  Avg Waiting Time    : {agg['avg_waiting_time']}")
    print(f"  Avg Turnaround Time : {agg['avg_turnaround_time']}")
    print(f"  Avg Response Time   : {agg['avg_response_time']}")
    print(f"  CPU Utilization     : {agg['cpu_utilization']}%")
    print(f"  Throughput          : {agg['throughput']} proc/unit\n")

    # Export
    if args.export:
        csv_str = Simulator.export_csv(result["metrics"])
        with open(args.export, "w", encoding="utf-8") as f:
            f.write(csv_str)
        print(f"  ✓ Exported to {args.export}\n")


def cmd_compare(args):
    """Handle the 'compare' subcommand."""
    sim = Simulator()
    sim.load_processes_from_csv(args.file)
    result = sim.run_comparison(quantum=args.quantum)

    print_table(
        ["Algorithm", "Avg WT", "Avg TAT", "Avg RT", "CPU Util %", "Throughput"],
        [
            [c["algorithm"], c["avg_waiting_time"], c["avg_turnaround_time"],
             c["avg_response_time"], c["cpu_utilization"], c["throughput"]]
            for c in result["comparison"]
        ],
        title="Algorithm Comparison",
    )


def cmd_memory(args):
    """Handle the 'memory' subcommand."""
    ref_string = [int(x.strip()) for x in args.ref_string.split(",")]

    sim = Simulator()
    if args.compare_all:
        results = sim.run_memory_comparison(ref_string, args.frames)
        print_table(
            ["Algorithm", "Faults", "Hits", "Hit Rate"],
            [[r["algorithm"], r["total_faults"], r["total_hits"],
              f"{r['hit_rate'] * 100:.1f}%"] for r in results],
            title="Page Replacement Comparison",
        )
    else:
        result = sim.run_memory_simulation(ref_string, args.frames, args.algorithm)
        print_table(
            ["Step", "Page", "Frames", "Fault?"],
            [[h["step"], h["page"], str(h["frames"]),
              "✗ FAULT" if h["fault"] else "✓ HIT"] for h in result["history"]],
            title=f"Memory Simulation — {result['algorithm']}",
        )
        print(f"  Total Faults : {result['total_faults']}")
        print(f"  Hit Rate     : {result['hit_rate'] * 100:.1f}%\n")


def main():
    parser = argparse.ArgumentParser(
        description="Mini OS Simulator — CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", help="Available commands")

    # ── schedule ─────────────────────────────
    p_sched = sub.add_parser("schedule", help="Run a scheduling algorithm")
    p_sched.add_argument("--algorithm", "-a", required=True,
                         choices=["fcfs", "sjf", "priority", "rr"])
    p_sched.add_argument("--file", "-f", required=True, help="Path to processes CSV")
    p_sched.add_argument("--quantum", "-q", type=int, default=2)
    p_sched.add_argument("--export", "-e", help="Export metrics to CSV file")

    # ── compare ──────────────────────────────
    p_comp = sub.add_parser("compare", help="Compare all scheduling algorithms")
    p_comp.add_argument("--file", "-f", required=True, help="Path to processes CSV")
    p_comp.add_argument("--quantum", "-q", type=int, default=2)

    # ── memory ───────────────────────────────
    p_mem = sub.add_parser("memory", help="Run page replacement simulation")
    p_mem.add_argument("--algorithm", "-a", default="fifo",
                       choices=["fifo", "lru", "optimal"])
    p_mem.add_argument("--ref-string", "-r", required=True,
                       help="Comma-separated page reference string")
    p_mem.add_argument("--frames", type=int, default=3)
    p_mem.add_argument("--compare-all", action="store_true",
                       help="Compare all three algorithms")

    args = parser.parse_args()
    if args.command is None:
        parser.print_help()
        sys.exit(1)

    setup_logging()

    commands = {"schedule": cmd_schedule, "compare": cmd_compare, "memory": cmd_memory}
    commands[args.command](args)


if __name__ == "__main__":
    main()
