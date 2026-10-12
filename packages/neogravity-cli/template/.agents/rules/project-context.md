---
trigger: always_on
---

# Project context rules

These rules tell your AI coding assistant how to keep context between sessions.
Edit them to fit your project. Delete anything you do not need.

## At the start of every session

1. Read `.knowledge/tasks/active_tasks.md` to see what is in progress.
2. Skim the newest files in `.knowledge/decisions/` so you do not undo a past decision.
3. Tell the user, in two or three lines, what you found and what you plan to do next.

## At the end of every session

1. Update `.knowledge/tasks/active_tasks.md`: tick finished items, add what is left.
2. If a real decision was made, record it using the `decision-log` skill.
3. Write the single most useful next step at the top of `active_tasks.md`.

## Ground rules

- Never invent file paths, URLs, credentials or API keys. If you do not know, say so.
- Never write secrets into `.knowledge/` or `.agents/`. Refer to them by name only.
- Prefer small, reviewable changes. Say what you changed and how you checked it.
