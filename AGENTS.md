# AGENTS.md — read first

The brief every AI agent reads before working in this repo (Claude Code, Codex, Cursor, Antigravity or any other). `CLAUDE.md` points here.

## 1. What this is

**NeoGravity** by Bodham Labs (https://bodhamlabs.com/research/agent-context-tooling): tools that help AI coding assistants keep context between sessions. Public repo, MIT licence.

| Package | What | Version |
|---|---|---|
| `packages/neogravity-cli` | `@vibcoder/neogravity` on npm: scaffolds a task list, decision log, workflows and skills into any project | 4.1.0 (on GitHub; npm still shows 4.0.0 until the publish) |
| `packages/sovereign-memory` | Python MCP memory server (local) | 1.0.0 |
| `packages/sentinel-suite` | Documentation and integration helpers | 1.0.0 |

## 2. Run and check

```bash
make install     # pnpm workspace + Python .venv for sovereign-memory
make lint
make test        # the CLI has node --test tests; they must pass
make build
```

Before any publish, run `npm pack --dry-run` in `packages/neogravity-cli` and read the file list: only `index.js`, `template/`, `README.md`, `LICENSE`, `CHANGELOG.md` may ship.

## 3. Rules that must not break

1. **Nothing personal ships.** 4.0.0 shipped files that did not belong in a public package; that is why 4.1.0 exists. No real names of clients, no machine paths, no keys, no default passwords in templates.
2. **Templates are authored upstream.** Workflows and skills are written and tested in the founder's private workspace, then synced here by a script that removes personal values. Don't hand-edit the CLI's `template/` workflows; change them upstream (see `DEVELOPMENT.md`).
3. **No secrets in git.** Use `.env.example`. Scan with gitleaks (`--redact`) before every push. See `SECURITY.md`.
4. **Commit email** must be `189221026+Prabhu0077@users.noreply.github.com`.
5. **Honest claims only** in README and CHANGELOG: describe what the code does today; no speed or accuracy numbers without a result file.
6. **Publishing to npm needs the owner's 2FA code.** Agents prepare the release; the owner runs the publish.

## 4. Where things live

| Path | What |
|---|---|
| `packages/neogravity-cli/index.js`, `template/` | The CLI and what it scaffolds |
| `packages/neogravity-cli/CHANGELOG.md` | Release notes |
| `packages/sovereign-memory/` | Memory server (Python) |
| `docs/decisions.md` | Decisions with reasons |
| `DEVELOPMENT.md`, `SECURITY.md` | Developer setup; how to report a security issue |

## 5. Ending a phase

Commit with a clear message and add any decision to `docs/decisions.md` (newest on top). Company-level context for the owner lives outside this repo.
