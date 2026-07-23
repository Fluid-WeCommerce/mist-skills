---
name: Failed-payment recovery pipeline
description: Quantify the dollars sitting behind declined and error-rate payments this period, and propose a dunning-first recovery order.
icon: credit-card
---

# Goal

Give `{{company.name}}` a dollars-and-cents view of payment failures over the last 30 days ending `{{today}}`, and a recovery order so cash gets chased where it matters most first.

# Steps

1. Call `fluid_api("/api/v202506/payments/reports/kpis?period=last_30_days", "GET")`. Read `kpis.approval_rate` and `kpis.error_rate`, each with `current`/`previous`/`growth`. This is the trend line: is approval health improving or degrading period over period.
2. Call `fluid_api("/api/v202506/payments/reports/transaction_volume?period=last_30_days", "GET")` and `.../transaction_amount?period=last_30_days` for the same window, so failure rates can be translated into dollars, not just percentages.
3. Pull the declined/error transaction detail: `fluid_api("/api/v202506/transactions?status=declined&limit=100", "GET")`, paginating until exhausted, then repeat with `status=error`. (`/api/payment/v2026-04/transactions` is not a real path — it happens to return `200 {"data":[]}` for any query, which reads as "no results" rather than a 404, so don't use it; the real transactions listing lives at `/api/v202506/transactions`.) This endpoint has no server-side date filter, so sort by the most recent first and stop paginating once `created_at` falls outside the last 30 days — don't rely on `limit` alone to bound the window. For each row, keep `amount` (already a dollar-denominated string, e.g. `"110.0"` — NOT cents), `payment_account.name` (the gateway/processor), `action`, `created_at`, `card_id`.
4. Cross-reference against subscriptions in trouble: `fluid_api("/api/checkout/v2026-04/subscriptions?limit=100&status=active", "GET")`, filter to rows with `decline_count > 0` or `last_failed_at` set — these are recurring-revenue dollars actively at risk, not one-off cart declines. Use `status=active`, not `active=true` — the latter 500s with a `PG::UndefinedColumn` error (confirmed live; the underlying column is `status`, there is no boolean `active` column on subscriptions).
5. Compute:
   - **Total $ at risk this period** — sum of declined transaction `amount` (dollars) + sum of `price` across past-due subscriptions.
   - **Approval-rate delta** — `current - previous` from step 1, called out as improving/worsening.
   - **Recovery-priority list** — the 15 largest-dollar declines/past-due subscriptions, sorted by amount descending, each tagged with a suggested action: "retry now" (single recent decline, card likely still valid), "update payment method" (2+ consecutive declines), or "manual outreach" (subscription past-due 14+ days).
6. Render a summary (total at risk, approval-rate trend) followed by the recovery-priority table, ending with a **Decision**: the dollar amount recoverable if the top 5 priority items convert, and which action type dominates the list (retry vs. update-payment-method vs. manual outreach) so the team knows where to focus this week.
7. If `payments/reports/kpis` or the transactions endpoint returns no data for the period, say so plainly rather than reporting a zero that reads as "all clear."
