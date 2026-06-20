---
name: Monthly close report
description: Generate a one-page financial summary for the most recently completed calendar month.
icon: file-text
---

# Goal

Produce a month-end close report for `{{company.name}}` covering the most recently completed calendar month.

# Steps

1. Compute the date window: the first and last day of the previous calendar month relative to `{{today}}`.
2. Pull orders via `fluid_api("/api/v202604/orders?filter[created_at_gte]=<start>&filter[created_at_lte]=<end>&limit=100", "GET")`. Paginate via the cursor.
3. Pull refunds via `fluid_api("/api/v202604/refunds?filter[created_at_gte]=<start>&filter[created_at_lte]=<end>&limit=100", "GET")`.
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
