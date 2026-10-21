---
name: Slow-mover clearance list
description: Find inventory tying up capital with near-zero sell-through and build a ranked clearance list by dollars freed.
icon: archive
---

# Goal

Find the products at `{{company.name}}` tying up the most capital in slow-moving stock, and build a clearance list ranked by cash freed if cleared.

# Steps

1. Call `fluid_api("/api/company/v1/products?per_page=100", "GET")`, paginating until exhausted. Keep only products/variants with `track_quantity: true` and `inventory_quantity` present. Record `title`, price, and stock on hand.
2. Call `fluid_api("/api/v202506/orders?start_date=<90-days-ago>&end_date={{today}}&limit=100", "GET")`, paginating via `meta.pagination.next_cursor` until exhausted. Use `start_date`/`end_date` — `filter[created_at_gte]`-style bracket params are silently ignored by this endpoint (no error, it just returns the unfiltered set). Tally units sold per product over the trailing 90 days. If `meta.pagination` comes back as `{}`, there were zero orders in the window — treat every tracked product as a slow mover by definition rather than skipping the step.
3. Compute **90-day sell-through velocity** = units sold ÷ 90 (units/day) per product. Flag as a **slow mover** anything with velocity under a low threshold (default: fewer than 1 unit sold in the full 90 days) that still carries stock on hand.
4. For each slow mover, compute **capital tied up** = stock on hand × unit price. Compute **days of cover at current pace** — if velocity is exactly zero, report it as "no sales in 90 days" rather than an infinite number.
5. Rank slow movers by capital tied up, descending. Cross-check the top 10 against `fluid_api("/api/v2025-06/discounts?limit=100", "GET")` to see whether an active clearance discount already exists for any of them — don't recommend a markdown that's already running.
6. Render a table: product, stock on hand, units sold (90d), capital tied up, existing-discount flag. Group into **No sales at all** (most urgent — dead stock) vs. **Slow but not dead** (some velocity, just too much stock for the pace).
7. End with a **Decision**: total capital tied up across the list, the single highest-capital slow mover, and a suggested clearance discount depth (start at 20% for slow-but-not-dead, 40%+ for zero-sales dead stock) — framed as a recommendation, not an action this skill takes.
8. If no product has both `track_quantity: true` and zero/low sales, say inventory looks healthy rather than forcing a list.
