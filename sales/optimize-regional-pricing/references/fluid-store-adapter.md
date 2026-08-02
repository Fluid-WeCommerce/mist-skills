# Fluid store adapter

Use this adapter when the skill runs for a Fluid merchant or inside Mist.

## Read-only boundary

The pricing audit is advisory. It may read products and prices, but it must not
create, update, archive, duplicate, or delete products, variants, prices, pages,
themes, or assets.

Allowed product operations:

- list products with
  `fluid_api("/api/v202604/company/products?page[limit]=100", "GET")`;
- follow every `meta.pagination.next_cursor` with `page[cursor]` until it is
  `null`;
- retrieve product detail with
  `fluid_api("/api/v202604/company/products/{id}", "GET")`;
- request relevant `country_code` values;
- follow pagination until the in-scope catalog is complete;
- use Mist's authenticated active-company context.

Do not call `POST`, `PUT`, `PATCH`, or `DELETE` during an audit. Do not ask for a
broad company token or attempt a legacy product endpoint. Never place an access
token in a report, CSV, command, or saved catalog response.

Mist tool availability is an integration precondition, not an assumption. Search
the tools available in the current run for an authenticated Fluid product-list
or product-detail resource. If none is available, ask for a read-only product
export or a saved Product API JSON response. Do not claim that Mist inspected the
store when the run only used demonstration data.

## Catalog capture

Capture and preserve:

- product ID, title, status, official product URL, and product image;
- variant ID, title, SKU, and master-variant status;
- country code, currency code, numeric price, and display price;
- the response timestamp or export date and the requested country codes.

Use the product response's `compressed_image_url`, `image_url`, ordered `images`,
or variant image, in that order. These are the merchant's catalog assets. Do not
generate a visual substitute. If a catalog product has no image, show an honest
empty state.

The list response is cursor-paginated. Do not treat the first page as the
complete store. Continue with
`/api/v202604/company/products?page[limit]=100&page[cursor]=<next_cursor>` until
`meta.pagination.next_cursor` is `null`. Reject a repeated cursor rather than
looping or silently truncating the catalog. Do not expect `total_count`.

## Normalize a saved response

Run:

```bash
python3 <IMPORT_FLUID_CATALOG_PATH> \
  --catalog <absolute-saved-products-json> \
  --output <absolute-normalized-catalog-json>
```

Obtain `<IMPORT_FLUID_CATALOG_PATH>` by calling
`run_skill("sales/optimize-regional-pricing")` and using the exact
content-addressed project-relative path printed for
`scripts/import_fluid_catalog.py` under `.mist-desktop/skill-assets/`. Do not
copy or edit the materialized file.

The importer performs no network calls and writes only local files. It accepts
the documented `products[]` and `product` responses plus common `data` or
`result` wrappers used by agent tools.

To attach catalog truth to performance/planning rows:

```bash
python3 <IMPORT_FLUID_CATALOG_PATH> \
  --catalog <absolute-saved-products-json> \
  --output <absolute-normalized-catalog-json> \
  --market-input <absolute-market-csv> \
  --market-output <absolute-catalog-enriched-csv>
```

Matching uses `product_id`, optional `variant_id`, and `market_id`. The importer
sets the real product name and image and replaces the current price/currency only
when the saved Fluid response includes an exact country match. It records missing
products and prices rather than inventing them.

## Choose the honest output tier

### Catalog-only audit

Use this when the store connection supplies products and current prices but not
country-level performance.

Return:

- missing or inconsistent country prices;
- currency and price-ending issues;
- unusually large price gaps that merit review;
- candidate markets and externally sourced purchasing-power context;
- a proposed experiment price, break-even lift, and data request.

Label every candidate as a hypothesis. Do not produce projected revenue gains
without traffic, orders, refunds, and cost inputs.

### Performance-backed recommendation

Use this when the agent also has an approved source for eligible visitors or
checkout exposures, paid orders, refunds, taxes, fees, and variable costs by
product and country.

Merge the catalog into the market rows, then run the deterministic regional
pricing analysis. Keep low, base, and high assumptions visible and identify
which assumptions are observed, benchmarked, or synthetic.

## Mist handoff

A good Mist run should say:

1. what authenticated read-only tool or export supplied the catalog;
2. how many products and country-price records were inspected;
3. whether performance data was available;
4. which output tier was produced;
5. that no live product, price, page, or theme was changed.
