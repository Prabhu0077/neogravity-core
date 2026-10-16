# Decisions (NeoGravity)

Newest on top. Status: **Active / Changed / Revisit / Open**. Decided by: **Founder** or **MD** (delegated to Claude, reversible).

| ID | Date | Decision | Why | By | Status |
|---|---|---|---|---|---|
| NG-007 | 2026-10-15 | Repo carries the module kit: `AGENTS.md`, `CLAUDE.md`, this log | Any agent or session can pick up the work without old chats | MD | Active |
| NG-006 | 2026-10-13 | npm two-factor stays on; the owner types each publish code (script prompts for it) | Agents never handle login codes | Founder | Active |
| NG-005 | 2026-10-12 | Deprecate 4.0.0 on npm right after 4.1.0 is published | 4.0.0 contained files that did not belong in a public package | MD | Done 2026-10-16 (4.1.0 published as latest; 4.0.0 deprecated) |
| NG-004 | 2026-10-12 | 4.1.0: generic template, zero runtime dependencies, tests, no default secrets, Neo4j ports bound to localhost, `SECURITY.md`, `.env.example` | Make the package safe and reusable by anyone | MD | Active |
| NG-003 | 2026-10-12 | bodhamlabs.com links to GitHub, not npm, until 4.1.0 is on npm | npm still serves 4.0.0 | MD | Changed 2026-10-16: the site links to npm |
| NG-002 | 2026-03-06 | Polyglot monorepo: Turborepo + pnpm for Node, a Python venv for the memory server, one root Makefile | One way to install and test everything | Founder | Active |
| NG-001 | 2026-03-05 | Templates are written in the owner's private workspace and synced here with personal values removed | One source of truth; nothing personal leaks | Founder | Active |
