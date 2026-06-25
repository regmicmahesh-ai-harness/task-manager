"""TUI configuration and constants."""

from __future__ import annotations

from shared.socket import API_PREFIX, SOCKET_PATH

PRIORITY_COLORS = {
    "urgent": "red",
    "high": "darkorange",
    "medium": "dodgerblue",
    "low": "gray",
}

__all__ = ["API_PREFIX", "PRIORITY_COLORS", "SOCKET_PATH"]
