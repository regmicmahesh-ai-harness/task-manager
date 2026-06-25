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

You have access to a Trello-like task manager with boards, lists, and cards.
Use the CLI commands below to manage tasks. The CLI is optimized for minimal
token output.

## Setup

Install the package from GitHub (one-time):

```bash
uv pip install "task-manager @ git+https://github.com/regmicmahesh-ai-harness/task-manager.git"
```

### Starting the server (singleton, Unix socket)

The API server listens on a **Unix domain socket** at
`~/.local/share/task-manager/task_manager.sock` — no TCP port needed.

**IMPORTANT — singleton server:** Only ONE instance of the server should run
at a time, even if multiple models or skill invocations are active. Always
check before starting:

```bash
SOCK="$HOME/.local/share/task-manager/task_manager.sock"
PID_FILE="$HOME/.local/share/task-manager/server.pid"

if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
  : # Server already running — do nothing
else
  rm -f "$SOCK"
  uvicorn api.main:app --uds "$SOCK" &
  echo $! > "$PID_FILE"
fi
```

To verify the server is reachable:

```bash
curl --unix-socket "$SOCK" http://localhost/api/v1/health
```

## CLI Reference

All commands use the `task` entry point. Output is terse tab-separated by
default. Add `--json` before the subcommand for JSON output.

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
