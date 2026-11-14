---
name: Shipping cost vs. collected
description: Compare what customers were charged for shipping against actual carrier cost, by carrier and region, to find where you're losing money on delivery.
icon: truck
---

# Goal

Find where `{{company.name}}` is eating shipping cost instead of recovering it, broken down by carrier and region, over the last 30 days ending `{{today}}`.

# Steps

1. Call `fluid_api("/api/v202506/orders?start_date=<30-days-ago>&end_date={{today}}&limit=100", "GET")`, paginating via `meta.pagination.next_cursor` until exhausted. Use `start_date`/`end_date` — `filter[created_at_gte]`-style bracket params are silently ignored by this endpoint (no error, it just returns the unfiltered set), so don't use them anywhere in this skill. Keep `shipping` (or `current_shipping` — the amount collected from the customer), `shipping_address` (for region), and `order_number`. If `meta.pagination` comes back as `{}`, there were zero orders in the window — say so rather than reporting $0 margin as if it were measured.
2. Call `fluid_api("/api/v2025-06/shipping_methods?limit=100", "GET")` to see the configured shipping methods and their rate structure (`shipping_method_rates`), so collected amounts can be sanity-checked against what the storefront was supposed to charge for each region/weight tier.
3. **Actual carrier cost is not exposed by the Fluid API** — it lives in whatever accounting/reporting system tracks paid invoices (commonly the Exigo reporting database via Connect). Check for it before assuming it's unavailable, but be precise about what `db_query`/`sql_answer_card` can actually reach: **both only ever operate against the ACTIVE PROJECT's own database connection** — there's no way to point either tool at a different project's connection that `list_projects` merely reports exists.
   - Call `list_projects` first — only to see whether a reporting-database project (or a Mist app, which has its own database) exists in this workspace at all. It does NOT give you a way to query that project from here if it isn't the one you're currently in.
   - If the **active project itself** is that reporting-database connection, run `db_query` for actual shipping spend by carrier/region for the same 30-day window — Exigo reporting connections are SQL Server, so start with `SELECT TOP 20 s.name, t.name FROM sys.tables t JOIN sys.schemas s ON s.schema_id = t.schema_id WHERE t.name LIKE '%ship%' OR t.name LIKE '%freight%' OR t.name LIKE '%carrier%'` to find the right table before writing the real query. Follow with `sql_answer_card` for the final query **only if the active project is a "database" kind project** (it's the only kind `sql_answer_card` works on — on a Mist app project, stick with `db_query` for the answer instead, since `sql_answer_card` will refuse there).
   - If `list_projects` shows a reporting-database project exists but it ISN'T the one you're currently running in, don't attempt `db_query` against it — tell the user to open that project and re-run this skill there for real carrier-cost detail.
   - If no reporting connection exists anywhere, or the query returns nothing, say plainly that this run only covers collected-vs-configured (steps 1-2) and actual paid-cost comparison needs a reporting-database connection.
4. Group collected shipping revenue by destination region (state/country from `shipping_address`) and, if a carrier field is present on the order or shipping method, by carrier. Compute average shipping collected per order per region.
5. If real carrier cost was available from step 3, compute **margin per region/carrier** = collected − actual cost, and flag any region/carrier combination running negative (subsidizing shipping) or with unusually thin margin vs. the rest.
6. If real carrier cost was not available, fall back to flagging regions where collected shipping is meaningfully below what the configured `shipping_method_rates` says it should be for that zone — a likely misconfiguration or a promo (free/discounted shipping) eating margin silently.
7. Render a region/carrier table (orders, avg shipping collected, actual cost if known, margin if known, or configured-rate delta if not) and end with a **Decision**: the single worst-performing region or carrier and the dollar amount it's costing over the period, or — if no reporting connection was available — the concrete ask ("connect an Exigo reporting database to get real carrier-cost margin instead of a configured-rate proxy").
