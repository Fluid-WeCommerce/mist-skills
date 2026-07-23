---
name: Shipping cost vs. collected
description: Compare what customers were charged for shipping against actual carrier cost, by carrier and region, to find where you're losing money on delivery.
icon: truck
---

# Goal

Find where `{{company.name}}` is eating shipping cost instead of recovering it, broken down by carrier and region, over the last 30 days ending `{{today}}`.

# Steps

1. Call `fluid_api("/api/v202506/orders?filter[created_at_gte]=<30-days-ago>&limit=100", "GET")`, paginating until exhausted. Keep `shipping` (or `current_shipping` — the amount collected from the customer), `shipping_address` (for region), and `order_number`.
2. Call `fluid_api("/api/v2025-06/shipping_methods?limit=100", "GET")` to see the configured shipping methods and their rate structure (`shipping_method_rates`), so collected amounts can be sanity-checked against what the storefront was supposed to charge for each region/weight tier.
3. **Actual carrier cost is not exposed by the Fluid API** — it lives in whatever accounting/reporting system tracks paid invoices (commonly the Exigo reporting database via Connect). Check for it before assuming it's unavailable:
   - Call `list_projects` to see if a database project or Mist app with a reporting connection is active in this workspace.
   - If one exists, run `db_query` for actual shipping spend by carrier/region for the same 30-day window — Exigo reporting connections are SQL Server, so start with `SELECT TOP 20 s.name, t.name FROM sys.tables t JOIN sys.schemas s ON s.schema_id = t.schema_id WHERE t.name LIKE '%ship%' OR t.name LIKE '%freight%' OR t.name LIKE '%carrier%'` to find the right table before writing the real query, and use `sql_answer_card` for the final query so the user gets a saved answer card.
   - If no reporting connection exists, or the query returns nothing, say plainly that this run only covers collected-vs-configured (steps 1-2) and actual paid-cost comparison needs a reporting-database connection.
4. Group collected shipping revenue by destination region (state/country from `shipping_address`) and, if a carrier field is present on the order or shipping method, by carrier. Compute average shipping collected per order per region.
5. If real carrier cost was available from step 3, compute **margin per region/carrier** = collected − actual cost, and flag any region/carrier combination running negative (subsidizing shipping) or with unusually thin margin vs. the rest.
6. If real carrier cost was not available, fall back to flagging regions where collected shipping is meaningfully below what the configured `shipping_method_rates` says it should be for that zone — a likely misconfiguration or a promo (free/discounted shipping) eating margin silently.
7. Render a region/carrier table (orders, avg shipping collected, actual cost if known, margin if known, or configured-rate delta if not) and end with a **Decision**: the single worst-performing region or carrier and the dollar amount it's costing over the period, or — if no reporting connection was available — the concrete ask ("connect an Exigo reporting database to get real carrier-cost margin instead of a configured-rate proxy").
