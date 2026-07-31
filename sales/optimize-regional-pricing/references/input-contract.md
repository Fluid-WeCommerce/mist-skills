# Input contract

Use one CSV row per product-plan and market. Keep an unchanged copy of the source export.

For Fluid stores, first read `fluid-store-adapter.md`. A saved Product API
response can supply the real product title, image, current country price, and
currency. It does not supply the performance metrics or candidate price needed
for a revenue scenario.

## Required columns

| Column | Meaning |
| --- | --- |
| `market_id` | Stable country or storefront code, preferably ISO 3166-1 alpha-2 |
| `market_name` | Human-readable market name |
| `currency` | ISO 4217 local currency |
| `visitors` | Eligible checkout exposures in the analysis period |
| `orders` | Paid orders before refunds |
| `refunds` | Refunded orders in the same cohort |
| `current_local_price` | Current displayed unit price |
| `proposed_local_price` | Candidate displayed unit price |
| `usd_per_local` | Dated USD value of one local-currency unit |
| `lift_low_pct` | Conservative conversion-lift assumption |
| `lift_base_pct` | Base conversion-lift assumption |
| `lift_high_pct` | Upside conversion-lift assumption |
| `assumption_basis` | `observed`, `experiment`, `benchmark`, `hypothesis`, or `synthetic` |
| `assumption_note` | Short source or rationale |

## Optional columns

| Column | Default | Meaning |
| --- | ---: | --- |
| `tax_inclusive_pct` | `0` | Indirect tax included in the displayed price |
| `payment_fee_pct` | `0` | Percentage payment fee or platform commission |
| `payment_fee_fixed_usd` | `0` | Fixed fee per retained order |
| `variable_cost_usd` | `0` | Incremental cost per retained order |
| `product_id` | project product | Stable product or plan identifier |
| `variant_id` | master/default variant | Stable variant identifier when a non-master variant is in scope |
| `product_name` | project product | Human-readable product or plan name |
| `product_url` | none | Official product page used for image discovery |
| `product_image_url` | none | Official image URL or local path relative to the CSV |
| `product_image_alt` | product preview | Useful alt text for the product image |
| `product_image_source` | provided/official image | Readable image provenance |

Percent fields use percentage points: enter `20` for twenty percent, not `0.20`.

## Project configuration

Pass a JSON file with:

```json
{
  "project": "Project name",
  "product": "Product or plan",
  "product_url": "https://example.com/products/product-or-plan",
  "product_image_url": "images/product-cover.webp",
  "product_image_alt": "Product or plan cover",
  "product_image_source": "Official product catalog",
  "analysis_date": "YYYY-MM-DD",
  "period_label": "month",
  "periods_per_quarter": 3,
  "default_test_reach_pct": 10,
  "default_horizon_quarters": 4,
  "base_currency": "USD",
  "cohort": "New customers only",
  "data_label": "Synthetic demonstration",
  "revenue_basis": "First-order contribution revenue",
  "sources": [
    {
      "label": "Source name",
      "url": "https://example.com",
      "accessed": "YYYY-MM-DD"
    }
  ]
}
```

Projection configuration:

- `periods_per_quarter` is optional when `period_label` is a recognizable week,
  month, quarter, or year. Set it explicitly for nonstandard analysis periods.
- `default_test_reach_pct` must be from 5 through 100 and defaults to 10.
- `default_horizon_quarters` must be from 1 through 4 and defaults to 4.
- The report treats the per-period scenario as a constant run rate. These fields
  size a planning scenario; they do not add demand evidence.

Project-level product-image fields are optional and remain useful for a single-product report:

- `product_image_url` accepts an HTTP(S) URL or a local path relative to the project JSON.
- When `product_image_url` is absent and `product_url` is present, the script looks for `og:image`, `twitter:image`, or `image_src` metadata on that official page.
- `product_image_alt` should identify the product, not describe decorative styling.
- `product_image_source` is the readable provenance label shown with the image.

The generator copies the selected image into the local report. It accepts PNG, JPEG, GIF, WebP, AVIF, and SVG up to 8 MB. An explicit broken or unsupported image fails validation. Failed automatic discovery records a warning and leaves the report usable without an image.

For a portfolio report, put the product fields on each CSV row. The generator deduplicates repeated product sources, copies every distinct product image into `assets/`, and exposes the image on the corresponding product-market recommendation. Prefer one row per product-market candidate and rank the combined portfolio by base-case contribution result.

Use an honest `data_label`, such as `Observed billing export`, `Planning assumptions`, or `Synthetic demonstration`.
Use `revenue_basis` to state exactly what is modeled. Prefer `First-order contribution revenue` unless retention, renewal, and churn data support a subscription-lifetime model.

## Validation rules

- Require `visitors > 0`.
- Require `orders >= refunds >= 0`.
- Require positive current and proposed prices and FX rates.
- Require `low <= base <= high`.
- Reject contribution margins at or below zero.
- Keep one analysis period and one eligible cohort per report.
- Keep one analysis period, cohort, and contribution basis across a portfolio report. Split products into separate reports only when those foundations differ materially.
- Prefer a supplied or official catalog image. Do not use arbitrary image-search results or generate a substitute product image.
