---
name: Order attribution mix
description: See which touch model (first-touch rep, last-touch rep, enrollment rep) is actually driving completed orders, to know which channel/relationship investment to double down on.
icon: git-branch
---

# Goal

Find out which touch model — first-touch, last-touch, or enrollment relationship — is actually driving completed orders at {{company.name}}, so Marketing knows whether to invest in top-of-funnel discovery content or in the rep/relationship layer.

# Steps

1. Pull the last 30 days of completed orders: `fluid_api("/api/v202506/orders?status=completed&start_date={{thirty_days_ago}}&end_date={{today}}&limit=100", "GET")`, paginating fully via `meta.pagination.next_cursor`.
2. For each order, call `fluid_api("/api/v202506/orders/<order_id>/journey", "GET")`. Capture `attribution_rep`, `attribution_state`, `first_touch_rep`, `last_touch_rep`, `most_touch_rep`, `enrollment_rep`, and the `fairshare_settings` block (`attribution_config`, `order_volume_config`). This is a per-order call — if the order volume is large, sample the top 50 by `amount` rather than calling every single order, and say so in your answer.
3. Tally: % of sampled orders where `attribution_rep` is null (orphaned — no rep gets credit) vs. attributed. Of the attributed ones, tally how often `first_touch_rep` and `last_touch_rep` are the SAME rep (single-touch, direct conversion) vs. different reps (a multi-touch journey where someone else opened the door).
4. Cross-reference the company's `attribution_config` (from `fairshare_settings`, e.g. `last_touch`) against the actual data — if the configured model rarely matches which rep would "deserve" credit under a different model (e.g. most conversions are multi-touch but the config is `last_touch`), that's a policy mismatch worth flagging to the CRO/CMO jointly, not just an FYI stat.
5. Render: an orphaned-orders %, a single-touch vs multi-touch split, and a one-paragraph read on whether the current attribution config matches the real behavior in the data.
6. Close with ONE recommendation: e.g. "attribution is mostly single-touch — top-of-funnel discovery content isn't the bottleneck, relationship-closing content is" or "a large multi-touch share isn't reflected in the current last-touch-only config — first-touch reps are doing the discovery work and getting under-credited."
