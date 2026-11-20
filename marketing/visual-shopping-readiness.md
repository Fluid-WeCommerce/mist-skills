---
name: Visual shopping readiness
description: Audit the live catalog for what AI shopping agents and virtual try-on need (a primary image, several images per product, size and color options, a real description) and list the products to fix first.
icon: scan-search
category: marketing
---

# Goal

AI shopping agents (Meta's Muse added virtual try-on on Nov 18) pick products by looking at images and structured attributes. Check which products at {{company.name}} give an agent enough to show and sell them, and list what to fix first. Read-only: this skill never edits products.

# Steps

1. Ask which products to audit if the user has not said: all active products, or only a category the user names (apparel, footwear, accessories). Default to all active products. Tell the user the audit makes one detail call per product and give the count before you start.
2. List the products: `fluid_api("/api/company/v1/products?status[]=active&per_page=50&page=1", "GET")`, increasing `page` until a page returns no products. For each row keep `id`, `title`, `sku`, `image_url` and `in_stock`. If the user named a category, ask for the tag ids to filter on and add `tag_ids[]=<id>`.
3. For each product call `fluid_api("/api/company/v1/products/<id>", "GET")` and read `product.variants`, `product.image_url` and, when the response includes it, the `images` list and `description`. Not every response carries `images` or `description`. When a field is absent for the whole store, say so once and drop that check instead of scoring every product down for it.
4. Score each product on these checks:
   - **Primary image:** `image_url` is present. Missing is BLOCKED.
   - **Image depth:** at least 4 entries in `images` (front, back, detail, on-model). Fewer than 4 is FIXABLE. Skip this check when `images` is absent.
   - **Options:** more than one variant has a size or color value that is set. A product with a single default variant is fine; do not flag it.
   - **Description:** at least 200 characters of plain text. Shorter is FIXABLE. Skip this check when `description` is absent.
   - **Stock:** `in_stock` is false. Do not flag these, but list them separately, because a try-on that ends in a sold-out product wastes the shopper's time.
5. Group the results: READY (no failed check), FIXABLE (one or more failed checks, with each reason), BLOCKED (no primary image).
6. Render a summary line (counts for each group) and a table of the FIXABLE and BLOCKED products with the failed checks, 25 rows at most, BLOCKED first. If there are more, say how many were left off.
7. Close with ONE recommendation grounded in the counts, for example "212 of 340 active products have fewer than 4 images, so start with the 30 in the apparel tag," or "no product is blocked, and image depth is the only gap."

# Notes

- This checks the data Fluid stores, not image quality. Resolution, lighting and whether a photo is on-model need a person's eye. Say so under the results.
- Image count comes from the product detail response. If the store's responses carry no `images` list, the report covers the primary image, options and description only; state that plainly.
