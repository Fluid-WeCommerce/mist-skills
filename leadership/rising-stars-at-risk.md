---
name: Rising stars & at-risk leaders
description: Find brand-new reps already showing content-activity momentum worth a shout-out, and long-tenured reps who've gone quiet before it shows up in the numbers.
icon: trending-up
---

# Goal

Find {{company.name}}'s rising-star reps worth a personal shout-out, and the at-risk ones who've gone quiet, before either becomes obvious.

# Steps

1. Paginate `fluid_api("/api/v2025-06/reps?sort=-created_at&limit=100", "GET")` fully.
2. **Rising-star candidates**: reps created within the last 60 days. For each, call `fluid_api("/api/v2025-06/reps/<id>/most_shared?limit=5", "GET")` and `.../most_viewed?limit=5`. A brand-new rep already generating shares/views in their first weeks is the strongest available "this one's going to stick" signal — flag any with non-empty `resources`.
3. **At-risk candidates**: reps created 6+ months ago whose `updated_at` is 45+ days stale. Run the same `most_shared`/`most_viewed` check — zero recent content activity plus a stale `updated_at` together are the at-risk signal (either alone is weaker).
4. Rank rising stars by (most recent join first) × (content activity present). Rank at-risk by staleness (days since `updated_at`, descending).
5. Render two tables:
   - **Rising Stars** — name, joined date, country, content-activity signal, suggested outreach ("personal welcome message + invite to the next training").
   - **At-Risk** — name, tenure, days stale, suggested outreach ("check-in call — what changed?").
6. Close with a one-line count per list and the single most time-sensitive name in each (the newest rising star, the longest-stale at-risk rep).

If `most_shared`/`most_viewed` come back empty for every candidate in either list, say so — that's real signal (new reps aren't being onboarded into content-sharing yet), not a tool failure.
