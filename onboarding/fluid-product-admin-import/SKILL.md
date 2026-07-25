---
name: fluid-product-admin-import
description: >-
  Import a complete source catalog and related store resources into the active
  Fluid company. Builds an evidence-backed source manifest, preserves product
  identity, images, prices, options, and variants, resumes safely, and proves
  one-to-one coverage before reporting completion.
---

# Fluid Product & Admin Import

Use this skill when a workflow or user asks to import products, collections,
categories, pages, posts, menus, brand assets, or related store setup from an
existing commerce site.

Inside Mist, the active company and credentials are already selected:

- use `fluid_api(path, method, body)` for Fluid API calls;
- use `crawl` for public source pages;
- use `dam_upload` for source image bytes;
- never ask for a Fluid token, store URL, Firecrawl key, or global CLI install.

This is an execution contract. A row count is not proof of a complete import.

## Safety and scope

Honor the caller's scope. A manifest/discovery step is read-only against Fluid.
Only create or update destination records when the parent workflow or user has
authorized an import.

Never:

- overwrite an unrelated existing product based on title alone;
- invent copy, prices, variants, currency, subscriptions, or exclusions;
- hotlink source CDN images;
- treat a page/batch limit as catalog completion;
- treat HTTP 200 as proof that a requested PDP still exists;
- claim completion with unresolved source routes or missing checkpoints.

## 1. Build the source catalog manifest

Before any product write, create a fresh run-specific `source-catalog.json`.
Record the absolute path, observation time, and final SHA-256.

Discovery is a union:

1. Parse `sitemap.xml` and every referenced child sitemap. Preserve product
   URLs, last-modified timestamps, and sitemap images.
2. Exhaust structured catalog endpoints when available. Follow documented
   cursors or pages until their real terminator; do not stop at the first
   successful page.
3. Exhaust every collection/category pagination and collect product links.
4. Fetch every unique PDP. Use an advertised `.md` twin for copy and simple
   facts, but recover images, JSON-LD, options, and variants from rendered HTML,
   sitemap images, or structured APIs.
5. Reconcile all sets. Every discovered product URL becomes one live manifest
   product or one evidence-backed exclusion.

Required shape:

```json
{
  "source_url": "https://example.com",
  "observed_at": "2026-07-25T18:00:00Z",
  "discovery": {
    "sitemap_urls": 343,
    "api_urls": 0,
    "collection_urls": 324,
    "unique_product_urls": 343
  },
  "products": [
    {
      "source_id": "https://example.com/products/front-wheel-c4",
      "source_url": "https://example.com/products/front-wheel-c4",
      "source_handle": "front-wheel-c4",
      "final_url": "https://example.com/products/front-wheel-c4",
      "http_status": 200,
      "content_type": "text/html",
      "title": "Front Wheel",
      "description": "Exact source description",
      "price": 120,
      "compare_price": null,
      "currency": "EUR",
      "image_urls": ["https://source.example/front-wheel.jpg"],
      "option_axes": { "Compatibility": ["C4", "Cruiser"] },
      "variants": [
        {
          "source_variant_id": "front-wheel-c4",
          "options": ["C4"],
          "price": 120
        }
      ],
      "evidence": ["sitemap", "rendered-html", "json-ld"]
    }
  ],
  "excluded": [
    {
      "source_url": "https://example.com/products/old-item",
      "reason": "redirects to the home page; no product evidence",
      "evidence": {
        "final_url": "https://example.com/",
        "http_status": 200
      }
    }
  ]
}
```

A stale PDP can redirect to the home page and still return a large HTTP 200
body. Require the final URL to remain a product route and require product
evidence such as an offer/price or Product JSON-LD.

Do not exclude a product merely because:

- one parser failed;
- Markdown omitted an image;
- a collection card did not include it;
- a tool returned only its first 100/200/250 items;
- the title duplicates another product.

Only classify a `$0` route as junk when independent evidence identifies it as an
internal/test/app-helper item. A legitimate free source product remains part of
the catalog.

## 2. Persist immutable identity and resume state

Create `id-mapping.json` and a per-item checkpoint next to the source manifest.
For products, the key is the normalized source ID or canonical source URL,
never title.

```json
{
  "products": {
    "https://example.com/products/front-wheel-c4": {
      "fluid_product_id": 123,
      "fluid_slug": "front-wheel-2f91",
      "source_handle": "front-wheel-c4"
    }
  }
}
```

Duplicate titles are normal in parts catalogs. Report duplicate-title groups
before import. If a mapping is missing and an existing destination product must
be recovered, require a unique composite fingerprint such as verified
`external_id`, source handle + SKU, or another stable source identifier.
Ambiguous matches stop for review.

After each successful destination write:

1. persist the returned Fluid ID and slug;
2. re-read the record;
3. mark the checkpoint successful;
4. only then start the next item.

On restart, verify checkpointed records and resume the remaining identities.

## 3. Resolve company country and destination state

Before product creates:

1. `GET /api/settings/company_countries`
2. choose the intended active company country from caller/source context;
3. use `company_countries[].country.id` as integer `country_id`;
4. retain the source currency and confirm it agrees with the selected market;
5. paginate `GET /api/company/v1/products` to understand existing destination
   state.

Do not substitute `country_iso` for `country_id`.

## 4. Move source images into Fluid DAM

