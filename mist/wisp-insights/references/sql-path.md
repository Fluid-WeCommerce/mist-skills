# Asking Wisp with `db_query` — no token, no MCP

On a **Mist app project**, `db_query` targets that project's own database. Wisp's tables live
there. So on the Wisp Mist you can answer insight questions with plain SQL and **no setup at all** —
no `wmcp_` token, no MCP server, no Settings dialog.

This is usually the right path for an operator working inside Mist Desktop. The MCP exists for
portability (Claude Desktop, Cursor, Claude Code) and for anything where tenancy must be structural
rather than remembered.

## Why this path is good

- **Zero setup.** `db_query` is a native Mist tool on the active connection.
- **Survives Safe Mode.** `db_query` is read-only enforced by its own SQL gate — SELECT, EXPLAIN,
  SHOW and SELECT-only CTEs; anything mutating is rejected — so Safe Mode permits it. Every
  `mcp__*` tool is refused outright under Safe Mode, which makes SQL the only path there.
- `db_schema` first if you are unsure of a column. Do not guess and let the error teach you.

> ### `sql_answer_card` does NOT work here — do not reach for it
>
> On a **Mist app project** — which is what Wisp is — `sql_answer_card` refuses every call with
> *"sql_answer_card only works on database projects. On a Mist app, use db_query."* It is gated on
> `projectInfo.kind === "database"` and a Mist app's kind is `"mist"`
> (`fluid-mono/apps/mist-desktop/src/main/tools/index.ts:11336-11350`). The card opens its result in
> the SQL editor tab, and that tab only exists on database projects.
>
> So on this path **`db_query` does everything** — exploration *and* the final answer — and you write
> the answer as prose plus the tables in Step 7. That is the intended shape on a Mist app, not a
> degradation. Do not paste a wall of raw rows either: query, read, and report the numbers.

`db_query` **does** bind parameters — pass `params: [companyId, from, to]` alongside the `$1/$2/$3`
SQL below. It also takes `side: "local" | "production"`, and on a Mist app it **defaults to
`production`** (the Neon database), which is the corpus you want. Pass `side: "local"` only if you
deliberately want the PGlite dev copy — it holds seed data, not real shoppers.

## The one rule you cannot get wrong

**Every query filters on `company_id`.**

The MCP derives the tenant from the token, so no MCP tool can read another merchant's data even if
asked to. **Raw SQL has no such protection.** One Wisp database holds every company that installed
the droplet, and an unfiltered `SELECT` reads recordings of other merchants' customers — the worst
possible outcome for this product.

Get the company id first and put it in every statement:

```sql
-- The tenant key is companies.id (TEXT uuid), NOT the Fluid numeric id.
SELECT id, name, fluid_company_id
FROM companies
WHERE active = true
ORDER BY created_at;
```

If more than one row comes back, **ask which company before querying anything else.** Never assume,
and never answer across all of them.

## Canonical queries

These mirror what the MCP tools compute, so answers agree whichever path you took. Keep the
semantics — especially the denominators.

### Signal rates over a window (`signal_stats`)

```sql
WITH scope AS (
  SELECT id FROM wisp_sessions
  WHERE company_id = $1
    AND started_at >= $2 AND started_at < $3
)
SELECT s.kind,
       COUNT(*)                        AS events,
       COUNT(DISTINCT s.session_id)    AS sessions,
       ROUND(100.0 * COUNT(DISTINCT s.session_id)
             / NULLIF((SELECT COUNT(*) FROM scope), 0)) AS rate_pct
FROM wisp_signals s
WHERE s.company_id = $1
  AND s.session_id IN (SELECT id FROM scope)
GROUP BY s.kind
ORDER BY sessions DESC;
```

**Always report the denominator alongside the rate** — "7 of 41 sessions", never a bare 17%. Run
`SELECT COUNT(*) FROM scope` and say it out loud.

### Worst sessions, with something to watch

```sql
SELECT se.id,
       se.started_at, se.duration_ms, se.device_class,
       se.entry_path, se.exit_path, se.reached_checkout,
       COUNT(sg.id) FILTER (WHERE sg.kind NOT IN
         ('viewed_product','add_to_cart','reached_cart','started_checkout','reached_checkout')
       ) AS fault_signals,
       ARRAY_AGG(DISTINCT sg.kind) AS kinds
FROM wisp_sessions se
LEFT JOIN wisp_signals sg
       ON sg.session_id = se.id AND sg.company_id = se.company_id
WHERE se.company_id = $1
  AND se.started_at >= $2 AND se.started_at < $3
GROUP BY se.id
ORDER BY fault_signals DESC, se.duration_ms DESC
LIMIT 20;
```

Build the watchable link yourself — the MCP returns it, SQL does not:

```
https://<mist-host>.wecommerce.dev/droplet/sessions/<id>
```

**Every behavioural claim still carries one.** That rule does not relax because the transport
changed.

### Friction by path

```sql
SELECT se.entry_path AS path,
       COUNT(DISTINCT se.id) AS sessions,
       COUNT(sg.id)          AS signals,
       ROUND(COUNT(sg.id)::numeric / NULLIF(COUNT(DISTINCT se.id), 0), 2) AS signals_per_session
FROM wisp_sessions se
LEFT JOIN wisp_signals sg
       ON sg.session_id = se.id AND sg.company_id = se.company_id
WHERE se.company_id = $1
  AND se.started_at >= $2 AND se.started_at < $3
GROUP BY se.entry_path
HAVING COUNT(DISTINCT se.id) >= 5      -- below this a rate is an anecdote
ORDER BY signals_per_session DESC;
```

### Funnel, and the thing you must say about it

```sql
SELECT COUNT(*)                                        AS sessions,
       COUNT(*) FILTER (WHERE reached_checkout)        AS reached_checkout
FROM wisp_sessions
WHERE company_id = $1
  AND started_at >= $2 AND started_at < $3;
```

**`reached_checkout` means they reached the doorway, not that they bought.** Checkout runs on a
different origin and is not recorded in v1. Say which one you mean, every time — the MCP's
`funnel_summary` returns a `blindSpot` field precisely so this cannot be forgotten, and on the SQL
path remembering it is on you.

### Daily trend

```sql
SELECT day, sessions, signals
FROM wisp_daily_rollups
WHERE company_id = $1 AND day BETWEEN $2 AND $3
ORDER BY day;
```

Rollups are written by cron, so today's row lags until the next tick. For "right now", count
`wisp_sessions` directly.

## What this path loses

Be honest about these rather than quietly approximating:

- **The frustration score is not a column.** It is a weighted sum over signal kinds, dampened by
  session duration, computed in TypeScript. `fault_signals DESC` above is a reasonable proxy for
  "look here first" — it is not the same number the library shows. Do not quote a score from SQL.
- **Sufficiency guards are yours to apply.** The MCP returns a `sufficient` flag; SQL does not.
  Single-digit sessions is an anecdote — say so before analysing, not after.
- **Never read `wisp_chunks`.** Payloads are compressed recorded DOM. They are large, they are not
  meant to be read as data, and nothing an insight needs lives there.
- **Schema drift.** These queries name columns directly. If one errors, run `db_schema` and adapt
  rather than assuming the data is missing.
