---
name: Enrollment kit scorecard
description: Judge each enrollment kit by what happens to the reps who join with it — reorders, autoship, refunds and who is still active 30, 60 and 90 days later — so you keep the kits that build a field and fix the ones that only sell a box.
icon: package-check
---

# Goal

Score every enrollment kit {{company.name}} sells by the reps it produces, not by how many it sells. A kit that sells well but whose buyers never order again, ask for refunds or go quiet within a month is costing the company reps, and in direct selling it is also the pattern regulators read as people paying to join rather than buying to use or sell. This skill follows one group of new reps from their enrollment order through their first 90 days, compares the kits side by side, and ends with one recommendation per kit. It reads only; it changes nothing.

# Rules

- **Read only.** Every call in this skill is a `GET`. Don't edit kits, prices or members; the hand-over lists what the user may want to change.
- **A mature group.** Score people who joined between 180 and 91 days before {{today}}, so every one of them has had a full 90 days. The user may pick another window; say plainly when a group is younger than 90 days.
- **Small kits are not verdicts.** A kit with fewer than 20 enrollments in the window gets its numbers shown but no verdict.
- **Talk in plain words.** Name kits and markets. Refer to people by first name only, and only in the follow-up list. No ids, paths or JSON in the chat.
- **No accusations.** A kit or sponsor pattern that looks like people buying to qualify is a question for the owner, not a finding against anyone. Point to the `compliance/inventory-loading-check` skill where the catalog has it.

# Steps

## 1. Learn the company's kits and rep types

1. `fluid_api("/api/v2025-06/member-types", "GET")` and keep the slugs that are reps (not shoppers or customers). If it isn't clear, ask the user once with a `steps` panel.
2. `fluid_api("/api/v202604/company/enrollment-packs", "GET")`, following the pagination, then `fluid_api("/api/v202604/company/enrollment-packs/<id>", "GET")` for each. Keep the kit's title, status, the markets it is sold in, its price per market, and what it holds (`member_enrollable_products` and `subscription_enrollable_products`), including whether it starts an autoship.

## 2. Collect the enrollment orders

1. `fluid_api("/api/v2/orders?type=enrollment_order&start_date=<MM/DD/YYYY, 180 days before {{today}}>&end_date=<MM/DD/YYYY, 91 days before {{today}}>&per_page=100&page=1", "GET")`, then the next `page` until `meta.next_page` is empty. Dates are month/day/year.
2. For each order keep `id`, `order_number`, `created_at`, `order_status`, `financial_status`, `enrollment_pack_id`, `enrollment_member_type`, `resulting_member_type`, `total` and `currency_code`.
3. Split them into **finished** (`order_status` `completed` or `processing`) and **didn't finish** (`draft`, `pending`, `pending_review`, `cancelled`). Count the second group per kit; it is the kit's drop-off, not part of the scorecard.
4. If there are more than 1,000 finished enrollments, score a sample: up to 150 per kit, spread across the window. Say it is a sample.

## 3. Follow each new rep for 90 days

For each finished enrollment in the scorecard:

1. `fluid_api("/api/v202506/orders/<id>", "GET")` for the buyer's email and the order's `created_subscriptions`.
2. `fluid_api("/api/v2025-06/members/find?email=<email>", "GET")` for the member, then `fluid_api("/api/v2025-06/members/<member_id>", "GET")` for `activity_status`, `country_code`, member type and `sponsor`. If the person's member type today is not a rep type, they joined and then changed back to a customer or were removed: count them as **left**.
3. `fluid_api("/api/v202506/members/<member_id>/orders?sort=created_at&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`. Keep orders after the enrollment order with `order_status` `completed`, and note the day each one came, counted from the enrollment.
4. Work out for this person:
   - **Second order** by day 30, 60 and 90: their own next completed order from item 3, or a customer sale credited to them from `fluid_api("/api/v2025-06/members/<member_id>/credited_orders?start_date=<enrollment date>&end_date=<enrollment date + 90 days>&status=completed", "GET")`, whichever came first. Count the two separately too: a kit whose reps only reorder for themselves and never sell is worth knowing.
   - **Autoship by day 90:** a subscription created with the enrollment or any later order, still active per `fluid_api("/api/v2025-06/subscriptions?filter[search]=<email>", "GET")`.
   - **Kit refunded:** the enrollment order's `financial_status` is `refunded` or `partially_refunded`.
   - **Still active today:** `activity_status` is active and their type is still a rep type.
   - **Spend in 90 days** after the kit, in the order's currency.
   - **Kit only:** no completed order after the enrollment at all.

Pause every 100 people to tell the user how far along you are.

## 4. Build the scorecard

One row per kit with at least one finished enrollment:

| Kit | Joined | Didn't finish | 2nd order by 30 / 60 / 90 days | Autoship by 90 | Kit refunded | Kit only | Active today | Median spend in 90 days |
|---|---|---|---|---|---|---|---|---|

Show percentages with the count behind them (for example `41% (37)`). Add a **company** row for all kits together, and then split the same table by market when the company sells kits in more than one market and a market has 20 or more enrollments.

Then give each kit with 20 or more enrollments one verdict:

- **Keeps reps:** second order and active today at or above the company row, refunds and kit-only at or below it.
- **Fix:** sells well but one of second order, autoship or active today is clearly below the company row. Say which, and the most likely reason from what the kit holds (for example no consumable to reorder, no autoship started, a price far above the other kits in that market).
- **Review:** refunds or kit-only clearly above the company row. Say it is a pattern worth a look, not proof of anything, and suggest `compliance/inventory-loading-check` for the sponsors behind it.
- **Too few to judge:** under 20 enrollments.

## 5. Hand over

Lead with one sentence: how many people joined in the window, which kit keeps the most of them, and which keeps the fewest. Then the scorecard and verdicts, and finish with:

- **Two or three changes worth testing**, each tied to a kit and a number (for example "Add a 30-day refill to the Business kit: only 18% of its reps ordered again by day 60, against 41% for the Starter kit").
- **People to reach now:** new reps from the last 30 days who joined with a **Fix** or **Review** kit and haven't placed a second order, listed by first name, market, kit and sponsor's first name, so a sponsor or the field team can check in. Don't message them.
- **Method line:** the window, whether it was a sample, how "active" and "second order" were counted, and that causes are estimates.

If the company had no finished enrollments in the window, say so plainly and offer to run it on the last 90 days instead, as an early read rather than a scorecard.
