---
name: Decision Log
description: Record a decision and its reasons so it is not re-argued later. Load when the user and assistant choose between options.
---

# Decision log

Create one file per decision: `.knowledge/decisions/NNNN-short-title.md`
(`0001`, `0002`, ... in order). Do not edit old decisions. If you change your mind,
write a new one that says "Supersedes 0003".

## Template

```markdown
# NNNN. Short title

- Date: YYYY-MM-DD
- Status: accepted | superseded by NNNN

## Context
What problem were we solving? One short paragraph.

## Decision
What did we choose?

## Alternatives considered
- Option A: why not
- Option B: why not

## Consequences
What gets easier, and what gets harder?
```
