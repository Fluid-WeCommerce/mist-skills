---
name: Autoship stock runway
description: Forecast how many days of stock each product has left in each warehouse from recent one-time sales plus the autoship renewals already scheduled, flag what runs out before a reorder can arrive, and hand over a dated reorder list.
icon: package-search
---

# Goal

Tell {{company.name}}, as of {{today}}, which products will run out in which warehouse, when, and what to reorder now so they don't.

Social-selling and direct-sales companies have demand that most stock reports miss. A large share of what ships each month is autoship, and those renewals are already on the calendar with a date, a product, a quantity and a destination. A stockout on an autoship product skips or fails renewals for loyal customers. Those customers cancel, and the reps they buy through lose volume. This skill adds two kinds of demand: one-time orders, estimated from the last 28 days, and autoship renewals, read from the schedule. It compares the total with available stock and the user's supplier lead times.

At the end the user has:

1. A runway table: every tracked product and warehouse with available units, daily demand, the share that is autoship, days of stock left and the date it runs out.
2. A **reorder now** list: products that run out before a reorder placed today could arrive, with a suggested quantity.
3. The autoship renewals at risk: how many renewals, customers and how much revenue fall after each stockout date.
4. A dated record in the project, so the next run reuses lead times and shows what changed.

# Rules

- **Read-only.** This skill never adjusts stock, moves orders between warehouses, or changes subscriptions. Fixes are recommendations for the user's team.
- **Talk in plain words.** Name products by title and SKU, and warehouses and countries by name. Don't show ids, paths or JSON in the chat.
- **Never add across currencies.** Revenue at risk is shown per currency.
- **Say what is an estimate.** Stock and scheduled renewals are read from the records. One-time demand, stockout dates and reorder quantities are estimates; label them that way.
- If a read is refused or a feature is off, say in plain words which part you couldn't check and carry on with the rest.

# Steps

## 1. Load the last run and the inputs

1. Look for `stock-runway/` in the active project with `list_dir`. If there is an earlier run, read the newest file with `read_file` and keep its lead times, safety days and the stockout dates it predicted.
2. Ask the user in a `steps` panel, prefilled from the last run if there is one:
   - **Horizon:** how many days ahead to look. Default 45.
   - **Supplier lead time:** days from placing a reorder to stock being sellable in the warehouse. Ask for one default, plus any products or brands that differ. If they don't know, use 30 and mark every reorder date as based on a guess.
   - **Safety days:** extra days of cover to keep. Default 14.
   - **Coming spikes (optional):** launches, promotions, contests or events in the horizon, with the products involved and the extra units expected. If the user has no number, record the spike as a named risk with no number attached.

## 2. Warehouses and which countries they serve

1. `fluid_api("/api/company/v2026-10/warehouses/routing-summary", "GET")`. Keep each warehouse's name, whether it is active and sellable, and its `country_isos`, plus each country's `warehouse_id`.
2. If that answers 404 (the feature is off for this company), call `fluid_api("/api/settings/warehouses", "GET")` for the warehouse list. Then learn which warehouse ships each country from the orders in step 4, using the `warehouse_id` most of that country's orders used.
3. Note any warehouse that holds stock but serves no country. Its units can't cover demand anywhere until it is routed.

## 3. Stock on hand

1. For each active warehouse, call `fluid_api("/api/inventory_levels?warehouse_ids=<id>&page=1&page_size=100", "GET")` and page with `page` until `meta.current_page` reaches `meta.total_pages`.
2. For each level, keep the warehouse, `variant.id`, `variant.sku`, `variant.product_id`, the product title, `available`, `committed` and `on_hand`, plus `variant.track_quantity` and `variant.keep_selling`.
3. Set aside variants with `track_quantity` false. They have no count to forecast, so list how many there are at the end. Flag variants with `keep_selling` true: they keep accepting orders at zero, so running out creates backorders, not a sold-out page.

## 4. One-time demand (last 28 days)

1. Set `<start>` to the date 28 days before `{{today}}`. Work it out yourself; there is no token for it. Then call `fluid_api("/api/v202506/orders?start_date=<start>&end_date={{today}}&page[limit]=100", "GET")` and follow `meta.pagination.next_cursor` as `page[cursor]` until it is empty.
2. Keep orders that were paid: drop drafts, pending and cancelled orders. **Drop orders whose `subscription` is not null.** Those are autoship renewals, which step 5 counts from the schedule, so counting them here would double them. Keep orders with `starts_subscription` true: the first order is a one-time event.
3. For each kept order, call `fluid_api("/api/v202506/orders/<id>", "GET")` and read `items` (`sku`, `quantity`), `warehouse_id` and `country`. Add each line's `quantity` to that SKU in that warehouse. Lines whose SKU matches no tracked variant go into an "unmatched" count.
4. One-time daily demand = units ÷ 28 per SKU and warehouse. If the window contained an unusual spike the user named, such as a launch week, say so: it will overstate normal demand.
5. If there are more than about 1,500 orders in the window, tell the user, then work from the 14 most recent days and divide by 14 so the run finishes.

