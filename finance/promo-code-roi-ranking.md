---
name: Promo code ROI ranking
description: Rank every active promo code by margin-aware ROI, not just redemption volume, and flag codes to kill.
icon: percent
---

# Goal

Rank every discount code at `{{company.name}}` by the revenue it actually drove per dollar of discount given up — not just order count — over the last 90 days ending `{{today}}`, and call out which codes are worth keeping, tightening, or killing.

# Steps

1. Call `fluid_api("/api/v2025-06/discounts?limit=100", "GET")`, paginating until exhausted. Keep `code`, `discount_type`, `price_discount_type`, `price_discount_percent`, `price_discount_amount`, `active`, `total_usage`, `apply_to_subscriptions`, `customer_usage_limit`, `end_date`, `country_codes`.
2. **There is no working way to filter orders by promo/discount code.** The orders API's documented filters are `status`, `type`, `customer_id`, `user_company_id`, `subscription_id`, `start_date`/`end_date`, `country_isos`, `order_number` — no promo/discount-code param exists, and the generic `search` param is explicitly order/customer-identity only (order number, email, name, phone), not discount codes. `filter[...]`-bracket params of any kind are silently ignored by this endpoint (no error — it just returns the unfiltered set), so don't reach for that syntax anywhere in this skill. Per-order discount info (`discount_codes`) only exists on the single-order detail endpoint, not the list, so cross-referencing every code against real per-order revenue would mean an individual `GET` per order across the whole 90-day window — not viable at any real order volume. Given that, this skill computes an **estimate**, not a per-code tie-out, and says so plainly in the report:
   - Pull the account-wide average order value once via `fluid_api("/api/v202506/orders/stats", "GET")` → `average_amount_base`.
   - Per code, estimate revenue driven = `total_usage × average_amount_base`. This assumes a code's redemptions look like an average order — call that assumption out next to the number, don't present it as measured.
3. Per code, compute:
   - Estimated revenue (from step 2) and order count (`total_usage`).
   - Estimated discount cost — for percentage-type discounts (`price_discount_type: "percentage"`, `price_discount_percent` as a 0-100 number), estimated revenue × (rate / (1 − rate)) approximates the pre-discount price given up; for flat discounts (`price_discount_type: "flat"`, use `price_discount_amount`), multiply the flat amount by `total_usage`. Note which method was used per code.
   - **ROI** = estimated revenue ÷ estimated discount cost. Higher is better; below ~3x is a code likely costing more than it's worth once payment processing and fulfillment cost are factored in.
   - Skip the AOV-vs-baseline comparison from earlier drafts of this idea — it requires real per-code order data, which isn't available (see step 2). Don't fabricate it.
4. Rank all codes with nonzero `total_usage` by ROI descending. Flag any code with `end_date` in the past that's still `active: true` — a stale code nobody remembered to retire is free money leaking out.
5. Render a table: code, `total_usage`, estimated revenue, estimated discount cost, ROI — label the revenue/ROI columns "estimated" in the header, not as measured fact. Follow with:
   - **Keep** — top ROI codes, worth promoting harder.
   - **Tighten or kill** — codes below the 3x ROI line.
   - **Stale/expired but still live** — the housekeeping list.
6. End with a **Decision**: name the single lowest-ROI code with meaningful volume and state the estimated dollar cost of leaving it running unchanged for another 90 days at the current pace. Note plainly that this is directional (built on `total_usage × average order value`, not real per-code revenue) and best used to prioritize which 2-3 codes are worth a manual look, not as an exact P&L number.
