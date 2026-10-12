---
name: Session Handoff
description: How to leave notes so the next session (yours or a teammate's) can continue without re-asking. Load at session start and end.
---

# Session handoff

An AI assistant forgets everything when a chat ends. Files do not. The handoff is
three small files you keep up to date:

| File | What it holds | How it changes |
| --- | --- | --- |
| `.knowledge/tasks/active_tasks.md` | What is done, in progress, next | Edited every session |
| `.knowledge/decisions/NNNN-title.md` | Why we chose X over Y | One new file per decision, never edited later |
| `.agents/rules/project-context.md` | How the assistant should behave | Edited rarely |

## Good handoff notes

- Say what you did **and how you checked it**: "fixed login redirect, ran `npm test`, 12 pass".
- Name files by path, not "that file".
- For anything the user must do by hand, give the command, what it does, and why you could not run it.

## Bad handoff notes

- "Worked on auth." (what, and is it finished?)
- Secrets, tokens or passwords. Name the variable instead: "set `STRIPE_KEY` in the host dashboard".
