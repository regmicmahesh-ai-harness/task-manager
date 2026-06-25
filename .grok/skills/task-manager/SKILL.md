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

All scripts live in `scripts/` next to this file. Nothing is installed
globally — the virtual environment lives inside the repo. Removing the
skill directory cleans up everything.

```bash
# One-time: install dependencies (creates .venv/ in the repo)
.grok/skills/task-manager/scripts/setup.sh
```

### Starting the server (singleton, Unix socket)

The API server listens on a **Unix domain socket** at
`~/.local/share/task-manager/task_manager.sock` — no TCP port needed.

**IMPORTANT — singleton server:** Only ONE instance of the server should run
at a time, even if multiple models or skill invocations are active. The
script handles this automatically:

```bash
.grok/skills/task-manager/scripts/start-server.sh   # safe to call repeatedly
.grok/skills/task-manager/scripts/stop-server.sh     # stop when done
```

To verify the server is reachable:

```bash
curl --unix-socket ~/.local/share/task-manager/task_manager.sock \
  http://localhost/api/v1/health
```

## Scripts

All scripts auto-resolve the repo root — call them from any directory.

| Script | Purpose |
|--------|---------|
| `scripts/setup.sh` | One-time dependency install (creates `.venv/`) |
| `scripts/start-server.sh` | Start API server (singleton, safe to re-call) |
| `scripts/stop-server.sh` | Stop the API server |
| `scripts/task.sh` | CLI wrapper — pass any `task` args after it |
| `scripts/task-tui.sh` | Launch the interactive TUI |

## CLI Reference

Output is terse tab-separated by default. Add `--json` before the subcommand
for JSON output.

### Boards

```bash
.grok/skills/task-manager/scripts/task.sh board list                              # List all boards
.grok/skills/task-manager/scripts/task.sh board create --name "Project X"         # Create board
.grok/skills/task-manager/scripts/task.sh board get <board_id>                    # Get board details
.grok/skills/task-manager/scripts/task.sh board update <board_id> --name "New"    # Rename board
.grok/skills/task-manager/scripts/task.sh board delete <board_id>                 # Delete board
```

### Lists (columns within a board)

```bash
.grok/skills/task-manager/scripts/task.sh list ls --board-id <board_id>                              # List all lists
.grok/skills/task-manager/scripts/task.sh list create --board-id <board_id> --name "Backlog"         # Create list
.grok/skills/task-manager/scripts/task.sh list get --board-id <board_id> <list_id>                   # Get list
.grok/skills/task-manager/scripts/task.sh list update --board-id <board_id> <list_id> --name "Done"  # Update list
.grok/skills/task-manager/scripts/task.sh list delete --board-id <board_id> <list_id>                # Delete list
```

### Cards (tasks within a list)

```bash
.grok/skills/task-manager/scripts/task.sh card list                                                     # List all cards
.grok/skills/task-manager/scripts/task.sh card list --list-id <id> --priority high                      # Filter cards
.grok/skills/task-manager/scripts/task.sh card create --list-id <id> --title "Fix bug" --priority high  # Create card
.grok/skills/task-manager/scripts/task.sh card get <card_id>                                            # Get card
.grok/skills/task-manager/scripts/task.sh card update <card_id> --title "New title"                     # Update card
.grok/skills/task-manager/scripts/task.sh card move <card_id> --to-list-id <list_id>                    # Move card
.grok/skills/task-manager/scripts/task.sh card bulk-move --card-ids "id1,id2" --to-list-id <list_id>    # Bulk move
.grok/skills/task-manager/scripts/task.sh card delete <card_id>                                         # Delete card
```

### Card options

- `--priority`: low, medium (default), high, urgent
- `--labels`: Comma-separated labels, e.g. "bug,urgent"
- `--description`: Task description text

## TUI Reference

Launch with `scripts/task-tui.sh`. Keyboard-only, vim-style navigation.
Arrow keys also work everywhere alongside hjkl.

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
TASK=".grok/skills/task-manager/scripts/task.sh"
$TASK board create --name "My Project"
# Default columns (To Do, In Progress, Done) are auto-created
```

### Create and track tasks

```bash
$TASK card create --list-id <todo_list_id> --title "Implement feature X" --priority high
$TASK card create --list-id <todo_list_id> --title "Write tests" --priority medium
# Move to in-progress when starting work
$TASK card move <card_id> --to-list-id <in_progress_list_id>
# Move to done when complete
$TASK card move <card_id> --to-list-id <done_list_id>
```

### Check current status

```bash
$TASK --json card list --list-id <todo_list_id>       # What's pending
$TASK --json card list --list-id <in_progress_id>     # What's active
$TASK --json card list --priority urgent               # What's urgent
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
