#!/usr/bin/env bash
# TUI wrapper — launches the interactive terminal UI.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/../../../.." && pwd)"
exec uv run --project "$REPO_ROOT" task-tui "$@"