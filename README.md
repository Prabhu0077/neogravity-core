# NeoGravity Core

Small tools that help AI coding assistants keep context between sessions.

This repository is a monorepo by [Bodham Labs](https://bodhamlabs.com). It holds two things at different stages of maturity:

| Package | What it is | Status |
| --- | --- | --- |
| [`packages/neogravity-cli`](./packages/neogravity-cli) | `npx @vibcoder/neogravity init` creates a task list, a decision log and short assistant instructions as plain Markdown files | Published on npm. Small and tested. |
| [`packages/sovereign-memory`](./packages/sovereign-memory) | A local MCP server that gives an agent long-term memory (ChromaDB vectors, Neo4j entity graph, tiered storage) | Experimental. Used internally Mar to May 2026. Latency numbers are pending a proper re-run, so none are claimed here. |
| [`packages/sentinel-suite`](./packages/sentinel-suite) | Placeholder | Not started. |

## Quick start (the CLI)

```bash
npx @vibcoder/neogravity init
```

See the [CLI README](./packages/neogravity-cli/README.md) for what it creates and how to use it.

## Why this exists

AI assistants forget everything when a chat ends. Files do not. The simplest fix we found is to keep the state the assistant needs (what is in progress, what was decided and why) in files it reads at the start of a session and updates at the end. We wrote down what worked and what did not in [Agent context tooling](https://bodhamlabs.com/research/agent-context-tooling).

## Develop

Requires Node 18+ and pnpm.

```bash
pnpm install
pnpm test      # runs the CLI tests (node:test)
```

The Python package has its own instructions in [`packages/sovereign-memory`](./packages/sovereign-memory). Secrets (for example `NEO4J_PASSWORD`) come from your environment; none are stored in this repository. See [SECURITY.md](./SECURITY.md) to report a problem.

## Licence

MIT. See [LICENSE](./LICENSE).

Built by [Prabhakar Chandra](https://bodhamlabs.com/about) at [Bodham Labs](https://bodhamlabs.com), Delhi, India.
