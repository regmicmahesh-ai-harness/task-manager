#!/usr/bin/env bash
# CLI wrapper — forwards all arguments to `task`.
set -euo pipefail
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
exec uv run --project "$REPO_ROOT" task "$@"