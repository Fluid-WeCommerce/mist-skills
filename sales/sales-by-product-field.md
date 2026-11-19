---
name: Sales by product field
description: Break the last 90 days of sales down by any custom product field (material, supplier, collection line) kept as a variant metafield, with units, revenue and share per value.
icon: bar-chart-3
---

# Goal

Answer "what did we sell last quarter by <fabric / supplier / designer / scent / any custom field>?" for {{company.name}} using the custom data already stored on products, so merchandising and buying decisions rest on numbers instead of a spreadsheet pass.

# Steps

1. Ask which field to group by if the user has not said. Then list the candidates: call `fluid_api("/api/company/v1/products?per_page=50&page=1", "GET")`, open the first two products with `fluid_api("/api/company/v1/products/<id>", "GET")`, and collect the `namespace` and `key` of every entry in each variant's `metafields`. Show the distinct `namespace.key` pairs (with `metafield_definition.name` when present) and let the user pick one. If no variant has metafields, stop and say plainly that this store keeps no custom product data to group by, and name the one product you checked.
2. Build the lookup from variant to field value. Page through products (`page` from 1 while a page returns products, `per_page=50`, `status[]=active` and `status[]=draft`). For each product, read its variants from `GET /api/company/v1/products/<id>` and record, per variant `sku`, the `value` of the chosen `namespace.key` in `metafields`. Variants with no such entry map to `(not set)`. Keep SKU as the join key, since order lines carry `sku`. If the same SKU appears on more than one variant and those variants have different values for the field, mark that SKU `ambiguous` instead of picking one; if they share the same value, it is safe to use.
3. List the orders to analyze: `fluid_api("/api/v202604/orders?filter[status]=completed&filter[start_date]=<start>&filter[end_date]={{today}}&page[limit]=100", "GET")`, passing `meta.pagination.next_cursor` back as `page[cursor]`. Set `<start>` to the date 90 days before `{{today}}` (work it out yourself; there is no token for it). If the window has no orders, stop and report that.
4. For each order id, call `fluid_api("/api/v202506/orders/<id>", "GET")` and read `order.items`. For every line with `quantity` above 0, look it up by the line's variant id when the order line carries one (`variant.id` or `variant_id`), and by its `sku` in the map from step 2 otherwise and add `quantity` to units and `total_after_discounts` (fall back to `total` when it is null) to revenue under that field value. Lines whose SKU is not in the map go to `(unmatched SKU)`: a deleted variant or a custom line. Lines whose SKU is `ambiguous` go to `(ambiguous SKU)`; never assign them to a value.
5. Render a table per field value: units, revenue, share of revenue, and average unit price, sorted by revenue descending. Show `(not set)`, `(unmatched SKU)` and `(ambiguous SKU)` as their own rows with their share, so the reader sees how much data is missing.
6. If `(not set)`, `(unmatched SKU)` and `(ambiguous SKU)` together exceed 20% of revenue, say the grouping is unreliable and name the five highest-revenue SKUs missing the field so someone can fill it in.
7. Close with ONE recommendation grounded in the table, for example "supplier <X> is N% of revenue but only M% of SKUs, so reorder depth there matters most", or "fabric data covers only P% of revenue, so fill it in before using this to plan buys."

# Notes

- SKU matching is a best effort: an order line can reference a variant that was later discarded, and its SKU may now belong to a current variant. The API does not let this skill detect that, so when a line has no variant id, state in the output that SKU-matched figures can be off for reused SKUs.
- Read-only: this skill never writes to products or orders.
- Revenue is line totals after discounts, in each order's own currency. Render one table per `currency_code` (read it from the order) with shares and average unit prices computed within that currency only; never add amounts across currencies.
