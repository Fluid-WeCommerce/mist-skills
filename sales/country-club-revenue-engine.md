---
name: Country Club Revenue Engine
description: Identify your highest-value repeat buyers, score their referral influence, and calculate the incremental revenue a structured affiliate tier would unlock — without any new marketing spend.
icon: zap
---

# Goal

Turn {{company.name}}'s most engaged repeat buyers into a formal affiliate tier. Find who's already buying frequently and referring others organically, project what a structured 10% commission program would cost vs. the incremental orders it would generate, and deliver a prioritized outreach list — more revenue from assets already in the building.

# Steps

1. Paginate `fluid_api("/api/v202506/orders?status=completed&start_date={{thirty_days_ago}}&end_date={{today}}&limit=100", "GET")` fully, following `meta.pagination.next_cursor` until exhausted. For each order capture: `member_id` (or `customer_id`), `amount` (fall back to `amount_in_base`), `created_at`, and `referral_code` if present. Build a per-customer map: order count, total spend, list of any referral codes used.

2. Widen the window: repeat step 1 for the prior 60 days by setting `start_date` to 90 days before `{{today}}` and `end_date` to 31 days before `{{today}}`. Merge into the same per-customer map so you have 90 days of history total. If the API supports a `start_date` parameter, prefer a single 90-day call; if not, merge the two windows.

3. Filter to customers with **3 or more completed orders** across the combined 90-day window. These are proven repeat buyers — not one-time purchasers.

4. For each repeat buyer, call `fluid_api("/api/v2025-06/members/<id>", "GET")` to get `full_name`, `email`, `created_at`, and `enrollment_source`. If the endpoint returns 404 or the ID doesn't resolve to a member record, skip that customer without halting.

5. Estimate referral influence for each customer:
   - **Direct evidence**: count how many orders in your full dataset from steps 1-2 carry a `referral_code` that matches this customer's ID or a code attributed to them. Each such order = a confirmed referred sale.
   - **Proxy signal**: if `enrollment_source` shows they were enrolled via referral (not organic/direct), they are statistically more likely to refer others — flag this with a ★.
   - Score each customer: `(order_count × avg_order_value) + (referred_order_count × avg_order_value × 2)`. The 2× multiplier weights confirmed referral activity above pure purchase volume.

6. Rank the top 20 by score descending. For each compute:
   - **90-day LTV**: total spend across the window
   - **Avg order value**: total spend ÷ order count
   - **Confirmed referrals**: referred orders attributed to them
   - **Projected annual revenue driven**: `avg_order_value × confirmed_referrals × 4` (annualizing the 90-day window)
   - **Estimated annual commission cost**: projected revenue driven × 10%
   - **Net incremental revenue**: projected revenue driven minus commission cost

7. Render a ranked table with columns: **Rank | Name | 90-day Spend | Orders | Confirmed Referrals | Proj. Revenue Driven | Est. Commission | Net Gain**. Sort by Net Gain descending.

8. Below the table, show a portfolio summary:
   - Total net incremental revenue if all top-20 are activated
   - Equivalent paid-media cost to acquire the same volume (ask the user for their CAC, or estimate $45 if unknown): `referred_orders_total × avg_order_value × 4 ÷ avg_order_value × $CAC`
   - The ratio: "This affiliate program costs $X to run and replaces $Y in paid acquisition — a Zx return on affiliate spend."

9. Close with ONE recommendation: the top 5 customers to personally invite to the affiliate tier this week, and a one-sentence pitch for each grounded in their numbers. Example: "Jordan T. drove 4 referred orders worth $240 in 90 days — a 10% commission tier costs $24/year and generates $240 in revenue, a 10× return. Invite them first."

If confirmed referral data is sparse (fewer than 3 customers have any `referral_code` activity), say so plainly — the lack of referral attribution is itself a finding: "You have no visibility into who's referring whom. The highest-leverage first step is issuing unique referral codes to your top 20 buyers this week, then running this skill again in 30 days." Fall back to ranking by purchase frequency only and present that table as the starting outreach list.
