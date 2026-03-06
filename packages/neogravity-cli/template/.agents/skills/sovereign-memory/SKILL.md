---
name: Sovereign Memory
description: Reference manual for Sovereign Memory MCP tools — intent vocabulary, ingest/query patterns, MoE-aware rules. Load this before ANY workflow that reads or writes to Sovereign Memory.
---

# Sovereign Memory Operations

Load this skill whenever a workflow needs to ingest data into or query from Sovereign Memory.

> [!IMPORTANT]
> **SM Resilience — The Self-Healing Rules**
>
> NeoGravity treats SM as **advisory, never critical**. No workflow ever crashes because SM broke.
>
> | State        | How You Know                                               | What To Do                                                                                                         |
> | ------------ | ---------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
> | **OFFLINE**  | SM tools not in tool list at boot                          | Skip this skill entirely. All SM steps silently skipped.                                                           |
> | **DEGRADED** | SM was ONLINE but a tool call returns an error mid-session | Log the error in your context. Skip all remaining SM steps for this session. Report "SM: DEGRADED" at session-end. |
> | **ERROR**    | A single SM tool call fails (timeout, exception)           | Skip that one step. Continue the workflow. Do NOT retry — the next natural SM call will test health again.         |
>
> **Recovery:** If SM goes DEGRADED, suggest user runs `/memory-start` to restart. Do not attempt to fix SM yourself.
>
> **Session-end rule:** If SM was DEGRADED this session, note it in `session_log.md` so next boot knows.

## Intent Vocabulary (Controlled — pick exactly one)

| Intent         | When to Use                                                  | Example Source Name                 |
| -------------- | ------------------------------------------------------------ | ----------------------------------- |
| `session`      | Session logs, boot context, handoff notes                    | `session-2026-03-05`                |
| `decision`     | Architectural/strategic decisions that must survive sessions | `decision-2026-03-05`               |
| `outreach`     | Cold emails, LinkedIn messages, company research             | `outreach-towerresearch-2026-03-05` |
| `deploy`       | Deployment events, build results, verification logs          | `deploy-neonerd-2026-03-05`         |
| `research`     | Technical research, benchmark results, audit findings        | `research-chunking-2026-03-05`      |
| `harvest`      | Data harvest health snapshots, gap reports                   | `harvest-health-2026-03-05`         |
| `architecture` | System design docs, ADRs, component specifications           | `architecture-sentinel-moe`         |
| `general`      | Default — anything that doesn't fit above                    | `general-notes`                     |

## Ingest Template

```
memory_ingest(
  text: "<structured summary — WHO/WHAT/WHEN/WHY>",
  source: "<category>-<identifier>-<YYYY-MM-DD>",
  intent: "<one of 8 values above>"
)
```

**Rules:**

- Text should be a meaningful summary, not raw dumps
- Source name follows `category-identifier-date` convention
- Dedup is automatic (SHA-256 content hash → upsert) — safe to re-ingest
- Context prefix (`[source | intent]`) is added automatically for the embedder
- GLiNER receives raw text (no prefix) — never manually prepend metadata

## Query Patterns

| Pattern        | Use Case                  | Example                                               |
| -------------- | ------------------------- | ----------------------------------------------------- |
| **Recall**     | "What happened before?"   | `memory_query("deployment history for NeoNerd")`      |
| **Pre-flight** | "Did we already do this?" | `memory_query("outreach to TowerResearch")`           |
| **Trend**      | "Is this a pattern?"      | `memory_query("harvest health check")` → check last 3 |

## MoE-Aware Rules (DO NOT BREAK)

- **Embedder** (vector path): receives `[source | intent] + text` — context improves retrieval 35-49%
- **GLiNER** (graph path): receives raw text only — metadata words are noise for entity extraction
- This dual-format routing is handled automatically by `server.py` — do NOT manually prefix text
