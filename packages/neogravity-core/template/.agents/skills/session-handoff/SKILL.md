---
name: Session Handoff
description: Patterns for preserving and restoring context across sessions — what to capture at session-end, how to recall at boot. Load during bootstrap and shutdown.
---

# Session Handoff — Cross-Session Context Preservation

Load this skill during session boot (bootstrap) and session-end (shutdown protocol) to ensure nothing is lost between sessions.

## The Volatility Problem

- `session_log.md` is **overwritten** each session → only last session survives
- `decision_log.md` is **append-only** → grows forever, hard to search
- Memory MCP graph is **static** → good for stable facts, bad for session context
- **Sovereign Memory** is the permanent semantic store → survives indefinitely, searchable

## Session-End Capture Template

At session end, ingest two things:

### 1. Session Summary
```
memory_ingest(
  text: "Session YYYY-MM-DD: [what was accomplished]. Key changes: [files modified]. Next step: [immediate priority].",
  source: "session-YYYY-MM-DD",
  intent: "session"
)
```

### 2. Decisions Made (if any)
```
memory_ingest(
  text: "Decision: [what was decided]. Rationale: [why]. Alternatives rejected: [what else was considered].",
  source: "decision-YYYY-MM-DD",
  intent: "decision"
)
```

**Skip silently** if Sovereign Memory is OFFLINE.

## Boot Recall Pattern

At session boot (after Sovereign Memory status check):

```
memory_query("key decisions and changes from recent sessions")
→ Surface top-3 results in status report under "Deep Recall"
→ This recovers context that session_log.md may have lost
```

## Source Naming Convention

```
<category>-<YYYY-MM-DD>     (for date-scoped events)
<category>-<identifier>     (for entity-scoped items)
```

Examples: `session-2026-03-05`, `decision-2026-03-05`, `outreach-towerresearch-2026-03-05`
