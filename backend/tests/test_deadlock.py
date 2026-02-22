"""
test_deadlock.py - Unit tests for deadlock detection.

Tests cycle detection in the Resource Allocation Graph for
both deadlocked and safe configurations.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.deadlock_detector import ResourceAllocationGraph


def test_circular_deadlock():
    """Three processes in a circular wait should be detected as deadlocked."""
    rag = ResourceAllocationGraph()
    rag.add_process("P1")
    rag.add_process("P2")
    rag.add_process("P3")
    rag.add_resource("R1")
    rag.add_resource("R2")
    rag.add_resource("R3")

    # P1 holds R1, wants R2
    rag.add_assignment("R1", "P1")
    rag.add_request("P1", "R2")

    # P2 holds R2, wants R3
    rag.add_assignment("R2", "P2")
    rag.add_request("P2", "R3")

    # P3 holds R3, wants R1
    rag.add_assignment("R3", "P3")
    rag.add_request("P3", "R1")

    result = rag.detect_deadlock()
    assert result["deadlocked"] is True
    assert result["cycle"] is not None
    assert len(result["cycle"]) >= 2


def test_no_deadlock():
    """A linear chain (no cycle) should be safe."""
    rag = ResourceAllocationGraph()
    rag.add_process("P1")
    rag.add_process("P2")
    rag.add_resource("R1")
    rag.add_resource("R2")

    # P1 holds R1, wants R2
    rag.add_assignment("R1", "P1")
    rag.add_request("P1", "R2")

    # P2 holds R2 (but doesn't want anything held by P1)
    rag.add_assignment("R2", "P2")

    result = rag.detect_deadlock()
    assert result["deadlocked"] is False
    assert result["cycle"] is None


def test_single_process():
    """A single process with no dependencies should be safe."""
    rag = ResourceAllocationGraph()
    rag.add_process("P1")
    rag.add_resource("R1")
    rag.add_assignment("R1", "P1")

    result = rag.detect_deadlock()
    assert result["deadlocked"] is False


def test_empty_graph():
    """Empty graph should be safe."""
    rag = ResourceAllocationGraph()
    result = rag.detect_deadlock()
    assert result["deadlocked"] is False


def test_graph_serialization():
    """get_graph_data should return nodes and edges."""
    rag = ResourceAllocationGraph()
    rag.add_process("P1")
    rag.add_resource("R1")
    rag.add_request("P1", "R1")

    data = rag.get_graph_data()
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1
    assert data["edges"][0]["type"] == "request"


def test_clear():
    """clear() should reset the graph."""
    rag = ResourceAllocationGraph()
    rag.add_process("P1")
    rag.add_resource("R1")
    rag.clear()
    assert len(rag.processes) == 0
    assert len(rag.resources) == 0


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
