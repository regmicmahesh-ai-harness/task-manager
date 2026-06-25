# Task Manager

A file-based task manager designed for AI agents. No server, no dependencies,
no installation — just folders and YAML files.

- **Boards** = folders under `./todos/`
- **Tasks** = YAML files (`todo_fix-bug.yaml`, `in_progress_refactor.yaml`, `done_deploy.yaml`)
- **Status** = the filename prefix — rename to move between statuses

## Usage

Use as a [Grok](https://github.com/anthropics/grok) skill:

```bash
git clone https://github.com/regmicmahesh-ai-harness/task-manager.git \
  ~/.grok/skills/task-manager
```

Then invoke with `/task-manager` or just ask the agent to manage tasks.

See [SKILL.md](SKILL.md) for the full reference.