---
description: Quick check on Neo Swarm Nexus local data harvest health — verifies Parquet files are being written and scripts are alive.
---
// turbo-all

# Data Harvest Health Check

Run this to verify the local data collection pipeline is alive.

## Required Skills
- Load `sovereign-memory` skill (for health persistence)
- Load `context-guard` skill (for trend detection)

## Step 0: Pre-flight Trend Check (context-guard → Trend Analysis)
- `memory_query("harvest health check")`
- If last 3 results all show STALE → escalate: "⚠️ HARVEST STALE FOR 3+ CHECKS — likely script crash, not transient WS disconnect"

## Step 1: Check Latest Parquet Files

// turbo
```powershell
Get-ChildItem d:\P-Projects\neo_swarm_nexus\data\raw_harvest\ | Sort-Object LastWriteTime -Descending | Select-Object -First 6 | Select-Object Name, LastWriteTime
```

**Interpret results:**
- Latest file < 10 minutes old → ✅ ACTIVE — data is flowing
- Latest file 10-30 minutes old → ⚠️ SLOW — possible WS disconnect, may self-recover
- Latest file > 30 minutes old → ❌ STALE — scripts likely crashed, investigate
- Directory empty or missing → ❌ NOT RUNNING — scripts never started

## Step 2: Check Running Processes

// turbo
```powershell
Get-WmiObject Win32_Process -Filter "name = 'python.exe'" | Where-Object { $_.CommandLine -like "*local*" } | Select-Object ProcessId, @{N='Script';E={($_.CommandLine -split '\\')[-1]}}
```

**Expected output:** Two python.exe processes:
- `live_oracle_local.py`
- `live_l2_recorder_local.py`

## Step 3: Report

Report a one-line summary:
- "Data Harvest: ✅ ACTIVE (latest: HH:MM, 2 scripts running)"
- "Data Harvest: ⚠️ STALE (latest: HH:MM, X scripts running) — investigate"
- "Data Harvest: ❌ DEAD — scripts not found"

If STALE or DEAD, remind user:
> To restart: `cd d:\P-Projects\neo_swarm_nexus && start_local_harvest.bat`

## Step 4: Update Status Doc (optional)

If the check reveals a change in status, update:
`d:\P-Projects\profile-neo\neo-swarm-nexus\DATA_HARVEST_STATUS.md`

## Step 5: Persist to Sovereign Memory (if SM ONLINE — per `sovereign-memory` skill)
Ingest harvest health snapshot with `intent: "harvest"` and `source: "harvest-health-YYYY-MM-DD"`.
