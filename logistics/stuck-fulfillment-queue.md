---
name: Stuck-fulfillment & aging-order queue
description: Find every order stalled past a normal ship SLA, broken down by stage, so the oldest and biggest orders get unstuck first.
icon: package-search
---

# Goal

Surface every order at `{{company.name}}` that's aging past a reasonable ship SLA as of `{{today}}`, grouped by where it's stuck, so operations can clear the queue oldest/highest-value first.

# Steps

1. Call `fluid_api("/api/v202506/orders?status=completed&limit=100", "GET")`, paginating via `meta.pagination.next_cursor` until exhausted. Use the flat `status=` param, not `filter[order_status]=` — bracket-style `filter[...]` params are silently ignored by this endpoint (no error, it just returns the unfiltered set). Note the naming collision: the query param `status` filters on the order's overall commerce state (`completed`/`cancelled`/`draft`/etc — confirmed live) — this is the SAME data as the order object's own `order_status` field, but a DIFFERENT field from the order object's `status` field (which instead holds shipment-pipeline substates like `awaiting_shipment`/`awaiting_payment`, and is what step 2 below actually bucket on). Keep `id`, `order_number`, `amount`, `created_at`, `sale_date`, `fulfillment_status`, `status`, `first_item`, `items_count`.
2. Define the SLA: an order is **at risk** if it's 3-5 days old and still not shipped, and **breached** if it's over 5 days old and still not shipped (`status` in `awaiting_shipment`/`in_progress`-equivalent, `fulfillment_status` not `shipped`/`fulfilled`). Adjust the thresholds down if the user tells you their normal ship time is faster.
3. Bucket every non-shipped order by `status`/`fulfillment_status` value (e.g. awaiting_shipment, in_progress, backordered) — this tells you *where* in the pipeline orders are piling up, not just that they are.
4. Within each bucket, sort by `created_at` ascending (oldest first) and by `amount` descending as a tiebreaker. Compute per bucket: order count, oldest order's age in days, total $ tied up.
5. Call `fluid_api("/api/v202506/orders/stats", "GET")` for `fulfilled_orders_count` vs `total_count` as a company-wide fulfillment-rate sanity check alongside the bucketed detail.
6. Render: a bucket-summary table (stage, count, oldest age, $ tied up), then the top 20 oldest/highest-value stuck orders as a flat list (order number, age, amount, stage).
7. End with a **Decision**: name the stage with the most $ tied up and the single oldest order overall (order number + age + amount) as the two things to clear today.
8. If every order shipped within the SLA window, say the queue is clean — don't manufacture a finding.
