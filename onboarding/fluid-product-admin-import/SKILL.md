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

## Authoritative API contract

The documented admin catalog surface is the April 2026 storefront API:

- `GET/POST /api/v202604/company/products`
- `GET/PATCH/DELETE /api/v202604/company/products/{id}`
- the same `/api/v202604/company/{resource}` CRUD pattern for categories,
  collections, enrollment packs, posts, media, playlists, and pages.

Before the first write in a run, use `query_docs` against
`/openapi/api-reference/storefront-v2026-04.yaml` and inspect the exact path
and write schema you need. The docs beat copied examples in this skill if the
contract changes. Do not fall back to `/api/company/v1/*` when a documented
v202604 call fails; report the docs/runtime mismatch instead of silently using
a legacy surface.

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
3. Exhaust every collection/category pagination and collect product links. A
   collection whose bounded retries ended in a network/fetch error is
   unresolved, not exhausted; retry it independently and fail the manifest
   gate if it still has no content-based terminal page/cursor.
4. Fetch every unique PDP. Use an advertised `.md` twin for copy and simple
   facts, but recover images, JSON-LD, embedded application state, options, and
   variants from rendered HTML, sitemap images, or structured APIs. Capture the
   complete product gallery from JSON-LD, embedded state,
   `src`/`srcset`/`data-src`, and gallery thumbnails while excluding unrelated
   recommendation and chrome images. One sitemap or Open Graph image is not a
   complete gallery when the rendered PDP exposes more.
5. Reconcile all sets. Every discovered product URL becomes one live manifest
   product or one evidence-backed exclusion.

Do not synthesize variant combinations as a Cartesian product unless the
source explicitly proves every combination exists. Before finalizing, re-open
a deterministic sample of at least 10 PDPs that includes the
flagship/most-complex product, most-expensive product, one single-variant
product, and multiple multi-variant products. The manifest's exact gallery
URLs/count and real variant options/count must match the rendered or embedded
source evidence for every sample. Store that compact `fidelity_sample` plus the
whole-manifest image-count distribution in the manifest and step output; a
mismatch is repair work, not a note.

Required shape:

