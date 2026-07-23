---
name: Field leader scoreboard
description: Rank field leaders by tenure, activity, and content engagement, with an optional deeper team-depth/genealogy pass when a reporting database (e.g. Exigo) is connected.
icon: award
---

# Goal

Rank {{company.name}}'s field leaders by growth and activity — and, when a back-office reporting connection exists, by real team depth — the board Leader Lester uses to know who's carrying momentum and who needs support.

# Steps

1. **Check for a connected reporting database first**: `fluid_api("/api/v202604/connect/reporting_databases", "GET")`. If it 403s or returns an empty `reporting_databases` array, note "no reporting connection — using admin-API signals only" and skip to step 3. If it returns an entry whose `slug` is NOT the reserved `fluid` slug (e.g. a connector named "Exigo"), that's a genealogy/back-office system worth a deeper pass — remember its name for step 2.
2. **Only if a non-`fluid` connector was found**: `db_query` only runs against a database project the user has already connected in Mist Desktop — it is not automatically available in every chat. If the active project isn't that connection, tell the user which project to switch to and continue with step 3 in the meantime rather than blocking. If it IS available: run a schema-discovery query FIRST (e.g. `SELECT TOP 20 TABLE_NAME FROM INFORMATION_SCHEMA.TABLES` for a SQL-Server-style Exigo database) — never assume table/column names, they vary per company. Look for a distributor/rep table with rank and sponsor/upline columns, then compute team size and rank distribution per top-level leader with a read-only query, presented via `sql_answer_card` (not a plain code block, so the user gets a saveable query).
3. Paginate `fluid_api("/api/v2025-06/reps?limit=100", "GET")` fully. Capture `id`, `full_name`, `country_code`, `created_at`, `updated_at`, `rank`.
4. Build the base scoreboard from what's always available: tenure (days since `created_at`), recency (days since `updated_at`), `country_code`, and `rank` when populated. If `rank` is null across the whole roster, say so plainly — rank tracking isn't wired up for this company at the admin-API level, which is exactly why the Exigo/db_query path in step 2 matters when it's available.
5. For the top 15 reps by tenure, call `fluid_api("/api/v2025-06/reps/<id>/most_shared?limit=3", "GET")` and `.../most_viewed?limit=3` to add a content-activity signal — tenure alone doesn't show who's still actively building.
6. Render one table: rank (if step 2 produced one) or an activity-tier derived from recency + content activity, name, country, tenure, last-active.
7. Close with two named lists: who's carrying the org right now (top of the board) and who's gone quiet (long tenure, stale `updated_at`, zero recent shares) — the two lists Lester actually acts on.
