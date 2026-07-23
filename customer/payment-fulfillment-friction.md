---
name: Payment & fulfillment friction audit
description: Surface payment-decline spikes and the unfulfilled-order backlog — the two verified signals that map directly to support tickets — since bulk refund/return-reason data isn't exposed by the admin API.
icon: life-buoy
---

# Goal

Surface the payment and fulfillment friction actually reaching {{company.name}}'s customers right now, using the two signals the admin API verifiably exposes: payment-decline trends and the unfulfilled-order backlog. (There is no bulk refunds/returns endpoint in Fluid's admin API today — say so plainly if the user is expecting a returns-reason breakdown, rather than fabricating one.)

# Steps

1. Call `fluid_api("/api/v202506/payments/company_reports/error_rate?period=last_30_days", "GET")` and `fluid_api("/api/v202506/payments/company_reports/approval_rate?period=last_30_days", "GET")` — the `period` param only accepts `last_24_hours`, `last_7_days`, `last_30_days`, `last_month`, `last_year`, `custom`. Both return a `data_points` array with daily `breakdown.approved`/`breakdown.declined`.
2. Compute the trailing 30-day average decline share, then flag any single day whose decline share is well above that average — a spike customers definitely noticed (a processor blip, a bad deploy, a new bank's fraud filter).
3. Pull the fulfillment side: `fluid_api("/api/v202506/orders?status=completed&start_date={{thirty_days_ago}}&end_date={{today}}&limit=100", "GET")`, paginating fully via `meta.pagination.next_cursor`. There's no bulk filter by `fulfillment_status`, so tally it client-side from the `fulfillment_status` field on each returned order (`fulfilled`/`unfulfilled`/`partial`).
4. For every `unfulfilled` order, compute days-since-`created_at`. Anything sitting unfulfilled for longer than your company's normal ship SLA (ask the user if unknown, default assumption: 5 business days) is backlog — the kind of thing generating "where's my order" support tickets right now.
5. Render: a payment-decline trend table with the worst day called out, and a fulfillment-backlog table (customer, order_number, days unfulfilled) sorted oldest-first.
6. Close with ONE recommendation: e.g. "12 orders sitting unfulfilled averaging 9 days old — that's this week's support-ticket source, work the backlog before running new promos" or "decline rate spiked on `<date>` specifically — flag it to the payment processor before it recurs."
