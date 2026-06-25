---
name: task-manager
description: >
  Single-file task manager. All boards and tasks live in
  .task-manager.todos.yaml at the project root.
  No server, no dependencies — just one YAML file.
  Use when: the user wants to create tasks, manage a todo list, organize work
  into boards, move tasks between statuses, or runs /task-manager.
  Trigger keywords: "task", "todo", "board", "card", "create task",
  "move task", "task list", "manage tasks", "kanban".
---

# Task Manager Skill

Single-file task manager. No server, no CLI, no dependencies.
All boards and tasks live in one file: `.task-manager.todos.yaml`

One read to see everything. One write to change anything.

## File Location

```
<project-root>/.task-manager.todos.yaml
```

Create it when you need it. Delete it to remove all tasks.

## File Format

```yaml
my_project:
  todo:
    - title: Implement auth
      priority: high
      labels: [backend, security]
    - title: Write tests
  in_progress:
    - title: Fix login bug
      description: Users can't log in with special characters
      priority: urgent
      labels: [bug]
  done:
    - title: Setup CI

backend_refactor:
  todo:
    - title: Migrate to Postgres
      priority: high
    - title: Update ORM models
  in_progress: []
  done:
    - title: Design new schema
```

## Structure

```yaml
<board_name>:
  todo:
    - <task>
    - <task>
  in_progress:
    - <task>
  done:
    - <task>
```

- **Top-level keys** = board names (snake_case)
- **Second-level keys** = status columns: `todo`, `in_progress`, `done`
- **Lists under each status** = tasks

## Task Fields

A task can be a simple string (title only) or an object:

```yaml
# Minimal — just a title
- title: Fix the bug

# Full — all fields
- title: Fix the payment flow
  description: |
    Users get a 500 error when submitting payment
    with international cards.
  priority: high
  labels: [bug, payments]
  created: 2026-06-26
  due: 2026-07-01
```

| Field | Required | Type | Notes |
|-------|----------|------|-------|
| `title` | yes | string | Short, descriptive title |
| `description` | no | string | Details (use `\|` for multiline) |
| `priority` | no | string | `low`, `medium`, `high`, `urgent` |
| `labels` | no | list | Freeform tags |
| `created` | no | date | `YYYY-MM-DD` |
| `due` | no | date | `YYYY-MM-DD` deadline |

## Operations

All operations are just edits to `.task-manager.todos.yaml`.

### Create a board

Add a new top-level key:

```yaml
new_board:
  todo: []
  in_progress: []
  done: []
```

### Create a task

Append to the `todo` list of a board:

```yaml
my_project:
  todo:
    - title: Existing task
    - title: New task        # ← add here
      priority: high
```

### Move a task

Cut from one status list, paste into another:

```yaml
# Before — task is in todo
my_project:
  todo:
    - title: Fix login bug
  in_progress: []

# After — moved to in_progress
my_project:
  todo: []
  in_progress:
    - title: Fix login bug
```

### Update a task

Edit fields in place.

### Delete a task

Remove it from the list.

### Delete a board

Remove the entire top-level key.

### Clean up done tasks

Clear the `done` list: `done: []`

## Example Session

Read the file to see current state:

```bash
cat .task-manager.todos.yaml
```

Then edit it to make changes. That's it.

## Why This Design

- **One file, one read** — the agent sees all boards and tasks in a single tool call
- **Zero dependencies** — no Python, no server, no database, no installation
- **Minimal tokens** — compact YAML, no repeated boilerplate per file
- **Git-friendly** — one file to track in version control
- **Self-cleaning** — delete the file and everything is gone
