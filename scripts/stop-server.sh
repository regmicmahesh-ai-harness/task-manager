#!/usr/bin/env bash
# Stop the task-manager API server.
set -euo pipefail
PID_FILE="$HOME/.local/share/task-manager/server.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  kill "$(cat "$PID_FILE")"
  echo "Server stopped"
else
  echo "Server not running"
fi