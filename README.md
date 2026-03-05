# NeoGravity — The Autonomous Agentic Operating System

> Turn your IDE into a self-healing, decision-aware engineering lab.

NeoGravity is a **local-first Agentic Operating System** that lives inside your workspace. It doesn't write code for you — it manages the *infrastructure around your code*: deployments, context persistence, architectural enforcement, and multi-session memory.

## Why NeoGravity?

Development teams lose **30-40% of their time** to context switching, environment setup, chasing deployment bugs, and re-litigating old decisions. NeoGravity eliminates that overhead by acting as a sovereign OS layer that:

- **Remembers everything** — Decisions, architecture rationale, and project state persist across sessions via the `.knowledge/` state machine.
- **Enforces consistency** — Skills like `context-guard` and `elite-vocabulary` prevent drift in terminology and architecture.
- **Automates DevOps** — Cron watchdogs monitor data pipelines, trigger deployments, and self-heal broken environments.
- **Orchestrates workflows** — Pre-built protocols for deployment, outreach, bootstrapping, and project registration.

## Quick Start

```bash
npx @vibcoder/neogravity init
```

This scaffolds the OS into your current workspace:

```
your-project/
├── .agents/
│   ├── workflows/    # deploy, bootstrap, verify, outreach
│   └── skills/       # context-guard, github-ops, elite-vocabulary
├── .knowledge/       # persistent brain (tasks, blueprints, research)
├── scripts/          # cron watchdogs and automation
└── projects.json     # multi-project registry
```

## Product Tiers

| Tier | What You Get | Price |
|---|---|---|
| **NeoGravity Core** | Workflows, skills, crons, `.knowledge/` state machine | **Free** (MIT) |
| **Sovereign Memory** | Neo4j + MoE routing + ChromaDB + local LLM memory | Coming Soon |
| **Sentinel Suite** | Full OS + Sovereign Memory — total autonomy | Coming Soon |

## Architecture

NeoGravity is not a plugin or extension. It is a **workspace-level operating system** composed of:

- **Workflows** — Step-by-step protocols (`.agents/workflows/`) triggered by slash commands.
- **Skills** — Domain-specific instruction sets (`.agents/skills/`) loaded on demand.
- **Persistent Brain** — A `.knowledge/` directory that survives across sessions, containing tasks, blueprints, and research artifacts.
- **Cron Watchdogs** — PowerShell scripts that run on schedule to monitor pipelines, consolidate memory, and enforce freshness.
- **Project Registry** — A `projects.json` file that tracks multiple projects, their deploy targets, and vocabulary profiles.

## Documentation

Full documentation available at [docs.vibcoder.com](https://docs.vibcoder.com)

## Built By

**[VibCoder](https://vibcoder.com)** — Founded by Prabhakar Chandra, Principal AI Infrastructure Researcher.

## License

MIT — See [LICENSE](./LICENSE) for details.
