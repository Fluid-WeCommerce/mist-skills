---
name: Reward points liability report
description: Close the month on reward points — what customers earned, spent and got back on refunds, what the unspent balance is worth in each currency, and which markets or refunds need fixing before the books close.
icon: coins
---

# Goal

Give {{company.name}}'s finance team a month-end reward points schedule for the most recently completed calendar month before {{today}} (or the month the user names). Every point a customer holds is a promise to give product or money off later, so the company carries the unspent balance as a liability. This report gives finance the figures and the method behind them. Choosing an accounting treatment is left to the user's accountant.

The report covers:

1. **Activity in the month:** points earned on orders, points spent at checkout, spent points returned by refunds, and earned points that refunds couldn't take back.
2. **Unspent balance:** the points customers still hold, and their cash value in the primary currency.
3. **Setup gaps:** markets where points have no value, so customers there can't spend them and finance can't value them.
4. **Spend rate and reward cost:** how the month compares with the two months before it.

# Rules

- **Read only.** This skill changes nothing: no points values, settings or balances. If a fix is needed, say what to change and where in Fluid's admin, and leave it to the user.
- **Label every figure** as *read* (taken straight from Fluid), *computed* (added up from Fluid records) or *estimated* (partly assumed), and name the period. Never present an all-time figure as a monthly one.
- **Value points with the right currency.** Each currency has its own points value. A currency with no value gets no cash figure. Write "not valued" instead of guessing.
- **Plain words in the chat.** Name currencies, countries and months. Don't show ids, paths or JSON. Name customers only in the reconciliation sample, and only by first name.
- No accounting or tax conclusions. Give the quantities and the method, and say the treatment is the user's or their accountant's call.

# Steps

## 1. Check the program is on and set the window

1. `fluid_api("/api/settings/checkout", "GET")`. If `reward_points_enabled` is false, say in one line that reward points are off, so there is nothing to report, and stop. Otherwise keep `reward_points_label_plural` (what customers call points: use that word in the report) and `reward_points_apply_to_subtotal`.
2. Set `<start>` and `<end>` to the first and last day of the previous calendar month relative to {{today}}, unless the user named a month. Also set the two months before it for comparison.

## 2. Read the points values

`fluid_api("/api/v202506/points_values?per_page=100", "GET")`. For each row keep `currency_code`, `configured`, `worth_of_100_points.amount`, `worth_of_100_points.home_amount` and `unavailable_reason`. Keep `primary_currency` and `primary_currency_data`.

- The **value of one point** in a currency is `worth_of_100_points.amount ÷ 100`. In the primary currency it is `home_amount ÷ 100`.
- Every row with `configured: false` or a null `amount` is a **setup gap**. Then `fluid_api("/api/company/v2026-10/markets", "GET")` and name the markets that sell in that currency.
- If two configured currencies' `home_amount` values differ by more than 10%, note it. It may be deliberate, but finance should know a point is worth more in one market than another.

## 3. Add up the month's earn and spend

`fluid_api("/api/v202506/orders?start_date=<start>&end_date=<end>&page[limit]=100", "GET")`. Follow `meta.pagination.next_cursor` as `page[cursor]` until it is null. Leave out orders whose `status` is `draft`, `cancelled` or `archived`. For every other order keep `id`, `currency_code`, `total_points_credited`, `points_applied`, `points_applied_amount_in_currency` and `financial_status`.

Per currency, compute:

- **Points earned** = the sum of `total_points_credited`.
- **Points spent** = the sum of `points_applied`. Their **cash value** = the sum of `points_applied_amount_in_currency`, which is what the order actually took off.
- **Orders that spent points** as a share of all orders.

Run the same pull for each of the two comparison months, keeping only these totals.

## 4. Refunds that moved points

Refunds in the month can belong to orders sold earlier. Pull orders from 90 days before `<start>` to `<end>` the same way, and keep those whose `financial_status` mentions `refunded` and that earned or spent points. For each one, `fluid_api("/api/v202506/orders/<id>", "GET")` and read its `refunds`. Keep only refunds whose `created_at` falls between `<start>` and `<end>`. When a refund carries no `created_at`, use the dates of that order's refund entries in the customer's points ledger (step 6 shows the call).

- **Spent points returned:** each refund's `points_restored`. If it is absent, use the order's `points_refunded` flag together with the ledger's `order_refund` entries for that order.
- **Earned points not taken back:** `points_reclaim_shortfall` on each refund. These are points the customer earned on the order and spent before the refund, so the company gave value it couldn't recover. List the orders, the points and their value. Three or more for one customer is a pattern worth a look.

## 5. Estimate the unspent balance

Fluid keeps a balance for each customer, not one company-wide total, so build the total from the customers who hold points.

1. **Who might hold points:** every customer on an order in the last 12 months with `total_points_credited` or `points_applied` above zero. Pull those orders as in step 3 and keep each `customer.id`, deduplicated.
2. **Read balances:** for each of those customers, `fluid_api("/api/v2025-06/customers/<id>", "GET")` and keep `points_decimal`. If there are more than 2,000 customers, read the 500 with the most points activity plus a random 500 of the rest, scale the random sample up to the rest, and mark the total *estimated* with the method.
3. **Total unspent** = the sum of balances (*computed* when every customer was read, *estimated* when sampled). **Cash value** = total × the primary currency's value of one point. Also give it in each configured currency where customers are concentrated, if the user asks.
4. **Coverage gap:** customers whose last points activity is older than 12 months aren't read. Say so in one line with the date cut-off. Finance may want a one-off full read before year end.
5. **Concentration:** the share of the unspent total held by the top 1% of holders, and the share held by customers with no order in the last 180 days.

## 6. Reconcile a sample

Pick 5 customers: the 3 largest holders and 2 random ones. For each one, `fluid_api("/api/v2026-10/customers/<id>/points-ledgers?per_page=100", "GET")`, then:

- Check that the newest entry's `total_balance_decimal` matches the balance read in step 5.
- Within the month, total the entries by `metadata.transaction_type` (`order_credit`, `order_redemption`, `order_refund`, `order_refund_deduction`, `adjustment` and the rest) and compare them with that customer's orders from step 3.
- List any `adjustment` entries in the month with their `reason`. Large manual adjustments belong in the report.

Report each customer as matched, or as off by an amount with the likely reason. A mismatch is a finding, not a failure of the report.

## 7. Report

Lead with one line: the unspent balance and its value at month end, and how much it grew or shrank during the month.

Then:

- **Roll-forward table, per currency:** earned, spent, spent points returned by refunds, earned points not taken back, and net change, in points and cash value. Note: the roll-forward covers order activity and refunds. Manual adjustments appear only for the sample, so the net change won't exactly match the change in balances. Say so in one line.
- **Unspent balance:** the total in points and primary-currency value, how it was built (*computed* or *estimated*, with coverage), and concentration.
- **Spend rate:** points spent ÷ points earned, for this month and the two before. **Reward cost:** the cash value of points spent as a share of the month's sales in that currency.
- **Needs fixing:** markets with no points value, a large gap in point value between markets, refunds that left earned points behind, unexplained manual adjustments, and sample mismatches. Each comes with the one change that fixes it.
- **For the accountant:** the period, the method, and every figure labeled *read*, *computed* or *estimated*. Offer to save the report as a Markdown file in the project for the month's close folder.
