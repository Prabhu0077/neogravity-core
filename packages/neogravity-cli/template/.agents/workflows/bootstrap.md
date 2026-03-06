---
description: Initialize a fresh Antigravity session by loading all project context, memory graph, and reporting status to the user.
---

// turbo-all

# Boot Protocol — Session Initialization v3.1

Run these steps in order at the start of every new session.
This protocol is part of **NeoGravity** — the agentic operating system for AI sessions.

## Required Skills (load at start — DO NOT skip)

- Load `session-handoff` skill (for deep recall and session context patterns)
- Load `sovereign-memory` skill (for SM tool usage patterns) — **skip if SM is OFFLINE**

## Phase 0: Concurrent Session Awareness

0. Check for active sibling sessions:
   - List files in `d:\P-Projects\profile-neo\.knowledge\sessions\`
   - For each `session_*.json` file:
     - Read it
     - If `status = "active"` AND `last_active` < 30 min ago → live sibling
     - If `status = "active"` AND `last_active` > 30 min ago → dead session, ignore
     - If `status = "done"` → completed session, ignore
   - If live siblings found:
     → Report: "ℹ️ Active sibling: [name] working on [focus] (last seen [last_active])"
     → Suggest non-overlapping work area. NEVER block — always proceed.
   - Register THIS session:
     - Create `d:\P-Projects\profile-neo\.knowledge\sessions\session_<first-8-chars-of-conversation-id>.json`
     - Set status="active", focus="awaiting user direction", started=now, last_active=now
   - If `.knowledge/sessions/` directory doesn't exist → create it, then register

## Phase 1: Load Core Context (3 files — ALWAYS read)

1. Read the master context index (hierarchical — Quick Reference is critical):
   - Use `view_file` tool on `d:\P-Projects\profile-neo\context_index.md`

2. Read the session log to understand what the PREVIOUS session accomplished:
   - Use `view_file` tool on `d:\P-Projects\profile-neo\session_log.md`

3. Read active tasks to know EXACTLY what's pending across all phases:
   - Use `view_file` tool on `d:\P-Projects\profile-neo\.knowledge\tasks\active_tasks.md`

## Phase 1.5: Load Neo Swarm Nexus Context (CONDITIONAL)

4. ALWAYS read `neo-swarm-nexus/DATA_HARVEST_STATUS.md` — this is small (30 lines) and gives harvest state.
   - Only ALSO read `neo-swarm-nexus/MIGRATION_PLAN.md` if the user's request involves training, data, or Neo Swarm Nexus.
   - Only ALSO read `neo-swarm-nexus/ARCHITECTURE.md` if the user's request involves coding, debugging, or technical discussion about the system.

## Phase 2: Load Persistent Memory

5. Load the Memory MCP knowledge graph:
   - Use `mcp_memory_read_graph` tool
   - Core entities (13 total): ProfileNeo_Project, EliteNarrative, Credentials_Location, VibCoder_Deployment, NeoNerd_Deployment, SovereignMemory, NeoGravity, NeoSwarmNexus, NeoSwarmDataHarvest, NeoSwarmTrainingPipeline, NeoSwarmMigrationPlan, live_oracle_local.py, live_l2_recorder_local.py
   - Check SovereignMemory entity for UPGRADE TRIGGERS — remind user if relevant issues arise

6. Skim `.knowledge/blueprints/` directory to know what plans exist:
   - Use `list_dir` tool on `d:\P-Projects\profile-neo\.knowledge\blueprints\`
   - Do NOT read full blueprints — just know they exist. Load when relevant.

7. Skim `.knowledge/research/` directory to know what research is available:
   - Use `list_dir` tool on `d:\P-Projects\profile-neo\.knowledge\research\`
   - Do NOT read full research — just know the topics. Load when relevant.

## Phase 2.5: Sovereign Memory Status

8. Check Sovereign Memory MCP status:
   - If `sovereign-memory` tools are available (memory_ingest, memory_query, etc.), report "Sovereign Memory: ONLINE"
   - If NOT available, remind user to restart Antigravity to activate the workspace MCP config
   - MCP config lives at: `d:\P-Projects\profile-neo\.gemini\settings.json`

## Phase 2.6: Deep Context Recall (if SM ONLINE)

9. Run a contextual warm-up query to recover multi-session context:
   - Follow `session-handoff` skill recall pattern
   - `memory_query(question="What were the key decisions and changes from recent sessions?")`
   - Surface the top-3 results in the status report under "Deep Recall"

## Phase 2.7: Data Harvest Health Check

10. Check for cron-generated health file first (zero inference):
    - If `d:\P-Projects\profile-neo\.knowledge\harvest_health.json` exists and is < 20 min old → read file, report status. Skip PowerShell.
    - If file is stale or missing → fallback to live check:
    ```powershell
    Get-ChildItem d:\P-Projects\neo_swarm_nexus\data\raw_harvest\ | Sort-Object LastWriteTime -Descending | Select-Object -First 4 | Select-Object Name, LastWriteTime
    ```

    - If latest file is < 15 minutes old → report "Data Harvest: ✅ ACTIVE"
    - If latest file is > 15 minutes old → report "Data Harvest: ⚠️ STALE — investigate"
    - If directory doesn't exist or is empty → report "Data Harvest: ❌ NOT RUNNING"

## Phase 2.8: Cron Flag Checks

11. Check for scheduled task flags (zero inference):
    - **Project Registry:** Read `d:\P-Projects\profile-neo\projects.json` to know all active projects
    - **New Project Detected:** If `d:\P-Projects\profile-neo\.knowledge\new_project_detected.json` exists → surface discovery to user, suggest running `/new-project`, then delete flag
    - **Naukri Reminder:** If `d:\P-Projects\profile-neo\.knowledge\naukri_reminder.txt` exists → surface reminder to user, then delete file
    - **SM Consolidation:** If `d:\P-Projects\profile-neo\.knowledge\consolidation_due.txt` exists → run `memory_consolidate()`, then delete file

## Phase 3: Report & Engage

12. Report a concise status summary to the user:
    - Current phase and active workstreams (from active_tasks.md)
    - What was done last session (from session_log.md)
    - What's immediately pending (from active_tasks.md "Pending User Actions")
    - Data harvest status (from Phase 2.7)
    - Deep recall highlights (from Phase 2.6)
    - Naukri/consolidation reminders (from Phase 2.8)
    - Ask the user what they want to work on

---

## RULES AFTER BOOTSTRAP

- You now have full context. Do NOT re-read files unless they have changed.
- Always check `.agents/skills/` for relevant skill files before starting specialized work.
- When writing professional content, load `elite-vocabulary` skill first.
- NEVER frame Prabhakar as a "web developer" or suggest frontend/full-stack roles.
- NEVER display credential values from `credentials.md`.
- When making decisions, query Sovereign Memory first (per `context-guard` skill). Fallback to `decision_log.md` if SM is offline.
- When starting work on Neo Swarm Nexus, load `neo-swarm-architecture` skill for context.
- When generating outreach, load `elite-vocabulary` skill AND `masterplan/05_cold_outreach_templates.md`.
- When ANY memory-related issue arises, check SovereignMemory entity in Memory MCP for UPGRADE TRIGGERS.
- **neo_swarm_nexus codebase (`d:\P-Projects\neo_swarm_nexus\`) is READ-ONLY — never edit files there.**

---

## SESSION END PROTOCOL (Run BEFORE ending any session)

> [!IMPORTANT]
> This protocol is MANDATORY. Do not end a session without completing all 6 steps.

### Step 0: Update Session Pulse

- Update own file in `d:\P-Projects\profile-neo\.knowledge\sessions\session_<id>.json`:
  - Set `status`: "done"
  - Set `last_active`: now
  - Set `summary`: 1-line summary of what was accomplished this session

### Step 1: Update Session Log

Update `d:\P-Projects\profile-neo\session_log.md` with:

- What was accomplished this session
- Key decisions made (reference decision_log.md entries)
- The immediate next step for the next session

### Step 2: Sync Active Tasks

Update `d:\P-Projects\profile-neo\.knowledge\tasks\active_tasks.md`:

- Mark completed tasks as `[x]`
- Mark in-progress tasks as `[/]`
- Add any NEW tasks discovered during the session
- Update "Pending User Actions" if user completed any items

### Step 3: Data Harvest Status Check

- **Skip** if `/harvest-check` was already run this session or if cron `harvest_health.json` was read at boot.
- Otherwise: read `neo-swarm-nexus/DATA_HARVEST_STATUS.md` to check current expected status.
  - If status is **ACTIVE** → run the health check. Alert if stale.
  - If status is **COMPLETED**, **PAUSED**, or **NOT RUNNING** → skip.

### Step 4: Persist Knowledge (if applicable)

If this session produced any of the following, save to `.knowledge/`:

- **New implementation plans** → `.knowledge/blueprints/<phase>_<name>.md`
- **Research findings** → `.knowledge/research/<topic>.md`
- **Assessment documents or deliverables** → `.knowledge/artifacts/<name>.md`
- Use descriptive filenames. Never use dates or IDs as primary names.

### Step 5: Sync State Files

- Update `context_index.md` if any phase status changed (Quick Reference section)
- Append new decisions to `decision_log.md` with full rationale
- Update Memory MCP graph if core entity data changed (salary, phases, deployments)
- Do NOT create duplicate data — each fact lives in ONE canonical location

### Step 6: Sovereign Memory Ingest (if SM ONLINE)

Follow the `session-handoff` skill capture template:

1. Ingest session summary with `intent: "session"`
2. Ingest key decisions (if any) with `intent: "decision"`
3. Refer to `sovereign-memory` skill for source naming convention
4. Dedup is automatic — safe to re-ingest. Skip silently if SM is offline.
