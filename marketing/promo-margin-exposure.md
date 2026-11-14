---
name: Promo margin exposure audit
description: Rank active promo codes by usage and discount depth to flag margin-eroding codes and dead codes before the next planning cycle.
icon: percent
---

# Goal

Audit every active promo code at {{company.name}} for margin exposure — which codes are driving volume at a healthy discount depth, and which are quietly eroding margin — so Marketing can prune before the next planning cycle.

# Steps

1. Call `fluid_api("/api/v2025-06/discounts?active=true&limit=100", "GET")`, paginating via `page`/`per_page` if `meta.pagination.total_pages` > 1. Also call with `active=false` to see the recently-expired set for a shelf-life comparison.
2. For every discount record `code`, `name`, `price_discount_type` (`flat`/`percentage`/`free_product`/`free_shipping`), `price_discount_amount` or `price_discount_percent`, `total_usage`, `source` (this endpoint only returns `source: promo` codes, not manual discounts — say so if the user expects manual codes too), `start_date_time`/`end_date_time`, `has_end_date`, `apply_to_subscriptions`.
3. Classify each **active** code:
   - **Margin-erosion watchlist** — `total_usage` in the top quartile of the active set AND discount depth that's steep (`percentage` type above ~20%, or a `flat` amount that's a large fraction of a typical order).
   - **Healthy** — meaningful usage, shallow depth.
   - **Runs forever** — `has_end_date: false` with any usage — no deliberate sunset date was ever set.
   - **Dead code** — live for 14+ days (`start_date_time` old enough) with `total_usage` at or near zero — candidate to retire outright.
4. Render a Markdown table sorted by `total_usage` descending: code, discount type/depth, total_usage, flag from step 3.
5. Close with a "## Prune list" section — the specific codes to sunset, tighten, or retire this week, and the one-line reason (usage + depth numbers, not a vibe).

**Known gap**: this endpoint doesn't expose per-order attribution, so "which promos bring in NEW customers vs. just discount existing ones" isn't verifiable from `/discounts` alone (no `orders` filter by promo code was found in the admin API). State this gap explicitly instead of fabricating a new-vs-existing split — if the user wants that depth, offer to pull the raw completed-order set for the window and manually match against known code patterns (e.g. `first_item`/email) as a manual follow-up, not a guaranteed exact match.
