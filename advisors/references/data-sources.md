# Where the numbers live

Use whichever sources best answer the question. Pick the two or three that fit, prefer aggregates for speed, and cross-reference when it sharpens the story.

## 1. Fluid REST API (`fluid_api`, GET only while investigating)

Use these exact paths. If one returns 404 or 403, that data isn't available for this company; move on. Never invent other paths.

- **Orders list:** `/api/v202506/orders` (params: `page[limit]` ≤ 100, `start_date`, `end_date`, `within_days`, `status`, `type`, `search`). For recent activity use `within_days=30`, or explicit dates relative to today ({{today}}). An empty list means no orders in that window, so fetch the newest order (unfiltered, `page[limit]=1`) and report how long ago it was.
- **Orders aggregate:** `/api/v202506/orders/stats`. Without `start_date` and `end_date` it returns **all-time** totals. To report a period you must pass both dates; never present the unfiltered total as a recent figure.
- **Customers:** `/api/customers` and `/api/customers/stats`.
- **Inventory:** `/api/inventory_levels`. Requires `variant_ids` or `warehouse_ids` (comma-separated); get variant ids from a products call first. Filters: `on_hand_less_than`, `available_less_than`, `product_tags`.
- **Fulfillments:** `/api/order_fulfillments` for ship times.
- **Money:** `/api/v202506/transactions` and `/api/v202506/payments/reports/kpis` (also `approval_rate`, `error_rate`, `transaction_volume`; these reports need `start_date` and `end_date`).
- **Field:** `/api/v202506/ranks`, `/api/company/contacts`, `/api/subscriptions`, `/api/subscription_plans`, `/api/enrollment_packs`.
- **Storefront content:** `/api/v202604/company/{products|collections|pages|posts|media|playlists}`; each has `/:id/lighthouse` (page speed), `/:id/compliance` (FTC/FDA checks) and `/:id/shares` (engagement).

## 2. Reporting database (`db_query`, `db_schema`)

`db_query` runs read-only SQL against the company's Fluid reporting database for deep historical and aggregate data. If it isn't connected you'll get an error; fall back to the API. Run `db_schema` (mode `search` for a keyword, mode `tables` for columns and foreign keys) before writing SQL against a table you haven't seen. Don't guess column names.

## 3. Local codebases

`read_file`, `list_dir` and `search_files` over the company's cloned projects (Mist apps, themes, MySites, portals), and `run_cli` for `git -C <repo> log` or `git -C <repo> shortlog -sn`. Use these for technical questions: recent changes, contributors, config and security smells.

## 4. The web

`web_fetch` or `crawl` for public pages, such as the live storefront, when the answer lives outside Fluid. `social_search` for TikTok, Instagram, YouTube and Pinterest content.
