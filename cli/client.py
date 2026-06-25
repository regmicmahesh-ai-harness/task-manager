"""HTTP client for the Task Manager API (Unix domain socket)."""

from __future__ import annotations

import sys
from typing import Any

import httpx

from cli.config import API_PREFIX, SOCKET_PATH

# Dummy base URL — host is ignored over UDS.
_UDS_BASE = "http://localhost"


class APIClient:
    """Thin httpx wrapper for the Task Manager API over a Unix socket."""

    def __init__(self, socket_path: str = SOCKET_PATH) -> None:
        """Initialize client with a UDS transport."""
        self._transport = httpx.HTTPTransport(uds=socket_path)
        self.prefix = API_PREFIX

    def _url(self, path: str) -> str:
        """Build full URL."""
        return f"{_UDS_BASE}{self.prefix}{path}"

    def _handle_error(self, resp: httpx.Response) -> None:
        """Print error to stderr and exit on failure."""
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("detail", resp.text)
            except Exception:
                detail = resp.text
            print(f"Error {resp.status_code}: {detail}", file=sys.stderr)
            sys.exit(1)

    def get(self, path: str, params: dict[str, Any] | None = None) -> Any:
        """GET request."""
        with httpx.Client(transport=self._transport) as client:
            resp = client.get(self._url(path), params=params)
        self._handle_error(resp)
        return resp.json()

    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """POST request."""
        with httpx.Client(transport=self._transport) as client:
            resp = client.post(self._url(path), json=json)
        self._handle_error(resp)
        return resp.json()

    def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """PATCH request."""
        with httpx.Client(transport=self._transport) as client:
            resp = client.patch(self._url(path), json=json)
        self._handle_error(resp)
        return resp.json()

    def delete(self, path: str) -> None:
        """DELETE request."""
        with httpx.Client(transport=self._transport) as client:
            resp = client.delete(self._url(path))
        self._handle_error(resp)
