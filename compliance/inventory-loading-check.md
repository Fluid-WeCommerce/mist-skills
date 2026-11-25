---
name: Inventory loading check
description: Find reps whose own purchases look like stocking up to qualify rather than buying to use or resell (volume that is mostly self-bought, quantities no one person uses, month-end spikes before a rank change, stacked kits, refunds after qualifying), rank them by risk with the evidence, and save a dated review record without changing anything in Fluid.
icon: package-search
---

# Goal

Give {{company.name}}'s compliance team a monthly, evidence-backed answer to one question regulators always ask a direct-selling company: **is the volume that pays reps and earns ranks coming from real use and real customers, or from reps buying stock they don't need to qualify?**

The FTC's guidance on multi-level marketing says pay must rest on real sales to real customers, defines inventory loading as reps buying product to move up in the plan rather than to meet real demand, and says a buyback policy helps but doesn't settle the question. Industry codes such as the DSA Code of Ethics ban inventory loading and expect companies to take reasonable steps so reps use or resell what they buy. This skill does those steps from Fluid's own orders.

At the end the user has:

1. A company-wide picture for the window: how much of reps' credited volume came from their own orders, overall and by rank.
2. A ranked list of reps with one or more warning signs, each with the facts behind it and a suggested next step.
3. A dated review record in the project that shows what was checked, what was found and what the team decided.

This skill is a screen, not a finding. A sign is a reason to look, not proof of wrongdoing: a rep with a large family, a party next week or a small shop can buy a lot for good reasons. It is not legal advice; point the user to their counsel for decisions about a specific rep.

# Rules

- **Read only.** This skill changes nothing in Fluid and messages nobody. It never changes a rank, a volume figure, an order or an account, and never contacts a rep. Follow-up happens outside this skill, by the user's team.
- **No accusations.** Describe what the orders show ("bought 14 of the 30-day supply in 6 weeks"), never intent ("is loading"). Keep reps' names out of anything except the chat with the user and the record.
- **Same rules for everyone.** Apply the same thresholds to every rep; never skip leaders or top earners.
- **Talk in plain words.** Name reps, products, kits, ranks and months. Don't show ids, paths or JSON in the chat.
- If a read is refused, say in plain words which part you couldn't check and carry on with the rest.
- Keep your own working numbers in the project (`inventory-loading/work/`), not in the chat, when the field is large.

# Steps

## 1. Load the last run and set the thresholds

