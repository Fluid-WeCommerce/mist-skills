---
name: Sales tax filing check
description: Before a sales tax return is filed, check that every taxed sale, refund and cancellation from last month reached your tax provider, and get a fix list for anything stuck, missing or sent to a test account.
icon: landmark
---

# Goal

Get {{company.name}}'s tax records ready for last month's sales tax returns. Your tax provider (for example Avalara) files returns from the tax documents Fluid sends it: a **sale** for each order, a **return** for each refund, a **void** for each cancellation. A document that is stuck, never sent or sent to a test account means a return that under- or over-reports tax, and that is a liability you find out about in an audit. This skill finds those documents while there is still time to fix them, and ends with a verdict: **ready to file** or **fix these first**.

The period is the last full calendar month before {{today}}, unless the user names another one.

# Rules

- **Read only.** This skill changes nothing. Fluid support retries built-in filings; the company's team fixes product tax codes, addresses and provider settings.
- **Talk in plain words.** Refer to orders by order number and countries by name. No ids, paths, JSON or provider error codes in the chat; put the provider's message in plain words.
- **Don't give tax advice.** Report what was and wasn't sent to the provider. Whether and where the company must file is for its tax adviser.
- Money amounts are decimal strings. Total them only within one currency.

# Steps

## 1. Who files tax, where

`fluid_api("/api/v202604/company/tax_settings", "GET")`.

- If it answers **404**, tax filing records aren't turned on for this company. Say so in one line, suggest asking Fluid support to turn on the tax filings page, and stop.
- For each entry in `data.tax_settings.countries`, note the country (`iso`), `served_by`, `avalara.commit_enabled`, `avalara.commit_state` and `setup_risks`. A country is **expected to file** when `commit_state` is `filing`.
- Flag straight away, before anything else:
  - a country whose `served_by` is `sandbox_avalara`: its tax goes to a test account, so nothing it sells is on a real return;
  - a country with orders (step 3) whose `commit_state` is `dormant` or `off`: tax is charged but no documents are sent;
  - any `setup_risks`, in plain words.
- Note which Avalara account is active in `data.tax_settings.avalara.accounts` (environment `production` or `sandbox`).

## 2. Every tax document for the period

1. Set `from` to the first day of the period at 00:00 UTC and `to` to **7 days after** the period ends (orders placed on the last day are often filed a few days later).
2. `fluid_api("/api/v202604/company/tax_filings/summary?window[from]=<from>&window[to]=<to>", "GET")`. Keep `counts` (by status and environment) and `outstanding`.
3. `fluid_api("/api/v202604/company/tax_filings?window[from]=<from>&window[to]=<to>&page[limit]=100", "GET")`. Follow `meta.pagination.next_cursor` as `page[cursor]`, sending the same `window[from]` and `window[to]` every time, until it is null.
4. `fluid_api("/api/v202604/company/tax_filings?filter[outstanding]=true&page[limit]=100", "GET")`, paged the same way, for everything still `needs_attention` or `in_progress` from any month.
5. For each filing keep `order_number`, `order_id`, `document_type`, `status`, `environment`, `tax_amount`, `currency`, `attempts`, `filer_label`, `fluid_actionable`, `attention_reason` and `provider_reason`. Index them by order number and document type.

If a call answers 503, wait a moment and try once more with a shorter window (one week at a time).

## 3. The sales that should have a document

For each country expected to file (step 1):

1. `fluid_api("/api/v202506/orders?country_isos=<ISO>&start_date=<first day>&end_date=<last day>&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`.
2. Keep orders whose `order_status` is `processing`, `completed` or `archived`. Set aside `cancelled` orders for step 5.
3. An order is **missing a sale document** when step 2 found no `sale` filing for its order number.
4. For up to 25 missing orders, largest first, confirm: `fluid_api("/api/v202604/company/tax_filings?filter[order_number]=<number>&window[from]=<period start minus 30 days>&window[to]=<{{today}}>", "GET")` (the document may sit outside the window), then `fluid_api("/api/v202506/orders/<id>", "GET")` for its `current_tax`. Group the confirmed ones into **taxed, never sent** (tax above zero) and **no tax charged** (tax zero: often correct, for example a tax-exempt member, but list them).

## 4. Refunds that should have a return document

Refunds often land on orders from earlier months, so look back further than the period.

1. For each country expected to file, `fluid_api("/api/v202506/orders?country_isos=<ISO>&start_date=<period start minus 60 days>&end_date=<last day>&page[limit]=100", "GET")`, paged as in step 3 (reuse step 3's pages for the period itself). Keep orders whose `financial_status` is `refunded` or `partially_refunded`.
2. A refunded order with a filed `sale` document needs a `return` document. For each refunded order that step 2's index doesn't show with both, check it directly: `fluid_api("/api/v202604/company/tax_filings?filter[order_number]=<number>&window[from]=<period start minus 90 days>&window[to]=<{{today}}>", "GET")`.
3. List refunded orders that have a filed sale document but no return document, with the order date, the order amount and whether it was refunded in full or in part. Orders with `financial_status` `refund_pending` aren't settled yet: mention their count only.

## 5. Cancellations that should have a void

For each `cancelled` order from step 3 that has a `filed` sale document, there should be a `void` (or a `return`) document. List the ones that don't: the provider still counts that tax as owed.

## 6. Read the stuck documents

For each filing with status `needs_attention`, and each `in_progress` filing whose `last_event_at` is more than 2 days old:

1. `fluid_api("/api/v202604/company/tax_filings/<id>", "GET")`. Read `provider_reason` (the full text) and the latest `events`.
2. Put the reason into one of these groups, in plain words: **address** (the provider couldn't place the delivery address), **product tax code** (a product has an unknown or missing tax code), **account or credentials** (the provider refused the company's account), **duplicate or locked** (the document already exists or the period is locked at the provider), **other**.
3. Note who fixes it: `fluid_actionable: true` filings are Fluid's built-in filing, which Fluid support can retry once the cause is fixed; `fluid_actionable: false` filings were filed by the app named in `filer_label`, and that app's owner fixes them.

## 7. Report

Lead with the verdict in one line: **Ready to file** (nothing stuck, missing or sent to a test account for the period) or **Fix these first**, with the count and the tax at stake per currency.

Then, only the sections that have something in them:

1. **Sent to a test account** (Critical): countries served by a sandbox account and any period filings in the `sandbox` environment, with the order count and tax.
2. **Stuck at the provider:** one table per reason group (order number, document type, tax, attempts, the reason in plain words), then the fix and who does it.
3. **Taxed sales never sent:** order number, country, order date, tax.
4. **Refunds with no return document**, and **cancellations with no void**: order number, order date, amount.
5. **Countries charging tax that send no documents.**
6. **Totals for the period** per currency: tax on filed sale documents, minus filed returns and voids, so the team can tie it to the provider's return worksheet.
7. **No tax charged** orders from step 3, collapsed at the end, as a list to glance over.

Close with the next step: fix the causes in step 6, then ask Fluid support to retry the built-in filings by order number, and run this check again before the filing deadline.
