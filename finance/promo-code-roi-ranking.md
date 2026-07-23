---
name: Promo code ROI ranking
description: Rank every active promo code by margin-aware ROI, not just redemption volume, and flag codes to kill.
icon: percent
---

# Goal

Rank every discount code at `{{company.name}}` by the revenue it actually drove per dollar of discount given up — not just order count — over the last 90 days ending `{{today}}`, and call out which codes are worth keeping, tightening, or killing.

# Steps

1. Call `fluid_api("/api/v2025-06/discounts?limit=100", "GET")`, paginating until exhausted. Keep `code`, `discount_type`, `active`, `apply_to_subscriptions`, `customer_usage_limit`, `end_date`, `country_codes`.
2. For each **active** code, call `fluid_api("/api/v202506/orders?filter[promo_code]=<code>&filter[created_at_gte]=<90-days-ago>&limit=100", "GET")`, paginating until exhausted. Skip a code after two consecutive empty pages if it clearly has zero usage — don't burn calls chasing a dead code across 100 pages.
3. Per code, compute:
   - Order count and gross revenue (`sum(amount)`).
   - Estimated discount cost — for percentage-type discounts, revenue × (rate / (1 − rate)) approximates the pre-discount price given up; for fixed-amount discounts, multiply the fixed amount by order count. Note which method was used per code.
   - **ROI** = gross revenue ÷ estimated discount cost. Higher is better; below ~3x is a code likely costing more than it's worth once payment processing and fulfillment cost are factored in.
   - Average order value for orders using the code, compared against the account-wide AOV (pull once via `orders/stats` → `average_amount_base`) — a code with a lower AOV than baseline is discounting sales that might have happened anyway.
4. Rank all codes with nonzero usage by ROI descending. Flag any code with `end_date` in the past that's still `active: true` — a stale code nobody remembered to retire is free money leaking out.
5. Render a table: code, order count, revenue, estimated discount cost, ROI, AOV vs. baseline delta. Follow with:
   - **Keep** — top ROI codes, worth promoting harder.
   - **Tighten or kill** — codes below the 3x ROI line, especially any with AOV below baseline.
   - **Stale/expired but still live** — the housekeeping list.
6. End with a **Decision**: name the single lowest-ROI code with meaningful volume and state the dollar cost of leaving it running unchanged for another 90 days at the current pace.
