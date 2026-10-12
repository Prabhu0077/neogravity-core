# @vibcoder/neogravity

Scaffold a small set of files that give an AI coding assistant (Cursor, Windsurf, Claude Code and similar) a memory between chat sessions.

AI assistants forget everything when a chat ends. This tool does not change that. It creates plain Markdown files, a task list and a decision log, plus short instructions that tell the assistant to read them at the start and update them at the end. Nothing runs in the background and nothing is sent anywhere.

## Use

```bash
npx @vibcoder/neogravity init
```

Options: `--yes` (skip the prompt), `--dir <path>`, `--dry-run`. Existing files are never overwritten.

## What it creates

```
.agents/
  rules/project-context.md        # how the assistant should start and end a session
  workflows/session-start.md      # load context
  workflows/session-end.md        # save context
  workflows/new-task.md           # add a well-formed task
  skills/session-handoff/SKILL.md # how to write good handoff notes
  skills/decision-log/SKILL.md    # how to record a decision
.knowledge/
  tasks/active_tasks.md           # what is done, in progress, next
  decisions/README.md             # one file per decision goes here
```

## Then

1. Write your first next step in `.knowledge/tasks/active_tasks.md`.
2. Tell your assistant: "Run the session-start workflow." At the end: "Run the session-end workflow."

Different assistants read rules from different places. If yours looks elsewhere (for example `.cursor/rules/`), copy `.agents/rules/project-context.md` there.

## What this is not

- It is not an operating system, an agent or a memory database. It is a folder of text files.
- It has not been tested in a controlled study. It is a small tool that we use ourselves; see the write-up below for what we learned.

## More

- Write-up: <https://bodhamlabs.com/research/agent-context-tooling>
- Source and issues: <https://github.com/Prabhu0077/neogravity-core>
- Changelog: [CHANGELOG.md](./CHANGELOG.md). Version 4.0.0 contained files that did not belong in a public package; please use 4.1.0 or later.

Built by [Bodham Labs](https://bodhamlabs.com), Delhi. MIT licence.
