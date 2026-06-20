---
name: Promo code summary
description: Summarize orders that used a given promo code over the last 30 days.
icon: receipt
---

# Goal

Pull every order at `{{company.name}}` that used a given promo code in the last 30 days and produce a tight summary.

# Steps

1. Ask the user which promo code to summarize (default: `SUMMER10` if the user doesn't say).
2. Call `fluid_api("/api/v202604/orders?filter[promo_code]=<code>&filter[created_at_gte]={{thirty_days_ago}}&limit=100", "GET")`. Follow cursor pagination until you've collected every matching order.
3. From the results, compute:
   - Total order count
   - Gross revenue (`sum(total_cents) / 100`)
   - Average order value
   - Top 5 customers by spend
   - Day-by-day order count (sparkline-style)
4. Render as a Markdown table. Don't include raw JSON in the response unless the user asks.
5. If zero orders match, say so plainly and suggest checking the code spelling.
