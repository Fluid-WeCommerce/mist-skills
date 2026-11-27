---
name: Promo code leak check
description: Find promo codes that are costing more than you meant — open-ended or deep codes, codes that still pay full volume, codes whose use suddenly jumped, and codes listed on public coupon sites — estimate what each cost in the last 30 days, and tighten or retire only the ones you approve.
icon: ticket-x
---

# Goal

Check every active promo code at {{company.name}} as of {{today}} and answer one question for each: **is this code being used by the people it was made for, on the terms we meant?**

Promo codes leak. A code made for one rep's party, one influencer or one launch week ends up on coupon sites and browser extensions, and from then on any shopper gets it at checkout, including the company's own full-price customers. In direct sales the cost is doubled when the code doesn't lower volume: the company gives the discount away and still pays commission on the full price.

At the end the user has:

1. A ranked list of codes that need attention, each with the plain reason and a suggested fix.
2. An estimate of what each flagged code cost in the last 30 days: orders, discount given, and volume credited on discounted orders.
3. The fixes they approved applied, one code at a time.
4. A dated record in the project, so next month's run can tell which codes suddenly got busier.

# Rules

- **Read first, write only with approval.** Every change to a code goes through one `human_in_the_loop` card, and at most 3 cards per turn: then END your turn and wait for the clicks.
- **Never delete a code.** Retire a code by turning it off, or by giving it an end date, so its history stays.
- **Turning a code off breaks it for everyone who holds it,** including the rep or partner it was made for. Say so on the card, and offer an inactive copy they can rename and hand out instead.
- **Leave alone what Fluid manages for you:** codes whose `source` is `droplet` or `subscription_pro`, and codes with `value_managed_by_droplet` true. List them as "managed elsewhere" and skip them.
- **Talk in plain words.** Name codes, products, countries and dates. Don't show ids, paths or JSON in the chat.
- **Estimates are estimates.** The order sample and the coupon-site check can miss things. Say what you checked and what you didn't.
- If a read is refused, say in plain words which part you couldn't check and carry on with the rest.

# Steps

## 1. Load the last run and confirm the thresholds

1. `list_dir` on `promo-codes/` in the active project. If there is an earlier record, read the newest `usage-<date>.json` with `read_file`: each code's `total_usage` on that date, codes the user marked as **meant to be public** (a code printed on the storefront or in ads), and codes the user cleared with a reason.
2. Ask the user once, in one `steps` panel, prefilled from the last run when there is one:
   - **Deep discount:** percent off at or above which a code counts as deep. Default 30%.
   - **Public codes:** codes that are meant to be shared widely, so finding them on a coupon site is expected (default: none).
   - **Order window for the cost estimate:** the last 30 days (default).

## 2. List the active codes

1. Page through `fluid_api("/api/v2025-06/discounts?active=true&per_page=100&page=<n>", "GET")`. This endpoint is page-numbered: increment `page` while `meta.pagination.total_pages` is greater than the current page.
2. Skip discounts with `automatic` true (there is no code to leak) and set aside the "managed elsewhere" ones from the Rules. Say how many of each you set aside.
3. For each remaining code keep: `code`, `price_discount_type`, `price_discount_percent` or `price_discount_amount`, `applicable_for`, `customer_filter`, `country_filter` with `country_codes`, `purchase_requirement` with its minimums, `has_end_date`, `end_date_time`, `limit_usage_of_code`, `customer_usage_limit`, `limit_usage_per_customer`, `other_product_discounts`, `apply_to_volume`, `apply_to_subscriptions`, `apply_to_recurring_subscription_orders`, `free_variant_ids`, `free_enrollment_pack_ids`, `waive_enrollment_fee`, `exclude_free_items_from_volume`, `total_usage`, `created_at`, `created_by` and `description`.

## 3. Check how each code is set up

Mark every sign that applies:

| Sign | When it applies | Why it matters |
|---|---|---|
| **Open to anyone, forever** | `customer_filter` is `all_customers`, `has_end_date` is false, `limit_usage_of_code` is false and `limit_usage_per_customer` is false | Once it leaks, nothing ever stops it |
| **Deep** | A `percentage` code at or above the deep threshold, a `free_product` code, or a `free_enrollment_pack` code (worse when `waive_enrollment_fee` is true) | Each leaked use gives away a lot |
| **Pays full volume** | A product discount with `apply_to_volume` false, on a deep code | Reps are credited, and paid, on money the company never collected |
| **Free items count as volume** | A `free_product` or `free_enrollment_pack` code with `exclude_free_items_from_volume` false | Free product earns commission |
| **Stacks** | `other_product_discounts` true | It combines with other product codes for a deeper total discount |
| **Discounts every autoship renewal** | `apply_to_recurring_subscription_orders` true | One use lowers the price on every future renewal |
| **No minimum** | A `flat` code with `purchase_requirement` `no_minimum_required` | A flat amount off a small order can be most of its price |
| **Past its end** | `end_date_time` is in the past but `active` is true | Clutter: it no longer works, but it still reads as live |
| **Easy to guess** | The code is a common word plus a number (`WELCOME10`, `SAVE20`, `FREESHIP`) | Shoppers and extensions try these without ever seeing them |

