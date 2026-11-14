---
name: Subscriber churn-risk signals
description: Flag customers who cancelled or let a subscription go inactive, ranked by what they were spending, with a save-play scoped to what they last subscribed to.
icon: user-x
---

# Goal

Find every {{company.name}} customer showing a real subscription-churn signal — not a vanity "at risk" score, but customers who verifiably HAD an active subscription and no longer do — and give Customer Experience a save-play scoped to what they actually bought.

The customer record has **no** `active_subscriptions_count`/`inactive_subscriptions_count` field — confirmed live (neither the list nor the single-customer detail endpoint returns anything like it, even for a customer with a real active subscription). The real, verified source is the bulk subscriptions endpoint itself: `fluid_api("/api/checkout/v2026-04/subscriptions?status=<status>&limit=100", "GET")` — it supports a `customer_id` filter and a `status` filter (`active`/`cancelled`/etc, confirmed live), and each row already embeds the full `customer` object (`id`, `total_spent`, `orders_count`, …) and the subscribed `variant.product.title` — no separate per-customer order lookup needed at all.

# Steps

1. Paginate `fluid_api("/api/checkout/v2026-04/subscriptions?status=cancelled&limit=100", "GET")` fully via `meta.pagination`/`page`. For each row, capture `customer.id`, `customer.total_spent`, `customer.orders_count`, `variant.product.title`, `cancelled_at`. Group by `customer.id` — one customer can have dropped more than one subscription.
2. Paginate `fluid_api("/api/checkout/v2026-04/subscriptions?status=active&limit=100", "GET")` fully as well, and build a set of `customer.id` values that still have at least one active subscription.
3. Split the cancelled-subscription customers from step 1 into two risk tiers using the active-customer-id set from step 2:
   - **Churned** — the customer's id is NOT in the active set (no active subscription left at all).
   - **Partial churn** — the customer's id IS in the active set (still has at least one running, but has already dropped others — an early warning, not a full loss yet).
4. Rank both tiers by `customer.total_spent` descending — the highest-LTV churned customers are the highest-priority saves. The dropped product name(s) (`variant.product.title`, deduplicated per customer) are already in hand from step 1 — no extra order-history call needed to scope the save-play.
5. Render two tables (Churned, Partial Churn), each with: customer, total_spent, dropped product(s), orders_count. Cap at 20 rows per tier, highest spend first.
6. Close with a save-play per tier:
   - Churned + high `total_spent` → a personal win-back offer referencing the specific product they dropped
   - Partial churn → a proactive "don't lose this one too" check-in before the remaining subscription lapses
   Total the `total_spent` dollars represented in the Churned tier specifically — that's the number to report up.

If `status=cancelled` returns zero rows for this company, say so plainly rather than reporting an empty churn list as "no risk found" — it may mean subscriptions aren't a product line here yet, not that retention is perfect.
