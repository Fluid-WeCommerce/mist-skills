# 05 — Validation gates G0–G7

Every gate **reads state back**. None trusts the screen. A gate either auto-repairs
(idempotent, bounded) or stops with a message naming the exact resource and field.

> A bundle page that merely *looks* right is not evidence. A bundle on a bundle-unaware theme
> renders as a normal product with a working add-to-cart and only dies at checkout; add-to-cart
> failures resolve silently.

---

## G0 — Preflight
Token scope · exactly one `status:"active"` theme · countries, currency symbol and decimal
places · subscription plan inventory · SDK boot tag present on a live storefront page.

## G1 — Discovery
Every candidate classified with evidence · no product both "bundle" and unclassified ·
enrollment bundles flagged unsupported and excluded · every source-page option matched,
ambiguous, or missing — never silently dropped.

## G2 — Config write-back
Re-`GET` each product and diff field-by-field against the plan. Assert:
- `products.bundle_config` is non-empty
- every mutex tuple references an **existing `sort_order`**, ≤2 per set, each group in ≤1 set
- `is_default` is present **inside `config`**
- no customizable group has a nil surviving selection bound
- every `included` group has an explicit price or an explicitly recorded $0 decision
- no group carries `hidden: true` while customizable or inside an exclusive pair

## G3 — Render
Blob present, key count as expected (50 = page scope, 40 = drop) · zero raw `<` inside the
blob script · post-JS `[data-group-id]`/`[data-bb-group]` count matches expectation
**excluding `<template>`s** (the DOM is client-built; a server-side grep matches the templates
and misleads you) · `[data-bb-ready="true"]` · **a non-bundle product on the default template
is byte-untouched** · zero console errors · 390 px with no horizontal overflow.

## G4 — Interaction
Each `selection_type` gates correctly · defaults ≤ max and skip out-of-stock · at-max gives a
real disabled affordance with a reason, or swaps · `max_only` can submit zero · a nil bound
never enables a doomed CTA · subscribe controls appear only where allowed and are locked where
forced · **a real scrolled mouse click** on the CTA *and on a child element of it* (synthetic
`element.click()` can pass where a user click fails).

## G5 — Cart
Capture the request body:
- every entry tagged with `product_bundle_group_id`
- included items **absent** — exclusive-set members **present**
- duplicates collapsed into `quantity`, zero-quantity entries omitted

Then read the cart back:
- exactly one line, `metadata.is_bundle === true`
- every expected child present, **including the ones the server reconstitutes**
- `items[].errors` and `skipped_items` inspected **even on HTTP 200**
- a resolved-`undefined` promise surfaces our error UI
- add the same bundle twice → the lines you expect (re-adding **sets** quantity)

## G6 — Money
Displayed total == cart total == checkout total, in **every pricing mode the company uses**.
Read the recurring subtotal from `cart.recurring[0]` and confirm the PDP disclosed it. Never
accept a silent `$0.00`. Confirm the CV/QV expectation matches the mode (fixed and flat credit
0/0 unless re-entered). Reach the checkout page and read the totals — **do not place an order**.

## G7 — Reusability (the platform proof)
Synthesise a **second bundle with a different shape** — an extra group, nested exclusivity, a
per-item max, a subscription-forced item — and confirm it renders and adds to cart with **zero
code changes and no new template**. Then delete it (**Bundle first, then Product** — reverse
order leaves an orphan whose DELETE 500s forever).

Grep the generated theme for every live id and group title. Any hit fails the gate.

---

## Test-safety rules on a shared company
Creating new templates and products is additive and safe — prefix `[QA]`. **Never** modify the
default product template, an existing bundle template, or the global section row. Never
`fluid theme push --force`. Carts are fine; do not place orders. **Never put markup in a
product title** — titles are emitted into an inline `<script>` and that is live stored XSS.
