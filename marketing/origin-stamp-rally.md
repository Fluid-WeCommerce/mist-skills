---
name: Origin Stamp Rally
description: Transform each customer’s order history into a stamp-rally passport of product origins, then craft personalized emails featuring the exact product that completes their collection.
icon: stamp
---

# Origin Stamp Rally

A stamp rally (スタンプラリー) is the Japanese loyalty mechanic where you collect a stamp at every station and can't stop until the card is full. This skill turns {{company.name}}'s catalog into the rally map and every customer's order history into their passport: which origins they've collected, which stamps they're missing, and a ready-to-send nudge that sells exactly the product that fills the next slot.

Built for catalogs where products have a place of origin — coffee and tea by country, wine by region, chocolate by plantation. Anything with a "from somewhere" story works.

# Steps

## 1. Build the rally map from the catalog

1. Pull the full catalog via the company products API — `fluid_api("/api/v202604/company/products?limit=100", "GET")` (fall back to the newest products index the API exposes) — following `meta.pagination.next_cursor` until it's null.
2. For each product, infer its **origin** from the title, subtitle, and description (e.g. "Ethiopia Guji", "Colombia Huila", "Uji Matcha" → Japan). Normalize to a country or named region, one origin per product.
3. Products with no inferable origin (merch, gift cards, grinders) are **off the rally** — list them in one line so the user can see what was excluded, but don't count them anywhere.
4. Show the rally map: every origin, its flag emoji, and the products that stamp it. Ask the user to confirm or correct the mapping in one message (e.g. "Sumatra should be Indonesia") — then continue with their corrections. If the mapping is unambiguous and the user asked to just run it, confirm in one line and proceed.

## 2. Stamp the passports

1. Pull completed orders from the live orders API (e.g. `fluid_api("/api/v2/orders?status=completed&limit=100", "GET")`, or the newest orders index available), following pagination until exhausted. Use full history, not a window — stamps never expire. `limit` may not be strictly honored; paginate by cursor, not by counting rows. Read from the live API, never the company reporting database — it is a lagging replica and will undercount both products and orders.
2. For each order capture `customer.email`, `customer.full_name`, the line items' product names, and `created_at`. Map every line item to its origin from step 1.
3. Build one passport per customer: origins collected (with first-collected date), stamps missing, completion percent, and last order date.

## 3. Present the rally

1. Lead with the wall-of-fame table, sorted by stamps collected then most recent order: customer, passport (flag emoji run like 🇪🇹🇨🇴🇬🇹 · 3/8), missing stamps, last order.
2. Call out three groups by name:
   - **One stamp from finishing** — the goldmine. Completing a card is the strongest nudge in the rally.
   - **Streak at risk** — 60%+ complete but no order in 45+ days.
   - **Fresh passports** — exactly one stamp; the second stamp is the habit-former.
3. Total the picture in one line: average completion, most-collected origin, and the rarest stamp (the origin almost nobody owns — that's a marketing angle by itself).

## 4. Draft the next-stamp nudges

1. Offer to draft nudge emails for the three groups above; wait for the user to pick before writing.
2. Each draft is personal and specific: greet by first name, show their passport row (their actual flags), name the missing origin, and pitch the exact product that stamps it — subject line included. Keep each under 120 words; collector's pride is the hook, not a discount.
3. Do NOT send or dispatch anything — no send tool exists for this in Mist Desktop. Hand back the drafted copy for the user's own outreach channel.

## Empty states

- **No completed orders yet** (a brand-new shop): still build and show the rally map from the catalog, render one blank passport as a preview of what customers will see, and say plainly that passports start stamping with the first completed order.
- **Catalog has no inferable origins at all**: stop and say so — this skill only earns its keep on an origin-story catalog — and suggest the closest alternative (e.g. collect by product line instead, if the user wants to adapt the idea).
