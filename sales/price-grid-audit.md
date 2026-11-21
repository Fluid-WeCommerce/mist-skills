---
name: Price grid audit
description: Audit every active product's prices across price types, markets and autoship — missing prices, member prices too close to retail, autoship above one-time, markets out of line, kits above their parts and bad compare-at prices — then fix only what you approve.
icon: scale
---

# Goal

Check that {{company.name}}'s prices hold together. In direct sales a product has a retail price, a member or wholesale price, often a preferred price and an autoship price, each in every market and currency. Edits drift those apart one at a time. This skill reads the whole price grid, finds the cells that break the company's own pattern, ranks them by what they cost in money or trust, and applies only the fixes the user approves, one at a time.

Read-only until Step 6. Never invent a price: every fix uses a number the user gives or approves.

# Step 1 — Price types and markets

1. `fluid_api("/api/v2025-06/pricing-tiers", "GET")` gives the price types in `tier_level` order (Retail first, then Wholesale and any custom types). `fluid_api("/api/v2025-06/member-types", "GET")` shows which member type buys at which price type (`pricing_tier`). Tell the user in one line which price types exist and who pays each.
2. `fluid_api("/api/company/v2026-10/markets", "GET")` lists each market, its countries and currencies. If it is refused, use `fluid_api("/api/settings/company_countries", "GET")` and treat each country as its own market.
3. Open a `steps` panel with three questions, each with a default the user can accept:
   - **Home market:** the market with the most completed orders in the last 90 days (count from Step 3's order read if needed; otherwise the first market listed).
   - **Intended gap per price type:** how far below retail each price type should sit. Default: the median gap you measure in Step 4, ±5 points.
   - **Market corridor:** how far a market's price may sit from the home market once converted. Default ±15%.

# Step 2 — Read the grid

1. List active products: `fluid_api("/api/v202604/company/products?filter[status]=active&page[limit]=100", "GET")`, following `meta.pagination.next_cursor` as `page[cursor]`. Keep each product's id, title and whether it is a bundle.
2. Read prices in batches of up to 50 product ids: `fluid_api("/api/v2025-06/prices?product_ids[]=<id>&product_ids[]=<id>…&page[limit]=100", "GET")`, following `page[cursor]` until done. The response carries `price_types`, `markets`, `variants` and sparse `rows`. Each row is one `(variant_id, market_id, currency_code, pricing_tier_id)` cell with `one_time` (`price`, `compare_at_price`, `cv`, `qv`) and `subscription` (a `price`, or `follows_one_time`, or `unset`). A missing row means nothing is priced there. Note `no_fallback`.
3. If the grid is refused (the company isn't on the price editor), read `fluid_api("/api/v202604/company/products/<id>", "GET")` per product instead. Its variants carry each country's price, wholesale price, subscription price and compare price. Audit what's there and tell the user once that per-price-type rows weren't available.
4. For each bundle product, `fluid_api("/api/v2025-06/products/<id>/bundle-prices", "GET")` gives the bundle's own cells and its groups' in-kit items. Kits from `fluid_api("/api/v202604/company/enrollment-packs", "GET")` and `/{id}` list their products.

# Step 3 — Read what sold (for ranking)

`fluid_api("/api/v202506/orders?status=completed&start_date=<90 days ago>&end_date={{today}}&page[limit]=100", "GET")`, paged by cursor, gives the last 90 days. For each product, count units and revenue per market from `GET /api/v202506/orders/<id>` lines (`price`, `discount_amount`, `quantity`, the order's `country` and `currency_code`). Above 2,000 orders, sample the most recent 2,000 and say so. Also count active autoships per product with `fluid_api("/api/subscriptions?status=active&search=<product title>&per_page=100", "GET")` for the products you flag. Don't do this for every product.

# Step 4 — Run the checks

Compare like with like: same variant, market, currency and purchase type.

| # | Check | Flag when | Severity |
|---|---|---|---|
| P1 | **Missing price** | A variant sold in a market (ordered there in 90 days, or the market is its product's only one) has no Retail one-time row, or a price type a member type buys at has no row | Critical if it sold in 90 days, else High |
| P2 | **Tier inverted** | A lower-tier price type (member, wholesale, preferred) is at or above Retail for the same cell | Critical |
| P3 | **Tier gap off pattern** | A price type's gap below Retail is outside the intended band | High for a top-20 seller, else Medium |
| P4 | **Autoship above one-time** | A `subscription.price` is higher than the same cell's `one_time.price`, or the market offers autoship and the row is `unset` where `no_fallback` is true | High |
| P5 | **Market out of corridor** | Converted to the home currency, a market's Retail price sits outside the corridor | Medium (High for a top-20 seller) |
| P6 | **Kit above its parts** | A bundle or kit price is higher than the sum of its items' own prices at the same price type, market and currency | High |
| P7 | **Bad compare-at price** | `compare_at_price` is at or below `price` (shows no saving), or more than double it, or set on a product that sold at no price near it in 90 days | Medium; savings claims go to the user to confirm |
| P8 | **Odd price ending** | A market's prices mostly end one way (.99, .95, .00) and this one doesn't, usually after a currency conversion | Low |

For P5, get each currency's rate with `run_cli` `fluid countries prices <ISO> --from-country <home ISO>` with no `--write`. The dry run reports the reference rate and its date and changes nothing. State the rate and date beside every converted figure. Tax-inclusive markets: compare with the home market's price plus that market's standard rate, and say so.

For P2 and P3, if prices differ by rank among reps who resell to each other, add one line: different prices for competing resellers can carry legal risk, so the user may want counsel to look at it. Don't call it unlawful.

# Step 5 — Report, ranked

Lead with one sentence: how many products, cells and markets you checked, and how many findings by severity.

Then a table sorted by severity, then by 90-day revenue: product, market, price type, check, what's stored, what the pattern expects, autoship customers affected, and the proposed fix. Quote stored values exactly. Group repeats ("14 products: member price within 5% of retail") instead of listing every cell.

End with the single change worth making first and why, in plain words.

# Step 6 — Approved fixes, one at a time

Go through findings in report order. For each, show the cell, the current value and the proposed value, then gate it with `human_in_the_loop` (title `Change <product> <price type> price in <market>`). On approval:

- **One or a few cells:** `fluid_api("/api/v2025-06/prices", "PATCH", {"cells": [{"variant_id": …, "market_id": "…", "currency_code": "…", "pricing_tier_id": "…", "purchase_type": "one_time" | "subscription", "price": "…"}]})`. Add `"compare_at_price": null` to clear a bad compare-at price. The batch is all-or-nothing: if a cell is refused, read the per-cell reason, tell the user, and don't retry blindly.
- **A whole market's missing prices from a currency conversion:** `run_cli` `fluid countries prices <ISO> --from-country <home ISO>` to preview, then, after approval, the same command with `--rate <reviewed rate> --write --yes`. It fills only prices the market doesn't have. If the company's prices are managed in the price editor, it says so; then change existing prices there or with the cell write above.
- **A kit:** recommend a price; bundle grids carry lock tokens and belong in the admin bundle price editor. Don't write them from this skill.
- Never write bulk variant prices any other way.

Before you raise any price that autoship customers pay, show how many active autoships hold that variant and their next bill dates. If any renew within 30 days, say the change needs a notice to those customers first (California's auto-renewal law asks for 7 to 30 days' notice of a price change) and offer to move the change date instead. Don't send notices from this skill.

After each write, read the cell back with `fluid_api("/api/v2025-06/products/<product_id>/prices", "GET")` and confirm the new value.

# Step 7 — Record

Write `pricing/price-grid-audit-{{today}}.md` in the active project with the settings used (home market, gaps, corridor, rates and dates), the findings table, what was changed (before → after) and what was left for a person. That file is the baseline for the next audit's "what drifted since last time".

# Gotchas

- `rows` are sparse. No row means unpriced; it doesn't mean zero. A row whose `one_time` is null is also unpriced.
- `subscription.follows_one_time` means the autoship price is the one-time price. That's not a finding.
- Prices are decimal strings. Compare numerically, in the row's own currency, before converting.
- `unwritable_system_cells` on a variant lists cells the price editor won't take. Skip those fixes and say why.
- Archived price types and Preferred are refused on write. Report them; don't try to write them.
