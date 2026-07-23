---
name: Rep signup momentum scoreboard
description: Track rep/enrollment signup momentum by week and market, and surface the newest reps already active enough to be worth a personal spotlight.
icon: users
---

# Goal

Read enrollment and recruiting momentum for {{company.name}} — who's driving growth, which markets are heating up, and which brand-new reps deserve a field spotlight before the numbers make it obvious.

# Steps

1. Paginate `fluid_api("/api/v2025-06/reps?sort=-created_at&limit=100", "GET")` fully, following `meta.pagination.next_cursor` (or `current_page`/`total_pages` if cursor fields are null) until exhausted. Capture `id`, `full_name`, `country_code`, `created_at`, `updated_at`, `active`, `rank`.
2. Bucket every rep by `created_at` into **this week**, **this month** (excluding this week), and **prior month**, relative to {{today}}. Compute week-over-week and month-over-month signup counts and % change.
3. Bucket the same full set by `country_code` and rank the top 3 by new-rep count **this month** — the markets heating up right now.
4. For the 10 most recently created reps (from step 1's sort), call `fluid_api("/api/v2025-06/reps/<id>/most_shared?limit=5", "GET")` and `fluid_api("/api/v2025-06/reps/<id>/most_viewed?limit=5", "GET")` for each. A brand-new rep who's already sharing or getting views in their first days is the strongest predictor of a rep who sticks — flag any with non-empty `resources`.
5. Render: a momentum headline (WoW % and MoM % change in new-rep count), the top-3-markets table, and an "early movers" table (the new reps from step 4 who already show content activity, worth a personal welcome call this week).
6. Close with ONE recommendation: which market to double down recruiting efforts in, and which 2-3 early movers to personally reach out to.

If `most_shared`/`most_viewed` return empty `resources` for every recent rep, say so plainly — that's a real signal (new reps aren't being onboarded into sharing content yet), not a tool failure.
