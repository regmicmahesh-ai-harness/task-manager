"""TUI configuration and constants."""

from __future__ import annotations

import os

API_BASE = os.environ.get("TASK_MANAGER_API_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"

PRIORITY_COLORS = {
    "urgent": "red",
    "high": "darkorange",
    "medium": "dodgerblue",
    "low": "gray",
}


REFRESH_INTERVAL = 2.0
