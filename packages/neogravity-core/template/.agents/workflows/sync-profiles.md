---
description: Provide the latest copy-paste content for updating LinkedIn and Naukri profiles, ensuring it matches current product descriptions.
---

# Sync Profiles — LinkedIn & Naukri Content Provider

## Required Skills
- Load `sovereign-memory` skill (for content persistence)
- Load `elite-vocabulary` skill (for vocabulary enforcement)

## Steps

1. Read the latest versions of:
   - `d:\P-Projects\profile-neo\job-hunt\linkedin_update.md`
   - `d:\P-Projects\profile-neo\job-hunt\naukri_update.md`
   - `d:\P-Projects\profile-neo\cv_optimized.md`

2. Check if the product descriptions in these files match the current state of:
   - `d:\P-Projects\profile-neo\masterplan\01_nexus_product_suite.md`
   - The live webapps (run `/verify-narrative` if unsure)

3. If any content is outdated, regenerate the affected sections

4. Present the final copy to the user in clearly labeled sections:
   - **LinkedIn Headline** (copy-paste ready)
   - **LinkedIn About** (copy-paste ready)
   - **LinkedIn Experience entries** (copy-paste ready)
   - **Naukri Resume Headline** (copy-paste ready)
   - **Naukri Profile Summary** (copy-paste ready)
   - **Naukri Work Experience** (copy-paste ready)

5. Remind the user to upload `cv_optimized.md` as a PDF to Naukri's "Attached Resume" section

6. **Persist generated content** (if SM ONLINE — per `sovereign-memory` skill):
   - Ingest content summary with `intent: "outreach"` and `source: "profile-sync-YYYY-MM-DD"`
