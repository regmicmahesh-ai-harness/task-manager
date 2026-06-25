#!/usr/bin/env bash
# One-time setup: install dependencies into a project-local .venv.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"
uv sync
echo "Setup complete. .venv created in $REPO_ROOT"