---
name: Genealogy & rank-advancement pipeline
description: Show who's closest to their next rank using a connected reporting database (Exigo or similar) when one exists, degrading gracefully to admin-API rank data when it doesn't.
icon: network
---

# Goal

Show {{company.name}}'s rank-advancement pipeline — who's closest to their next rank — using a connected back-office reporting database when one exists, and degrading gracefully to what the admin API can show when it doesn't. This skill must never fail silently or fabricate a genealogy view it can't actually produce.

# Steps

1. **Always check for a reporting connection first**: `fluid_api("/api/v202604/connect/reporting_databases", "GET")`. Read the `reporting_databases` array.
   - 403 response, or an empty array, or only the reserved `fluid` slug present → tell the user plainly that no back-office (Exigo or similar) connection is available, and go straight to step 4 for the admin-API fallback. This is a normal, expected outcome for many companies — present it as a fact, not an error.
   - A connector with a real name (e.g. "Exigo") present → that system likely holds genealogy depth and rank-qualification math the admin API doesn't expose. Continue to step 2.
2. **Only if a connector was found**: `db_query` only works against a database project the user has already connected in Mist Desktop, not automatically in every chat context. If the current project isn't wired to that connection, tell the user which project to switch to, and still produce step 4's admin-API fallback in this same turn rather than stopping.
3. **If `db_query` is available against that connection**: discover the schema BEFORE writing any query — e.g. list tables via `INFORMATION_SCHEMA.TABLES` (most back-office systems including Exigo are SQL-Server-style). Exigo schemas vary per company migration; treat every table/column name as unverified until you've seen it via `db_query`. Once you've identified the distributor/rank table (look for rank + sponsor/upline columns), write a read-only query computing, per active leader, their current rank and the gap to the next rank up (team volume, personally-enrolled count, or whatever qualification fields the actual schema has — don't assume Exigo's stock field names). Rank results by smallest gap first. Present the final query via `sql_answer_card`, not a plain code block, so the user gets the saveable SQL + a card in the chat.
4. **Admin-API fallback (always run this — either as the headline output or as a supplement to step 3)**: `fluid_api("/api/v202506/ranks?limit=100", "GET")` for the rank ladder, and paginate `fluid_api("/api/v2025-06/reps?limit=100", "GET")` for the roster's `rank` field. If `rank` is populated, tally a headcount-per-rank distribution. If it's null across the board (rank sync not configured for this company), say so explicitly — that's a real gap, not a query mistake.
5. If step 3 ran successfully: present the db_query-derived "closest to advancing" list as the headline, with the admin-API rank-ladder distribution as supporting context. If only step 4 ran: present the headcount-per-rank distribution as the headline, and close with a one-line recommendation to connect a reporting database (Exigo or similar) via Connect for the full advancement-gap view.