For every real product/gallery/variant image:

1. ingest the source asset with `dam_upload` when it is already in the sandbox,
   or use `fluid dam upload --url <SOURCE_URL>` for a remote URL;
2. take `asset.default_variant_url` from the result;
3. store source URL → DAM URL in `id-mapping.json`;
4. use only the Fluid DAM URL in product payloads.

The underlying `POST https://upload.fluid.app/upload` service accepts either:

- multipart file bytes (`fileName`, then `file` for large streaming uploads); or
- multipart `external_asset_url`, which the service fetches server-side and
  auto-detects `fileName` from when it is omitted.

The exact remote field is `external_asset_url`, not `external_url`, and it is a
multipart field rather than a JSON payload. JSON mode is reserved for
`b64_json`/`data_uri`. A placeholder image is an unfinished import when the
source has a real image.

## 5. Create or update products

Create products with nested attributes:

```json
{
  "product": {
    "title": "Exact Source Product Title",
    "description": "Exact source description",
    "active": true,
    "status": "active",
    "images_attributes": [
      {
        "image_url": "https://ik.imagekit.io/fluid/...",
        "position": 1
      }
    ],
    "option_attrs": ["Color", "Configuration"],
    "variants_attributes": [
      {
        "is_master": true,
        "option_attrs": ["Black", "A (+ rear rack)"],
        "variant_countries_attributes": [
          {
            "country_id": 20,
            "active": true,
            "currency_code": "EUR",
            "price": 3418,
            "compare_price": null
          }
        ]
      }
    ]
  }
}
```

Endpoint: `POST /api/company/v1/products`

Contract:

- `images_attributes` uses `image_url`, not `url`.
- Exactly one variant has `is_master: true`.
- Product `option_attrs` are option names.
- Variant `option_attrs` are values in the same order.
- Create every real axis and variant combination on the first POST.
- Every variant country includes integer `country_id`, `active`, exact
  `currency_code`, exact price, and compare price when present.
- Preserve source description, gallery order, option names/values, and exact
  prices.
- Do not attach a subscription plan unless the source offers that plan.
- Use each returned Fluid slug/canonical URL for destination navigation; do not
  assume the source handle became the Fluid slug.

For Connect imports, trigger the provider's documented product sync, wait for it
to settle, then run this same manifest reconciliation. A Connect sync is not
self-certifying.

## 6. Import related resources when in scope

Use GET-before-write and persist source identity → Fluid ID mappings.

| Resource           | Endpoint                              | Important rule                                                                         |
| ------------------ | ------------------------------------- | -------------------------------------------------------------------------------------- |
| Categories         | `POST /api/company/v1/categories`     | Create parents before children; resolve `parent_id` from the mapping.                  |
| Collections        | `POST /api/company/v1/collections`    | Preserve source collection identity and membership.                                    |
| Product membership | `PATCH /api/company/v1/products/{id}` | Send verified `collection_ids`; do not assume an `add_product` route exists.           |
| Static pages       | `POST /api/company/pages`             | Space writes to avoid WAF bursts; do not use the currently-404ing `/v1/pages` variant. |
| Blog posts         | `POST /api/posts`                     | Preserve title, body, date, slug, and DAM hero image.                                  |
| Menus              | `POST /api/menus`                     | Use destination canonical routes and preserve nesting/order.                           |

Theme pushes happen before page creates because page creation can auto-generate
theme templates that a later push may try to remove.

Legitimately empty resource types are reported as zero with evidence. Do not
fabricate content to make a count nonzero.

## 7. Bounded performance and recovery

- Fetch source pages with at most 10 concurrent requests.
- Start DAM downloads/uploads at 5 concurrent items.
- Start product writes at 2 concurrent requests.
- On 429/5xx, honor `Retry-After`, apply exponential backoff with jitter, and
  temporarily reduce concurrency.
- Retry each item a bounded number of times, then record the terminal error
  beside its source identity.
- Print progress at least every 20 products.
- Never hold the complete image catalog in memory.
- Resume missing items after slow Wi-Fi, process restart, or provider failure.

These are starting limits, not targets. Reduce them on a lower-end computer or
when the source/destination begins throttling.

## 8. Prove completion

Paginate the destination until exhausted and reconcile it against the hashed
source manifest.

The product import passes only when:

- every live source identity maps to one distinct Fluid product ID;
- no two source identities map to the same Fluid product;
- every discovered route is live or has an evidence-backed exclusion;
- unresolved source and destination counts are zero;
- coverage is exactly 100%;
- destination products are active;
- exact price and currency match;
- source option axes and variant counts match;
- every available source image is represented by a resolving Fluid DAM URL;
- descriptions match the source;
- no placeholder images or accidental `$0` shells remain;
- a second run verifies idempotency without duplicates.

Report discovered, live, excluded, imported, and failed counts separately.

End with:

```text
STEP_OUTPUT: manifest=<absolute path> sha256=<hash> discovered=<n> live=<n> excluded=<n> imported=<n> coverage=100% unresolved=0 duplicate_title_groups=<n> checkpoint=<absolute path> match_rates={title,price,currency,images,variants,description} related_resources={categories,collections,pages,posts,menus}
```

If any gate is unmet, report `BLOCKED` or `needs-review` with exact identities
and evidence. Never downgrade partial work into a pass.
