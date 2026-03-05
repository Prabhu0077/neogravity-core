---
description: Full CI/CD pipeline — commit changes, push to GitHub, and trigger Vercel deployment for NeoNerd and/or VibCoder.
---
// turbo-all

# Deploy — CI/CD Pipeline

This workflow handles the full deployment cycle for both webapps.

## Required Skills
- Load `sovereign-memory` skill (for deploy audit trail)
- Load `context-guard` skill (for double-deploy guard)

## Pre-Deploy Checks
0. **Pre-flight: Double-Deploy Guard** (context-guard → Duplicate Detection):
   - `memory_query("deploy [app] today")`
   - If match found with today's date → warn: "[app] was already deployed today. Proceed?"
1. Read credentials from `d:\P-Projects\profile-neo\credentials.md` to get the GitHub PAT and Vercel Token.
2. Check which app(s) have uncommitted changes:
// turbo
```
cd d:\P-Projects\profile-neo\neonerd; git status
```
// turbo
```
cd d:\P-Projects\profile-neo\vibcoder; git status
```

## Deploy NeoNerd (if changes detected)
3. Stage, commit, and push NeoNerd:
```
cd d:\P-Projects\profile-neo\neonerd; git add -A; git commit -m "update: <describe changes>"; git push github master
```

## Deploy VibCoder (if changes detected)
4. Stage, commit, and push VibCoder:
```
cd d:\P-Projects\profile-neo\vibcoder; git add -A; git commit -m "update: <describe changes>"; git push github master
```

## Post-Deploy Verification
5. Wait 60 seconds for Vercel to rebuild via GitHub integration.
6. Verify deployments are live:
   - Use `read_url_content` to fetch `https://neonerd.vercel.app` and confirm it loads the new changes.
   - Use `read_url_content` to fetch `https://vibcoder.vercel.app` and confirm it loads the new changes.

## Fallback: Manual Vercel Deploy (If GitHub Integration Fails)
If Vercel does not auto-build from the GitHub push, or serves a stale cache:
1. Clear the local build cache and force deploy for NeoNerd:
```
cd d:\P-Projects\profile-neo\neonerd; Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue; npx -y vercel --prod --yes
```
2. Clear the local build cache and force deploy for VibCoder:
```
cd d:\P-Projects\profile-neo\vibcoder; Remove-Item -Recurse -Force .next -ErrorAction SilentlyContinue; npx -y vercel --prod --yes
```
3. Report deployment status to the user.

## Step 7: Deploy Audit Trail (if SM ONLINE — per `sovereign-memory` skill)
After successful verification, ingest deploy event with `intent: "deploy"` and `source: "deploy-[app]-YYYY-MM-DD"`.

## If Git Remote Is Not Set
If `git push github master` fails with "does not appear to be a git repository":
- Read the PAT from `credentials.md`
- Run: `git remote add github https://<PAT>@github.com/Prabhu0077/<repo-name>.git`
- The remote name MUST be `github`, not `origin`
