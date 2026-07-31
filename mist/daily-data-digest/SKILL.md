---
name: Daily data digest
description: Read a Mist app's own database and report what changed in the last 24 hours — volume trends per table, spikes, drops, stalls — as a chat digest plus a live dashboard that updates in place every day.
icon: activity
category: mist
---

# Daily data digest

Produce a daily read on the health of **this Mist app's database**: what moved in
the last 24 hours, how that compares to normal, and what looks wrong. Deliver it
twice — as a written digest in chat, and as a saved dashboard that overwrites
itself each day so the user always has one current view.

Today is {{today}}.

This skill is **schema-agnostic on purpose**. Every Mist app has its own tables,
so you discover the schema first and derive what's worth reporting. Never assume
a table or column exists because it usually does.

## Scope: one Mist app per run

`db_query` and `db_schema` target the **active project's** database only. There is
no cross-app query tool. So one run = one Mist app. To cover several apps, the
user schedules this skill once per app (see the last section).

## Runs unattended — never block

This is built to run headless on a schedule. **Never ask a question and wait,
never call `human_in_the_loop`.** If something is missing, make the safest call,
say so in the digest, and finish the turn. Your final assistant message becomes
the schedule's run summary and the notification the user actually reads — so it
must stand alone as the digest, not as "I've put it on the dashboard."

## 0. Pick the side

A Mist app has two databases: **production** (Neon) and **local** (PGlite in
`local.db/`, or a Postgres URL from `.env.local`). `db_query` defaults to
production on a Mist project — that is what you want. Local is a dev scratch
database; trends there are meaningless.

Only fall back to `side: "local"` if production errors with "No production
database is available", and when you do, **label the whole digest LOCAL DEV** in
the first line so nobody reads dev noise as a business signal. If neither side
answers, say exactly that and stop — do not fabricate a digest.

## 1. Map the schema

Call `db_schema` with `mode: "overview"` — every table, grouped by schema, ranked
by estimated size, with a one-line purpose guess. That is your candidate list.

Shortlist the tables that could carry a daily signal: pick roughly the **8
largest / most clearly transactional** and drop the obvious non-signal ones
(migrations, sessions, caches, join tables that only mirror a parent, framework
bookkeeping). Then call `db_schema` with `mode: "tables"` on the shortlist to get
real columns, types, and foreign keys.

**Read the types, don't guess them.** You need, per table:

- a **time column** — `created_at`, `inserted_at`, `occurred_at`, `timestamp`,
  `submitted_at`, whatever this app actually named it. A table with no time
  column cannot be trended; note it and move on.
- whether that column is `timestamptz` or plain `timestamp` — the two need
  different SQL (see below), and mixing them silently shifts your day boundaries.
- any **status / state / error / failed** column, for the anomaly probe in §3.

## 2. The roll-up query — one call, rolling windows

Use **rolling 24-hour windows, not calendar days.** A calendar "today" is a
partial day at almost every hour the schedule fires, so comparing it to full-day
averages invents a drop every single morning. Rolling windows are always
complete and always comparable.

Build **one** `db_query` that unions every trendable table:

```sql
SELECT 'public.orders' AS source,
       count(*) FILTER (WHERE created_at >= now() - interval '24 hours')      AS last_24h,
       count(*) FILTER (WHERE created_at >= now() - interval '48 hours'
                          AND created_at <  now() - interval '24 hours')      AS prev_24h,
       count(*) FILTER (WHERE created_at >= now() - interval '8 days'
                          AND created_at <  now() - interval '24 hours')      AS prior_7d,
       count(*)                                                               AS total_rows,
       max(created_at)                                                        AS latest_row
FROM public.orders
UNION ALL
SELECT 'public.submissions', …
FROM public.submissions
ORDER BY 1;
```

`now()` is `timestamptz` and compares correctly against a `timestamptz` column.
For a plain `timestamp` column, compare against `now() AT TIME ZONE 'UTC'`
instead — otherwise Postgres coerces using the server timezone and your windows
quietly slide.

Rules:

- Only union tables where `db_schema` **confirmed** the time column. One wrong
  column name fails the entire union.
- Schema-qualify every table (`public.orders`) — bare names are ambiguous.
- If the union still errors, don't debug it in a loop: fall back to one small
  query per table, skip the ones that fail, and note which were skipped.
- Cap it at ~10 tables. This must stay a handful of bounded queries, never a scan.

