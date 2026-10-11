---
name: Promo code summary
description: Summarize orders that used a given promo code over the last 30 days.
icon: receipt
---

# Goal

Pull every order at `{{company.name}}` that used a given promo code in the last 30 days and produce a tight summary.

# Steps

1. Ask the user which promo code to summarize (default: `SUMMER10` if the user doesn't say).
2. Confirm the code exists: `fluid_api("/api/v2025-06/discounts?search_query=<code>&per_page=100", "GET")` and find the exact `code` (case-insensitive). Its `total_usage` is the all-time redemption count — a useful cross-check.
3. The order API has no promo-code filter, and its list rows carry no discount codes. List the window's orders with `fluid_api("/api/v202604/orders?filter[start_date]={{thirty_days_ago}}&filter[end_date]={{today}}&page[limit]=100", "GET")`, passing `meta.pagination.next_cursor` back as `page[cursor]` until it is null. Then read each order's `discount_codes` from `fluid_api("/api/v202506/orders/<id>", "GET")` and keep the orders that include the code. If that is more than a few hundred detail calls, tell the user the count before you continue.
4. From the matching orders, compute:
   - Total order count
   - Gross revenue (sum of `amount_in_base`, in the company's base currency)
   - Average order value
   - Top 5 customers by spend
   - Day-by-day order count (sparkline-style)
5. Render as a Markdown table. Don't include raw JSON in the response unless the user asks.
6. If zero orders match, say so plainly and suggest checking the code spelling.