## 5. Autoship demand (scheduled)

1. Set `<end>` to `{{today}}` plus the horizon. Call `fluid_api("/api/subscriptions?status=active&next_bill_start={{today}}&next_bill_end=<end>&per_page=100&page=1", "GET")` and page with `page` until `meta.pagination.total_pages` is reached.
2. For each subscription, keep `variant.sku`, `variant.id`, `quantity`, `next_bill_date`, `subscription_plan.billing_interval` and `billing_interval_unit`, `price` and `currency.code`, and the destination country from `customer.default_address.country_code`. Map the country to its warehouse with step 2.
3. Project every renewal inside the horizon: the first on `next_bill_date`, then one every billing interval until `<end>`. A monthly autoship billing on day 3 of a 45-day horizon counts twice.
4. Count every scheduled renewal, including ones that may fail payment. Stock has to be there if the charge goes through. Separately, call `fluid_api("/api/v202604/analytics/subscription_billing/calendar", "GET")` for this month and next (`month=YYYY-MM`) and note the share of renewals that are failing or at risk. This gives context; it doesn't reduce demand.
5. Autoship daily demand per SKU and warehouse = projected units ÷ horizon days. Keep the dated list too, because step 6 needs the exact days.

## 6. Runway and stockout date

For every tracked SKU and warehouse:

1. **Usable stock** = `available`. Committed units already belong to paid orders.
2. Walk forward day by day from `{{today}}`. Each day, subtract one-time daily demand and that day's scheduled autoship units, plus any spike the user gave for that day. The **stockout date** is the first day stock falls below zero, or "beyond horizon".
3. **Days of stock** = days until the stockout date.
4. **Reorder-by date** = stockout date − lead time − safety days.
5. **Status:**
   - **Reorder now:** the reorder-by date is today or already past.
   - **Reorder soon:** the reorder-by date is within 14 days.
   - **Healthy:** everything else.
   - **Overstocked:** more than 180 days of stock at current demand. List these separately; they tie up cash.
6. **Suggested reorder quantity** = (lead time + safety days + 30) × total daily demand − usable stock, rounded up, and never below zero. The 30 days give one month of cover after the reorder arrives. Say it is a starting point for the buyer, not a purchase order.
7. **Autoship at risk:** for each SKU with a stockout date inside the horizon, count the scheduled renewals on or after that date. Report the number of renewals, distinct customers and revenue (`price` × `quantity`, per currency).
8. **Stock in the wrong place:** when a SKU runs out in one warehouse while another holds more than 90 days of it, say so. A transfer may beat a reorder.

## 7. Report

Lead with one sentence: how many products need a reorder now, and the earliest stockout. For example: "3 products need reordering today; the Glow Serum runs out in Dallas on December 9, with 212 autoship renewals due after that date."

Then show, in this order:

1. **Reorder now:** product and SKU, warehouse, available units, daily demand (and the autoship share), stockout date, reorder-by date, suggested quantity, and the autoship renewals and revenue at risk.
2. **Reorder soon:** the same columns.
3. **Stock in the wrong place**, and warehouses holding stock no country ships from.
4. **Overstocked:** product, warehouse, units and days of stock.
5. **What changed since the last run:** stockout dates that moved by more than 7 days, and products that were "reorder now" last time and still are.
6. **Not forecast:** counts of untracked variants and unmatched order lines, and any part you couldn't read.

Use `product_card` for the top three "reorder now" products when it helps the user recognize them.

Close with one recommendation grounded in the numbers. For example: "Place the serum reorder today and move 300 units from Toronto to Dallas this week to cover the gap," or "Autoship is 70% of demand on your top five products, so check this every week, not every month."

## 8. Save the record

Write `stock-runway/stock-runway-{{today}}.md` with `write_file`. Include the inputs (horizon, lead times, safety days, spikes), the full runway table, the reorder lists, the autoship-at-risk counts and the stockout dates predicted. The next run reads it in step 1 and compares.

# Notes

- **Order lines carry SKU, not variant id.** Demand from orders is joined to stock by SKU. If one SKU sits on more than one tracked variant, show those variants as one line and say so.
- **Fluid holds no purchase orders or inbound shipments.** Stock already on its way isn't visible. Ask the user whether any reorder is in transit for a "reorder now" product before calling it urgent.
- **Bundles and kits.** If order lines show a bundle's own SKU instead of its components, component demand is understated. Mention this when a bundle is among the top sellers.
- **Seasonality.** A 28-day window doesn't know that next month is the holiday peak. Ask about it as a coming spike in step 1 instead of guessing.
