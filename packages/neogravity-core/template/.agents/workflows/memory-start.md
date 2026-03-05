---
description: Start the Sovereign Memory engine — Neo4j, MCP models, health verification
---

# /memory-start — Start the Sovereign Memory Engine

// turbo-all

## Steps

1. Run the orchestrator script to start Neo4j and verify health:
```powershell
& "d:\P-Projects\profile-neo\scripts\memory_engine.ps1" -Action start
```

2. Parse the JSON output. If `"success": true`, proceed. If `"success": false`, report the failed phase to the user and STOP.

3. Warm up the MCP models by calling `memory_recent(n=1)`. This triggers lazy loading of the embedder (~90MB) and GLiNER (~200MB) models. Expected cold start: ~8 seconds. If this fails, report the error.

4. Report final status to the user:
   - Neo4j: healthy / failed
   - Ollama: running / offline (non-blocking for queries)
   - MCP: connected / failed
   - Tier stats: HOT/WARM/COLD chunk counts
   - Note: First query after cold start takes ~8s, subsequent queries <1s