```json
{
  "source_url": "https://example.com",
  "observed_at": "2026-07-25T18:00:00Z",
  "discovery": {
    "sitemap_urls": 343,
    "api_urls": 0,
    "collection_urls": 324,
    "unique_product_urls": 343,
    "collection_errors": 0
  },
  "products": [
    {
      "source_id": "https://example.com/products/source-product-123",
      "source_url": "https://example.com/products/source-product-123",
      "source_handle": "source-product-123",
      "final_url": "https://example.com/products/source-product-123",
      "http_status": 200,
      "content_type": "text/html",
      "title": "Exact Source Product Title",
      "description": "Exact source description",
      "price": "29.99",
      "compare_price": null,
      "currency": "USD",
      "image_urls": ["https://source.example/source-product-123.jpg"],
      "option_axes": { "Size": ["Small", "Large"] },
      "variants": [
        {
          "source_variant_id": "source-variant-456",
          "options": ["Small"],
          "price": "29.99"
        }
      ],
      "evidence": ["sitemap", "rendered-html", "json-ld"]
    }
  ],
  "image_count_distribution": [
    { "image_count": 1, "product_count": 12 },
    { "image_count": 6, "product_count": 331 }
  ],
  "fidelity_sample": [
    {
      "source_url": "https://example.com/products/source-product-123",
      "manifest_image_count": 6,
      "source_image_count": 6,
      "manifest_variant_count": 2,
      "source_variant_count": 2,
      "status": "match"
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
    "https://example.com/products/source-product-123": {
      "fluid_product_id": 123,
      "fluid_slug": "source-product-title-2f91",
      "source_handle": "source-product-123"
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
5. paginate `GET /api/v202604/company/products?page[limit]=100` to understand
   existing destination state. Follow each opaque
   `meta.pagination.next_cursor` via `page[cursor]` until it is `null`; this
   surface does not promise a `total_count`.

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

```jsonc
{
  "product": {
    "title": "Exact Source Product Title",
    "description": "Exact source description",
    "status": "active",
    "public": true,
    "product_subscription_plans_attributes": [
      {
        "_destroy": true
      }
    ],
    "images_attributes": [
      {
        "image_url": "https://ik.imagekit.io/fluid/...",
        "position": 1
      }
    ],
    "option_attrs": ["Size"],
    "variants_attributes": [
      {
        "is_master": true,
        "option_attrs": ["Small"],
        "variant_countries_attributes": [
          {
            "country_id": 123, // example only; replace from company_countries
            "active": true,
            "price": "29.99",
            "compare_price": null
          }
        ]
      }
    ]
  }
}
```

Endpoint: `POST /api/v202604/company/products`

Contract:

- Use the documented raw Product enum on writes: `status: "active"` plus
  `public: true` for a live product. The v202604 `ProductWrite` schema accepts
  `active`, `draft`, or `archived`; `published` is a presentation label on
  some read surfaces and is not a valid ProductWrite enum.
- `images_attributes` uses `image_url`, not `url`.
- Exactly one variant has `is_master: true`.
- Product `option_attrs` are option names.
- Variant `option_attrs` are values in the same order.
- Create every real axis and variant combination on the first POST.
- Every variant country includes integer `country_id`, `active`, exact decimal
  string `price`, and `compare_price` when present. Do not send
  `currency_code`: the selected country determines currency on this contract.
  Verify the response's country-relative `pricing.currency_code` matches the
  source currency.
- Preserve source description, gallery order, option names/values, and exact
  prices.
- Preserve a genuinely blank source description as `""` (or omit it on an
  update). Do not coerce an empty string to `null`: the live v202604 create
  returns `422 product.description must be a string` for `null`, even though
  some generated/docs-side schemas describe the field as nullable.
- Do not attach a subscription plan unless the source offers that plan. Fluid
  companies can have a company-default plan that the product create action
  attaches when `product_subscription_plans_attributes` is omitted or empty.
  For a source product with no subscription offer, send the non-empty skip
  sentinel `product_subscription_plans_attributes:[{"_destroy":true}]`. The
  v202604 create contract accepts `_destroy`; the write action treats the
  non-empty array as an instruction to skip its default and creates no join.
  An empty array is not equivalent. Re-read every created product and require
  `has_subscription_plans:false` plus zero active/default subscription joins.
  For a pre-existing join on the current production contract, PATCH the
  returned join `id` with `active:false` and `default:false`, then re-read it;
  never disable the company-wide plan to repair one import. Although the
  v202604 update schema advertises `_destroy`, its delegated product-update
  validator currently drops `_destroy` for this nested association, so do not
  claim physical deletion unless the re-read proves the join is gone.
- Static bundle links use documented `product_bundles_attributes`. Dynamic
  `product_bundle_groups_attributes` are not writable on v202604; if the source
  requires that unsupported shape, stop and report the exact gap instead of
  flattening or silently dropping bundle choices.
- Use each returned Fluid slug/canonical URL for destination navigation; do not
  assume the source handle became the Fluid slug.

For Connect imports, trigger the provider's documented product sync, wait for it
to settle, then run this same manifest reconciliation. A Connect sync is not
self-certifying.

## 6. Import related resources when in scope

Use GET-before-write and persist source identity → Fluid ID mappings.

| Resource           | Endpoint                                                 | Important rule                                                                                                             |
| ------------------ | -------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Categories         | `POST /api/v202604/company/categories`                   | Create parents before children; resolve `parent_id` from the mapping.                                                      |
| Collections        | `POST /api/v202604/company/collections`                  | Preserve source identity. `product_ids` is a full replacement; omission leaves membership unchanged.                      |
| Product membership | `PATCH /api/v202604/company/products/{id}`               | Send verified `collection_ids`; PATCH is partial and does not require resending `title`.                                   |
| Static pages       | Mist `create_page`; underlying `/api/v202604/company/pages` | Use `create_page` so the page, theme template, preview route, and preview pane stay coordinated.                          |
| Blog posts         | `POST /api/v202604/company/posts`                        | Preserve documented source fields, lifecycle, the response's canonical URL, and DAM hero/SEO image.                       |
| Playlists          | `POST /api/v202604/company/playlists`                    | The route says playlists but the documented request wrapper is intentionally `library`.                                  |
| Menus              | `POST /api/menus`                                        | Menus are the explicit legacy exception; use destination canonical routes and preserve nesting/order.                     |

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
- destination products resolve as the documented live lifecycle
  (`status: "active"` on the raw v202604 resource) and `active: true`;
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
