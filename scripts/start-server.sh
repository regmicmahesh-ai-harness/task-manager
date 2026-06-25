#!/usr/bin/env bash
# Start the task-manager API server (singleton — safe to call multiple times).
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PID_FILE="$HOME/.local/share/task-manager/server.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  echo "Server already running (PID $(cat "$PID_FILE"))"
else
  echo "Starting task-manager server..."
  uv run --project "$REPO_ROOT" task-server &
  # Wait briefly for PID file to appear
  for i in 1 2 3 4 5; do
    [ -f "$PID_FILE" ] && break
    sleep 0.5
  done
  echo "Server started (PID $(cat "$PID_FILE" 2>/dev/null || echo '?'))"
fi