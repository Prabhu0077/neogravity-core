---
description: Audit both live webapps against the elite narrative vocabulary to ensure content alignment with the masterplan.
---

# Verify Narrative — Webapp Content Audit

This workflow checks that both deployed webapps reflect the elite AI Infrastructure narrative, not generic web-dev language.

## Required Skills
- Load `sovereign-memory` skill (for audit persistence)
- Load `context-guard` skill (for diff against prior audit)
- Load `elite-vocabulary` skill (for vocabulary reference)

## Required Vocabulary (Must Appear)
These terms MUST be present somewhere on each respective webapp:
- **VibCoder (vibcoder.vercel.app):** FlashIPC, SentryOS, SimuBook, zero-copy, shared memory, low-latency, POSIX, infrastructure
- **NeoNerd (neonerd.vercel.app):** AI Infrastructure, Research, Systems, Quantitative, Autonomous

## Forbidden Vocabulary (Must NOT Appear Prominently)
These terms should NOT be primary descriptors:
- "Web Developer", "Frontend Developer", "Full Stack Developer", "WordPress", "Shopify", "PHP", "jQuery"

## Execution Steps

0. **Pre-flight: Prior Audit Diff** (context-guard → Trend Analysis):
   - `memory_query("narrative audit results")`
   - If prior audit exists:
     - Extract list of violations (missing terms, forbidden terms found) from prior result text
     - After completing Steps 1-4 (current audit), compare:
       - Violations in **prior but NOT current** = 🔄 FIXED
       - Violations in **current but NOT prior** = 🆕 NEW
       - Violations in **both** = ⚠️ RECURRING
   - If no prior audit → skip diff, report current results only

1. Use the browser tool or `read_url_content` to scrape the visible text from `https://vibcoder.vercel.app`
2. Check for presence of Required Vocabulary and absence of Forbidden Vocabulary
3. Repeat for `https://neonerd.vercel.app`
4. Generate a compliance report:
   - ✅ Terms found
   - ❌ Terms missing
   - ⚠️ Forbidden terms detected
   - 🔄 FIXED since last audit (if prior audit exists)
5. If misalignment is found, propose specific code changes to fix the content
6. **Persist audit** (if SM ONLINE — per `sovereign-memory` skill):
   - Ingest compliance report with `intent: "research"` and `source: "narrative-audit-YYYY-MM-DD"`
7. Report findings to the user

## When To Run
- After ANY content change to either webapp
- After running `/deploy`
- Before sending any cold outreach emails (to ensure the links are clean)
