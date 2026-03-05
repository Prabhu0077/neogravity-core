---
description: Generate personalized cold outreach emails from the masterplan templates for a specific target company or person.
---

# Outreach — Personalized Cold Email Generator

> **Relationship to `/job-hunt`:** This workflow generates a SINGLE outreach payload for ONE target. The `/job-hunt` workflow is the daily master protocol that calls this workflow as its Step 3 (Payload Generation). Use `/outreach` directly when the user names a specific company. Use `/job-hunt` for the full daily cycle.

## Required Skills
- Load `sovereign-memory` skill (for ingest patterns)
- Load `context-guard` skill (for duplicate detection)
- Load `elite-vocabulary` skill (for content generation)

## Prerequisites
- Read `d:\P-Projects\profile-neo\masterplan\05_cold_outreach_templates.md` for the base templates
- Read `d:\P-Projects\profile-neo\masterplan\02_job_strategy_and_vocabulary.md` for vocabulary enforcement

## Steps

0. **Pre-flight: Duplicate Guard** (context-guard → Duplicate Detection):
   - `memory_query("outreach to [Company]")`
   - If match found → warn user with date and summary of prior contact
   - If no match → proceed silently

1. Ask the user for the target:
   - Company name
   - Person's name and title (if known)
   - Whether the target is (A) HFT/Quant Firm or (B) AI Infrastructure Startup

2. Research the target company briefly using `firecrawl_search` or `search_web` to find:
   - Their engineering blog or tech stack
   - Recent funding rounds or news
   - Specific technical challenges they face

3. Generate a personalized version of the appropriate template (Vector A or B):
   - Replace `[Company Name]` and `[First Name]`
   - Add a specific reference to their engineering blog/tech stack
   - Keep the core technical pitch (FlashIPC / SentryOS) intact

4. Present the email to the user for approval before sending
5. Optionally generate a LinkedIn connection request message (shorter, 300 chars max)
6. **Sovereign Memory Ingest** (if SM ONLINE — per `sovereign-memory` skill):
   - Ingest outreach summary with `intent: "outreach"` and `source: "outreach-[company]-YYYY-MM-DD"`
   - Dedup is automatic — re-generating for the same company won't create duplicates
   - Query later with: `memory_query("have we contacted [Company]?")`
