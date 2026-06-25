# AGENTS.md — Task Manager Monorepo

## Project Overview

A **Trello-like task manager** designed to be **consumed primarily by AI agents**.
The system is a monorepo with two main packages:

| Package | Path | Purpose |
|---------|------|---------|
| **API** | `api/` | FastAPI + Pydantic REST API — the source of truth |
| **CLI** | `cli/` | Lean Python CLI — minimal token usage for LLM agents |

---

## Architecture Principles

1. **AI-agent-first** — Every interface (API responses, CLI output) must be
   token-efficient. Prefer structured, compact output over human-friendly prose.
2. **Monorepo** — API and CLI live in one repo; they share a common models
   package (`shared/`) for Pydantic schemas.
3. **Lean CLI** — The CLI is the primary consumer. Output must be as terse as
   possible (short IDs, minimal whitespace, no decorative formatting). Flags
   over interactive prompts.
4. **Well-tested API** — Target **100% test coverage** on the API. Every
   endpoint, model, and edge case must have tests.
5. **Well-documented** — Every feature, endpoint, and CLI command must be
   documented. OpenAPI spec is auto-generated from FastAPI. CLI has `--help`
   on every command.
6. **Scalable API** — Use async FastAPI, connection pooling, and keep the
   data layer swappable (start with SQLite, easy to move to Postgres).

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| API framework | FastAPI (async) |
| Validation / Schemas | Pydantic v2 |
| Database | SQLite (dev) / PostgreSQL (prod) via SQLAlchemy async |
| Migrations | Alembic |
| CLI framework | `click` (lightweight) |
| Testing | pytest + pytest-asyncio + httpx (AsyncClient) |
| Coverage | pytest-cov — enforce 100% in CI |
| Linting | ruff |
| Formatting | ruff format |
| Type checking | mypy (strict) |
| Docs | Auto-generated OpenAPI (Swagger / ReDoc) |
| Package management | `uv` (preferred) or `pip` |

---

## Monorepo Structure

```
task-manager/
├── AGENTS.md                  # This file
├── README.md                  # Project overview & quickstart
├── pyproject.toml             # Root project config (workspaces)
├── shared/                    # Shared Pydantic models & constants
│   ├── __init__.py
│   ├── models.py              # Board, List, Card, Label, etc.
│   ├── enums.py               # Status, Priority enums
│   └── schemas.py             # Request/Response schemas
├── api/                       # FastAPI application
│   ├── __init__.py
│   ├── main.py                # App factory & lifespan
│   ├── config.py              # Settings via pydantic-settings
│   ├── database.py            # Async engine & session
│   ├── routers/               # One router per resource
│   │   ├── boards.py
│   │   ├── lists.py
│   │   ├── cards.py
│   │   └── health.py
│   ├── crud/                  # DB operations (thin layer)
│   │   ├── boards.py
│   │   ├── lists.py
│   │   └── cards.py
│   ├── db_models.py           # SQLAlchemy ORM models
│   └── dependencies.py        # Shared FastAPI deps (get_db, etc.)
├── cli/                       # Click CLI
│   ├── __init__.py
│   ├── main.py                # CLI entry point & groups
│   ├── commands/              # One module per resource
│   │   ├── boards.py
│   │   ├── lists.py
│   │   └── cards.py
│   ├── client.py              # httpx-based API client
│   ├── config.py              # CLI config (API URL, output format)
│   └── formatters.py          # Terse output formatters
├── tests/                     # All tests
│   ├── conftest.py            # Fixtures (test DB, async client)
│   ├── api/                   # API tests (100% coverage target)
│   │   ├── test_boards.py
│   │   ├── test_lists.py
│   │   ├── test_cards.py
│   │   └── test_health.py
│   └── cli/                   # CLI tests
│       ├── test_boards.py
│       ├── test_lists.py
│       └── test_cards.py
├── alembic/                   # DB migrations
│   ├── alembic.ini
│   └── versions/
└── .github/
    └── workflows/
        └── ci.yml             # Lint + type-check + test + coverage
```

---

## Domain Model

Core entities (Trello-like):

- **Board** — top-level container (name, description, archived)
- **List** — column within a board (name, position, board_id)
- **Card** — task within a list (title, description, position, list_id,
  priority, status, labels, due_date)
- **Label** — tag on a card (name, color)

All entities have: `id` (UUID short prefix for CLI), `created_at`, `updated_at`.

---

## API Conventions

- All endpoints are under `/api/v1/`.
- Use standard HTTP methods: `GET`, `POST`, `PUT`, `PATCH`, `DELETE`.
- Return JSON with Pydantic models. Keep payloads flat — avoid deep nesting.
- Use proper HTTP status codes (201 on create, 204 on delete, 422 on validation).
- Pagination: `?limit=N&offset=M` on all list endpoints.
- Filtering: query params (e.g., `?status=todo&priority=high`).
- Bulk operations: `POST /api/v1/cards/bulk` for moving multiple cards.
- Health check: `GET /api/v1/health` returns `{"status": "ok"}`.

---

## CLI Conventions

- Entry point: `task` (e.g., `task board list`, `task card create`).
- **Terse output by default** — optimized for LLM token consumption:
  - IDs are 8-char short UUIDs.
  - `task card list` outputs tab-separated: `ID\tSTATUS\tTITLE`
  - No color codes, no emoji, no decorative borders.
- `--json` flag on every command for structured JSON output.
- `--verbose` flag for human-friendly output when needed.
- All commands are non-interactive (all args via flags).
- Exit code 0 on success, 1 on error, 2 on validation error.
- Errors go to stderr, data goes to stdout.

---

## Testing Standards

- **100% line coverage** on `api/` — enforced in CI with `--cov-fail-under=100`.
- Tests use an in-memory SQLite database (async).
- Use `httpx.AsyncClient` with FastAPI's `TestClient` for integration tests.
- Every endpoint tested for: happy path, validation errors, not-found, edge cases.
- CLI tests mock the API client — no real HTTP calls.
- Test file naming: `test_<module>.py` mirroring source structure.

---

## Code Style

- Python 3.12+.
- All code must pass `ruff check` and `ruff format`.
- All code must pass `mypy --strict`.
- Use `async def` for all API route handlers and CRUD functions.
- Docstrings on all public functions (Google style).
- No `# type: ignore` without a comment explaining why.
- Imports sorted by ruff (isort-compatible).

---

## Git & Workflow

- Commit messages: `type(scope): description` (e.g., `feat(api): add card CRUD`).
- One feature per branch, small focused PRs.
- CI must pass before merge: lint + typecheck + test + coverage.

---

## Common Commands

```bash
# Install dependencies
uv sync

# Run API server
uvicorn api.main:app --reload

# Run tests with coverage
pytest --cov=api --cov=shared --cov-report=term-missing --cov-fail-under=100

# Lint & format
ruff check . && ruff format --check .

# Type check
mypy api/ shared/ cli/

# Run CLI
python -m cli.main --help
```
