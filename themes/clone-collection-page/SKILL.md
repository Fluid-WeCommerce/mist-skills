---
name: clone-collection-page
description: >-
  Recreate a source collection index or collection detail page as a Fluid
  Liquid collection route with real collection/product data, merchandising
  modules, responsive interactions, and visual evidence.
---

# Clone Collection Page

Call `run_skill("themes/clone-page-to-liquid")` first. Supply this collection
contract to the universal visual-copy loop.

## Classify the route

Distinguish a collections index, one collection detail, the global Shop route,
and a Category. Preserve the source's real information architecture rather
than treating these labels as synonyms.

## Minimum data contract

Reuse a matching Fluid Collection. If none renders, create/reconcile one
source-backed preview Collection and at most three representative products
through documented v202604 contracts after verifying market/currency. Record
all IDs for later catalog reconciliation. Full collection completeness is not
a page-copy prerequisite.

## Fluid template contract

- Use `collection_index` for the collection index and `collection_showcase`
  for detail where the scaffold supports them.
- Reuse the Shop card/grid/filter contract.
- In Liquid, the `collections` global is not the REST shape. Read `c.image`,
  `c.url`, and `c.products`; never depend on `c.product_collections`.
- Use the image fallback chain `c.image` → `c.image_url` → `c.image_path` →
  first product image.
- Do not calculate `c.products.size` across a large index. Cap visible
  collections and keep counts optional.
- Add a slug-specific template only for a source-proven structural variant.

## Collection proof

Compare collection title/description/media, merchandising modules, product
grid, card states, filters/sort, pagination, empty state, and mobile controls.
Verify one actual product link and, for an index, one actual collection link.

Return the universal `PAGE_OUTPUT` plus the collection IDs, index/detail
classification, reusable list contract, and unsupported source behaviors.
