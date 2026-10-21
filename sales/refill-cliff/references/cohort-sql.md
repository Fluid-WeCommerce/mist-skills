# Refill Cliff — query patterns

Every query below is a **template**, not a paste target. Run `db_schema`
(`mode: "search"`, keyword `subscription`) first and substitute the real table
and column names it returns. Fluid reporting databases are provisioned per
company and the schemas differ.

Both dialects appear because Fluid reporting connections are Postgres on some
companies and SQL Server on others. Check which one you are on before writing
`date_trunc` (Postgres) versus `DATEDIFF` / `DATEADD` (T-SQL).

All of these are read-only. Sessions enforce that client-side anyway.

## 0. Reconnaissance — run these before anything else

Never filter on a status value you have not seen.

```sql
SELECT status, COUNT(*) AS subs
FROM subscriptions
GROUP BY status
ORDER BY subs DESC;
```

Find the billing-event join. You want whichever column links an order back to
the subscription that generated it — commonly `subscription_id`, sometimes a
token column.

```sql
-- Postgres
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_name = 'orders' AND column_name ILIKE '%subscription%';
```

```sql
-- T-SQL
SELECT COLUMN_NAME, DATA_TYPE
FROM INFORMATION_SCHEMA.COLUMNS
WHERE TABLE_NAME = 'orders' AND COLUMN_NAME LIKE '%subscription%';
```

If no such column exists, skip to §2 (date-derived cycles) and say in the output
that cycles are inferred from elapsed time rather than counted from real billing
events — it is a weaker measurement and the reader deserves to know.

## 1. Cycle counts from real billing events (preferred)

Counting actual orders is the honest way to say "this subscription reached cycle
4." It survives paused months, skipped cycles and mid-life plan changes, all of
which break date arithmetic.

```sql
-- Postgres
WITH billed AS (
  SELECT
    s.id,
    s.created_at,
    s.cancelled_at,
    s.status,
    s.price,
    COUNT(o.id) AS cycles
  FROM subscriptions s
  LEFT JOIN orders o
    ON o.subscription_id = s.id
   AND o.status IN ('completed')     -- confirm against §0 first
  GROUP BY s.id, s.created_at, s.cancelled_at, s.status, s.price
)
SELECT cycles, COUNT(*) AS subs, AVG(price) AS avg_price
FROM billed
GROUP BY cycles
ORDER BY cycles;
```

Swap `COUNT(o.id)` for `COUNT(DISTINCT o.id)` if the join fans out through line
items.

## 2. Cycle counts derived from dates (fallback only)

`plan_interval_months` comes from the subscription plan. A weekly plan is
`0.25`; guard the division so a null or zero interval does not blow up the query.

```sql
-- Postgres
SELECT
  s.id,
  FLOOR(
    EXTRACT(EPOCH FROM (COALESCE(s.cancelled_at, s.last_bill_date, NOW()) - s.created_at))
    / (86400 * 30.44 * NULLIF(p.interval_months, 0))
  ) AS cycles
FROM subscriptions s
JOIN subscription_plans p ON p.id = s.subscription_plan_id;
```

```sql
-- T-SQL
SELECT
  s.id,
  FLOOR(
    DATEDIFF(DAY, s.created_at, COALESCE(s.cancelled_at, s.last_bill_date, GETUTCDATE()))
    / (30.44 * NULLIF(p.interval_months, 0))
  ) AS cycles
FROM subscriptions s
JOIN subscription_plans p ON p.id = s.subscription_plan_id;
```

## 3. The survival curve, censored correctly

This is the query the whole skill turns on. The `eligible` CTE is the part that
makes it correct: a subscription only counts toward cycle `n`'s denominator once
enough calendar time has passed that it *could* have reached cycle `n`.

Without that filter, every recently-acquired subscription reads as a cycle-2
churn and the curve reports a cliff that is really just recent growth.

```sql
-- Postgres. `cycles` comes from §1 or §2; `interval_months` from the plan.
WITH lifecycle AS (
  SELECT s.id, s.created_at, b.cycles, p.interval_months
  FROM subscriptions s
  JOIN billed b ON b.id = s.id
  JOIN subscription_plans p ON p.id = s.subscription_plan_id
),
cycle_axis AS (
  SELECT generate_series(1, 12) AS n           -- T-SQL: a numbers table or VALUES list
),
eligible AS (
  SELECT
    c.n,
    COUNT(*) FILTER (
      WHERE l.created_at <= NOW() - (c.n * l.interval_months || ' months')::interval
    ) AS eligible_subs,
    COUNT(*) FILTER (
      WHERE l.created_at <= NOW() - (c.n * l.interval_months || ' months')::interval
        AND l.cycles >= c.n
    ) AS reached
  FROM cycle_axis c
  CROSS JOIN lifecycle l
  GROUP BY c.n
)
SELECT
  n                                              AS cycle,
  eligible_subs,
  reached,
  ROUND(100.0 * reached / NULLIF(eligible_subs, 0), 1) AS pct_reached,
  ROUND(
    100.0 * reached
    / NULLIF(LAG(reached) OVER (ORDER BY n), 0), 1
  )                                              AS conditional_retention_pct
FROM eligible
ORDER BY n;
```

