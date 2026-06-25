"""Async HTTP helpers for the TUI (Unix domain socket)."""

from __future__ import annotations

from typing import Any

import httpx

from tui.config import API_PREFIX, SOCKET_PATH

# Dummy base URL — host is ignored over UDS.
_UDS_BASE = "http://localhost"


def _make_transport() -> httpx.AsyncHTTPTransport:
    """Create a fresh async UDS transport."""
    return httpx.AsyncHTTPTransport(uds=SOCKET_PATH)


async def api_get(path: str, params: dict[str, Any] | None = None) -> Any:
    """Async GET request to the API."""
    try:
        async with httpx.AsyncClient(transport=_make_transport(), timeout=5.0) as client:
            resp = await client.get(f"{_UDS_BASE}{API_PREFIX}{path}", params=params)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError:
        return None


async def api_post(path: str, json: dict[str, Any] | None = None) -> Any:
    """Async POST request to the API."""
    try:
        async with httpx.AsyncClient(transport=_make_transport(), timeout=5.0) as client:
            resp = await client.post(f"{_UDS_BASE}{API_PREFIX}{path}", json=json)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError:
        return None


async def api_patch(path: str, json: dict[str, Any] | None = None) -> Any:
    """Async PATCH request to the API."""
    try:
        async with httpx.AsyncClient(transport=_make_transport(), timeout=5.0) as client:
            resp = await client.patch(f"{_UDS_BASE}{API_PREFIX}{path}", json=json)
            resp.raise_for_status()
            return resp.json()
    except httpx.HTTPError:
        return None


async def api_delete(path: str) -> bool:
    """Async DELETE request to the API. Returns True on success."""
    try:
        async with httpx.AsyncClient(transport=_make_transport(), timeout=5.0) as client:
            resp = await client.delete(f"{_UDS_BASE}{API_PREFIX}{path}")
            resp.raise_for_status()
            return True
    except httpx.HTTPError:
        return False
