---
name: Subscriber churn-risk signals
description: Flag customers who cancelled or let a subscription go inactive, ranked by what they were spending, with a save-play scoped to what they last subscribed to.
icon: user-x
---

# Goal

Find every {{company.name}} customer showing a real subscription-churn signal — not a vanity "at risk" score, but customers who verifiably HAD an active subscription and no longer do — and give Customer Experience a save-play scoped to what they actually bought.

There is no bulk subscriptions-list endpoint in Fluid's admin API today (only a per-customer subscription count and an async CSV export exist) — this skill is built entirely on what's verifiably there: `active_subscriptions_count` / `inactive_subscriptions_count` on the customer record, cross-referenced with their order history.

# Steps

1. Paginate `fluid_api("/api/v2025-06/customers?sort=-created_at&limit=100", "GET")` fully. Filter client-side to customers where `inactive_subscriptions_count > 0` — this is a real signal (they had at least one subscription that is no longer active), not an inference.
2. Split that filtered set into two risk tiers:
   - **Churned** — `active_subscriptions_count == 0` AND `inactive_subscriptions_count > 0` (no active subscription left at all).
   - **Partial churn** — `active_subscriptions_count > 0` AND `inactive_subscriptions_count > 0` (still has at least one running, but has already dropped others — an early warning, not a full loss yet).
3. For each customer in both tiers, call `fluid_api("/api/v202506/customers/<id>/orders?limit=5&sort=-created_at", "GET")` and look at the `subscription` field and `created_subscriptions` array on their recent orders to identify what product(s) they were subscribed to — this is what the save-play needs to be scoped to, a generic "come back!" offer performs far worse than one naming the actual product.
4. Rank both tiers by `total_spent` (from the customer record) descending — the highest-LTV churned customers are the highest-priority saves.
5. Render two tables (Churned, Partial Churn), each with: customer, total_spent, last known subscribed product(s), orders_count. Cap at 20 rows per tier, highest spend first.
6. Close with a save-play per tier:
   - Churned + high `total_spent` → a personal win-back offer referencing the specific product they dropped
   - Partial churn → a proactive "don't lose this one too" check-in before the remaining subscription lapses
   Total the `total_spent` dollars represented in the Churned tier specifically — that's the number to report up.

If `inactive_subscriptions_count` is null/undefined across the whole customer set (subscription tracking not populated for this company), say so plainly rather than reporting an empty churn list as "no risk found."
