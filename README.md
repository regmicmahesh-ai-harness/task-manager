# Task Manager

AI-agent-first Trello-like task manager. Monorepo with a **FastAPI REST API** and a **lean CLI** optimized for LLM token efficiency.

## Quickstart

```bash
# Install dependencies
uv sync

# Start the API
uvicorn api.main:app --reload

# API docs at http://localhost:8000/docs
```

## Architecture

| Package | Path | Purpose |
|---------|------|---------|
| API | `api/` | FastAPI + Pydantic REST API |
| CLI | `cli/` | Lean Click CLI for AI agents |
| Shared | `shared/` | Pydantic models & schemas |

## CLI Usage

The CLI is optimized for minimal token output — terse tab-separated format by default.

```bash
# Boards
task board list
task board create --name "Sprint 1"
task board get <board_id>
task board update <board_id> --name "Sprint 2"
task board delete <board_id>

# Lists
task list create --board-id <board_id> --name "To Do"
task list ls --board-id <board_id>
task list update --board-id <board_id> <list_id> --name "Done"
task list delete --board-id <board_id> <list_id>

# Cards
task card create --list-id <list_id> --title "Fix bug" --priority high
task card list --status todo --priority high
task card get <card_id>
task card update <card_id> --status done
task card move <card_id> --to-list-id <list_id>
task card bulk-move --card-ids "id1,id2" --to-list-id <list_id>
task card delete <card_id>
```

Add `--json` for structured JSON output:
```bash
task --json board list
```

## API Endpoints

All under `/api/v1/`:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/boards` | Create board |
| GET | `/boards` | List boards |
| GET | `/boards/{id}` | Get board |
| PATCH | `/boards/{id}` | Update board |
| DELETE | `/boards/{id}` | Delete board |
| POST | `/boards/{id}/lists` | Create list |
| GET | `/boards/{id}/lists` | List lists |
| GET | `/boards/{id}/lists/{id}` | Get list |
| PATCH | `/boards/{id}/lists/{id}` | Update list |
| DELETE | `/boards/{id}/lists/{id}` | Delete list |
| POST | `/cards` | Create card |
| GET | `/cards` | List cards (filterable) |
| GET | `/cards/{id}` | Get card |
| PATCH | `/cards/{id}` | Update card |
| POST | `/cards/{id}/move` | Move card |
| POST | `/cards/bulk` | Bulk move cards |
| DELETE | `/cards/{id}` | Delete card |

## Development

```bash
# Run tests (100% coverage enforced)
pytest --cov=api --cov=shared --cov-report=term-missing --cov-fail-under=100

# Lint & format
ruff check . && ruff format --check .

# Type check
mypy api/ shared/ cli/
```

## License

MIT
