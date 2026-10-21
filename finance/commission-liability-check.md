---
name: Commission liability check
description: Reconcile estimated commission payout against revenue for the period and flag liability creep before it hits payroll.
icon: scale
---

# Goal

Estimate the commission liability `{{company.name}}` is carrying for the most recently completed calendar month relative to `{{today}}`, compare it against the prior month as a share of revenue, and flag any product or category driving liability creep.

# Steps

1. Compute the date window: first and last day of the previous calendar month, and the same window for the month before that (for the comparison).
2. Call `fluid_api("/api/v202506/orders?status=completed&start_date=<start>&end_date=<end>&limit=100", "GET")` for both months, paginating via `meta.pagination.next_cursor` until exhausted. Use `start_date`/`end_date` — `filter[created_at_gte]`/`filter[created_at_lte]`-style bracket params are silently ignored by this endpoint (no error, it just returns the unfiltered set), so don't use them. Keep `amount`, `first_item`. If `meta.pagination` comes back as `{}`, that month had zero completed orders — treat it as $0 revenue/commission for that month rather than skipping it.
3. Call `fluid_api("/api/company/v1/products?per_page=100", "GET")`, paginating until exhausted, and build a lookup of `product title → commission` (percent). Note: this is the storefront-facing commission rate, not a guarantee it matches the payroll engine's actual payout rule — call that out in the report rather than presenting it as authoritative.
4. For each order in each month, estimate commission owed = `amount × (commission / 100)` using the matching product's rate (fall back to the account-wide average commission rate for line items that don't match a known product, and say how many fell into that bucket).
5. Compute per month: total revenue, total estimated commission, commission as a % of revenue. Compare the two months — flag **liability creep** if commission-as-%-of-revenue rose more than 1.5 points month over month, since that's payout growing faster than sales.
6. Break out the current month's estimated commission by product category (using the product lookup's category field) and surface the top 5 categories by commission dollars — this is where a payout-structure change would land hardest.
7. Render: a two-month comparison table (revenue, estimated commission, % of revenue), the top-5-category breakdown, and a **Decision**: state plainly whether liability is trending up or flat/down, the dollar delta month over month, and — if creeping — which category to review first.
