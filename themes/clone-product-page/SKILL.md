---
name: clone-product-page
description: >-
  Recreate one source product detail page (PDP) as a real Fluid Liquid product
  template with source-backed product data, gallery/options/price states,
  responsive behavior, and visual evidence. Use for PDP, product page, product
  detail, or product-template copying.
---

# Clone Product Page

Call `run_skill("themes/clone-page-to-liquid")` first. Supply this PDP contract
to the universal visual-copy loop.

## Resolve the representative PDP

Prefer the source's visually richest normal PDP. Record why it represents the
template and which special states it does not cover. Use the actual Fluid
product's returned canonical path; never compose a slug.

## Minimum data contract

Reuse an existing matching product. If none renders, import one source-backed
preview product through documented v202604 contracts after verifying
market/currency. Preserve exact title, primary price/currency, real option and
variant combinations, and the priority gallery needed for the page. Record its
source identity and Fluid ID for later catalog reconciliation. Do not start a
bulk catalog import.

## Fluid template contract

- Inspect the scaffold before editing `product/default/index.liquid`.
- Keep its canonical product-data/add-to-cart section first: current scaffolds
  use `product_hero`; older ones may use `main_product`.
- Never fork, replace, or imitate that canonical data section with static
  Liquid.
- Compose subsequent sections in source order: benefits, details/ingredients,
  how-to-use, accordions, reviews, recommendations, or whatever the source
  actually renders.
- Keep product title, price, availability, options, variants, gallery,
  subscription, and recommendations bound to `product.*`.

## PDP evidence and interactions

Classify and compare:

- gallery order, thumbnails, crop, zoom/video, and mobile gallery behavior
- title, badges, rating summary, price/compare-at/subscription formatting
- exact option axes and valid combinations
- quantity, availability, shipping, sticky purchase UI
- description, accordions/tabs, reviews, and related products

Exercise gallery selection, one option change, and every safe disclosure from
rendered selectors. Verify add-to-cart markup/hooks and enabled/disabled states;
do not place an order merely to obtain evidence.

Return the universal `PAGE_OUTPUT` plus:

```text
product_contract:{
  source_product_id,
  fluid_product_id,
  canonical_path,
  canonical_data_section,
  gallery,
  option_states,
  purchase_state,
  related_state
}
```
