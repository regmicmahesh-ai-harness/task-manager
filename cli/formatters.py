"""Output formatters — terse by default, JSON optional."""

from __future__ import annotations

import json
import sys
from typing import Any


def format_terse(items: list[dict[str, Any]], columns: list[str]) -> str:
    """Tab-separated terse output."""
    lines = []
    for item in items:
        row = "\t".join(str(item.get(c, "")) for c in columns)
        lines.append(row)
    return "\n".join(lines)


def format_json(data: Any) -> str:
    """Compact JSON output."""
    return json.dumps(data, default=str)


def output(
    data: Any,
    columns: list[str],
    *,
    as_json: bool = False,
    single: bool = False,
) -> None:
    """Print formatted output to stdout."""
    if as_json:
        print(format_json(data), file=sys.stdout)
    elif single and isinstance(data, dict):
        print(format_terse([data], columns), file=sys.stdout)
    elif isinstance(data, list):
        print(format_terse(data, columns), file=sys.stdout)
    else:
        print(format_json(data), file=sys.stdout)
