"""CLI configuration."""

import os

API_BASE_URL = os.environ.get("TASK_MANAGER_API_URL", "http://localhost:8000")
API_PREFIX = "/api/v1"
