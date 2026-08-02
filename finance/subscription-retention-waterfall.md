---
name: Subscription retention waterfall
description: Break recurring revenue into healthy, at-risk, and lost buckets with dollar impact, and rank the subscriptions worth a manual save.
icon: heart-pulse
---

# Goal

For `{{company.name}}`, build a subscription-revenue retention waterfall as of `{{today}}`: how much recurring revenue is healthy, how much is at risk of failing out, and how much has already churned this period — each bucket sized in dollars — then hand back a ranked save list.

# Steps

1. Call `fluid_api("/api/checkout/v2026-04/subscriptions?limit=100&status=active", "GET")`, paginating until exhausted. Note the top-level `stats` block (`total_count`, `active_count`, `average_order_value`, `churn_rate`) as the baseline. Use `status=active` — the subscription record has no boolean `active` field; filtering with `active=true`/`active=false` 500s with a `PG::UndefinedColumn` error (confirmed live), because the real column backing this is `status` (a string: `"active"`, `"cancelled"`, etc.).
2. Call the same endpoint with `status=cancelled` to pull the cancelled side, same pagination.
3. Bucket every subscription by billing health:
   - **Healthy** — `status: "active"`, `decline_count: 0`, `next_bill_date` in the future.
   - **At risk** — `status: "active"` and (`last_failed_at` is set or `decline_count > 0`) — billing is failing but Fluid hasn't cancelled it yet.
   - **Skipped** — `skipped_count > 0` in the trailing 60 days — not a failure, but a save opportunity.
   - **Lost this period** — `cancelled_at` falls within the last 30 days of `{{today}}`.
4. Sum `price` per bucket for monthly-recurring-revenue-at-stake. Multiply the at-risk and lost totals by 12 for an annualized figure.
5. Rank at-risk + lost subscriptions by `price` descending, take the top 15. For each: the identifying token/customer info on the record, `price`, `decline_count`, `last_failed_at` or `cancelled_at`, and the failing-cycle count.
6. Render: a one-line waterfall (Healthy $X/mo → At risk $Y/mo, N subs → Lost this period $W/mo), the top-15 save-list table, and a **Decision** line naming the single highest-leverage action — e.g. "Recovering the top 5 at-risk subscriptions saves ~$N/mo (~$12N/yr). Dunning retry is available per-subscription via the subscriptions API but this skill does not fire it without your go-ahead."
7. If total subscription count is under 5, say the sample is too small for a reliable churn read and show the raw numbers only, without a save-list ranking.
