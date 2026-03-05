---
description: Stop the Sovereign Memory engine — Neo4j container, report RAM freed
---

# /memory-stop — Stop the Sovereign Memory Engine

// turbo-all

## Steps

1. Run the orchestrator script to stop Neo4j:
```powershell
& "d:\P-Projects\profile-neo\scripts\memory_engine.ps1" -Action stop
```

2. Parse the JSON output. Report to the user:
   - Neo4j: stopped
   - RAM freed: from JSON `total_freed_mb` field
   - Note: MCP server process stops automatically when the Antigravity session ends

3. Do NOT kill any Python processes — data collection scripts (live_oracle_local.py, live_l2_recorder_local.py) must remain untouched.
