---
trigger: always_on
---

## Boot Protocol
At the start of ANY session in this workspace, BEFORE doing any work:
1. Read [d:\P-Projects\profile-neo\context_index.md](cci:7://file:///d:/P-Projects/profile-neo/context_index.md:0:0-0:0) for project state.
2. Read [d:\P-Projects\profile-neo\session_log.md](cci:7://file:///d:/P-Projects/profile-neo/session_log.md:0:0-0:0) for what was done last session.
3. Load Memory MCP graph (`mcp_memory_read_graph`) for VibCoder, NeoNerd, and EliteNarrative facts.
4. Report status to the user before proceeding.

## Session End Protocol
Before ending ANY session or when the user says goodbye:
1. Update `d:\P-Projects\profile-neo\session_log.md` with what was accomplished and the immediate next step.
2. Update `d:\P-Projects\profile-neo\context_index.md` if any phase status changed.

## Identity & Narrative
- Prabhakar Chandra is positioned as: **Principal AI Infrastructure Researcher & Founder of VibCoder**.
- NEVER frame as "Web Developer", "Frontend Engineer", or "Full Stack Developer".
- Products: FlashIPC (zero-copy IPC), SentryOS (autonomous DevOps), SimuBook (latency-physics backtesting).
- The narrative arc: Web foundation → Payment latency bottleneck at Sago → C++ POSIX IPC research → Neo Swarm Nexus → VibCoder commercialization.

## Anti-Hallucination
- NEVER invent file paths, URLs, credentials, or API keys.
- NEVER suggest web-dev vocabulary as primary descriptors. Use: FlashIPC, SentryOS, SimuBook, POSIX mmap, zero-copy, seqlock.
- When writing professional content, load the `elite-vocabulary` skill from `.agents/skills/`.
- At the start of any session, load Memory MCP graph (`mcp_memory_read_graph`) for persistent facts.

## Project Layout
- Profile-Neo root: `d:\P-Projects\profile-neo\`
- Masterplan: `d:\P-Projects\profile-neo\masterplan\`
- NeoNerd app: `d:\P-Projects\profile-neo\neonerd\`
- VibCoder app: `d:\P-Projects\profile-neo\vibcoder\`
- Credentials: [d:\P-Projects\profile-neo\credentials.md](cci:7://file:///d:/P-Projects/profile-neo/credentials.md:0:0-0:0) (NEVER display values)
- Job Hunt: `d:\P-Projects\profile-neo\job-hunt\` (outreach targets, salary benchmarks, profile update content)
- Workflows: `.agents\workflows\` (bootstrap, deploy, verify-narrative, outreach, sync-profiles, job-hunt)
- Skills: `.agents\skills\` (elite-vocabulary, neo-swarm-architecture, vercel-deploy, github-ops)
