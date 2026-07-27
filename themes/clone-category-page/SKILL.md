---
name: clone-category-page
description: >-
  Recreate a source category index or category detail page as a Fluid Liquid
  category route with real category/product data, responsive list behavior,
  interactions, and visual evidence. Use when the source distinguishes
  categories from collections or shop/all-products pages.
---

# Clone Category Page

Call `run_skill("themes/clone-page-to-liquid")` first. Supply this category
contract to the universal visual-copy loop.

## Classify the route

Prove whether the source route is:

- a category index
- one category detail
- a collection/list page using different source terminology

Do not coerce every merchandising list into a Category. Record the source
navigation/sitemap/body evidence supporting the classification.

## Minimum data contract

Reuse the matching Fluid Category and products. If missing, create/reconcile
one source-backed preview Category and at most three representative products
through documented v202604 contracts after verifying market/currency. Record
all created IDs; do not await a complete catalog.

## Fluid template contract

- Use the scaffold's `category_index` for an index and `category_showcase` for
  a detail route when those canonical sections can express the source.
- Keep category title, description, image/editorial content, product
  membership, filters/sort, cards, and canonical links dynamic.
- Reuse the Shop product-card/list contract instead of cloning a second grid.
- Add a slug-specific template only when the source proves a different
  structure from the normal category template.

## Category proof

Compare the source-specific banner/editorial modules, grid, card fields,
filters/sort, pagination/load-more, empty state, and mobile disclosures.
Exercise available list controls and verify one card reaches its actual Fluid
PDP path.

Return the universal `PAGE_OUTPUT` plus the category resource IDs, index/detail
classification, reusable list contract, and unsupported source behaviors.
