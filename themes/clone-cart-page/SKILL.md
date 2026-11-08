---
name: clone-cart-page
description: >-
  Recreate a source cart page or cart drawer as the Fluid `cart_page` route with
  real line items, quantity controls, totals, promo entry, upsells, and a
  working path to checkout. Use after the PDP establishes add-to-cart.
---

# Clone Cart Page

Call `run_skill("themes/clone-page-to-liquid")` first. Supply this cart contract
to the universal visual-copy loop.

Follow
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
in full. This file adds cart semantics.

## Cart is a state, not just a URL

A cart cannot be inspected by loading a URL — an empty cart renders a different
page from a populated one. Before capturing source evidence:

1. Add one representative product to the source cart via the real add-to-cart
   control, using `interact_preview` against the source or a documented cart
   permalink where the source supports one.
2. Capture the POPULATED cart at both viewports.
3. Capture the EMPTY cart state separately — it is a real, frequently-seen page
   with its own copy and CTA, and it is routinely missed.

Determine which surface the source actually uses as its primary cart:

- a full cart page at `/cart`
- a slide-out cart drawer that never navigates
- a modal/popover confirmation after add-to-cart
- some combination — a drawer plus a full page reachable from it

Record the answer. Fluid's `cart_page` route must exist and be correct even when
the source leads with a drawer; if the source is drawer-primary, reproduce the
drawer in the shell and keep the full page as a consistent fallback. Report the
divergence rather than silently shipping only one.

## Minimum data contract

At least two distinct line items with different quantities, so quantity
controls, per-line totals, and subtotal math are all observable. Use products
already imported by the catalog steps. If the catalog is empty, create at most
two source-backed preview products through documented v202604 contracts after
verifying market and currency.

Currency and price formatting must match the company's market. A cart rendering
the wrong currency symbol is a hard failure, not a cosmetic delta.

## Fluid template contract

- Build `cart_page/default` using the scaffold's `main_cart` section.
- Keep line items, quantities, per-line and order totals, discounts, shipping
  estimates, and the checkout CTA dynamic and bound to real cart state.
- Never hardcode a line item or a subtotal to make a screenshot look right —
  totals that do not recompute are the defining failure of a cloned cart.
- Reuse the PDP's product-card/image contract for line-item thumbnails.

## Cart-specific inventory

Capture and compare:

- header/title and item-count wording, including its singular/plural form
- line item layout: thumbnail, title, variant/subscription label, unit price,
  quantity control, line total, remove control
- quantity control style (stepper, dropdown, free text) and its bounds
- promo/discount code entry and its applied and rejected states
- order summary: subtotal, discounts, estimated shipping, tax, total
- shipping-threshold progress bar, which is very common and easy to miss
- upsell / "you may also like" rail
- trust badges, accepted payment marks, and return-policy microcopy
- checkout CTA plus any express payment buttons, classified as `external`
- gift/note/delivery-instruction fields
- the empty-cart state: illustration, copy, and its CTA target

## Required interaction proof

Static screenshots cannot prove a cart. Exercise from inspected selectors:

- increment and decrement a quantity, and confirm the line total AND order
  total both recompute correctly
- remove a line item and confirm the cart and item count update
- submit an invalid promo code and confirm the rejected state renders
- reach the empty state and confirm its CTA resolves
- confirm the checkout CTA navigates to the real Fluid checkout — a cart that
  looks perfect and cannot check out is a hard failure

## Cart pass

In addition to the shared gate:

- both populated and empty states are built and evidenced at both viewports
- totals recompute correctly under quantity change and line removal
- currency and price formatting match the company market
- the checkout CTA reaches real Fluid checkout
- the source's primary cart surface (page vs drawer) is recorded, and any
  divergence from it is reported rather than hidden

Return the universal `PAGE_OUTPUT` plus the source cart surface type, the line
items used, the recomputation evidence, and any source cart behavior Fluid
cannot express.
