# Task Manager

Single-file task manager for AI agents. All boards and tasks live in one
YAML file (`.task-manager.todos.yaml`) at the project root. No server, no
dependencies, no installation.

## Usage

Use as a [Grok](https://github.com/anthropics/grok) skill:

```bash
git clone https://github.com/regmicmahesh-ai-harness/task-manager.git \
  ~/.grok/skills/task-manager
```

Then invoke with `/task-manager` or just ask the agent to manage tasks.

See [SKILL.md](SKILL.md) for the full reference.