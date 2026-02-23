"""
Vercel Python Serverless Function entry-point.

Re-exports the FastAPI `app` from the backend package so that
Vercel's Python runtime can serve it as an ASGI application.
"""

import sys
import os

# Add the backend directory to the Python path so that
# `from simulator import Simulator`, `from config import ...`, etc. resolve.
backend_dir = os.path.join(os.path.dirname(__file__), "..", "backend")
sys.path.insert(0, backend_dir)

from api import app  # noqa: E402, F401 — re-export FastAPI app
