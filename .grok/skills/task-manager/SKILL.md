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

Then ensure the API server is running:

```bash
# Check if server is running, start if not
curl -s http://localhost:8000/api/v1/health > /dev/null 2>&1 || \
  (uvicorn api.main:app --host 0.0.0.0 --port 8000 &)
```

## CLI Reference

All commands use the `task` entry point. Output is terse tab-separated by
default. Add `--json` before the subcommand for JSON output.

### Boards

```bash
task board list                              # List all boards
task board create --name "Project X"         # Create a board
task board get <board_id>                    # Get board details
task board update <board_id> --name "New"    # Rename board
task board delete <board_id>                 # Delete board
```

### Lists (columns within a board)

```bash
task list ls --board-id <board_id>                              # List all lists
task list create --board-id <board_id> --name "To Do"           # Create list
task list get --board-id <board_id> <list_id>                   # Get list
task list update --board-id <board_id> <list_id> --name "Done"  # Update list
task list delete --board-id <board_id> <list_id>                # Delete list
```

### Cards (tasks within a list)

```bash
task card list                                                   # List all cards
task card list --list-id <id> --status todo --priority high      # Filter cards
task card create --list-id <id> --title "Fix bug" --priority high  # Create card
task card get <card_id>                                          # Get card
task card update <card_id> --status done                         # Update card
task card move <card_id> --to-list-id <list_id>                  # Move card
task card bulk-move --card-ids "id1,id2" --to-list-id <list_id>  # Bulk move
task card delete <card_id>                                       # Delete card
```

### Card options

- `--priority`: low, medium (default), high, urgent
- `--status`: todo (default), in_progress, done, archived
- `--labels`: Comma-separated labels, e.g. "bug,urgent"
- `--description`: Task description text

## Common Workflows

### Set up a new project board

```bash
task board create --name "My Project"
# Use the board_id from output
task list create --board-id <board_id> --name "To Do" --position 0
task list create --board-id <board_id> --name "In Progress" --position 1
task list create --board-id <board_id> --name "Done" --position 2
```

### Create and track tasks

```bash
task card create --list-id <todo_list_id> --title "Implement feature X" --priority high
task card create --list-id <todo_list_id> --title "Write tests" --priority medium
# Move to in-progress when starting work
task card move <card_id> --to-list-id <in_progress_list_id>
# Mark done
task card update <card_id> --status done
task card move <card_id> --to-list-id <done_list_id>
```

### Check current status

```bash
task --json card list --status todo          # What's pending
task --json card list --status in_progress   # What's active
task --json card list --priority urgent      # What's urgent
```

## Output Format

Default output is tab-separated for minimal token usage:
```
abc12345	todo	medium	Fix the login bug
def67890	done	high	Deploy to production
```

Use `--json` when you need structured data for processing.

## API Direct Access

If you prefer HTTP directly, all endpoints are at `http://localhost:8000/api/v1/`.
Full OpenAPI docs at `http://localhost:8000/docs`.
