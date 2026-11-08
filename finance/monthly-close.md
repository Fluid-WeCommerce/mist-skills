---
name: Monthly close report
description: Generate a one-page financial summary for the most recently completed calendar month.
icon: file-text
---

# Goal

Produce a month-end close report for `{{company.name}}` covering the most recently completed calendar month.

# Steps

1. Compute the date window: the first and last day of the previous calendar month relative to `{{today}}`.
2. Pull orders via `fluid_api("/api/v202604/orders?filter[start_date]=<start>&filter[end_date]=<end>&page[limit]=100", "GET")`, passing `meta.pagination.next_cursor` back as `page[cursor]` until it is null. The dates are sale dates, inclusive. For the headline totals, `fluid_api("/api/v202506/orders/stats?start_date=<start>&end_date=<end>", "GET")` returns `stats.total_count`, `stats.total_amount_base` and `stats.average_amount_base`. Line items (for the SKU rankings) come from each order's detail, `fluid_api("/api/v202506/orders/<id>", "GET")`.
3. There is no refund list endpoint. Pull refund transactions via `fluid_api("/api/v202506/company_transactions?payment_action=refund&status=success&type=live&page[limit]=100", "GET")`: results are newest first and have no date filter, so keep following `page[cursor]` until `created_at` is before `<start>`, then keep only the rows inside the window. (`/api/v202506/company_transactions/filter_options` lists the accepted `payment_action` and `status` values.)
4. Compute:
   - Gross revenue (orders before refunds)
   - Refund total and refund rate
   - Net revenue
   - Order count and average order value
   - Top 10 SKUs by units shipped
   - Top 10 SKUs by revenue
   - New vs returning customer split
5. Render as a single Markdown document with one `##` heading per section. Round all dollar figures to whole dollars.
6. End with a "Suggested next steps" section calling out anything notable — refund rate spikes, SKU concentration, etc.