1. `list_dir` on `inventory-loading/` in the active project. If there is an earlier record, read the newest with `read_file` and keep: the thresholds used, reps already reviewed and what the team decided for each, and any rep cleared with a reason (so you don't raise the same thing again without something new).
2. Read the company's setup:
   - `fluid_api("/api/v2025-06/member-types", "GET")` to list member types. Pick the ones that are reps (sellers who earn), and confirm with the user if more than one could be.
   - `fluid_api("/api/v202506/ranks", "GET")` for the rank names.
   - `fluid_api("/api/enrollment_packs", "GET")` for the enrollment kits and starter packs, with `fluid_api("/api/enrollment_packs/<id>", "GET")` for what each contains, so kit purchases can be recognised by product.
3. Ask the user in one `steps` panel, prefilled from the last run when there is one:
   - **Window:** the last full month and the two before it (default), or another range.
   - **Self-purchase share:** the share of a rep's credited volume from their own orders that should be looked at. Default 70%. Many companies' policies use a 70% retail or personal-use rule; use the company's own rule if it has one.
   - **Monthly use:** how many units of a product one person reasonably uses in a month. Default: flag a product when a rep bought more than 3 times the field's typical monthly quantity of it (step 3.2), and at least 6 units.
   - **Month-end days:** how many days at the end of a month count as "month end". Default 3.
   - **Buyback policy:** the company's repurchase terms in their words (for example "90% of cost on resalable product bought in the last 12 months"), or "not sure". If unsure, `web_fetch` the policies page the user names and quote it.

## 2. Find the reps to check

1. Page through `fluid_api("/api/v2025-06/members?filter[member_type_slug][]=<rep type>&filter[active]=true&filter[orders_count_min]=2&page[limit]=100", "GET")` (repeat `filter[member_type_slug][]` for each rep type), following `meta.pagination.next_cursor` as `page[cursor]`. Keep each rep's name, country, rank, join date, `legacy_user_company_id` (whose sales they are credited with), `legacy_customer_id` (their own buyer record), `orders_count` and `total_spent_in_base`.
2. Reps with fewer than 2 orders of their own can't show a pattern; say how many you left out.
3. When more than 500 reps remain, check the 500 with the highest `total_spent_in_base` first, tell the user, and offer to continue with the rest in a second run.

## 3. Gather each rep's orders in the window

For each rep:

1. **Their own orders, with items:** `fluid_api("/api/v202506/members/<member id>/orders?status=all&sort=-created_at&page[limit]=100", "GET")`, following `next_cursor` until the orders are older than the window. Keep, per order: date, status, `financial_status`, `total_cv`, `total_qv`, `amount_in_base`, `enrollment_fee_in_base`, and each item's title, `sku`, `quantity`, `refundable_quantity` and `cv_total`. Units refunded on an item are `quantity` minus `refundable_quantity`.
2. **Orders credited to them:** `fluid_api("/api/v202506/orders?user_company_id=<legacy_user_company_id>&start_date=<from>&end_date=<to>&page[limit]=100", "GET")`, following `next_cursor`. Split them into **own** (the order's `customer.id` is the rep's `legacy_customer_id`) and **customers** (everyone else). Add up `total_cv` for each side.
3. **Rank changes:** `fluid_api("/api/v202506/user_company_change_logs?user_company_id=<legacy_user_company_id>", "GET")`, keeping entries whose `metadata.note_type` is `rank_changed` in the window and the month after, with their dates. If a rep has none, the month-end sign can only say "spike", not "before a rank change"; say so for that rep.

Then, across all reps:

4. **Typical monthly quantity per product:** for each product SKU, the median units per month bought by reps who bought it at all. This is the field's own baseline for step 4's quantity sign.

## 4. Score the warning signs

For each rep, mark each sign that applies and note its facts:

| Sign | When it applies | What to write down |
|---|---|---|
| **Mostly self-bought** | Own CV is at or above the self-purchase share of all CV credited to the rep, in a month where the rep has any customer orders or holds a rank above the first | Own CV, customer CV, the share, and the month |
| **More than one person uses** | Units of one product bought in a month exceed the monthly-use threshold | Product, units, the field's typical quantity, and the month |
| **Month-end spike before a rank change** | An own order in the last month-end days of a month, and the rep's rank went up for that month or the next | Order date and CV, the rank before and after |
| **Stacked kits** | Two or more enrollment kits or starter packs bought by the same rep within 90 days | Kits, dates and the volume each counted |
| **Refunded after qualifying** | An own order that counted in one month and was refunded, fully or partly, in a later month | Order date, refund timing, units and CV taken back |
| **Bought for others on their own account** | Own orders shipped to several different addresses, or many units of products customers usually autoship | Number of addresses or units, and the products |

For the last sign, read addresses only from orders already in hand (`fluid_api("/api/v202506/orders/<id>", "GET")` when the list didn't include one); don't look up anyone else's records.

Then give each rep a **risk level**:

- **High:** "Mostly self-bought" plus at least one other sign, or "Month-end spike before a rank change" together with "Refunded after qualifying".
- **Medium:** any two signs.
- **Low:** one sign.

Leave out reps cleared in the last record for the same reason unless the figures got worse, and say how many.

## 5. Show the picture first, then the list

1. **Company picture:** for the window, total credited CV, the share from reps' own orders, and that share by rank and by month. One line on the trend against the last record, if there is one. A share rising at the top ranks is the most important thing to say first.
2. **The list:** High first, then Medium. Read each listed rep's sponsor from `fluid_api("/api/v2025-06/members/<member id>", "GET")`. For each rep: name, rank, country, sponsor, the signs with their facts in one line each, and a suggested next step:
   - **Talk first:** a sponsor or field-support conversation about what they're buying and why, for most Medium cases.
   - **Policy reminder:** the company's personal-use and buyback terms, quoted, for reps with large stock and no customers.
   - **Compliance review:** for High cases, the team reviews the rep's orders against the plan and the back office's rank and bonus records before anything else happens.
   - **Back-office check:** for "Refunded after qualifying", hand the orders to the commission team; the `finance/commission-clawback-list` skill lists them with `run_skill` if the user wants.
3. **Plan signals:** if one product, kit or month drives most of the signs, say so. That's usually a plan or promotion design problem (a rank requirement just above a kit's volume, a double-volume promotion), not a rep problem. Suggest the user takes it to whoever owns the compensation plan.

Ask the user, with a `steps` panel, what the team decides for each High and Medium rep: **look into it**, **talk to them**, **cleared** (with a reason) or **later**.

## 6. Save the record

Write `inventory-loading/{{today}}.md` with `write_file`:

- Date, company, who ran it ({{user.name}}, {{user.email}}), the window and every threshold used, and the buyback policy as quoted.
- The company picture from step 5.1.
- Every flagged rep: risk level, signs with their facts, suggested step, and the team's decision with its reason.
- Reps left out and why (too few orders, cleared before, beyond the first 500).
- Open items and the date of the next run (default: the 5th of next month, after the month closes).

End with the path to the record and the three things that would cut the signs most next month.
