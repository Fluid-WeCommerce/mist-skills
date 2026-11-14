---
name: Commission clawback list
description: Before the commission run, list every order whose volume was taken back after it counted (refunds, cancellations, voids and order edits) by the rep it was credited to, and write a file the back office can import.
icon: undo-2
---

# Goal

Before {{company.name}}'s next commission run, find every order whose volume shrank after it was first counted, and hand the back office one clean list per rep. A refunded kit, a cancelled autoship or an edited order can leave a rep paid, or ranked, on volume that no longer exists. Commissions are calculated outside Fluid, so the back office needs to know exactly which orders to adjust and by how much, once per order and never twice.

This skill **only reads Fluid**. It writes two files in the active project: the list for this run and a ledger of what earlier runs already reported.

# Rules

- **Read-only.** Make no `fluid_api` writes. Never refund, cancel, edit an order or change a rank.
- **Report each change once.** The ledger records how much volume was already reported for each order. Report only what has changed since then.
- **Volume, not money.** Report commission volume (CV) and rank volume (QV) taken back. Say so plainly. How much commission that is depends on the company's plan and is the back office's call.
- **Plain words in chat.** Use order numbers, rep names and countries. Keep ids and JSON in the files, not in the chat.
- **No conclusions about reps.** A rep with many reversals may have customers who return a lot. Flag patterns, don't accuse.

# Steps

## 1. Set the window

1. Read `commission-adjustments/ledger.json` with `read_file`. If it doesn't exist, this is the first run: start an empty ledger `{ "orders": {}, "runs": [] }`.
2. The **look-back** is 90 days of sale dates ending {{today}}, unless the user named another range. It should be at least the company's return window. If the user named one, use it and save it as `lookback_days` in the ledger.
3. The **cut-off** is the last commission close. Use the date the user gave, or the last run's `cut_off` in the ledger. With neither, use the last day of the previous calendar month, and say you assumed it.

## 2. Find candidate orders

Page through the look-back with the commerce orders list:

`fluid_api("/api/v202604/orders?filter[start_date]=<look-back start>&filter[end_date]={{today}}&sort=sale_date&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]` until it is null.

Keep an order as a candidate when **any** of these holds:

- `financial_status` is `refunded`, `partially_refunded` or `voided`
- `financial_status` is `refund_pending`. Keep it in a separate "pending" group: the refund isn't settled yet, so it is reported but not added to the ledger.
- `order_status` is `cancelled` and `total_cv` or `total_qv` is above 0
- `updated_at` is after the cut-off **and** `sale_date` is on or before the cut-off. This is a possible edit after close.

Skip orders whose `total_cv` and `total_qv` are both 0, and orders that are already in the ledger with the same `financial_status`, `order_status` and `updated_at`.

If there are more than 400 candidates, check the refunded, voided and cancelled ones first, then the possible edits by largest `total_cv`. Stop at 400 detail reads and say how many are left for the next run.

## 3. Measure what was taken back

For each candidate: `fluid_api("/api/v202506/orders/<id>", "GET")`. From `order`, read:

- `total_cv`, `total_qv`: the volume the order was placed with
- `current_cv`, `current_qv`: its volume now, after refunds and edits
- `refunds[]`: each refund's `cv`, `qv`, `amount`, `refund_type` and `reason`
- `rep`: the rep the volume is credited to (`id`, `name`, `external_id`)
- `order_number`, `sale_date`, `order_status`, `financial_status`, `currency_code`, `order_class` (on the list row)

Then work out the reversal:

- **Taken back** = `total_cv − current_cv`, and the same for QV. For a cancelled or voided order whose current volume still shows the full amount, take back the whole `total_cv` and `total_qv`, and flag it "cancelled but volume not reduced in Fluid".
- **New this run** = taken back − the amount the ledger already reported for this order. Skip the order if both are 0.
- If the refunds' `cv` adds up to a different figure than total minus current, keep total minus current and flag the order. Usually an edit and a refund both touched it.
- When `refunds[]` is empty and volume went down, call it an **edit**. Confirm with `fluid_api("/api/v202604/orders/<id>/edits", "GET")` when the drop is the rep's largest this run.
- If the volume went **up** (an edit added items), list it separately as "volume added after close". The back office may owe the rep.
- An order with no `rep` goes in an "unassigned" group. Its volume counted for nobody, so there is nothing to claw back, but list it once.

Label each line with a **when** value:

- **Before close**: the sale was after the cut-off. The back office can simply leave this volume out of this run.
- **After close**: the sale was on or before the cut-off, so it was already counted. This line needs a clawback or adjustment.

## 4. Look for patterns

Over the lines for this run:

- Reps with 3 or more after-close reversals, or one reversal over 25% of their volume in the look-back. Read their credited total once with `fluid_api("/api/v2025-06/reps/<rep id>/credited_orders?start_date=<look-back start>&end_date={{today}}&status=all&per_page=1", "GET")` and use `meta.total_cv`.
- Enrollment orders (`order_class` `enrollment_order`) refunded after close. Kit returns can unwind a new rep's rank and the enroller's bonus.
- Autoship orders (`autoship_order`) cancelled after they billed.
- Reversals where the buyer is the rep. This happens when the order's buyer `email` (on the list row) matches the rep's email from `fluid_api("/api/v2025-06/members/<rep id>", "GET")`. Check only the reps already flagged.

## 5. Write the files

1. `commission-adjustments/<cut-off date>-<{{today}}>.csv`, one row per order line, sorted by rep and then sale date. Columns: `rep_external_id, rep_name, order_number, sale_date, when (before_close|after_close), reason (refund|partial_refund|void|cancel|edit|added), cv_taken_back, qv_taken_back, currency, refund_reason, pending (true|false), note`.
2. Update `commission-adjustments/ledger.json`:
   - For each line that isn't pending, set `orders[<order id>] = { order_number, cv_reported, qv_reported, financial_status, order_status, updated_at, run: "{{today}}" }`. Here `cv_reported` and `qv_reported` are the totals reported so far, not just this run.
   - Append `{ date: "{{today}}", cut_off, lookback_days, lines, cv_total, qv_total }` to `runs`.

Write both with `write_file`. Read the CSV back with `read_file` and check that its row count matches your line count.

## 6. Report

Lead with one line: how many orders and reps need an adjustment, and the total commission and rank volume taken back after close.

Then:

1. **After close, by rep:** a table with rep, orders, CV and QV taken back, and the largest single order. Biggest first, top 25. The full list is in the file.
2. **Pending refunds:** orders whose refund isn't settled yet. These will show up on the next run, so the back office shouldn't adjust them yet.
3. **Flags:**
   - cancelled orders whose volume wasn't reduced
   - refunds and edits that disagree
   - volume added after close
   - unassigned orders
4. **Patterns** from step 4, worded neutrally, each with one suggested next step. For example: "ask the enroller whether the kit was returned unopened", or "check whether this rep's rank last month depended on these orders".
5. Where the files are. Remind the user that the next run picks up from this ledger, so running it twice won't double-report.

If nothing changed since the last run, say so in one line and don't write a new CSV. Do record the run in the ledger.
