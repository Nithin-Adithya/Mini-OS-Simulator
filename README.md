# Mini Operating System Simulator

An interactive, educational simulator demonstrating how operating systems manage **CPU scheduling**, **memory allocation**, **deadlock detection**, and **system performance**. Built with a Python (FastAPI) backend and a React (Vite) frontend.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│         React Frontend (Vite + Recharts)        │
│  Scheduling │ Comparison │ Memory │ Deadlock    │
├─────────────────────────────────────────────────┤
│                  HTTP / JSON                    │
├─────────────────────────────────────────────────┤
│           FastAPI Backend (api.py)              │
├───────┬───────┬───────┬────────┬──────────────┤
│Process│Sched- │Metrics│Memory  │Deadlock       │
│Manager│uler   │       │Manager │Detector       │
└───────┴───────┴───────┴────────┴───────────────┘
│   cli.py (standalone CLI mode)                  │
└─────────────────────────────────────────────────┘
```

---

## 📦 Project Structure

```
Mini Operating System Simulator/
├── backend/
│   ├── modules/
│   │   ├── process_manager.py   # Process dataclass & manager
│   │   ├── scheduler.py         # FCFS, SJF, Priority, Round Robin
│   │   ├── metrics.py           # WT, TAT, RT, CPU utilization, throughput
│   │   ├── memory_manager.py    # FIFO, LRU, Optimal page replacement
│   │   └── deadlock_detector.py # Resource Allocation Graph + DFS cycle detection
│   ├── tests/                   # Unit tests
│   ├── api.py                   # FastAPI server
│   ├── simulator.py             # Facade orchestrating all modules
│   ├── cli.py                   # Command-line interface
│   ├── config.py                # Defaults & logging
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/          # Sidebar, GanttChart, MetricsTable, etc.
│   │   ├── pages/               # SchedulingPage, ComparisonPage, etc.
│   │   ├── api.js               # Axios wrapper
│   │   ├── App.jsx              # Root component with routing
│   │   └── index.css            # Dark-themed design system
│   ├── package.json
│   └── vite.config.js           # Dev proxy to backend
├── data/
│   ├── sample_processes.csv
│   └── sample_reference_string.csv
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.9+**
- **Node.js 18+** and **npm**

### 1. Backend Setup

```bash
cd backend

# Create virtual environment (recommended)
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Start the API server
uvicorn api:app --reload --port 8000
```

### 2. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start dev server (proxies /api to backend)
npm run dev
```

Open **http://localhost:5173** in your browser.

### 3. CLI Mode (no browser needed)

```bash
cd backend

# Run FCFS scheduling
python cli.py schedule --algorithm fcfs --file ../data/sample_processes.csv

# Compare all scheduling algorithms
python cli.py compare --file ../data/sample_processes.csv --quantum 3

# Run memory simulation
python cli.py memory --algorithm lru --frames 3 --ref-string 7,0,1,2,0,3,0,4,2,3,0,3,2

# Compare all page replacement algorithms
python cli.py memory --ref-string 7,0,1,2,0,3,0,4 --frames 3 --compare-all
```

---

## 📊 Features

### CPU Scheduling Algorithms

| Algorithm | Type | Description |
|-----------|------|-------------|
| **FCFS** | Non-preemptive | Executes processes in arrival order |
| **SJF** | Non-preemptive | Selects the ready process with the shortest burst time |
| **Priority** | Non-preemptive | Lower priority number = higher priority. Ties broken by arrival |
| **Round Robin** | Preemptive | Configurable time quantum; processes rotate through a ready queue |

### Page Replacement Algorithms

| Algorithm | Description |
|-----------|-------------|
| **FIFO** | Replaces the page that entered memory earliest |
| **LRU** | Replaces the page whose last access is furthest in the past |
| **Optimal** | Replaces the page not needed for the longest time in the future |

### Deadlock Detection

- Models a **Resource Allocation Graph** (RAG) with processes, resources, request edges, and assignment edges.
- Derives a **wait-for graph** and performs **DFS-based cycle detection**.
- Reports whether the system is safe or deadlocked, with the cycle path if found.

### Performance Metrics

- **Per-process**: Waiting Time, Turnaround Time, Response Time
- **Aggregate**: Average WT, Average TAT, Average RT, CPU Utilization %, Throughput

---

## 🧪 Running Tests

```bash
cd backend
python -m pytest tests/ -v
```

Or run individual test files directly:

```bash
python tests/test_scheduler.py
python tests/test_memory.py
python tests/test_deadlock.py
```

---

## 🖥️ Dashboard Pages

| Page | Description |
|------|-------------|
| **Scheduling** | Input processes, choose algorithm, see Gantt chart + metrics |
| **Comparison** | Run all 4 algorithms side-by-side with bar charts |
| **Memory** | Simulate page replacement with frame-by-frame visualization |
| **Deadlock** | Build a RAG interactively and detect circular waits |
| **Reports** | Generate and download CSV reports |

---

## ⚙️ Configuration

Edit `backend/config.py` to change defaults:

```python
DEFAULT_TIME_QUANTUM = 2    # Round Robin quantum
DEFAULT_MEMORY_FRAMES = 4   # Number of page frames
```

---

## 📄 License

This project is for educational purposes.
