---
name: Free Shipping Cart Nudge
description: Finds a company's real free-shipping threshold and cart gap, then builds a live cart-nudge section with product recommendations to close it.
icon: shopping-cart
---

# Goal

Build a real, live cart-page feature for {{company.name}} — not a report. The
output is a section that tells a shopper exactly how much more to add to
unlock free shipping, and recommends specific products that would get them
there, computed from this company's *actual* configuration and data. Nothing
here is hardcoded from another company's numbers; every threshold, gap, and
recommendation comes from what you discover for the company you're running
against.

# Steps

1. Find the real free-shipping threshold — do not assume a number or trust a
   single settings field at face value. Shipping in this platform can be
   configured under more than one pricing model (check Settings → Shipping):
   **Product-based Rates** (per-variant, no cart-level threshold possible —
   fields like a company's `base_shipping` can return `200` on write without
   the value actually taking effect), **Flat Country Rates**, **Use a
   Droplet**, or **Fluid Rates** (tiered by price or weight — this is the
   only model with a genuine subtotal threshold). If **Fluid Rates** isn't
   the active model, or its Rate Type isn't **Price-based**, there is no real
   free-shipping threshold to nudge toward — stop and report that plainly
   rather than inventing one. When Price-based Fluid Rates is active, read
   the rate table for the tier whose price is `0` and record the `min`
   subtotal of that tier as the threshold, plus the currency. Cross-check
   with a real cart quote via the checkout API before trusting the rate
   table alone — a written rule and the live quoted rate should agree.
2. Learn what a typical cart actually looks like — pull recent real
   order/cart data (via the Reporting Database if connected, otherwise the
   orders/carts API) to find the median cart subtotal and how far below the
   threshold it typically sits. If there's no order history and no connected
   reporting database, don't block: fall back to catalog pricing alone to
   estimate a plausible gap, and say explicitly in your final report that the
   picks below are based on catalog pricing, not purchase behavior.
3. From the product catalog, pick 2-4 low-to-mid-priced, in-stock products
   that could plausibly close a typical gap (e.g. a $12-18 gap wants a ~$15
   product, not a $60 one). Record each one's real price and why it was
   chosen. A recommendation only counts if its price is at least the
   remaining gap — a $6.66 item recommended for a $7.34 gap doesn't actually
   unlock anything; filter on `price >= remaining`, not just "cheap."
4. Build the section into the theme: a new Liquid cart-page section (and the
   cart drawer/mini-cart if it fits cleanly) that reads the *live* cart total
   against the threshold from step 1 — never a hardcoded amount, and expose
   the threshold itself as a schema setting so it isn't buried in the Liquid
   code. Below threshold, show a message naming the remaining dollar amount
   and "away from free shipping"; at or above it, a clear "You've unlocked
   free shipping" state. Show the products from step 3 with quick add-to-cart.
   Reuse the theme's existing cart data and section/component conventions
   rather than inventing a new pattern.
5. Verify before calling it done — use `screenshot_preview` on the cart page
   at three real cart states: well below the threshold, just under it, and
   at/above it. Confirm the copy, the math, and the recommended products all
   render correctly at each state. If the cart is empty, add a temporary test
   item, verify, then remove it — never leave test data behind.
6. Report the business case, not just the build: the exact threshold and
   currency discovered, the median (or catalog-estimated) gap, the specific
   products recommended and why, and a clearly-labeled *estimate* of impact
   (e.g. "if N% of below-threshold carts add one recommended item, that's
   roughly $X in incremental order value") — label it as an estimate, since
   it's projected from historical data, not from carts that have actually
   seen the new nudge yet. This is what turns the build into something a
   non-technical reader can act on without reading the code.
