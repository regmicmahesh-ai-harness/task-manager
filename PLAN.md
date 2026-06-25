# Implementation Plan — Task Manager

## Phase 1: Project Scaffolding
> Set up the monorepo skeleton, dependencies, and tooling.

- [ ] **1.1** Create `pyproject.toml` with project metadata, dependencies
      (FastAPI, Pydantic v2, SQLAlchemy async, httpx, click, alembic),
      dev dependencies (pytest, pytest-asyncio, pytest-cov, ruff, mypy),
      and workspace config for `shared/`, `api/`, `cli/`.
- [ ] **1.2** Create directory structure: `shared/`, `api/`, `api/routers/`,
      `api/crud/`, `cli/`, `cli/commands/`, `tests/`, `tests/api/`,
      `tests/cli/`, `alembic/`.
- [ ] **1.3** Add `__init__.py` files to all packages.
- [ ] **1.4** Configure ruff (`ruff.toml`), mypy (`mypy.ini` or
      `pyproject.toml` section), and pytest settings.
- [ ] **1.5** Create `.gitignore` (Python, venv, .env, __pycache__, *.db).
- [ ] **1.6** Create stub `README.md` with project overview and quickstart.
- [ ] **1.7** Run `uv sync` to verify dependency resolution.

**Exit criteria:** `ruff check .` and `mypy` pass on empty packages.

---

## Phase 2: Shared Models & Schemas
> Define the Pydantic models shared between API and CLI.

- [ ] **2.1** `shared/enums.py` — `CardStatus` (todo, in_progress, done,
      archived), `CardPriority` (low, medium, high, urgent).
- [ ] **2.2** `shared/models.py` — Base model with `id` (UUID), `created_at`,
      `updated_at`. Then: `Board`, `List`, `Card`, `Label` domain models.
- [ ] **2.3** `shared/schemas.py` — Request/response schemas:
      `BoardCreate`, `BoardUpdate`, `BoardResponse`,
      `ListCreate`, `ListUpdate`, `ListResponse`,
      `CardCreate`, `CardUpdate`, `CardResponse`, `CardMove`,
      `BulkCardMove`, pagination params, etc.
- [ ] **2.4** Write tests for schema validation (required fields, defaults,
      enum validation, UUID generation).

**Exit criteria:** All schemas instantiate correctly, validation rejects
bad input, tests pass.

---

## Phase 3: Database Layer
> SQLAlchemy async models, engine setup, Alembic migrations.

- [ ] **3.1** `api/config.py` — `Settings` class via pydantic-settings
      (DATABASE_URL, API_V1_PREFIX, etc.).
- [ ] **3.2** `api/database.py` — Async engine, `AsyncSession` factory,
      `get_db` dependency.
- [ ] **3.3** `api/db_models.py` — SQLAlchemy ORM models mirroring shared
      models: `BoardModel`, `ListModel`, `CardModel`, `LabelModel`.
      Include relationships, cascading deletes, indexes on foreign keys.
- [ ] **3.4** Set up Alembic with async support. Generate initial migration.
- [ ] **3.5** `tests/conftest.py` — Fixture for in-memory async SQLite,
      auto-create tables, provide `AsyncClient` wired to test DB.

**Exit criteria:** Migrations run, test fixtures create/drop tables,
a trivial test inserting a row passes.

---

## Phase 4: API — CRUD Operations
> Implement the data access layer (no HTTP yet).

- [ ] **4.1** `api/crud/boards.py` — `create_board`, `get_board`,
      `get_boards` (paginated), `update_board`, `delete_board`.
- [ ] **4.2** `api/crud/lists.py` — Same pattern for lists. Include
      `reorder_lists` for position management.
- [ ] **4.3** `api/crud/cards.py` — Same for cards. Include `move_card`
      (change list + position), `bulk_move_cards`.
- [ ] **4.4** Unit tests for all CRUD functions (happy path, not-found,
      duplicate handling, cascade deletes).

**Exit criteria:** All CRUD tests pass, 100% coverage on `api/crud/`.

---

## Phase 5: API — Routers & Endpoints
> Wire CRUD to FastAPI routes.

- [ ] **5.1** `api/dependencies.py` — `get_db` session dependency,
      common query params (pagination, filtering).
- [ ] **5.2** `api/routers/health.py` — `GET /api/v1/health`.
- [ ] **5.3** `api/routers/boards.py` — Full CRUD endpoints for boards.
- [ ] **5.4** `api/routers/lists.py` — Full CRUD endpoints for lists
      (nested under boards: `/api/v1/boards/{board_id}/lists`).
