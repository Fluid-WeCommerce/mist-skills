---
name: Checkout funnel diagnosis
description: Diagnose where the cart-to-completed-order funnel is leaking using order-status buckets and payment approval trends, with a fix recommendation.
icon: filter
---

# Goal

Diagnose where {{company.name}}'s checkout funnel is leaking — from cart creation through payment to a completed order — and recommend the single highest-leverage fix. Fluid's admin API doesn't expose a step-by-step page/cart-event funnel, so this uses the two most granular signals it DOES expose: order lifecycle status, and payment approval health.

# Steps

1. Pull the order-status distribution for the last 30 days ({{thirty_days_ago}} to {{today}}). For each status in `draft`, `pending`, `pending_review`, `processing`, `completed`, `cancelled` (skip `archived` — it's cold storage, not funnel signal), call:
   `fluid_api("/api/v202506/orders?status=<status>&start_date={{thirty_days_ago}}&end_date={{today}}&limit=1", "GET")`
   and read `meta.pagination.total_count` for each. Note: `limit` is not strictly honored by this endpoint (you may get more rows back than asked) — never infer a count from the returned array length, always read `total_count`. If `meta.pagination` comes back as `{}` (empty), treat that status's count as 0.
2. Compute the completion rate: `completed / (draft + pending + pending_review + processing + completed + cancelled)`. Compute the cancellation rate the same way with `cancelled` in the numerator. This status distribution is your cart→complete proxy funnel.
3. Pull the payment layer: `fluid_api("/api/v202506/payments/company_reports/kpis?period=last_30_days", "GET")`. The `period` param only accepts `last_24_hours`, `last_7_days`, `last_30_days`, `last_month`, `last_year`, or `custom` — don't invent other values. Read `approval_rate`, `error_rate`, and `average_latency_ms`, each with `current`/`previous`/`growth.percent`.
4. Also call `fluid_api("/api/v202506/payments/company_reports/approval_rate?period=last_30_days", "GET")` for the daily `data_points` (each with `breakdown.approved`/`breakdown.declined`). Scan for any single day whose decline share spikes well above the period average — that's a specific incident (processor blip, a bad release), not a trend.
5. Pull `fluid_api("/api/v202506/orders/stats", "GET")` for `average_amount_base` — you'll need it in step 7 to put a dollar figure on the leak.
6. Cross-reference the two layers:
   - Approval rate healthy (>90%) but a large draft/pending/pending_review share → the leak is upstream of payment (cart UX, shipping-cost surprise, missing payment methods for the customer's country). Point this at Marketing/Dev, not Payments.
   - Approval rate degraded or trending down (negative `growth.percent`) → the leak IS at the pay step. Point this at a payment-method/processor review.
7. Render two Markdown tables: the status distribution (status, count, % of total) and the payments KPI table (metric, current, previous, growth %). Then a one-paragraph "## Where the leak is" naming the single worst stage, its estimated dollar impact (`stage order count × average_amount_base`), and ONE concrete next step.

Be explicit in your answer that the status-bucket funnel is the best available proxy, not a true page-by-page funnel — Fluid doesn't expose cart-abandonment events at the admin-API level today.
