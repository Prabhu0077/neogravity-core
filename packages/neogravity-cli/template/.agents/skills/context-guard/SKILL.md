---
name: Context Guard
description: Pre-flight check patterns to prevent duplicate work, detect staleness, and identify trends. Load before any workflow that should check Sovereign Memory before acting.
---

# Context Guard — Pre-Flight Check Patterns

Load this skill when a workflow should CHECK before ACTING. These patterns query Sovereign Memory to prevent duplicate work and catch anomalies.

> [!IMPORTANT]
> **Offline Rule:** If Sovereign Memory is OFFLINE, skip ALL guards silently and proceed. Guards are advisory, not blocking. Never let a guard failure stop a workflow.
>
> **Warning Rule:** When a guard triggers a warning, present it **inline in the chat** (do NOT use `notify_user` — that exits task mode). Show the warning, then ask the user to confirm or abort.

## Guard 0: The Planning Loop (Mid-Session Sync)

**Use when:** You are formulating a plan for a new task or sub-task, AND when you finish executing it.

**Phase 1: Pre-Flight Query (Start of Planning)**
Before writing any code or finalizing a plan, check if a concurrent sibling session just modified your target component:

```text
Query: memory_query("<component name> recent changes")
If recent results highlight a conflict:
  → ADJUST your plan to incorporate the sibling's new state.
If no recent conflict:
  → PROCEED to Execution.
```

**Phase 2: Post-Flight Ingest (End of Execution)**
Immediately after successfully completing a task (before moving to the next item on your list), broadcast your change:

```text
Ingest: memory_ingest(
  text: "Task completed: [1-sentence summary of what you just built/changed]",
  source: "task-<component>-YYYY-MM-DD",
  intent: "session"
)
```

## Guard 1: Duplicate Detection

**Use when:** About to create something that may already exist (outreach, deploy, content).

```
Query: memory_query("<action description> <target>")
If results found with matching intent and recent date:
  → WARN user: "This was already done on [date]. Summary: [text]. Proceed anyway?"
If no results:
  → PROCEED silently
```

**Used by:** `/outreach` (duplicate contacts), `/deploy` (double-deploy), `/sync-profiles` (re-generation)

## Guard 2: Staleness Detection

**Use when:** Monitoring something that should have regular activity.

```
Query: memory_query("<activity type>")
If NO results in last N sessions:
  → ESCALATE: "[Activity] has been inactive for N sessions — investigate"
If results exist:
  → PROCEED silently
```

**Used by:** `/bootstrap` (stale in-progress tasks), `/harvest-check` (dead scripts)

## Guard 3: Trend Analysis

**Use when:** A single check is normal, but a pattern of identical results indicates a problem.

```
Query: memory_query("<check type>")
Review last 3 results:
  If all show same negative status → ALERT: "Pattern detected — [status] for 3+ checks"
  If mixed → PROCEED normally
```

**Used by:** `/harvest-check` (persistent STALE), `/verify-narrative` (recurring violations)

**Escalation = Alert + Continue:** Escalation means surfacing an alert at the top of the workflow output, then continuing execution normally. It does NOT block the workflow.

## Decision Table

| Guard     | Match Found                      | Action                         |
| --------- | -------------------------------- | ------------------------------ |
| Duplicate | Yes, same target + recent        | ⚠️ Warn user, ask to proceed   |
| Duplicate | Yes, same target + old (>7 days) | ℹ️ Note prior contact, proceed |
| Duplicate | No match                         | ✅ Proceed silently            |
| Staleness | No activity for 3+ sessions      | 🔴 Escalate to user            |
| Staleness | Recent activity exists           | ✅ Proceed silently            |
| Trend     | 3+ identical negative results    | 🔴 Alert — systemic issue      |
| Trend     | Mixed results                    | ✅ Proceed normally            |
