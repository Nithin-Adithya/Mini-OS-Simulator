"""
memory_manager.py - Page replacement algorithm simulations.

Implements three classic page replacement policies:
  • FIFO    — replaces the page that entered memory earliest
  • LRU     — replaces the least recently used page
  • Optimal — replaces the page not needed for the longest time (look-ahead)

Each algorithm processes a reference string against a fixed number of
frames and returns fault/hit counts plus a step-by-step frame history.
"""

from __future__ import annotations

from collections import OrderedDict, deque
from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class MemoryResult:
    """
    Output of a page replacement simulation.

    Attributes:
        total_faults: Number of page faults that occurred.
        total_hits:   Number of page hits.
        hit_rate:     Fraction of accesses that were hits (.0–1.0).
        history:      Step-by-step frame snapshots for visualization.
    """
    total_faults: int = 0
    total_hits: int = 0
    hit_rate: float = 0.0
    history: List[dict] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "total_faults": self.total_faults,
            "total_hits": self.total_hits,
            "hit_rate": round(self.hit_rate, 4),
            "history": self.history,
        }


# ══════════════════════════════════════════════════════════
#  1. FIFO Page Replacement
# ══════════════════════════════════════════════════════════


class FIFOPageReplacer:
    """
    First-In-First-Out page replacement.
    The page that has been in memory the longest is replaced first.
    """

    def simulate(self, reference_string: List[int], num_frames: int) -> MemoryResult:
        frames: deque = deque()
        result = MemoryResult()

        for step, page in enumerate(reference_string):
            fault = False
            if page in frames:
                result.total_hits += 1
            else:
                fault = True
                result.total_faults += 1
                if len(frames) >= num_frames:
                    evicted = frames.popleft()
                frames.append(page)

            result.history.append({
                "step": step,
                "page": page,
                "frames": list(frames),
                "fault": fault,
            })

        total = len(reference_string)
        result.hit_rate = result.total_hits / total if total > 0 else 0
        return result


# ══════════════════════════════════════════════════════════
#  2. LRU Page Replacement
# ══════════════════════════════════════════════════════════


class LRUPageReplacer:
    """
    Least Recently Used page replacement.
    Replaces the page whose last access is furthest in the past.
    Uses an OrderedDict to efficiently track recency.
    """

    def simulate(self, reference_string: List[int], num_frames: int) -> MemoryResult:
        frames: OrderedDict = OrderedDict()
        result = MemoryResult()

        for step, page in enumerate(reference_string):
            fault = False
            if page in frames:
                result.total_hits += 1
                # Move to end (most recently used)
                frames.move_to_end(page)
            else:
                fault = True
                result.total_faults += 1
                if len(frames) >= num_frames:
                    # Evict least recently used (first item)
                    frames.popitem(last=False)
                frames[page] = True

            result.history.append({
                "step": step,
                "page": page,
                "frames": list(frames.keys()),
                "fault": fault,
            })

        total = len(reference_string)
        result.hit_rate = result.total_hits / total if total > 0 else 0
        return result


# ══════════════════════════════════════════════════════════
#  3. Optimal Page Replacement
# ══════════════════════════════════════════════════════════


class OptimalPageReplacer:
    """
    Optimal (Bélády's) page replacement.
    Replaces the page that will not be used for the longest time
    in the future.  This is the theoretical best but requires
    knowledge of the full reference string.
    """

    def simulate(self, reference_string: List[int], num_frames: int) -> MemoryResult:
        frames: List[int] = []
        result = MemoryResult()

        for step, page in enumerate(reference_string):
            fault = False
            if page in frames:
                result.total_hits += 1
            else:
                fault = True
                result.total_faults += 1
                if len(frames) >= num_frames:
                    # Find the page used furthest in the future (or never)
                    farthest_use = -1
                    victim = frames[0]
                    for f in frames:
                        try:
                            next_use = reference_string[step + 1:].index(f)
                        except ValueError:
                            victim = f
                            break
                        if next_use > farthest_use:
                            farthest_use = next_use
                            victim = f
                    frames.remove(victim)
                frames.append(page)

            result.history.append({
                "step": step,
                "page": page,
                "frames": list(frames),
                "fault": fault,
            })

        total = len(reference_string)
        result.hit_rate = result.total_hits / total if total > 0 else 0
        return result