`prior_7d / 7.0` is the **baseline** — the normal day for that table.

## 3. Decide what's actually an anomaly

Apply fixed thresholds so the digest says the same thing about the same numbers
every day, instead of drifting with your mood:

| Signal        | Rule                                                            |
| ------------- | --------------------------------------------------------------- |
| **Spike**     | `last_24h >= 2 × baseline` **and** `last_24h - baseline >= 5`   |
| **Drop**      | `last_24h <= 0.5 × baseline` **and** `baseline - last_24h >= 5` |
| **Stalled**   | `last_24h = 0` **and** `prior_7d >= 7` (it normally sees daily traffic) |
| **Stale**     | `latest_row` older than 48h on a table that had rows in the prior 7 days |
| **Too quiet** | `prior_7d < 7` **and** `last_24h < 5` — list it, never trend it  |

The absolute floors matter. Without them, 1 → 3 rows reads as a "200% spike" and
the digest becomes noise nobody opens after a week.

Then run **at most two** extra probes, only where §1 found the columns:

1. **Status shift** — for a table with a status/state column, compare the
   distribution in the last 24h against the prior 7 days. A failure/error state
   climbing as a share of the total is the single most useful thing this digest
   can catch.
2. **Daily series for the hero chart** — 14 days of daily counts on the one table
   that best represents the app's core activity:

   ```sql
   SELECT date_trunc('day', created_at) AS day, count(*) AS n
   FROM public.orders
   WHERE created_at >= now() - interval '14 days'
   GROUP BY 1 ORDER BY 1;
   ```

**Aggregates only.** These are real production tables. Never select or print
row-level personal data — emails, names, phone numbers, addresses, tokens. Counts,
rates, and distributions tell the whole story; a sample row leaks a customer into
a chat log and a saved dashboard file.

## 4. Write the digest

Structure, in this order:

1. **One-line verdict.** "Busy day, nothing broken" / "Submissions stalled 19
   hours ago" / "Quiet — 3 tables idle, no errors." This is the notification
   text; make it carry the news on its own.
2. **Movement** — a short table: table, last 24h, vs baseline, direction. Only
   the tables that cleared the "too quiet" bar.
3. **Flags** — each anomaly from §3 with its real numbers and the rule it
   tripped. Nothing here without a number attached.
4. **What I'd look at** — at most two concrete next steps, tied to a flag. If
   there are no flags, say so plainly and skip this section.
5. **Coverage** — tables skipped and why (no time column, query failed, too
   small). This is what keeps the digest honest: a silent skip reads as "all
   clear" when it wasn't checked at all.

Never invent a number, never carry one forward from a previous run, and never
soften a stall into "slightly lower." If a probe failed, it failed — say it.

## 5. Render the dashboard

Call `show_dashboard` with `dataAsOf` set to the moment you gathered the data.

**The title must be stable and app-specific** — e.g. `"Acme Rewards Daily Data"`.
The dashboard id is derived from the title, so the same title **overwrites in
place** (one living dashboard per app, exactly what you want) while a title
containing the date creates a new file every single day and buries the panel.
Put the date in `subtitle` or `dataAsOf`, never in `title`.

A good layout for this digest:

- `stat_tiles` — last-24h counts for the top 3-4 tables, each with a `trend`
  (`direction` from the comparison, `value` non-negative, `format: "percent"`).
- `hero_chart` — `variant: "area"`, `xKey: "day"`, the 14-day series. One hero
  card, not several.
- `mini_table` — every trended table: last 24h / baseline / Δ. Accent the flagged
  rows `red` or `orange`.
- `insight_banner` — the single most important flag, `accent: "red"`. Omit the
  card entirely when there are no flags rather than banner-ing "all good."
- `stat_rows` — the status distribution, when §3 probe 1 ran.

Put **raw numbers** in `metric` with a `format` hint (`number`, `compact`,
`percent`) — never a pre-formatted string. If validation fails it names the exact
fields; fix those and call again without re-querying.

## 6. Tell the user how to schedule it

Close the first interactive run by telling them to open **Schedules**, add a
**recurring** schedule targeting this skill, captured against **this Mist app's
project**, with a daily cron (e.g. `0 8 * * *` in their timezone) and catch-up set
to **run once on next launch** — so a laptop that was closed overnight still
produces one digest instead of a burst of five.

One schedule per Mist app. Each writes its own dashboard and its own notification.
