---
name: Shareable content leaderboard
description: Rank media and enrollment-pack shareables by shares, unique sharers, and visits-per-share to find what's actually converting, not just getting shared.
icon: share-2
---

# Goal

Find which shareable content — media assets and enrollment packs — is actually converting at {{company.name}}, so the CMO can double down on what's already proven instead of guessing at the next creative brief.

# Steps

1. Call `fluid_api("/api/users/v2025-06/media?limit=100", "GET")`, paginating fully. Filter to `active: true`. Capture `id`, `kind` (video/pdf/image), `title` (the display name — `label` is always `null` in practice, don't rely on it), `leads`, `attached_shareables`, `created_at`.
2. Pick the top 20 candidates: if any assets have non-zero `leads`, rank by that first; otherwise fall back to the 20 most recently published (`created_at` descending).
3. For each candidate, call `fluid_api("/api/v2025-06/media/<id>/share_stats", "GET")` for `total_shares`, `shares_last_30_days`, `unique_sharers`, `total_visits`, `percent_change`.
4. Compute a visits-per-share ratio (`total_visits / total_shares`, guard against divide-by-zero) as a proxy "quality" score — high ratio means the content converts once shared; low ratio means it's getting shared but not landing.
5. Also call `fluid_api("/api/enrollment_packs?limit=20", "GET")` (unversioned endpoint — the identifying field on each record is `enrollment_pack_id`, there's no plain `id`) and `fluid_api("/api/v2025-06/enrollment_packs/<enrollment_pack_id>/share_stats", "GET")` per pack — some direct-selling companies drive most of their sharing through enrollment packs rather than media, and skipping this would miss it.
6. Render two leaderboards: **Top by total_shares** (raw reach) and **Top by visits-per-share** (quality/conversion). Call out any asset that's high on reach but near-zero on visits-per-share as needing a creative refresh, not more distribution push.
7. Close with the single highest-leverage move: which asset or format to clone for the next content push, backed by the numbers above.
