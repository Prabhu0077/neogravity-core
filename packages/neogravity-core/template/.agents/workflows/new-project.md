---
description: Register a new project into NeoGravity — updates registry, creates Memory MCP entity, and ingests into Sovereign Memory.
---

# /new-project — Register a New Project

Use this when a new project is detected (via scanner flag) or when the user explicitly wants to add one.

## Required Skills
- Load `sovereign-memory` skill (for ingest)

## Steps

1. **Gather project info** (ask user or read from scanner flag):
   - Project name (slug: lowercase, hyphens)
   - Path on disk
   - Type: `webapp`, `system`, `library`, `script`
   - GitHub repo name (if any)
   - Deploy target: `vercel`, `bare-metal`, `local`, `none`
   - Deploy URL (if any)
   - Vocabulary profile: `infra`, `saas`, `default`

2. **Read scanner flag** (if triggered automatically):
   - Read `d:\P-Projects\profile-neo\.knowledge\new_project_detected.json`
   - Pre-fill known fields (name, path, marker type)
   - Ask user to confirm and fill remaining fields
   - Delete the flag file after processing

3. **Update `projects.json`:**
   - Read `d:\P-Projects\profile-neo\projects.json`
   - Add new project block under `projects` key
   - Write back the updated JSON

4. **Create Memory MCP entity:**
   ```
   mcp_memory_create_entities([{
     name: "<ProjectName>_Project",
     entityType: "project",
     observations: ["Path: <path>", "Type: <type>", "Status: active", "Registered: YYYY-MM-DD"]
   }])
   ```

5. **Ingest into Sovereign Memory** (if SM ONLINE — per `sovereign-memory` skill):
   - Ingest project registration with `intent: "architecture"` and `source: "project-<name>-registered"`

6. **Update `context_index.md`:**
   - Add project to the Quick Reference section

7. **Report to user:** Confirm registration, show what was added.
