---
name: task-manager
description: >
  File-based task manager. Boards are folders, tasks are YAML files.
  Status is the filename prefix: todo_, in_progress_, done_.
  No server, no dependencies — just files.
  Use when: the user wants to create tasks, manage a todo list, organize work
  into boards, move tasks between statuses, or runs /task-manager.
  Trigger keywords: "task", "todo", "board", "card", "create task",
  "move task", "task list", "manage tasks", "kanban".
---

# Task Manager Skill

A file-based task manager. No server, no CLI, no dependencies. Just folders
and YAML files that any LLM can read and write directly.

- **Boards** = folders under `./todos/`
- **Tasks** = YAML files inside a board folder
- **Status** = the filename prefix (`todo_`, `in_progress_`, `done_`)

Moving a task between statuses = renaming the file.

## Setup

None. Create a `todos/` directory in your project root when you need it:

```bash
mkdir -p todos
```

## Directory Structure

```
<project-root>/
└── todos/
    ├── my_project/
    │   ├── todo_implement-auth.yaml
    │   ├── todo_write-tests.yaml
    │   ├── in_progress_fix-login-bug.yaml
    │   └── done_setup-ci.yaml
    └── backend_refactor/
        ├── todo_migrate-to-postgres.yaml
        └── in_progress_update-orm-models.yaml
```

## Naming Convention

### Board folders

- Location: `todos/<board_name>/`
- Use `snake_case` for folder names
- Create the folder to create a board, delete it to delete a board

### Task files

Filename format: `<status>_<slug>.yaml`

| Prefix | Meaning |
|--------|---------|
| `todo_` | Not started |
| `in_progress_` | Currently being worked on |
| `done_` | Completed |

- `<slug>` is a short, descriptive `kebab-case` identifier
- Example: `todo_fix-payment-flow.yaml`, `in_progress_add-retry-logic.yaml`

## Task File Format

Each task is a YAML file with these fields:

```yaml
title: Fix the payment flow
description: |
  Users are getting a 500 error when submitting payment with
  international cards. Need to handle currency conversion.
priority: high
labels:
  - bug
  - payments
created: 2026-06-26
due: 2026-07-01
```

### Fields

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `title` | yes | string | Short, descriptive title |
| `description` | no | string | Detailed description (use `\|` for multiline) |
| `priority` | no | string | `low`, `medium` (default), `high`, `urgent` |
| `labels` | no | list | Freeform tags |
| `created` | yes | date | `YYYY-MM-DD` — set when creating |
| `due` | no | date | `YYYY-MM-DD` — optional deadline |

## Operations

### Create a board

```bash
mkdir -p todos/my_project
```

### Delete a board

```bash
rm -rf todos/my_project
```

### Create a task

Write a YAML file with the `todo_` prefix:

```bash
cat > todos/my_project/todo_fix-login.yaml << 'EOF'
title: Fix login bug
description: Users can't log in with special characters in password
priority: high
labels:
  - bug
  - auth
created: 2026-06-26
EOF
```

### Move a task (change status)

Rename the file prefix:

```bash
# Start working on it
mv todos/my_project/todo_fix-login.yaml todos/my_project/in_progress_fix-login.yaml

# Mark as done
mv todos/my_project/in_progress_fix-login.yaml todos/my_project/done_fix-login.yaml
```

### Update a task

Edit the YAML file directly. Change any field.

### Delete a task

```bash
rm todos/my_project/done_fix-login.yaml
```

### List all tasks in a board

```bash
ls todos/my_project/
```

### List tasks by status

```bash
ls todos/my_project/todo_*          # What's pending
ls todos/my_project/in_progress_*   # What's active
ls todos/my_project/done_*          # What's completed
```

### List all boards

```bash
ls todos/
```

### Find urgent tasks across all boards

```bash
grep -rl "priority: urgent" todos/
```

### Find tasks by label

```bash
grep -rl "bug" todos/
```

## Common Workflows

### Set up a new project board

```bash
mkdir -p todos/my_project
```

That's it. No default columns needed — status is in the filename.

### Track work on a feature

```bash
# Create tasks
cat > todos/my_project/todo_implement-api.yaml << 'EOF'
title: Implement REST API
priority: high
labels: [backend]
created: 2026-06-26
EOF

cat > todos/my_project/todo_write-tests.yaml << 'EOF'
title: Write integration tests
priority: medium
labels: [testing]
created: 2026-06-26
EOF

# Start working
mv todos/my_project/todo_implement-api.yaml todos/my_project/in_progress_implement-api.yaml

# Finish
mv todos/my_project/in_progress_implement-api.yaml todos/my_project/done_implement-api.yaml
```

### Quick status check

```bash
echo "=== TODO ===" && ls todos/my_project/todo_* 2>/dev/null
echo "=== IN PROGRESS ===" && ls todos/my_project/in_progress_* 2>/dev/null
echo "=== DONE ===" && ls todos/my_project/done_* 2>/dev/null
```

### Clean up completed tasks

```bash
rm todos/my_project/done_*
```

## Why This Design

- **Zero dependencies** — no Python, no server, no database, no installation
- **LLM-native** — agents already know how to read/write files and run shell commands
- **Git-friendly** — tasks are plain text files, track them in version control
- **Grep-friendly** — find anything with `grep`, `find`, `ls`
- **Portable** — works on any machine with a filesystem
- **Self-cleaning** — delete the `todos/` folder and everything is gone
