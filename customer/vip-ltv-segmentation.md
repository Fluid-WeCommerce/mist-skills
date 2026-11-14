---
name: VIP / at-risk LTV segmentation
description: Segment customers by lifetime value and recent order recency into VIP/Growing/At-Risk/Dormant tiers, each with a next-best-action.
icon: crown
---

# Goal

Segment {{company.name}}'s customers by lifetime value and recency into VIP / Growing / At-Risk / Dormant tiers, and give Customer Experience a next-best-action per tier — not just a leaderboard.

# Steps

1. Paginate `fluid_api("/api/v2025-06/customers?sort=-created_at&limit=100", "GET")` fully (the `sort` param on this endpoint only accepts `created_at`/`-created_at`/`name`/`-name` — confirmed via a live 422 error; do NOT try to sort server-side by spend). Capture `id`, `full_name`/`name`, `email`, `total_spent`, `orders_count`, `created_at` — these come back on the LIST endpoint, no per-customer detail call needed. There is no `active_subscriptions_count`/`inactive_subscriptions_count` field on the customer record (confirmed live, list and detail both) — subscription state is handled per-customer in step 3 instead.
2. Sort the full pulled set client-side by `total_spent` descending. Take the top 50.
3. For each of the top 50, call `fluid_api("/api/v202506/customers/<id>/orders?limit=1&sort=-created_at", "GET")` to get their most recent order date — the customer record's own `last_order_id` is frequently null, so this per-customer call is the reliable way to get recency. Also call `fluid_api("/api/checkout/v2026-04/subscriptions?customer_id=<id>&limit=25", "GET")` (a real, confirmed-live filter) to see whether they have any `status: "active"` subscription vs. only `status: "cancelled"` ones — this replaces the nonexistent count fields.
4. Segment:
   - **VIP** — top quartile `total_spent` of the pulled set AND last order within 60 days.
   - **Growing** — below top quartile but `orders_count >= 2` AND last order within 60 days (repeat buyer, still active).
   - **At-Risk** — has at least one `status: "cancelled"` subscription and zero `status: "active"` ones from step 3 (they cancelled/paused and didn't replace it), OR top-quartile spend with last order older than 90 days.
   - **Dormant** — everyone else with `orders_count >= 1` but no order in 180+ days.
5. Render one table per segment (cap 15 rows, sorted by `total_spent` descending) with a next-best-action column:
   - VIP → personal outreach / early access to new drops
   - Growing → nudge toward a subscription if they have no active subscription from step 3
   - At-Risk → win-back offer scoped to what they last bought
   - Dormant → reactivation campaign, or suppress from paid retargeting spend
6. Close with segment sizes and the total lifetime-spend dollars sitting in At-Risk specifically — that's the number the CCO should be watching this week, not the VIP list (which takes care of itself).
