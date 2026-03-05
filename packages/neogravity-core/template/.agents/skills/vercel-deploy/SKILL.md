---
name: Vercel Deploy
description: Step-by-step instructions for deploying NeoNerd and VibCoder to Vercel using CLI or Git integration.
---

# Vercel Deployment Skill

## Credential Location
All tokens are stored in `d:\P-Projects\profile-neo\credentials.md`. NEVER hardcode tokens in commands visible to the user.

## Project Mapping
Read `d:\P-Projects\profile-neo\projects.json` to get the project's local path, GitHub repo, and Vercel URL.
- Filter to projects with `deploy_target: "vercel"` and `active: true`
- If the requested project is NOT in the registry, tell the user to run `/new-project` first

## Deployment Method: Git Push (Preferred)
If Vercel Git Integration is connected, simply push to GitHub and Vercel auto-deploys:
```
cd <app-directory>
git add -A
git commit -m "<message>"
git push github master
```

## Deployment Method: Vercel CLI (Fallback)
If Git integration is not connected:
```
cd <app-directory>
npx vercel --prod --token <VERCEL_TOKEN> --yes
```

## Common Issues
- **"origin" not a git repository:** The remote is named `github`, not `origin`. Use `git push github master`.
- **Build fails on Vercel:** Check `next.config.ts` for `eslint.ignoreDuringBuilds: true` and `typescript.ignoreBuildErrors: true`.
- **Token expired:** Generate a new Vercel token at https://vercel.com/account/tokens and update `credentials.md`.