- [ ] **5.5** `api/routers/cards.py` — Full CRUD endpoints for cards
      (nested under lists or flat with filters).
      Include `POST /api/v1/cards/bulk` for bulk moves.
- [ ] **5.6** `api/main.py` — App factory with lifespan handler (create
      tables on startup), include all routers.
- [ ] **5.7** Integration tests for every endpoint: 2xx happy paths,
      404 not found, 422 validation errors, pagination, filtering.

**Exit criteria:** All endpoint tests pass, `pytest --cov=api --cov-fail-under=100`.

---

## Phase 6: CLI — Client & Commands
> Build the lean CLI consumed by AI agents.

- [ ] **6.1** `cli/config.py` — CLI config: API base URL (default
      `http://localhost:8000`), output format.
- [ ] **6.2** `cli/client.py` — Thin httpx wrapper: `get`, `post`, `put`,
      `patch`, `delete` methods targeting the API. Error handling
      (connection refused, HTTP errors → stderr + exit code).
- [ ] **6.3** `cli/formatters.py` — Terse tab-separated formatter (default),
      JSON formatter (`--json`), verbose formatter (`--verbose`).
- [ ] **6.4** `cli/main.py` — Top-level Click group with global options
      (`--json`, `--verbose`, `--api-url`).
- [ ] **6.5** `cli/commands/boards.py` — `board list`, `board create`,
      `board get`, `board update`, `board delete`.
- [ ] **6.6** `cli/commands/lists.py` — Same for lists.
- [ ] **6.7** `cli/commands/cards.py` — Same for cards, plus `card move`,
      `card bulk-move`.
- [ ] **6.8** CLI tests — mock `client.py`, test output formatting,
      exit codes, error messages.

**Exit criteria:** `task --help` works, all CLI tests pass,
output is token-efficient.

---

## Phase 7: Documentation & CI
> Polish docs and set up CI pipeline.

- [ ] **7.1** Complete `README.md` — project overview, quickstart,
      API docs link, CLI usage examples, development setup.
- [ ] **7.2** Add docstrings to all public functions.
- [ ] **7.3** Verify OpenAPI auto-docs at `/docs` and `/redoc`.
- [ ] **7.4** `.github/workflows/ci.yml` — lint → typecheck → test+coverage
      pipeline on push/PR.
- [ ] **7.5** Final coverage audit — ensure 100% on API, identify any gaps.

**Exit criteria:** CI green, docs complete, coverage at 100%.

---

## Phase 8: Grok Skill — `task-manager`
> Package the CLI as a Grok skill so it can be plugged into any project for
> AI-agent task management.

- [ ] **8.1** Create skill directory at `.grok/skills/task-manager/`.
- [ ] **8.2** Write `SKILL.md` with frontmatter (`name`, `description` with
      trigger phrases: "task", "todo", "manage tasks", "create task",
      "board", "card", "/task-manager").
- [ ] **8.3** Skill body — instructions for the agent:
      - How to start/connect to the API (or auto-start if not running).
      - CLI command reference with examples (board/list/card CRUD).
      - Output format conventions (terse default, `--json` for structured).
      - Common workflows: create board → add lists → create cards → move cards.
- [ ] **8.4** Optional helper script (`scripts/ensure-server.sh`) — check if
      the API is running, start it if not, return the base URL.
- [ ] **8.5** Add setup instructions to README: how to install the skill
      in user scope (`~/.grok/skills/`) for cross-project use.
- [ ] **8.6** Test the skill end-to-end: invoke `/task-manager` in a
      separate project, verify it can manage tasks via the CLI.

**Exit criteria:** `/task-manager` skill works from any project,
agent can create boards/lists/cards with minimal token usage.

---

## Phase 9: Stretch Goals (Future)
> Not in initial scope, but planned for iteration.

- [ ] **9.1** WebSocket support for real-time board updates.
- [ ] **9.2** API key authentication (for multi-agent environments).
- [ ] **9.3** PostgreSQL support with connection pooling.
- [ ] **9.4** Card comments / activity log.
- [ ] **9.5** Due date reminders / overdue filtering.
- [ ] **9.6** `task watch` command — poll for board changes (long-polling).

---

## Dependency Graph

```
Phase 1 (Scaffold)
  └─► Phase 2 (Shared Models)
        └─► Phase 3 (Database)
              └─► Phase 4 (CRUD)
                    └─► Phase 5 (API Routers)
                          └─► Phase 6 (CLI)
                                ├─► Phase 7 (Docs & CI)
                                └─► Phase 8 (Grok Skill)
```

Each phase builds on the previous. Phases 7 and 8 can run in parallel
since they both depend on the CLI being done but not on each other.
