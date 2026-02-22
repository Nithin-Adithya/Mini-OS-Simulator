"""
config.py - Default simulation constants and logging configuration.

This module centralizes all configurable parameters for the OS simulator,
making it easy to adjust defaults without modifying core logic.
"""

import logging
import os

# ──────────────────────────────────────────────
# Simulation Defaults
# ──────────────────────────────────────────────
DEFAULT_TIME_QUANTUM = 2          # Round Robin default quantum
DEFAULT_MEMORY_FRAMES = 4         # Number of page frames in memory
DEFAULT_TOTAL_MEMORY_KB = 256     # Total simulated memory in KB
DEFAULT_PAGE_SIZE_KB = 4          # Page size in KB

# ──────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────
LOG_LEVEL = os.getenv("SIM_LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s | %(levelname)-7s | %(name)s | %(message)s"
LOG_FILE = "simulation.log"


def setup_logging() -> logging.Logger:
    """Configure and return the root simulator logger."""
    logger = logging.getLogger("os_simulator")
    logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))

    # Console handler
    console = logging.StreamHandler()
    console.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(console)

    # File handler
    file_handler = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
    file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
    logger.addHandler(file_handler)

    return logger


# Create logger on import
logger = setup_logging()
