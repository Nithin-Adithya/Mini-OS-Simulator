"""
deadlock_detector.py - Resource Allocation Graph (RAG) and deadlock detection.

Models processes, resources, and their request/assignment edges as a
directed graph.  Detects deadlock by searching for cycles in the
corresponding wait-for graph using DFS.
"""

from __future__ import annotations

from typing import Dict, List, Optional, Set, Tuple


class ResourceAllocationGraph:
    """
    Simulates a Resource Allocation Graph (RAG) for deadlock detection.

    Nodes:
        - Processes (prefixed with "P")
        - Resources (prefixed with "R")

    Edges:
        - Request edge:    Process → Resource  (process is waiting for resource)
        - Assignment edge: Resource → Process  (resource is held by process)

    Deadlock Detection:
        Builds a wait-for graph (process → process) from the RAG and
        searches for cycles via depth-first search.
    """

    def __init__(self):
        self.processes: Set[str] = set()
        self.resources: Dict[str, int] = {}       # resource_id → total instances
        self.requests: List[Tuple[str, str]] = []  # (process, resource)
        self.assignments: List[Tuple[str, str]] = []  # (resource, process)

    # ── Graph Construction ───────────────────────────────

    def add_process(self, pid: str) -> None:
        """Register a process node."""
        self.processes.add(pid)

    def add_resource(self, rid: str, instances: int = 1) -> None:
        """Register a resource node with a given number of instances."""
        self.resources[rid] = instances

    def add_request(self, pid: str, rid: str) -> None:
        """Add a request edge: process pid is waiting for resource rid."""
        self.processes.add(pid)
        if rid not in self.resources:
            self.resources[rid] = 1
        self.requests.append((pid, rid))

    def add_assignment(self, rid: str, pid: str) -> None:
        """Add an assignment edge: resource rid is held by process pid."""
        self.processes.add(pid)
        if rid not in self.resources:
            self.resources[rid] = 1
        self.assignments.append((rid, pid))

    # ── Deadlock Detection ───────────────────────────────

    def _build_wait_for_graph(self) -> Dict[str, Set[str]]:
        """
        Derive a wait-for graph (process → set of processes).

        For each request (P_i → R_k), find all assignments (R_k → P_j)
        where j ≠ i.  This means P_i is waiting for P_j.
        """
        wfg: Dict[str, Set[str]] = {p: set() for p in self.processes}

        # Map: resource → set of processes holding it
        holders: Dict[str, Set[str]] = {}
        for rid, pid in self.assignments:
            holders.setdefault(rid, set()).add(pid)

        # For each request, connect requester to holders
        for pid, rid in self.requests:
            for holder in holders.get(rid, set()):
                if holder != pid:
                    wfg.setdefault(pid, set()).add(holder)

        return wfg

    def detect_deadlock(self) -> Dict:
        """
        Detect deadlock by finding cycles in the wait-for graph.

        Returns:
            {
                "deadlocked": bool,
                "cycle": list of PIDs forming the cycle, or None
            }
        """
        wfg = self._build_wait_for_graph()

        # DFS-based cycle detection
        WHITE, GRAY, BLACK = 0, 1, 2
        color = {node: WHITE for node in wfg}
        parent: Dict[str, Optional[str]] = {node: None for node in wfg}

        def dfs(node: str) -> Optional[List[str]]:
            color[node] = GRAY
            for neighbor in wfg.get(node, set()):
                if neighbor not in color:
                    continue
                if color[neighbor] == GRAY:
                    # Found a cycle — reconstruct it
                    cycle = [neighbor, node]
                    current = node
                    while parent.get(current) and parent[current] != neighbor:
                        current = parent[current]
                        cycle.append(current)
                    cycle.reverse()
                    return cycle
                if color[neighbor] == WHITE:
                    parent[neighbor] = node
                    result = dfs(neighbor)
                    if result:
                        return result
            color[node] = BLACK
            return None

        for node in wfg:
            if color.get(node) == WHITE:
                cycle = dfs(node)
                if cycle:
                    return {"deadlocked": True, "cycle": cycle}

        return {"deadlocked": False, "cycle": None}

    # ── Serialization ────────────────────────────────────

    def get_graph_data(self) -> Dict:
        """
        Serialize the RAG for frontend visualization.

        Returns nodes (processes & resources) and directed edges.
        """
        nodes = []
        for pid in self.processes:
            nodes.append({"id": pid, "type": "process"})
        for rid in self.resources:
            nodes.append({"id": rid, "type": "resource", "instances": self.resources[rid]})

        edges = []
        for pid, rid in self.requests:
            edges.append({"from": pid, "to": rid, "type": "request"})
        for rid, pid in self.assignments:
            edges.append({"from": rid, "to": pid, "type": "assignment"})

        return {"nodes": nodes, "edges": edges}

    def clear(self) -> None:
        """Reset the graph."""
        self.processes.clear()
        self.resources.clear()
        self.requests.clear()
        self.assignments.clear()

    def __repr__(self) -> str:
        return (
            f"RAG(processes={len(self.processes)}, "
            f"resources={len(self.resources)}, "
            f"requests={len(self.requests)}, "
            f"assignments={len(self.assignments)})"
        )