`conditional_retention_pct` is the column that names the cliff — the cycle where
it bottoms out. `pct_reached` alone always slopes downward and tells you nothing
about *where* people leave.

Treat any row with `eligible_subs < 30` as thin. Report it, do not conclude from it.

## 4. The price step-up

The usual cause of a cycle-1 → cycle-2 cliff. If the average amount billed jumps
at exactly the cliff cycle, the churn is a pricing decision the business already
made, and that is the headline.

```sql
-- Postgres. Bill sequence per subscription, then averaged across the base.
WITH seq AS (
  SELECT
    o.subscription_id,
    o.total_amount,
    ROW_NUMBER() OVER (PARTITION BY o.subscription_id ORDER BY o.created_at) AS cycle
  FROM orders o
  WHERE o.subscription_id IS NOT NULL
    AND o.status IN ('completed')
)
SELECT
  cycle,
  COUNT(*)                AS bills,
  ROUND(AVG(total_amount), 2) AS avg_billed,
  ROUND(AVG(total_amount) - LAG(ROUND(AVG(total_amount), 2)) OVER (ORDER BY cycle), 2) AS step_vs_prior
FROM seq
WHERE cycle <= 12
GROUP BY cycle
ORDER BY cycle;
```

Report `step_vs_prior` in dollars and as a percentage of the cycle-1 average. A
$40 step on a $40 first order is a 100% increase, and that framing is the one
that lands.

## 5. At-risk buckets, live subscriptions only

Each bucket is a save play. Keep them as separate result sets so the counts stay
attributable, then deduplicate by subscription id before totaling — one
subscription routinely qualifies for three buckets, and summing the buckets
inflates the headline.

```sql
-- Retry window still open: the retry has not fired yet.
SELECT COUNT(*) AS subs, SUM(price) AS monthly_value
FROM subscriptions
WHERE last_failed_at IS NOT NULL
  AND next_retry_at > NOW()
  AND status IN ('active', 'past_due');       -- confirm against §0

-- Dunning exhausted: failed, no retry scheduled, still nominally billable.
SELECT COUNT(*) AS subs, SUM(price) AS monthly_value
FROM subscriptions
WHERE decline_count > 0
  AND (next_retry_at IS NULL OR next_retry_at <= NOW())
  AND cancelled_at IS NULL;

-- Skip-to-churn: disengaging but not yet cancelled.
SELECT COUNT(*) AS subs, SUM(price) AS monthly_value
FROM subscriptions
WHERE skipped_count >= 2
  AND cancelled_at IS NULL;

-- Standing at the cliff: one cycle short of it, billing inside the save window.
-- :cliff_cycle is the cycle you measured in §3, not a guess.
SELECT s.id, s.price, s.next_bill_date, b.cycles
FROM subscriptions s
JOIN billed b ON b.id = s.id
WHERE b.cycles = :cliff_cycle - 1
  AND s.next_bill_date BETWEEN NOW() AND NOW() + INTERVAL '14 days'
  AND s.cancelled_at IS NULL
ORDER BY s.price DESC;
```

The deduplicated union:

```sql
SELECT COUNT(DISTINCT id) AS at_risk_subs, SUM(price) AS monthly_value
FROM (
  SELECT id, price FROM subscriptions WHERE last_failed_at IS NOT NULL AND next_retry_at > NOW()
  UNION
  SELECT id, price FROM subscriptions WHERE decline_count > 0 AND cancelled_at IS NULL
  UNION
  SELECT id, price FROM subscriptions WHERE skipped_count >= 2 AND cancelled_at IS NULL
) u;
```

## 6. Cost control

The subscriptions and orders tables are among the largest in a Fluid reporting
database. Before running §3 or §4 on a big company:

- `EXPLAIN` the query on Postgres. On SQL Server, reason from row estimates and
  add `TOP` / `OFFSET-FETCH` bounds.
- Bound the cycle axis at 12. Nobody makes a decision from cycle 40.
- If the plan implies a heavy sequential scan, warn the user with what it will
  touch and offer a narrower window before running it.

## 7. Bulk escape hatch

`fluid_api("/api/v202506/subscriptions/export_csv", "GET")` produces a full
subscription export. It is a fallback for companies with no reporting database
and a base too large to page through the REST API — not the default path, and it
does not aggregate anything for you.
