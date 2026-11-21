---
name: Agent Checkout Dry Run
description: Walk a store's public cart path the way a shopping agent would, in each country it sells in, and report where an agent gets stuck before payment (unavailable items, missing prices, enrollment-only or subscription-only products, countries that fail), without placing an order.
icon: shopping-cart
category: marketing
---

# Goal

Shopping agents that drive a store's own checkout now place most agentic orders, and they buy at far more stores than the agents that wait for a store to adopt a protocol. They also stop at the first thing that needs a human: a product that cannot be added to a cart, a price that is missing in the buyer's country, a cart that only works as an enrollment or subscription. Find those stops for {{company.name}} before an agent does, and tell the merchant in plain words which products and countries lose an agent-driven sale.

This skill starts a few throwaway carts and reads them back. It never completes an order, never touches payment, never signs a shopper in, and never changes the catalog.

Today is {{today}}.

# Steps

1. **Pick what to test.**
   - `run_cli` `fluid countries list` - the countries the store sells in. Test at most 5; take the store's default country first, then the countries with the most products live.
   - `fluid_api("/api/v202604/products?country=<ISO>&page[limit]=25", "GET")` for each country - the public catalog, live products only, with `variants` and a price per country. Follow `meta.pagination.next_cursor` as `page[cursor]` for a second page only if the first has fewer than 25 products.
   - Choose up to 12 products per country: the first 8 listed, plus up to 4 that have a subscription plan, are bundles, or have more than one variant. Note each product's title, price, stock (`available`) and whether it lists `subscription_plans`.
2. **Check the catalog the agent sees.** For every chosen product, flag: no price in this country; zero units available; no variant sellable in this country; a description under 40 words (an agent has nothing to compare); no image. These are findings even if the cart step works.
3. **Start a throwaway cart per country.** Show the user the plan first: how many carts, in which countries, and that none will be paid for. Then, for each country, one cart per product group:
   - `fluid_api("/api/checkout/v2026-04/carts", "POST", { "fluid_shop": "{{company.subdomain}}", "country_code": "<ISO>", "items": [ { "variant_id": <id>, "quantity": 1 } ] })` using the first available variant of one product. The endpoint is public: if it asks for a sign-in, that is itself a finding, because an agent will not have one.
   - A `422` means the item is unavailable, the country is not set up, or a re-enrollment rule blocked it. Record the message verbatim next to the product.
   - Keep each `cart_token`.
   - Cap: 20 carts in the whole run. Stop early if three in a row fail the same way and report that one cause.
4. **Read each cart back.** `fluid_api("/api/checkout/v2026-04/carts/<cart_token>", "GET")`. Record: currency and totals present; line price equals the catalog price from step 1 (a mismatch is a finding, and agents notice); available shipping methods listed or not (an address is not set, so an empty list may only mean no address yet: say which); whether the cart is marked as enrollment, or a line is subscription-only.
5. **Group the stops.** Put every finding in one of these groups: **Blocks the cart** (cannot add, 422, sign-in demanded), **Needs a human** (enrollment-only, subscription-only, no shipping method for the country), **Wrong or missing data** (price mismatch, no price, no stock figure), **Thin data** (short description, no image). Count how many of the tested products land in each group, per country.
6. **Do not place or pay.** Never call `/complete`, `/payment`, `/auth`, `/points` or the enrollment endpoint, and never set an address. Leave the carts to expire; do not try to delete them.
7. **Report.** Open with one sentence: of N products tested in M countries, how many an agent could take to the point of payment. Then the four groups as tables (product, country, what happened, who fixes it: merchant, catalog data, or Fluid support). End with the three fixes that would unblock the most products. List the countries and products not tested so the user knows the limits. Ask whether to save the report to the workspace as `agent-checkout-dry-run.md`; write it only after they say yes.

# What this skill does not do

It does not drive a real browser, run a purchase, or tell the merchant whether a particular AI shopping agent is allowed on the store: that is the merchant's own bot and access policy. It does not judge claims in product copy; use Brand Agent Brief for that. It reads the public cart path only, so anything behind sign-in (wholesale pricing for members, saved cards) is outside its view.