## 4. Look for sudden jumps in use

For each code, work out uses per day:

- **With an earlier record:** (today's `total_usage` minus the recorded one) divided by the days between the runs.
- **First run:** `total_usage` divided by days since `created_at`.

Flag a **jump** when a code's recent daily use is at least 3 times its earlier daily use and at least 20 uses in the period, or when a code made for a list of customers (`customer_filter` `specific_customers`) with one use each (`limit_usage_per_customer` true) has more uses than the customers on its list (`eligible_customer_ids`). A code that jumps without a campaign behind it is the usual first sign of a leak: ask the user whether a campaign explains it before calling it one.

## 5. Check public coupon sites

1. Find the store's domains: `fluid_api("/api/domains", "GET")`, keeping those whose `verification_status` is `verified`, with the `primary` one first. Check at most 3 domains.
2. For each domain, `web_fetch` these public coupon pages:
   - `https://couponfollow.com/site/<domain>`
   - `https://www.retailmenot.com/view/<domain>`
   - `https://www.dealspotr.com/promo-codes/<domain>`
3. Search each page's text for every active code, ignoring case. Record which codes appear on which site. A code on the user's public list is expected there; every other code found is **listed publicly**.
4. Some sites refuse automated reads. Say which ones you couldn't read, and suggest the user open them in a browser and paste back any codes they see.

## 6. Estimate what flagged codes cost

1. Take every code with at least one sign from steps 3 to 5. If none, skip to step 7.
2. List the window's orders with `fluid_api("/api/v202604/orders?filter[start_date]=<window start>&filter[end_date]={{today}}&page[limit]=100", "GET")`, passing `meta.pagination.next_cursor` back as `page[cursor]` until it is null. The list rows carry no discount codes, so read each order with `fluid_api("/api/v202506/orders/<id>", "GET")` and keep those whose `discount_codes` include a flagged code.
3. Tell the user the order count before the detail reads when it is over 300. Above 1,500 orders, read the newest 1,500 and say the figures are a sample.
4. For each flagged code add up: orders, `discount_in_base` (discount given, in the base currency), `amount_in_base` (what was collected), and `total_cv` (volume credited). Count how many of its orders came from customers who had ordered before at full price (an earlier order in the same list without the code). That share is the best sign a code reached people who would have paid anyway.

## 7. Report

Lead with the decision, not the inventory. One short paragraph: how many active codes, how many need attention, the discount given on flagged codes in the window, and the one code to fix first.

Then a table, worst first, with: code, what it gives, the signs in plain words ("listed on 2 coupon sites, open to anyone with no end, pays full volume"), uses in the window, discount given, volume credited, and the suggested fix:

| Situation | Suggested fix |
|---|---|
| Listed publicly, made for a rep, partner or campaign | Turn it off and give them a fresh copy to rename |
| Open to anyone, forever | Add an end date, and a total-use cap or one use per customer |
| Deep and pays full volume | Turn on lowering volume with the discount, after the user checks this with whoever runs the comp plan |
| Free items count as volume | Exclude free items from volume |
| Discounts every autoship renewal, not meant to | Turn that off |
| Stacks, not meant to | Turn stacking off |
| Past its end | Turn it off |
| Jump with no campaign behind it | Watch it, or cap it, until the user knows why |

Close with what you could not check (sites that refused, a sampled window) and the codes set aside as automatic or managed elsewhere.

## 8. Apply the fixes the user approves

For each fix the user wants, post one `human_in_the_loop` card naming the code, the change, who it affects and what it cost in the window. On approval, call `fluid_api("/api/v2025-06/discounts/<id>", "PUT", {"discount": { … }})` with only the fields that change:

- **Add an end date:** `has_end_date: true`, `end_date` (YYYY-MM-DD), `end_time` (12-hour, for example `11:59 PM`) and `time_zone` (keep the code's own).
- **Cap use:** `limit_usage_of_code: true` with `use_limit` (the total across everyone), and/or `limit_usage_per_customer: true` (one use per email address).
- **Lower volume with the discount:** `apply_to_volume: true`. **Exclude free items from volume:** `exclude_free_items_from_volume: true`.
- **Stop stacking:** `other_product_discounts: false`. **Stop discounting renewals:** `apply_to_recurring_subscription_orders: false`.
- **Turn a code off:** `active: false`.
- **Fresh copy for the rightful holder:** `fluid_api("/api/v2025-06/discounts/<id>/clone", "POST")` creates an inactive copy named after the original. Tell the user to rename and activate it in Fluid when they are ready to hand it out; don't activate it yourself.

Read each code back with `fluid_api("/api/v2025-06/discounts/<id>", "GET")` and confirm the change took. If an update is refused, say in plain words why and leave the code as it was.

## 9. Save the record

`write_file`:

- `promo-codes/usage-{{today}}.json`: every active code with its `total_usage` today, the user's public list, and codes cleared with their reason.
- `promo-codes/review-{{today}}.md`: the thresholds, the table from step 7, the coupon sites read and not read, the order window and whether it was sampled, and each fix with the user's decision and whether it applied.

Tell the user that running this again next month shows which codes got busier since today.
