"""
test_memory.py - Unit tests for page replacement algorithms.

Verifies FIFO, LRU, and Optimal against the classic textbook
reference string: [7,0,1,2,0,3,0,4,2,3,0,3,2] with 3 frames.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from modules.memory_manager import FIFOPageReplacer, LRUPageReplacer, OptimalPageReplacer


REF_STRING = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
NUM_FRAMES = 3


def test_fifo_faults():
    """FIFO with classic ref string should produce 10 page faults."""
    result = FIFOPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    assert result.total_faults == 10, f"Expected 10 faults, got {result.total_faults}"


def test_lru_faults():
    """LRU with classic ref string should produce 9 page faults."""
    result = LRUPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    assert result.total_faults == 9, f"Expected 9 faults, got {result.total_faults}"


def test_optimal_faults():
    """Optimal with classic ref string should produce 7 page faults (theoretical best)."""
    result = OptimalPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    assert result.total_faults == 7, f"Expected 7 faults, got {result.total_faults}"


def test_optimal_beats_others():
    """Optimal should never have more faults than FIFO or LRU."""
    fifo = FIFOPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    lru = LRUPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    opt = OptimalPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    assert opt.total_faults <= fifo.total_faults
    assert opt.total_faults <= lru.total_faults


def test_history_length():
    """History should have one entry per reference string element."""
    result = FIFOPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    assert len(result.history) == len(REF_STRING)


def test_hit_rate_calculation():
    """Hit rate = hits / total accesses."""
    result = FIFOPageReplacer().simulate(REF_STRING, NUM_FRAMES)
    expected_rate = result.total_hits / len(REF_STRING)
    assert abs(result.hit_rate - expected_rate) < 0.001


def test_empty_reference_string():
    """Empty reference string should produce no faults."""
    result = FIFOPageReplacer().simulate([], NUM_FRAMES)
    assert result.total_faults == 0
    assert result.total_hits == 0


def test_single_page_repeated():
    """Repeated access to the same page should only fault once."""
    result = FIFOPageReplacer().simulate([5, 5, 5, 5], 3)
    assert result.total_faults == 1
    assert result.total_hits == 3


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
