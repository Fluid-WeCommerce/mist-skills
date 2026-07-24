---
name: Stalled order revenue recovery
description: Rank orders stuck in draft/pending/pending_review by recoverable revenue and win probability, and hand over a call list.
icon: shopping-cart
---

# Goal

Find every stalled order at {{company.name}} sitting in `draft`, `pending`, or `pending_review` — the closest proxy to an "abandoned cart" the admin API exposes — rank it by recoverable revenue and win probability, and hand the CRO a call list instead of a data dump.

# Steps

1. For each of `draft`, `pending`, `pending_review`, call `fluid_api("/api/v202506/orders?status=<status>&start_date={{thirty_days_ago}}&end_date={{today}}&limit=100", "GET")`, following `meta.pagination.next_cursor` until it's null. `limit` may not be strictly honored — keep paginating by cursor, not by counting rows.
2. From each stalled order capture: `order_number`, `customer.full_name`, `customer.email`, `amount` (fall back to `amount_in_base` if `amount` is zero/blank), `created_at`, `status`, `source`, and `customer.orders_count` (tells you if this is a first-time or repeat buyer).
3. Compute a win-probability tier per order:
   - **High** — created in the last 24 hours AND `customer.orders_count > 0` (a proven buyer, still warm).
   - **Medium** — created in the last 7 days (any buyer).
   - **Low** — older than 7 days, OR a first-time buyer (`orders_count == 0` counting only completed history) who never converted once — weaker signal, still worth a lighter-touch nudge.
4. Sort by `amount` descending within each tier. Render one Markdown table per tier: customer, amount, days stalled, order number, source.
5. Total the recoverable revenue across all three tiers, and call out the **High**-tier subtotal separately — that's the number worth acting on this week.
6. Close by offering to draft recovery emails/SMS copy for the High tier only. Do NOT send or dispatch anything — no send tool exists for this in Mist Desktop; hand back the drafted copy for the user to use in their own outreach channel.

If a status returns zero orders across the whole window, say so plainly per status rather than omitting the row — a clean checkout with nothing stalled is itself useful signal.
