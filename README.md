# 🪐 NeoGravity Core

<div align="center">
  <h3>The Autonomous Agentic Operating System</h3>
  <i>Turn your AI IDE (Antigravity, Cursor, Windsurf) into a self-healing, decision-aware engineering lab.</i>
</div>

NeoGravity is a **local-first Agentic Operating System** that lives inside your workspace. It doesn't write code for you — it manages the _infrastructure around your AI assistant_: context persistence, architectural enforcement, multi-session memory, and workflow orchestration.

## Why NeoGravity?

Development teams lose **30-40% of their time** to context switching, environment setup, chasing deployment bugs, and re-litigating old decisions. NeoGravity eliminates that overhead by acting as a sovereign OS layer that:

- **Remembers everything** — Decisions, architecture rationale, and project state persist across sessions via the `.knowledge/` state machine.
- **Enforces consistency** — Skills like `context-guard` and `elite-vocabulary` prevent drift in terminology and architecture.
- **Automates DevOps** — Cron watchdogs monitor data pipelines, trigger deployments, and self-heal broken environments.
- **Orchestrates workflows** — Pre-built protocols for deployment, outreach, bootstrapping, and project registration.

## 🚀 Quick Start & Installation

NeoGravity Core scaffolds directly into your existing workspace. It is designed to run natively on Windows/Linux/macOS alongside your preferred AI IDE.

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

````

---

## 🤖 Using NeoGravity with Antigravity (or Cursor/Windsurf)

AI coding assistants are brilliant at writing code, but they suffer from **context amnesia**. They forget architectural decisions, they hallucinate old API routes, and they break existing workflows because they can't remember what they did yesterday.

**NeoGravity mitigates this entirely.**

By installing NeoGravity Core, you provide your AI with a persistent "exocortex."

### How to use it:

1. **The Context Anchor:** At the start of every chat session with your AI, simply type:
   > *“Read my `projects.json` and `.knowledge/tasks/active_tasks.md` before doing anything.”*
2. **Workflow Triggers:** Instead of asking the AI to "deploy my app" and watching it stumble, type:
   > *“Run the `/deploy` workflow found in `.agents/workflows/deploy.md`.”*
3. **Skill Enforcement:** Need the AI to write a specific way? Tell it:
   > *“Load the `elite-vocabulary` skill from `.agents/skills/` before drafting this email.”*

---

## 🧠 How It Works (Visual Architecture)

```mermaid
graph TD
    UI[AI IDE - Antigravity/Cursor] -->|Reads| KG[.knowledge/ <br>Persistent State]
    UI -->|Executes| WF[.agents/workflows/ <br>Runbooks]
    UI -->|Enforces| SK[.agents/skills/ <br>Pre-flight Rules]

    subwatch[Background Processes]
    CRON[PowerShell Watchdogs] -->|Monitors Health| UI
    CRON -->|Consolidates| KG

    style UI fill:#2d3436,stroke:#00b894,stroke-width:2px,color:#fff
    style KG fill:#0984e3,stroke:#74b9ff,stroke-width:2px,color:#fff
    style WF fill:#6c5ce7,stroke:#a29bfe,stroke-width:2px,color:#fff
    style SK fill:#e84393,stroke:#fd79a8,stroke-width:2px,color:#fff
    style CRON fill:#d63031,stroke:#ff7675,stroke-width:2px,color:#fff
````

---

## 💎 Product Tiers

| Tier                 | What You Get                                          | Price          |
| -------------------- | ----------------------------------------------------- | -------------- |
| **NeoGravity Core**  | Workflows, skills, crons, `.knowledge/` state machine | **Free** (MIT) |
| **Sovereign Memory** | Neo4j + MoE routing + ChromaDB + local LLM memory     | Coming Soon    |
| **Sentinel Suite**   | Full OS + Sovereign Memory — total autonomy           | Coming Soon    |

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

---

<details>
<summary><b>🔍 Search & Discovery Tags (for humans and LLMs)</b></summary>
<i>
ai, agentic os, antigravity ide, cursor ide, windsurf ide, llm memory, chatgpt coding, copilot, developer tools, workflow automation, devops, rag, generative ai infrastructure, multi-session agent, context management, prompt engineering, zero-copy, neo-swarm, vibcoder
</i>
</details>
