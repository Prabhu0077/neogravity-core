---
name: GitHub Operations
description: Instructions for interacting with Prabhu0077's GitHub repositories — push, pull, README management.
---

# GitHub Operations Skill

## Credential Location
GitHub PAT is stored in `d:\P-Projects\profile-neo\credentials.md`. NEVER log or display the token.

## Repository Map
Read `d:\P-Projects\profile-neo\projects.json` to get the project's GitHub repo, owner, and remote name.
- Filter to projects with `github_repo` not null
- If the requested project is NOT in the registry, tell the user to run `/new-project` first
- Profile README repo (`Prabhu0077/Prabhu0077`) is a special case — content at `d:\P-Projects\profile-neo\Prabhu0077_README.md`

## GitHub Username
`Prabhu0077`

## Setting Up Remote (if missing)
```
git remote add github https://<PAT>@github.com/Prabhu0077/<repo-name>.git
```

## Standard Push Workflow
```
git add -A
git commit -m "<conventional commit message>"
git push github master
```

## Creating the Profile README
The Profile README content is stored at `d:\P-Projects\profile-neo\Prabhu0077_README.md`.
To create/update it:
1. Use the GitHub MCP tool `mcp_github-mcp-server_create_or_update_file` 
2. Owner: `Prabhu0077`, Repo: `Prabhu0077`, Path: `README.md`
3. Content: read from `Prabhu0077_README.md`

## Commit Message Convention
Use conventional commits: `feat:`, `fix:`, `docs:`, `style:`, `refactor:`, `perf:`, `chore:`
