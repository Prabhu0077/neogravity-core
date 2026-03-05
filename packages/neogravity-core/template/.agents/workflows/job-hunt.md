---
description: The daily operating procedure for executing the elite job hunt, targeting Principal Architect and Quant roles without using bulk-apply automation.
---

# 🎯 The Antigravity Job Hunt Protocol

*This workflow dictates how we approach the market. We do not use automation tools (Loopcv, etc.) to spam fast-apply buttons. We use surgical, high-signal strikes targeted at engineering leadership.*

## Required Skills
- Load `sovereign-memory` skill (for context recall)
- Load `context-guard` skill (for duplicate/staleness detection)
- Load `elite-vocabulary` skill (for payload generation)

## Prerequisites
1. Ensure the user's LinkedIn and Naukri profiles are fully updated using the assets in `d:\P-Projects\profile-neo\job-hunt\`.
2. Review `d:\P-Projects\profile-neo\job-hunt\salary_benchmarks.md` to ensure the target company fits our compensation tier.
3. Review `d:\P-Projects\profile-neo\job-hunt\outreach_targets.md` for the active hit-list.
4. **Pre-flight:** Query SM for prior outreach and decisions (replaces manual decision_log.md read):
   - `memory_query("outreach history and job hunt decisions")`
   - Surface prior contacts, responses, and open decisions
5. Check `.knowledge/tasks/active_tasks.md` Phase 6 section for pending user actions.

---

## 📅 Daily Execution Steps

### 1. Target Selection (AI Action)
- Select 1-2 companies from the `outreach_targets.md` list.
- Prioritize "Warm-Up" targets (Delhi NCR, Series A Remote) before attacking Tier-1 HFTs.

### 2. Reconnaissance (AI Action)
- Use `search_web` to find the target company's current **VP of Engineering, CTO, or Head of Quantitative Research**.
- Find one recent technical challenge, funding round, or blog post from the company.

### 3. Payload Generation (AI Action)
- Generate a highly customized 300-character LinkedIn connection note.
- Generate the full Email/InMail payload using the templates from `05_cold_outreach_templates.md`.
- Ensure the framing is strictly **"Principal Architect / Infrastructure Researcher"** (problem-solving, latency, autonomous swarms) and NOT "Senior Software Engineer" (ticket-closing).

### 4. Human-in-the-Loop Execution (User Action)
- Present the generated payload to the user in a `notify_user` block.
- The user manually locates the target on LinkedIn/Email, pastes the payload, and sends it.
- **Why Manual?** Bypasses automated bot detection, ensures high-signal delivery, and protects the elite narrative.

### 5. Naukri / Inbound Maintenance (User Action)
- The user must manually log into Naukri.com every 2-3 days.
- **Action:** Delete one line from the resume summary and re-type it, then hit "Save". This triggers Naukri's algorithm to mark the profile as "Active Today," bumping it to the top of recruiter searches.

### 6. Negotiation Tracking (AI + User)
- When responses arrive, use the `salary_benchmarks.md` "Never Blink" script. 
- AI acts as the advisor; User executes the negotiation.

### 7. Outcome Tracking (if SM ONLINE — per `sovereign-memory` skill)
After each outreach cycle, ingest outcome with `intent: "outreach"` and `source: "job-hunt-YYYY-MM-DD"`.

