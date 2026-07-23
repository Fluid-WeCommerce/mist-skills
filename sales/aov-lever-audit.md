---
name: AOV lever audit
description: Find which levers actually move average order value — item count, bundles, discount depth — with a dollar figure per lever.
icon: trending-up
---

# Goal

Find which levers actually move average order value (AOV) at {{company.name}} — multi-item orders, discount usage — so Sales pushes what's proven to work instead of guessing.

# Steps

1. Call `fluid_api("/api/v202506/orders?status=completed&start_date={{thirty_days_ago}}&end_date={{today}}&limit=1", "GET")` and read `meta.pagination.total_count`, `meta.average_amount_base`, and `meta.total_amount_base` — that's the period's headline AOV, precomputed server-side. (Ignore the `limit` value for counting purposes — read `meta`, not the array.) If there are zero completed orders in the window, `meta.pagination` comes back as `{}` and `average_amount_base`/`total_amount_base` are absent entirely — don't treat that as missing data or a 0 AOV; stop and report plainly that there were no completed orders in the window instead of rendering the rest of the audit against an empty set.
2. Paginate the full completed-order set for the same window (`limit=100`, follow `meta.pagination.next_cursor`). For every order, bucket by `items_count`: **1 item**, **2 items**, **3+ items**. Track count and sum of `amount` (fall back to `amount_in_base`) per bucket.
3. Compute average order value per bucket. The delta between the 2-item/3+-item buckets and the 1-item bucket is the real, dollar-denominated lift from bundling/upselling — not a guess.
4. Call `fluid_api("/api/v2025-06/discounts?active=true&limit=100", "GET")`, paginating via `page`/`per_page` if `meta.pagination.total_pages` > 1. For each active discount capture `code`, `price_discount_type`, `price_discount_percent` or `price_discount_amount`, and `total_usage`.
5. Flag any active discount with `total_usage` in the top quartile of the set AND a discount depth that looks steep (`price_discount_type: percentage` above ~20%, or a flat amount that's a large share of the period's average order value) — that's volume bought at a real margin cost, worth weighing against the bundle lift found in step 3.
6. Render: the headline AOV, the items-count bucket table (bucket, order count, average order value, delta vs 1-item), and the discount usage table sorted by `total_usage` descending with the depth flag.
7. Close with ONE recommendation grounded in the numbers — e.g. "the 2-item bucket AOV is $X higher than single-item orders across N orders — push the bundle at checkout harder," or "no meaningful multi-item lift this period — the AOV opportunity is upsell placement, not bundling," or "code `<CODE>` is buying volume at a steep discount with no matching AOV lift — worth tightening."
