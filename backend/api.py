"""
api.py - FastAPI REST server for the Mini OS Simulator.

Exposes endpoints for CPU scheduling, algorithm comparison,
memory management simulation, and deadlock detection.
"""

from __future__ import annotations

from typing import List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import PlainTextResponse
from pydantic import BaseModel, Field

from simulator import Simulator

# ── Pydantic Request / Response Models ───────────────────

class ProcessInput(BaseModel):
    pid: str
    arrival_time: int = Field(..., ge=0)
    burst_time: int = Field(..., gt=0)
    priority: int = Field(0, ge=0)
    memory_required: int = Field(0, ge=0)


class ScheduleRequest(BaseModel):
    processes: List[ProcessInput]
    algorithm: str
    quantum: Optional[int] = 2


class CompareRequest(BaseModel):
    processes: List[ProcessInput]
    quantum: Optional[int] = 2


class MemoryRequest(BaseModel):
    reference_string: List[int]
    num_frames: int = Field(4, gt=0, le=20)
    algorithm: str = "fifo"


class MemoryCompareRequest(BaseModel):
    reference_string: List[int]
    num_frames: int = Field(4, gt=0, le=20)


class ResourceInput(BaseModel):
    id: str
    instances: int = 1


class EdgeInput(BaseModel):
    process: str = ""
    resource: str = ""


class DeadlockRequest(BaseModel):
    processes: List[str]
    resources: List[ResourceInput]
    requests: List[EdgeInput]
    assignments: List[EdgeInput]


# ── App Setup ────────────────────────────────────────────

app = FastAPI(
    title="Mini OS Simulator API",
    description="Interactive OS scheduling, memory, and deadlock simulation",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Endpoints ────────────────────────────────────────────


@app.post("/api/schedule")
def schedule(req: ScheduleRequest):
    """Run a single scheduling algorithm."""
    try:
        sim = Simulator()
        sim.load_processes([p.model_dump() for p in req.processes])
        return sim.run_scheduling(req.algorithm, quantum=req.quantum or 2)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/compare")
def compare(req: CompareRequest):
    """Run all four scheduling algorithms and return comparison."""
    try:
        sim = Simulator()
        sim.load_processes([p.model_dump() for p in req.processes])
        return sim.run_comparison(quantum=req.quantum or 2)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/memory")
def memory(req: MemoryRequest):
    """Run a page replacement simulation."""
    try:
        sim = Simulator()
        return sim.run_memory_simulation(
            req.reference_string, req.num_frames, req.algorithm
        )
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/memory/compare")
def memory_compare(req: MemoryCompareRequest):
    """Run all three page replacement algorithms."""
    try:
        sim = Simulator()
        return sim.run_memory_comparison(req.reference_string, req.num_frames)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.post("/api/deadlock")
def deadlock(req: DeadlockRequest):
    """Detect deadlock from a Resource Allocation Graph."""
    try:
        sim = Simulator()
        graph_data = {
            "processes": req.processes,
            "resources": [r.model_dump() for r in req.resources],
            "requests": [e.model_dump() for e in req.requests],
            "assignments": [e.model_dump() for e in req.assignments],
        }
        return sim.run_deadlock_detection(graph_data)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@app.get("/api/sample-data")
def sample_data():
    """Return sample datasets for quick testing."""
    return {
        "processes": [
            {"pid": "P1", "arrival_time": 0, "burst_time": 6, "priority": 2, "memory_required": 40},
            {"pid": "P2", "arrival_time": 1, "burst_time": 8, "priority": 1, "memory_required": 30},
            {"pid": "P3", "arrival_time": 2, "burst_time": 7, "priority": 3, "memory_required": 20},
            {"pid": "P4", "arrival_time": 3, "burst_time": 3, "priority": 4, "memory_required": 15},
            {"pid": "P5", "arrival_time": 5, "burst_time": 4, "priority": 2, "memory_required": 25},
        ],
        "reference_string": [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2],
    }


@app.post("/api/export")
def export(data: List[dict]):
    """Export data as CSV."""
    csv_string = Simulator.export_csv(data)
    return PlainTextResponse(content=csv_string, media_type="text/csv")
