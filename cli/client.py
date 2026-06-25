"""HTTP client for the Task Manager API."""

from __future__ import annotations

import sys
from typing import Any

import httpx

from cli.config import API_BASE_URL, API_PREFIX


class APIClient:
    """Thin httpx wrapper for the Task Manager API."""

    def __init__(self, base_url: str = API_BASE_URL) -> None:
        """Initialize client."""
        self.base_url = base_url.rstrip("/")
        self.prefix = API_PREFIX

    def _url(self, path: str) -> str:
        """Build full URL."""
        return f"{self.base_url}{self.prefix}{path}"

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
        resp = httpx.get(self._url(path), params=params)
        self._handle_error(resp)
        return resp.json()

    def post(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """POST request."""
        resp = httpx.post(self._url(path), json=json)
        self._handle_error(resp)
        return resp.json()

    def patch(self, path: str, json: dict[str, Any] | None = None) -> Any:
        """PATCH request."""
        resp = httpx.patch(self._url(path), json=json)
        self._handle_error(resp)
        return resp.json()

    def delete(self, path: str) -> None:
        """DELETE request."""
        resp = httpx.delete(self._url(path))
        self._handle_error(resp)
