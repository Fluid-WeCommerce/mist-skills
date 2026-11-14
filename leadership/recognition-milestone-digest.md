---
name: Recognition & milestone digest
description: Draft a short, rallying field update covering new joiners, rank achievers (when tracked), and top content sharers this period.
icon: megaphone
---

# Goal

Draft a rallying field update for {{company.name}} covering new joiners, rank achievers, and top content sharers this period — the kind of message that makes the field feel seen, not a data dump.

# Steps

1. Paginate `fluid_api("/api/v2025-06/reps?sort=-created_at&limit=100", "GET")`, filter client-side to `created_at` within the last 7 days — this week's new joiners.
2. Call `fluid_api("/api/v202506/ranks?limit=100", "GET")` for the company's rank ladder (`name` + `external_id` per rank). Cross-reference against the roster's `rank` field (when populated) to spot anyone who moved up recently. If `rank` is null across the board, say so and skip the "rising in rank" section entirely rather than inventing an achiever.
3. For the 10 most-tenured reps, call `fluid_api("/api/v2025-06/reps/<id>/most_shared?limit=5", "GET")` for each and pick the top 3 by `total_shares` (from following up with `fluid_api("/api/v2025-06/media/<id>/share_stats", "GET")` on their top shared asset if you need the number) as "sharing the most" this period.
4. Draft the digest as a short, upbeat Markdown message — NOT a table or report. Three sections, in this order:
   - **Welcome to the team** — new joiners, first names + country.
   - **Rising in rank** — only if step 2 found real movement.
   - **Sharing the most** — top 3 sharers, one thank-you line each.
   Keep the whole thing under ~200 words — this is a message the field reads, not a KPI review.
5. Present the draft and ask whether to send as-is, edit, or hold. Do NOT dispatch it anywhere automatically — there is no send/broadcast tool for field comms in Mist Desktop; the user copies the draft to wherever they actually send it.
