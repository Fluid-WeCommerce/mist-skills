# Measuring cadence and attach rate

How to replace the assumed cadences in `replenishment-classes.md` with this merchant's
own behaviour, and how to get the one input a revenue estimate cannot be built without.

Requires a reporting database connected via **Settings → Reporting Databases** in Fluid
admin. It is a Postgres mirror. If it is absent, `404 No database-enabled reporting
connector` comes back and the honest move is to say cadence is assumed — not to
substitute something that looks close.

## Confirm the schema before trusting any query below

Table and column names below are the common shape, **not a guarantee**. Read the real
ones first:

```sql
SELECT schemaname, relname AS table_name, n_live_tup AS approx_rows
FROM pg_stat_user_tables ORDER BY n_live_tup DESC;

SELECT table_name, column_name, data_type
FROM information_schema.columns
WHERE table_schema NOT IN ('pg_catalog','information_schema')
  AND (table_name ILIKE '%order%' OR table_name ILIKE '%item%'
       OR table_name ILIKE '%product%' OR table_name ILIKE '%subscription%')
ORDER BY table_name, ordinal_position;
```

Three facts must exist or the analysis cannot proceed: an order row with a customer id
and a timestamp, a line-item row joining orders to products, and a way to tell a
subscription order from a one-time order. If the third is missing, attach rate is **not
measurable here** and any projection is borrowed and must be labelled so.

## Observed cadence

Median days between consecutive orders of the same product by the same customer.

```sql
WITH purchases AS (
  SELECT oi.product_id, o.customer_id, o.created_at::date AS purchased_on
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.id
  WHERE o.customer_id IS NOT NULL
    AND COALESCE(o.status,'') NOT IN ('cancelled','refunded','voided')
  GROUP BY oi.product_id, o.customer_id, o.created_at::date
),
intervals AS (
  SELECT product_id,
         purchased_on - LAG(purchased_on) OVER (
           PARTITION BY product_id, customer_id ORDER BY purchased_on) AS gap_days
  FROM purchases
)
SELECT product_id,
       COUNT(*)                                                    AS repeat_pairs,
       PERCENTILE_CONT(0.5)  WITHIN GROUP (ORDER BY gap_days)::int AS median_days,
       PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY gap_days)::int AS p25_days,
       PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY gap_days)::int AS p75_days,
       (COUNT(*) >= 30)                                            AS is_trustworthy
FROM intervals
WHERE gap_days BETWEEN 7 AND 730
GROUP BY product_id
ORDER BY repeat_pairs DESC;
```

**Median, not mean.** Repurchase intervals have a long right tail. The customer who comes
back after 400 days is real but is not the cadence, and a mean gets dragged by them.

**The 7-day floor** drops split shipments and corrections, which are not refills. **The
730-day ceiling** drops what is really a new customer relationship.

**The 30-pair floor** is the difference between a measurement and noise wearing a
number's clothes. Below it, keep the category default and label it an assumption.

**Read p25 and p75 before setting a cadence.** If they are far apart, that product has no
single cadence — different customers use it at different rates — and imposing one number
on everybody produces cancellations. Offer a customer-selectable interval instead.

## Buyers, repeat-buyer share, and attach rate

```sql
-- Buyers per product, and how many ever came back.
WITH buyer_orders AS (
  SELECT oi.product_id, o.customer_id, COUNT(DISTINCT o.id) AS order_count
  FROM orders o JOIN order_items oi ON oi.order_id = o.id
  WHERE o.customer_id IS NOT NULL
    AND COALESCE(o.status,'') NOT IN ('cancelled','refunded','voided')
  GROUP BY oi.product_id, o.customer_id
)
SELECT product_id,
       COUNT(*)                                    AS buyers,
       COUNT(*) FILTER (WHERE order_count > 1)     AS repeat_buyers,
       ROUND(100.0 * COUNT(*) FILTER (WHERE order_count > 1)
             / NULLIF(COUNT(*),0), 1)              AS repeat_buyer_pct
FROM buyer_orders GROUP BY product_id ORDER BY repeat_buyers DESC;
```

Repeat-buyer share is the whole argument in one column: **those customers are already
rebuying it manually.** A product with a high repeat-buyer share and no subscription plan
is the strongest case in the catalog.

For attach rate, run the same join filtered to orders you can identify as subscription
orders (commonly `orders.subscription_id IS NOT NULL` or an `order_type` column — confirm
against the real schema) and divide by orders containing that product. Use the merchant's
own rate. If the query returns zero rows, they have no subscription orders in the
reporting data at all; say that rather than importing a number from elsewhere.

## Applying it

Apply attach rate **conservatively across categories**. A blade refill and a body lotion
do not convert alike, so a single rate taken from the razor line and applied to the whole
catalog is the kind of flattering assumption that gets a forecast thrown back at you.
Give a band, not a point estimate.

Compute revenue only over products having **both** a trustworthy cadence and a buyer
count. Exclude the rest — never backfill them with category defaults and then present one
confident total — and state what share of the gap the number actually covers.
