---
name: Stockout risk vs. sales velocity
description: Compare current inventory against trailing sales velocity to flag every SKU on track to sell out, with a reorder recommendation and revenue at risk.
icon: package-x
---

# Goal

For every tracked-inventory product at `{{company.name}}`, compare stock on hand against how fast it's actually selling, and flag anything projected to run out — with the dollar revenue at risk if it does.

# Steps

1. Call `fluid_api("/api/company/v1/products?per_page=100", "GET")`, paginating until exhausted. Keep only products/variants with `track_quantity: true`. For each, record `title`, `in_stock`, and per-variant `inventory_quantity`.
2. Call `fluid_api("/api/v202506/orders?start_date=<30-days-ago>&end_date={{today}}&limit=100", "GET")`, paginating via `meta.pagination.next_cursor` until exhausted. Use `start_date`/`end_date` — `filter[created_at_gte]`-style bracket params are silently ignored by this endpoint (no error, it just returns the unfiltered set). Tally units sold per product over the trailing 30 days using `first_item`/line-item titles matched back to the product list from step 1 (note any order line that doesn't match a known product and report the unmatched count rather than silently dropping it). If `meta.pagination` comes back as `{}`, there were zero orders in the window — treat every tracked product's velocity as 0 rather than skipping the step.
3. Compute **daily sell-through velocity** = units sold in 30 days ÷ 30, per product. Compute **days of cover** = current `inventory_quantity` ÷ daily velocity. Skip products with zero velocity (nothing sold) — flag them separately as slow movers, not stockout risks (see the clearance-list skill for that angle).
4. Flag stockout risk by days of cover:
   - **Critical (reorder now)** — under 14 days of cover.
   - **Warning (reorder this week)** — 14-30 days of cover.
   - **Healthy** — over 30 days of cover.
5. For every Critical/Warning product, compute **revenue at risk** = daily velocity × average selling price × days of cover remaining until a typical reorder lead time (default 21 days if the user hasn't given a real supplier lead time) — i.e. the revenue that would be lost if the SKU sells out before a reorder could land.
6. Render a table sorted by revenue at risk descending: product, days of cover, tier, units/day, revenue at risk. Follow with a **suggested reorder quantity** per Critical item = daily velocity × (lead time + 14-day safety buffer) − current stock.
7. End with a **Decision**: total revenue at risk across all Critical items, and the single SKU to reorder first (highest revenue at risk, lowest days of cover).
8. If no products have `track_quantity: true`, say inventory tracking isn't enabled and this skill can't produce a stockout read until it is.
