---
description: Load project context at the start of a session.
---

# /session-start

Run this at the beginning of a chat with your AI assistant.

1. Read `.knowledge/tasks/active_tasks.md`.
2. List the files in `.knowledge/decisions/` and read the three newest.
3. Report back in this shape:
   - **In progress:** what the task list says is being worked on
   - **Recent decisions:** one line each
   - **Proposed next step:** one action, and why
4. Wait for the user to confirm or change the plan before editing any files.
