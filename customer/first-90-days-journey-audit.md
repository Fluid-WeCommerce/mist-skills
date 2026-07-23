---
name: First-90-days journey audit
description: Audit whether new customers are coming back — repeat-purchase and subscription-conversion rates by weekly cohort, plus what single-order customers actually bought.
icon: calendar-check
---

# Goal

Audit the first-90-days experience for {{company.name}}'s newest customers — is the second purchase happening, and if not, where does the relationship stall?

# Steps

1. Call `fluid_api("/api/v2025-06/customers?sort=-created_at&limit=100", "GET")`, paginating fully, and filter client-side to `created_at` within the last 90 days of {{today}}.
2. For each, read `orders_count`, `active_subscriptions_count`, `inactive_subscriptions_count` — already present on the list payload, no extra call needed.
3. Compute the repeat-purchase rate: % of this cohort with `orders_count >= 2`. Compute the subscription-conversion rate: % with `active_subscriptions_count >= 1`.
4. Split the cohort by the calendar week of `created_at` and compute both rates per week — a trend line, not a single snapshot, so you can see whether onboarding is improving or degrading week over week.
5. Take a sample of 10 single-order customers (`orders_count == 1`) whose account is 30+ days old (past the point a normal reorder would land). For each, call `fluid_api("/api/v202506/customers/<id>/orders?limit=1", "GET")` to see what they bought — is it a naturally-repeating consumable, or a one-time/gift-style item that wouldn't be expected to reorder?
6. Render: a weekly cohort table (week, repeat-purchase rate, subscription-conversion rate), and a short breakdown of what the single-order sample actually bought (by product category/title if discernible from `first_item.title`).
7. Close with ONE lever: e.g. "customers whose first purchase is `<category>` almost never come back — test a day-21 follow-up offer for that category specifically" or "reorder rate is fine but subscription conversion is flat — push the auto-ship option harder at checkout, that's the bigger lift."
