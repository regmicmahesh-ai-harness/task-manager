---
name: task-manager
description: >
  Manage tasks, boards, lists, and cards using the Task Manager API and CLI.
  Use when: the user wants to create tasks, manage a todo list, organize work
  into boards/lists/cards, move tasks between columns, track task status, or
  runs /task-manager. Trigger keywords: "task", "todo", "board", "card",
  "create task", "move task", "task list", "manage tasks", "kanban".
---

# Task Manager Skill

A Trello-like task manager with boards, lists (columns), and cards.
Columns ARE the status — moving a card between columns changes its status.
Creating a board auto-creates default columns: To Do, In Progress, Done.

Three interfaces available:
- **CLI** (`task`) — terse output optimized for AI agents
- **TUI** (`task-tui`) — interactive vim-style terminal UI
- **API** — Unix socket, no TCP port

## Setup

Everything runs from the project directory — no global installation. The
virtual environment lives inside the repo, so removing the skill directory
cleans up everything.

```bash
# One-time: install dependencies (creates .venv/ in project dir)
SKILL_DIR="$(cd "$(dirname "$0")/../../../" && pwd)"  # repo root
cd "$SKILL_DIR" && uv sync
```

When invoking from any working directory, use `--project` to point at the
repo root. All examples below use a `TASK` alias for brevity:

```bash
TASK_PROJECT="<path-to-this-repo>"
alias task="uv run --project $TASK_PROJECT task"
alias task-server="uv run --project $TASK_PROJECT task-server"
alias task-tui="uv run --project $TASK_PROJECT task-tui"
```

### Starting the server (singleton, Unix socket)

The API server listens on a **Unix domain socket** at
`~/.local/share/task-manager/task_manager.sock` — no TCP port needed.

**IMPORTANT — singleton server:** Only ONE instance of the server should run
at a time, even if multiple models or skill invocations are active. Always
check before starting:

```bash
PID_FILE="$HOME/.local/share/task-manager/server.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  : # Server already running — do nothing
else
  uv run --project "$TASK_PROJECT" task-server &
fi
```

To verify the server is reachable:

```bash
curl --unix-socket ~/.local/share/task-manager/task_manager.sock \
  http://localhost/api/v1/health
```

## Entry Points

All commands are run via `uv run --project <repo-root>`:

| Command | Purpose |
|---------|---------|
| `uv run --project <repo> task-server` | Start API server on Unix socket (singleton) |
| `uv run --project <repo> task` | CLI for AI agents (terse tab-separated output) |
| `uv run --project <repo> task-tui` | Interactive terminal UI with vim navigation |

## CLI Reference

Output is terse tab-separated by default. Add `--json` before the subcommand
for JSON output. Examples below assume the `task` alias from Setup, or
substitute `uv run --project <repo> task`.

### Boards

```bash
task board list                              # List all boards
task board create --name "Project X"         # Create (auto-creates To Do/In Progress/Done columns)
task board get <board_id>                    # Get board details
task board update <board_id> --name "New"    # Rename board
task board delete <board_id>                 # Delete board
```

### Lists (columns within a board)

```bash
task list ls --board-id <board_id>                              # List all lists
task list create --board-id <board_id> --name "Backlog"         # Create list
task list get --board-id <board_id> <list_id>                   # Get list
task list update --board-id <board_id> <list_id> --name "Done"  # Update list
task list delete --board-id <board_id> <list_id>                # Delete list
```

### Cards (tasks within a list)

```bash
task card list                                                     # List all cards
task card list --list-id <id> --priority high                      # Filter cards
task card create --list-id <id> --title "Fix bug" --priority high  # Create card
task card get <card_id>                                            # Get card
task card update <card_id> --title "New title"                     # Update card
task card move <card_id> --to-list-id <list_id>                    # Move card
task card bulk-move --card-ids "id1,id2" --to-list-id <list_id>    # Bulk move
task card delete <card_id>                                         # Delete card
```

### Card options

- `--priority`: low, medium (default), high, urgent
- `--labels`: Comma-separated labels, e.g. "bug,urgent"
- `--description`: Task description text

## TUI Reference

Launch with `task-tui` (or `uv run --project <repo> task-tui`).
Keyboard-only, vim-style navigation. Arrow keys also work everywhere
alongside hjkl.

### Three-tier navigation

| Level | h / ← | l / → | j / ↓ / Enter | k / ↑ / Esc |
|-------|--------|-------|---------------|-------------|
| **Board** | Prev board | Next board | Dive into columns | — |
| **Column** | Prev column | Next column | Dive into cards | Back to board |
| **Card** | — | — | Next card | Prev card (k/↑), Esc=back to column |

### Card actions (when focused on a card)

| Key | Action |
|-----|--------|
| `e` | Edit card via `$EDITOR` (opens YAML temp file, k9s style) |
| `x` | Delete card (confirmation prompt) |
| `m` then `h` | Move card to previous (left) column |
| `m` then `l` | Move card to next (right) column |

### Global shortcuts

| Key | Action |
|-----|--------|
| `b` | Create new board |
| `L` (shift) | Create new column in current board |
| `c` | Create new card in current column |
| `d` | Delete current board |
| `r` | Refresh data |
| `q` | Quit |

## Common Workflows

### Set up a new project board

```bash
task board create --name "My Project"
# Default columns (To Do, In Progress, Done) are auto-created
```

### Create and track tasks

```bash
task card create --list-id <todo_list_id> --title "Implement feature X" --priority high
task card create --list-id <todo_list_id> --title "Write tests" --priority medium
# Move to in-progress when starting work
task card move <card_id> --to-list-id <in_progress_list_id>
# Move to done when complete
task card move <card_id> --to-list-id <done_list_id>
```

### Check current status

```bash
task --json card list --list-id <todo_list_id>       # What's pending
task --json card list --list-id <in_progress_id>     # What's active
task --json card list --priority urgent               # What's urgent
```

## Output Format

Default output is tab-separated for minimal token usage:
```
abc12345	medium	Fix the login bug
def67890	high	Deploy to production
```

Use `--json` when you need structured data for processing.

## API Direct Access

If you prefer HTTP directly, all endpoints are available via the Unix socket:

```bash
# Example: list boards
curl --unix-socket ~/.local/share/task-manager/task_manager.sock \
  http://localhost/api/v1/boards
```
