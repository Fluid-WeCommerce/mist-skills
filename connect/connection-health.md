---
name: Connect connection health
description: Report on the health of the company's Fluid Connect integration over the last 7 days — sync errors, stuck records, and where the pipeline typically breaks.
icon: heart-pulse
---

# Goal

Produce a 7-day health report for `{{company.name}}`'s Fluid Connect integration(s) with a distributor/back-office platform (Exigo, ByDesign, InfoTrax, Pillars, or similar). Cover sync volume and errors by day and record type, flag records stuck in the pipeline, and gather a human decision on how to resolve each stuck cluster. Never write or mutate data — this is a read + report + ask skill.

# Steps

## 1. Discover the connection(s)

1. `fluid_api("/api/v202604/connect/reporting_databases", "GET")` — this is the verified source of truth for what's connected. Response shape: `{ "reporting_databases": [{ "name": "Exigo", "slug": "drp_..." }, ...] }`. An empty array means Connect isn't set up for this company — stop here and say so.
2. The `name` tells you the provider (`Exigo`, `ByDesign`, `InfoTrax`, `Pillars`, or `Fluid` for the native reporting DB). Treat all distributor-platform providers identically for the rest of this skill — same steps, just note the provider name in the report. `Exigo` is the most common case in practice.
3. Try to enrich with droplet/integration install status — probe likely endpoints such as `fluid_api("/api/v202604/droplets?filter[category]=connect", "GET")` or `fluid_api("/api/v202604/droplet_installs", "GET")`. These paths are **not verified** — discover the right one live and degrade gracefully:
   - `404` → that path doesn't exist on this build; try the next candidate, then move on without it if none work. Don't guess forever — two or three tries is enough.
   - `403` → the endpoint exists but the current user lacks permission. Say so explicitly in the report ("Couldn't check droplet install status — missing permission for `<path>`") rather than silently skipping it.
   - Anything you do successfully pull (last sync timestamp, install state) goes in the summary section.

## 2. Pull the last 7 days of sync/event/error activity

Compute the window as `{{today}}` minus 7 days.

1. Discover the right log/event source live — there is no single fixed endpoint for this across companies. Try, in order, and keep whatever responds:
   - A company events/webhooks feed, e.g. `fluid_api("/api/v202604/company_events?filter[created_at_gte]=<start>&limit=100", "GET")` or `fluid_api("/api/v202604/webhooks/events?filter[created_at_gte]=<start>", "GET")` (paginate via cursor if present).
   - Any connect-scoped log endpoint, e.g. `fluid_api("/api/v202604/connect/<slug>/events", "GET")` using the slug(s) from step 1.
   - Same 403/404 degrade rule as above — 404 means try the next candidate, 403 means tell the user what's missing.
2. `db_query` only ever runs against **the active project's own database connection** — it has no parameter for picking a different reporting database by slug, and it will not "reach into" a distributor DB just because `reporting_databases` listed one. So before relying on it:
   - Check whether the project you're currently running in *is* that reporting-database connection (a "database" kind project named after the provider, e.g. "Exigo"). If it is, you're clear to use `db_query` directly against it.
   - If you're running from a Mist app project instead, `db_query` will happily execute — but against that **app's own Postgres/Neon database**, not Exigo/ByDesign/etc. Do not treat rows it returns as distributor sync data. If the active project isn't the reporting-database connection, skip DB-level enrichment entirely and say so in the summary ("DB-level sync/queue detail wasn't available — open the `<provider>` reporting-database connection as its own project and re-run this skill there for row-level detail"). Don't guess at table names against the wrong database.
   - Only when you've confirmed you're against the right connection: introspect first (list tables if the tool supports it, or a broad `SELECT` against likely names) and look for tables that resemble a sync/import queue: names containing `queue`, `sync`, `import`, `log`, or `error`. Common shapes to expect: a row per record with a status (`pending` / `success` / `failed` / `error`), a `record_type` (order, customer/distributor, enrollment, commission, inventory, etc.), a timestamp, and a failure reason/message column.
3. Keep every event/row you pull scoped to the last 7 days — filter at the query/API level where you can, otherwise filter client-side after fetching.

## 3. Compute success vs. error counts

1. Bucket everything from step 2 by calendar day (7 rows) and by record type.
2. For each bucket, compute: total attempts, successes, errors, and error rate (%).
3. Note any day with an error-rate spike relative to the 7-day average — call it out later in the report, don't just bury it in the table.

## 4. Identify stuck records — human-in-the-loop before anything changes

1. A record is **stuck** if it's `pending` or `failed` and has been in that state for **more than 48 hours** as of `{{today}}`.
2. Cluster stuck records by `(record_type, failure_stage or reason)` — e.g. "12 orders stuck at inventory-hold sync, failing with `sku_not_mapped`". Don't present one row per record; present one card per cluster.
3. For each cluster, present it via `human_in_the_loop` before taking any action — this skill **never auto-retries, auto-skips, or auto-fixes** anything. The tool is Approve/Dismiss only (no custom multi-choice options), so frame `proposed_action` as the single follow-up you'd flag, and let Approve/Dismiss mean "flag this for follow-up" vs. "no action needed":
   ```
   human_in_the_loop({
     suggestion_id: "connect-health:<provider_slug>:<record_type>:<failure_reason>",
     source: "connect_health",
     title: "12 orders stuck at inventory-hold sync (sku_not_mapped)",
     description: "Pending 48h+, first seen <date>, last seen <date>. Sample record ids: [...]",
     proposed_action: "Flag this cluster for manual follow-up in the report — Connect has no verified retry/skip endpoint, so this skill will not attempt to act on it automatically.",
     metadata: { provider_slug: "<slug>", record_type: "<type>", failure_reason: "<reason>", sample_ids: [/* … */] }
   })
   ```
   - If the tool returns a card payload, present your batch (cap at 3 per turn, same as other skills that use this tool) and END YOUR TURN — the user's Approve/Dismiss click comes back as the next message.
   - If it returns "already approved/dismissed" for a cluster, don't re-prompt; use the stored decision in the report.
4. Record each cluster's decision (flagged for follow-up / no action needed) in the report. Never execute a retry, skip, or fix yourself, even on approval — there is no verified mutation endpoint for this, and the whole point of this skill is read + report + ask.
5. If there are no stuck clusters, say so plainly — don't manufacture a section.

## 5. Identify where records typically get stuck

1. Across the full 7-day window (not just currently-stuck records), rank failure stage/reason combinations by frequency, regardless of whether they eventually resolved.
2. Surface the top 3-5 as "typical stick points" — these are the recurring friction points worth the company's attention even after today's stuck records clear.

## 6. Render the report

Single Markdown document, in this order:

1. **Summary** — provider(s) connected (from step 1), window (`<start>`–`{{today}}`), total sync attempts, overall success/error rate, anything that couldn't be checked due to permissions.
2. **Daily breakdown** — one table, rows = day, columns = attempts / successes / errors / error rate. Call out any spike day in a line below the table.
3. **By record type** — one table, rows = record type, columns = attempts / successes / errors / error rate.
4. **Stuck records** — one subsection per cluster from step 4: description, count, age range, sample ids, and the resolution the user chose.
5. **Typical stick points** — the ranked list from step 5, one line each with a plain-English cause if you can infer one (e.g. "SKU not yet mapped in Connect field mapping").
6. **Suggested next steps** — 2-4 concrete, specific actions (e.g. "Map the 4 unmapped SKUs in Connect field settings", "Ask Exigo support about the recurring timeout on enrollment sync").
