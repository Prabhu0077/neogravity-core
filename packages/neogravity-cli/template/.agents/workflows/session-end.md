---
description: Save what happened before a session ends.
---

# /session-end

Run this before you close a chat, or when the user says they are done.

1. Update `.knowledge/tasks/active_tasks.md`:
   - tick what is finished
   - add anything new that came up
   - put the best next step at the very top
2. If a decision was made in this session, add a file to `.knowledge/decisions/`
   using the `decision-log` skill.
3. List anything the user must do by hand (a command, an approval, a secret to set).
   For each one say what it does and why you could not do it yourself.
4. Print a short summary: done, not done, next step.
