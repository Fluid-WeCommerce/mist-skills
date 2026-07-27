---
name: clone-shop-page
description: >-
  Reconstruct the source store's canonical all-products/shop listing in a
  Fluid theme, including real product cards, filters, sorting, search,
  pagination, responsive behavior, and exact source evidence.
---

# Clone Shop Page

Own one canonical product-list route: the source shop/all-products index mapped
to the equivalent Fluid local route.

Follow
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
in full. This file adds shop/PLP-specific requirements.

## Find the real shop route

Do not assume `/shop`. Discover it from:

1. the rendered desktop/mobile navigation
2. sitemap and collection/category indexes
3. links labeled Shop, All Products, Catalog, Store, or equivalent
4. final redirected URL and page body

Distinguish:

- a dedicated all-products/shop index
- a collection index
- one collection detail page
- search results masquerading as an all-products view

If the source has no dedicated shop route, use its primary all-products list
and record the fallback. Do not invent a source page that does not exist.

Write the chosen source URL and exact Fluid `built_path` to
`clone-manifest.json.visual_routes.shop`.

## Source inventory

Capture exact desktop/mobile HTML and full-page screenshots. Record:

- header/banner/breadcrumbs
- result count and page title
- product-card fields and their exact order
- grid columns, gaps, card aspect ratio, hover/alternate image behavior
- badges, ratings, swatches, price/compare-at/subscription formatting
- filters, selected-filter chips, clear-all behavior, and filter counts
- sorting options and default sort
- search affordance and no-results state
- pagination, infinite scroll, or load-more behavior
- mobile filter/sort drawers
- SEO/editorial content above or below the grid

Inventory at least three representative card states when the source exposes
them: ordinary, discounted/badged, and multi-option or unavailable.

## Fluid data mapping

The page must render actual Fluid resources:

- enumerate the destination products through documented v202604 pagination
- use raw `status == "active"` and `active == true`
- use DAM-backed product imagery
- keep price, country currency, inventory, badges, and links dynamic
- map collection/category membership from real IDs
- use canonical credit-prefixed detail routes returned by Fluid

Never hard-code a handful of source product cards to make the screenshot look
right. If the import is incomplete, fail with the exact missing resource
evidence instead of hiding it in the theme.

Filtering, sorting, search, and pagination must use the canonical Fluid
capability available in the current scaffold/API. If a source behavior has no
Fluid equivalent, implement the closest honest dynamic behavior and itemize the
difference. A decorative nonfunctional control is a major defect.

## Reusable list contract

Extract and report the reusable list-page pieces later collection/category
skills should consume:

- product-card component/section path
- grid tokens and breakpoints
- filter/sort control paths and state contract
- pagination/search behavior
- empty/loading/error states

Do not copy the shop implementation wholesale into every collection.

## Required interaction proof

Using inspected rendered selectors:

- change one sort option and prove card order/state changes
- apply and clear one real filter when the source offers filters
- open/close mobile filter or sort disclosure
- exercise load-more/pagination/infinite-scroll behavior
- open a representative product and verify the canonical Fluid PDP route
- verify no-results/empty state when safely reachable

Read the DOM again after state changes. A click with no observed result is not
proof.

## Materialize the shared audit

This page skill intentionally does not declare another skill's script as its
own asset. Mist sandboxes assets to their owning skill directory.

Before the final audit, call `run_skill("themes/theme-clone")` to materialize
that skill's bundled `theme_audit.py`. Use the exact materialized script path
returned by the tool and run it only against the touched theme files. Do not
restart the broad theme-clone workflow or weaken this page's narrower gate.

## Shop pass

In addition to the shared gate:

- signed `compare_preview_to_source` receipts prove the selected shop
  source/local pair at 1440 × 900 and 390 × 844 after the final shop code
  change, bind each source screenshot to its rendered-evidence sidecar, and
  report exact, non-truncated ordered copy. When the signed source final
  pathname differs from the Fluid `built_path`, pass it as `source_route` and
  keep `path` set to the Fluid route; never rewrite either side just to make
  their platform-specific pathnames equal
- the selected source route is truly the canonical shop/all-products list
- exact source wording and visible card fields match
- the complete expected Fluid product set is reachable through the page's
  pagination model
- cards use real product data and correct canonical routes
- filters/sort/search/pagination are functional or the exact unsupported gap is
  a declared major
- representative product-card states match at desktop and mobile
- reusable list contracts are recorded for dependent page skills

Do not fan out collection/category/PDP work until this page passes.
