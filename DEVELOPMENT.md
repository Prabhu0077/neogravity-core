# Elite Development: NeoGravity Core

This repository utilizes a high-performance polyglot monorepo structure, combining **Turborepo** and **PNPM** for the Node.js ecosystem (the CLI) paired with explicit **Python Virtual Environments** for the backend memory servers.

## Quick Start (The POSIX Way)

Do not run `npm install` or `pip install` manually deep inside subfolders. Instead, use the root Makefile to bootstrap the entire infrastructure automatically.

```bash
# 1. Install all dependencies (PNPM Workspace + Python .venv)
make install

# 2. Format code, check syntax, and run linters
make lint

# 3. Build all modules using Turborepo local caching
make build
```

## Repository Boundaries

- `packages/neogravity-cli`: The Node.js entry point representing `@vibcoder/neogravity` on NPM.
- `packages/sovereign-memory`: The Python backend representing the local MoE MCP server.
- `packages/sentinel-suite`: Premium documentation and integration orchestration.

## Syncing Upstream Workflows (Internal Use Only)

If you are Prabhakar, **do NOT** manually edit `.agents/` or `scripts/` inside the CLI template directory. This violates the Single Source of Truth rule.

Instead:

1. Author workflows and skills in the active `profile-neo` workspace.
2. Verify they operate flawlessly.
3. Run `.\scripts\sync-to-core.ps1` in the `profile-neo` workspace.
   _This script safely redacts personal parameters and injects the sanitized templates into `neogravity-core`, ready for NPM publishing._
