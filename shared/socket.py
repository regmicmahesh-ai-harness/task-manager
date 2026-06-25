"""Shared paths for the Unix domain socket and PID file.

All consumers (API server, CLI, TUI) import from here so they
agree on the same socket location.
"""

from __future__ import annotations

import os
from pathlib import Path

DATA_DIR = Path(
    os.environ.get(
        "TASK_MANAGER_DATA_DIR",
        Path.home() / ".local" / "share" / "task-manager",
    )
)
DATA_DIR.mkdir(parents=True, exist_ok=True)

SOCKET_PATH = str(DATA_DIR / "task_manager.sock")
PID_PATH = str(DATA_DIR / "server.pid")
API_PREFIX = "/api/v1"
