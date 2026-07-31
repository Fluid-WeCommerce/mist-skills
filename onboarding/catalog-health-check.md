---
name: Catalog Health Check
description: Audit a Fluid catalog after an import and return a scored health report — missing prices per market, duplicate SKUs, missing images, empty descriptions, SEO gaps, uncategorized products, currency mismatches, orphan variants — plus a separate enrollment-pack score covering signup tiers, fees, agreements and pack contents, and a storefront spot-check that catches products or join tiers a customer sees as broken or invented. Read-only. Use when the user asks "check my catalog", "did the import work", "catalog health", "are my products ready", "are my enrollment packs set up", "what's missing in my products", or right after any product-import workflow finishes.
icon: package-search
---

<!--
  Canonical community path: onboarding/catalog-health-check.md in
  Fluid-WeCommerce/mist-skills — single file, no references/, flat layout.
  Manifest slug: onboarding/catalog-health-check · category: onboarding.
  The repo's CI (scripts/validate_catalog.py) validates manifest.json on every
  PR, so a new skill needs BOTH the .md file and its manifest.json entry.
  Local install path: ~/Fluid/skills/catalog-health-check/SKILL.md
-->

# Goal

Audit a company's catalog after an import and hand back a scored report: what's broken, how much it matters, and what to do about it. Read-only — this skill never writes. The point is that a client migrating to Fluid finds their own gaps in one pass, instead of discovering them when a customer hits a product with no price — or a would-be rep hits a signup tier that was never real.

Two things are audited and scored separately: the **product catalog** and the **enrollment packs** (the paid signup tiers). On a direct-sales storefront the packs matter at least as much as the products, and they fail independently.

**Trigger** whenever the user asks about catalog quality or has just finished an import: "check my catalog", "did the import work", "catalog health", "are my products ready", "what's missing in my products", "I just migrated from Shopify". Also offer it unprompted right after any import workflow you ran finishes.

Ask nothing up front. The default market is the company's default country; only ask which market if the company sells in several AND the user's request is market-specific.

Write the report in the user's own language (Spanish request → Spanish report). The section headers below are the shape, not literal English strings.

# Step 0 — Gather

Every call is a GET on `fluid_api`. Run 1 and 2 in parallel, then 3.

1. **Markets** — `GET /api/settings/company_countries`.
   Each row carries `country.id`, `country.iso`, `country.currency_code`, and `default`. Pick the row with `default: true`; if **no** row is flagged default, use the first row and say so as a line in the report — a company whose only open market is not flagged default is itself a configuration finding worth naming, not just a fallback for you to take silently. Keep the full ISO list — you need it for the orphan-variant check, and to offer the other markets at the end.
   `GET /api/countries` is only needed if a row's `country` object is missing a currency.

2. **Taxonomy** — `GET /api/v202604/company/categories?page[limit]=100` and `GET /api/v202604/company/collections?page[limit]=100`. Keep only `id` and `title`. These lists do **not** contain product ids.

3. **Products** — `GET /api/v202604/company/products?page[limit]=100`.
   Pagination is **cursor-based**, not page numbers: follow `meta.pagination.next_cursor` into `?page[limit]=100&page[cursor]=<cursor>` until `next_cursor` is null. A health score computed on page one is a lie. Never pass `country_id` — this endpoint has no such filter; price-per-market lives on the variants.
   For catalogs over ~300 products, use the `fluid_catalog_index` tool instead to enumerate the roster without burning context, then detail-fetch from its output.

4. **Variants** — the list payload has **no** `variants` array. Variant-level checks need `GET /api/v202604/company/products/{id}` per product (5 in parallel at a time), which also returns `media` and `bundle_groups`.
   Cap this at **150 products**. If the catalog is larger, run product-level checks on everything, run variant-level checks on the first 150 by `-created_at`, and label those rows `partial` with their real denominator.

5. **Category membership** — for each category id: `GET /api/v202604/company/products?filter[category_ids][]=<id>&page[limit]=100` (same for `filter[collection_ids][]`), collecting product ids into one set. A handful of cheap calls. Products outside the union have no taxonomy.

6. **Warehouses** — `GET /api/settings/warehouses`, only if stock problems appear, to say where inventory should have landed.

7. **Storefront render spot-check** — the admin API is not what the customer sees. `web_fetch` the product's `canonical_url` **exactly as the API returned it** (never compose one from a slug) and read three signals out of the returned HTML:
   - the `application/ld+json` `Product` block → `offers.price`, `offers.availability`
   - `<meta property="product:price:amount">` and `product:availability`
   - any sold-out / unavailable marker in the rendered buy box
   Compare each against what the admin API claims for the same product. **This is the highest-value check in the skill** and the only one that reproduces the customer's actual experience.
   The public `/api/v202604/products` endpoint cannot substitute for it: it resolves the storefront by request host, so through the company API token it answers `404 Storefront not found`. The rendered page is the only reachable source of truth.
   Bounded, because each fetch is a full HTML page: **at most 8 products** — every product already flagged by another check first, then the highest-priced remaining ones. Say how many you sampled. Never fetch the whole catalog.

8. **Enrollment packs** — `GET /api/v202604/company/enrollment-packs?page[limit]=100` (same cursor pagination). These are the paid signup tiers, and on an MLM/direct-sales storefront they are the highest-value thing on the site: the pack is how a rep joins, so a broken pack costs a recruit, not just a sale. Detail is `GET /api/v202604/company/enrollment-packs/{id}` for `member_enrollable_products`, `subscription_enrollable_products`, and `enrollment_pack_agreements` (all SHOW-only).
   Audit them as their own population, running **both** the pack-specific checks and every shared product check (see *The same checks, on packs*) — never fold them into the product score, and never skip them just because the product catalog looks clean.
   Two filters on this endpoint are worth using rather than reimplementing: `filter[country]=<ISO>` proves per-market availability, and `filter[status]=published` separates live tiers from drafts. Compare filtered against unfiltered counts instead of interpreting the `countries` array by hand.
   **If the list comes back empty, that is a finding, not an absence of findings** — go look at the storefront's join/enrollment route before concluding the company simply has no packs. A theme that ships demo pricing tiers will happily render three purchasable-looking cards on top of zero real packs.

9. **Import reconciliation** — every check above is internal-consistency only, so a product that never arrived is invisible to all of them and a half-imported catalog can still score 100. If the company has an import manifest or a `fluid-catalog-index.json` in the project, compare its product count and titles against the live catalog and report anything missing as its own line. If neither exists, say plainly that arrival could not be verified and that the score covers only what is in Fluid.

Tell the user what you're auditing in one line, naming both populations ("Checking 412 products / 1,180 variants and 3 enrollment packs against the US market…"), and then go quiet until the report.

## The real field shapes (do not guess these)

- `status`: `published` | `draft` | `archived`. Plus `active` (bool) and `publish_at` (future date = not live yet). **Skip `archived` entirely** — an archived product with no description is not a problem to fix.
- `description` is an **object**: `description.body` holds HTML. Emptiness = `description` is null, or `body` under ~20 characters after stripping tags and `&nbsp;`.
- `seo` is a **real object**: `seo.title`, `seo.description`, `seo.block_crawler`, `seo.image_url`. Fluid *does* have SEO fields — never tell the user it doesn't. `seo.description` is auto-derived from the description, so an empty description usually drags SEO down with it; report both, don't double-count the cause.
- `image_url` (string) plus `images` as an **object** of `thumb` / `medium` / `large`, each `{url, width}` — not an array.
- `pricing`: `{ price, currency_code, compare_at, subscription_price, display_price }`. `pricing.price` is the default variant's price in the default market.
- `sku` at product level is usually `null` — real SKUs live on `default_variant.sku` and on each variant.
- Variant: `sku`, `is_master`, `image_url`, `images` (array), `option_attrs` / `option_ids`, `track_quantity`, `inventory_quantity`, `inventory_levels`, `position`.
- **Enrollment pack**: `title`, `slug`, `canonical_url`, `description` (string OR object OR null — handle all three), `image_url`, `images`, `active`, `status`, `publish_at`, `seo`, `languages`, `countries` (array of ISO codes; **empty means available everywhere**, not available nowhere), plus `enrollment_fee` (decimal string like `"249.0"`, or null), `additional_volume` (integer CV or null), `membership_after_one_month`, `membership_optional`. Detail adds `member_enrollable_products`, `subscription_enrollable_products`, `enrollment_pack_agreements`.
  Note the shape differences from products: the fee is `enrollment_fee`, NOT `pricing.price`, and there is no `variant_countries` — availability is the flat `countries` ISO array. Do not reuse the product price logic here.
- `variant_countries` is an **object keyed by ISO** — `variant_countries.US = { active, price, currency_code, buyable, cv, qv, country_id, display_price }`. It is not an array and has no `country_iso` field.

# Step 1 — The checks

Count each one and keep the offending ids — the user needs to act, not just feel bad.

**Packs get the same treatment as products, not a lighter one.** Every generic check below runs on the pack population too, against the pack's own field names; only the checks that depend on variants or taxonomy are product-only, because packs have neither. Run the mapping table in *The same checks, on packs* after the product table — skipping it is the most common way this skill under-reports.

| Check | What counts as a problem | Level |
|---|---|---|
| No price in market | The variant has no `variant_countries[ISO]` entry for the audited market, or that entry is `active: false`, or its `price` is null / `"0.0"` | variant |
| Orphan variants | A variant with no `sku` **and** empty `option_ids`; or a `variant_countries` key for an ISO the company has not opened | variant |
| Missing SKU | A variant whose `sku` is null or blank **but which has `option_ids`** — a real, selectable variant with nothing to identify it in inventory or fulfillment. This is distinct from an orphan and the orphan rule does not catch it | variant |
| Duplicate SKUs | The same SKU on more than one variant, compared trimmed and case-insensitively (include `default_variant.sku`). Ignore null/blank SKUs here — they belong to Missing SKU, and treating them as duplicates of each other is a false positive | variant |
| Inconsistent currencies | `variant_countries[ISO].currency_code` differs from that market's own `currency_code` | variant |
| Missing images | Product `image_url` empty **and** `images` empty/null | product |
| Broken images | Any URL in `image_url`, `images.*.url` or `seo.image_url` that is empty or does not start with `http`. Do **not** fetch the URLs — a health check that issues a thousand requests is a different, slower tool. Say that unreachable-but-well-formed URLs are out of scope | image |
| Missing description | `description.body` empty per the rule above | product |
| Weak SEO | `seo.title` empty, or `seo.description` empty, or `seo.block_crawler: true` (the product is deliberately hidden from search engines — call that out by name) | product |
| Boilerplate SEO | A non-empty `seo.description` that is byte-identical to another product's, or to the company's default storefront blurb. Fluid falls back to a generic company description when a product has none, so this passes an emptiness check while search engines see duplicate meta descriptions. Detect it by grouping products by exact `seo.description` and flagging every group with more than one member | product |
| No category | Product id absent from the category ∪ collection membership set | product |
| Out of stock | `in_stock: false`, or every variant's `variant_countries[ISO].buyable` is false, or `track_quantity: true` with `inventory_quantity` 0/null and `keep_selling: false` | product |
| Storefront mismatch | The rendered `canonical_url` disagrees with the admin API: a price of `0` / `0.0` where the API has a real price, an unavailable or sold-out buy box where the API says `in_stock: true`, or an empty rendered description where the API has one. Report the two values side by side — "admin $109.98 / storefront $0" — and never soften it. Population is the products actually sampled, not the whole catalog | sampled product |
| Phantom offer | The storefront's join/enrollment route renders purchasable tiers (title, price, a JOIN/BUY control) while `GET /api/v202604/company/enrollment-packs` returns fewer — or zero — packs. The theme is showing demo content as a real offer: the prices are invented, the button leads nowhere real, and no order can be produced. Report the rendered titles and prices verbatim next to the true pack count | storefront |
| Pack missing fee | `enrollment_fee` is null or `"0.0"` on an active pack, so a paid tier is free or unpriced | pack |
| Pack missing image | `image_url` empty **and** `images` empty/null. The join page is a conversion page; empty frames there cost recruits | pack |
| Pack missing description | `description` empty, or — after stripping tags — identical to another pack's. Tiers whose only differentiator is price are usually unfinished copy, not a pricing strategy | pack |
| Pack no agreements | An active pack whose detail returns an empty `enrollment_pack_agreements`. A rep is signing up with nothing to accept — a compliance exposure, not a cosmetic gap. Say so plainly and point at the country's required agreements | pack |
| Pack empty contents | An active pack where `member_enrollable_products` and `subscription_enrollable_products` are both empty: the buyer pays the fee and receives nothing | pack |
| Pack unavailable | `active: false`, a future `publish_at`, or a `countries` array that omits the audited market — while the storefront still renders the pack. Remember: an **empty** `countries` array means available everywhere and is NOT a problem | pack |
| Bundle integrity | A product priced like a bundle — `pricing.compare_at` above `pricing.price`, or a title joining two product names — that carries `is_bundle: false` and an empty `bundle_groups`. It will not decompose into its components for inventory or fulfillment | product |

## The same checks, on packs

Run every row of this table. The left column is the product check already defined above; the middle column is how it is evaluated on a pack. Same counting, same proportional scoring, separate population.

| Product check | On a pack | Why it matters here |
|---|---|---|
| Missing images | `image_url` empty **and** `images` empty/null | The join page is the conversion page; an empty frame there costs a recruit |
| Broken images | Any URL in `image_url`, `images.*.url`, `seo.image_url` that is empty or not `http`-prefixed. Do not fetch | Same rule, same out-of-scope note |
| Missing description | `description` empty — remember it is `string` OR `object` (`.body`) OR `null`, so handle all three before deciding it is empty | A tier with no copy is an unfinished import |
| Weak SEO | `seo.title` empty, `seo.description` empty, or `seo.block_crawler: true` | Packs have a full `seo` object exactly like products |
| Boilerplate SEO | Group packs by exact `seo.description`; flag every group with more than one member, and flag any that equals the company default blurb | Tiers are the likeliest place to inherit the same generic text |
| No price in market | `enrollment_fee` null or `"0.0"`, **or** the pack absent from `GET …/enrollment-packs?filter[country]=<ISO>` while present unfiltered | Verify availability with the API's own filter rather than interpreting `countries` yourself — it is authoritative and cheap |
| Out of stock / unavailable | `active: false`, `status` not `published`, or a future `publish_at` while the storefront still renders the pack | A scheduled pack rendered today is a dead JOIN button |
| Storefront mismatch | `web_fetch` the pack's own `canonical_url` and compare rendered fee, availability and description against the API, exactly as for a product. Packs are few — sample **all** of them, not eight | The pack page is where the money changes hands |
| Duplicate SKUs | **No pack equivalent** — packs carry no SKU. The nearest failure is two packs sharing a title or slug; flag that instead if you see it | — |
| No category | **Product-only.** `…/enrollment-packs` accepts no `filter[category_ids]`, and live categories carry `source_type: "product"`, so packs are not categorized. Do not report packs as uncategorized | — |
| Orphan / missing SKU / inconsistent currencies | **Product-only** — variant-level concepts. `enrollment_fee` is a single value in the company's base currency, so there is no per-market currency to disagree | — |

Population and lifecycle work the same way: **skip `archived` packs entirely**, exclude `draft` / inactive / future-`publish_at` packs from the score, and report those as the same informational line products get (`• 2 packs still in draft — the join page shows no tiers`). Packs are few enough that the 150-item detail cap never bites: fetch `…/enrollment-packs/{id}` for every one of them so the agreements and contents checks run on the whole population, and label nothing `partial` unless a call actually failed.

**False-positive guards — obey these or the report is noise:**

- A variant with `image_url: null` **inherits the product image**. That is normal Fluid behaviour. Only count a variant as image-less when the parent product has no image either.
- `compare_at: "0.0"` and `subscription_price: "0.0"` mean "not set", not "priced at zero". Never report them as a zero price.
- `cv` / `qv` of `"0"` are normal for a company that doesn't run a comp plan. Never flag them.
- On a pack, an **empty `countries` array means available in every market the company sells in** — unrestricted, not unavailable. Reporting it as a gap inverts the meaning of the field.
- `additional_volume` of 0 or null is normal, as are `membership_optional` / `membership_after_one_month` in either state. None of them are health findings.
- Products with `status: draft`, `active: false`, or a future `publish_at` are **not scored** — intentional drafts exist. Report them as one informational line under the score, because a post-import catalog stuck in draft is invisible to customers and is often the real finding.

## Scoring

Each check costs its full weight only when it affects the whole catalog, and proportionally otherwise — one bad product in a thousand must not read like a catalog on fire, and half the catalog with no price cannot be shrugged off.

```
deduction(check) = weight × (affected / population)
score            = round(100 − Σ deductions), floored at 0
```

Weights: storefront mismatch 25, no price in market 20, orphan variants 20, missing SKU 15, missing images 15, duplicate SKUs 15, inconsistent currencies 15, bundle integrity 10, missing description 10, weak SEO 10, boilerplate SEO 10, no category 10, broken images 10, out of stock 10.

Storefront mismatch outranks everything because it is the only check measured against what a customer actually sees. Its population is the sampled set, so one bad product out of eight sampled costs about 3 points, not 25 — state the sample size next to it in the report so the number is honest.

**Enrollment packs score separately.** Give them their own line — `Enrollment Packs: 40/100 (3 packs)` — computed the same proportional way over the pack population, with weights: phantom offer 40, pack storefront mismatch 25, pack no agreements 20, pack empty contents 20, pack missing fee / unavailable in market 20, pack unavailable 15, pack missing image 10, pack missing description 10, pack weak SEO 10, pack boilerplate SEO 10, pack broken images 10.
The shared checks carry the same weights on packs as on products; only the pack-specific ones (phantom offer, agreements, contents, fee) are new. A pack population of three means each failing pack moves the score by a third of the weight, so state the pack count next to the score. Two scores beat one blended number here, because a company can have a spotless product catalog and a completely broken join flow; averaging them hides exactly the thing the user needs to see. **A phantom offer forces the pack score to 0 regardless of the arithmetic** — you cannot partially score tiers that do not exist. When the company genuinely has no packs and the storefront renders none either, write `Enrollment Packs: n/a (none configured)` and score nothing.

Population is that check's own denominator: non-archived products for product-level checks, variants of those products for variant-level ones, image count for broken images. Archived products are outside every population.

# Step 2 — The report

Exactly this shape, nothing else:

```
Catalog Health Score: 91/100
Enrollment Packs: 0/100 — storefront shows 3 tiers, 0 exist in Fluid
Ready to sell: NO — 1 product unbuyable, join flow not real
412 products · 1,180 variants · United States (USD) · 8 storefront pages sampled

Issues

• 8 products missing descriptions (86808, 86809, 86811)
• 3 variants without images (335618, 335619)
• 2 products blocked from search engines (seo.block_crawler)

Recommendations

• …
```

The **Ready to sell** line is a blunt yes/no above the score, because 88/100 reads like a pass while a customer is staring at a broken product page. It is NO whenever any product is unbuyable — a storefront mismatch, no price in the market, or every variant unbuyable — or whenever the join flow is not real (a phantom offer, or every pack unavailable). The count is of products, not issues. Otherwise YES, optionally with "with cosmetic gaps".

List pack issues in the same Issues block as product issues, in the same one-line format, prefixed so the population is unambiguous (`• 3 packs missing agreements (Starter, Pro, Elite)`). Name packs by title rather than id — there are only ever a handful and the title is what the user sees in the admin. Do not give packs a separate Issues section; one ordered list of everything wrong, worst first, is the point of the report.

Order issues by how much they cost the score, not by the order you checked them. One line each: the count, the thing, and up to three example ids in parentheses. Say "none" under Issues when the catalog is clean, and use Recommendations to point at the next market instead. Add the drafts line (`• 14 products still in draft — not visible on the storefront`) below the Issues block when it applies.

Recommendations are per issue found, one line, concrete and specific to Fluid:

- **No price in market** — price lives per market on `variant_countries`, so an importer that created the variant without a row for this country leaves it unsellable there. Fix first; it is the only issue that makes a product literally unbuyable.
- **Orphan variants** — variants with no SKU and no options are usually an interrupted import; they break cart pricing rather than merely looking untidy.
- **Duplicate SKUs** — deduplicate before re-importing; a repeated SKU makes inventory and reporting ambiguous.
- **Inconsistent currencies** — align each `variant_countries` entry with its market's own currency before any order lands; mixed currencies corrupt every total that sums across variants.
- **Missing images** — re-run the image step of the import; some themes render an empty frame.
- **Broken images** — re-upload through the DAM rather than patching URLs.
- **Missing description** — `description.body` also feeds `seo.description`, so this costs twice.
- **Phantom offer** — the most serious finding this skill can produce, above even an unbuyable product: the storefront is advertising signup tiers at prices the company never set. Quote the rendered titles and prices, state that zero (or N) real packs exist, and say the fix is either to create the packs in Fluid or to remove the section from the theme — never to leave invented prices live. Do not describe it as "missing content"; it is incorrect content.
- **Pack no agreements** — a rep enrolling with no agreement to accept. Flag it as compliance, not polish, and offer to run the country compliance skill for the required list.
- **Pack empty contents / missing fee / unavailable** — one line each, naming the pack by title, since there are usually only a handful.
- **Storefront mismatch** — fix before anything else. Name the product, both values, and the likeliest cause: a rendered price of 0 with an unavailable buy box on a product the API prices and stocks normally almost always means the theme could not resolve a purchasable variant, and missing variant SKUs are the usual reason. Say that the customer sees this today.
- **Missing SKU** — a selectable variant with no SKU cannot be picked in a warehouse or reconciled in reporting. Common on imported bundles, where the parent got a SKU and the option rows did not. When the same product also fails the storefront check, treat the SKUs as the root cause and say so once instead of listing two unrelated problems.
- **Bundle integrity** — set the product up as a real bundle with component groups, or the discount is cosmetic and stock never decrements for the parts.
- **Weak SEO** — set `seo.title` / `seo.description` per product; `block_crawler: true` removes the product from search results entirely, so confirm that was deliberate.
- **Boilerplate SEO** — these products are inheriting the company's default blurb; write a real `seo.description` per product. Name the shared text once instead of repeating it per product.
- **No category** — the product is reachable only by direct link or search.
- **Out of stock** — confirm whether it's genuine; the flag hides the product from the storefront. Name the warehouse from `GET /api/settings/warehouses` when there is only one.
- **Drafts** — publishing is a bulk action in the admin; ask before assuming they should go live.

Close with a single next step, not a menu: the highest-weight issue, phrased as an action. If the company has other open markets, add one line offering to run the same audit for them.

## Optional deep pass — only if asked

If the user asks *why* copy is weak, or asks about claims/compliance, run `GET /api/v202604/company/products/{id}/compliance` on at most 25 products — and `GET /api/v202604/company/enrollment-packs/{id}/compliance` on every pack, since pack copy is where income and earnings claims live and it is the higher-risk surface of the two. It returns a pre-computed `score` (0–10), `status`, `summary` and `compliance_issues[]` with `severity` and a concrete `recommendation`. Report it as a separate block with its own 0–10 scale — never fold it into the 0–100 health score. For acting on those findings, hand off to the `themes/suggested-changes` skill rather than editing anything here.

# Rules

- Read-only. Every call is a GET. Never offer to fix anything by writing — if the user asks, tell them what to change and where, and let them decide.
- Never guess a number. If pagination stopped early, a detail fetch failed, or an endpoint errored, say which part of the catalog you could not see, give the score for what you did see, and label it `partial`. A confident score over half a catalog is worse than an honest gap.
- One market per report. Prices, currencies and availability are per market, so a single blended score across markets means nothing.
- Fluid is the source of truth, the theme is not. When rendered content and the API disagree about what exists, the API wins and the difference is the finding. Never read a price, tier name, or product off a rendered page and report it as company data — theme demo content looks exactly like real content, and repeating it back as real is the worst failure this skill can have.
- Empty is not automatically clean. Zero enrollment packs, zero categories, or zero variants returned means go check whether the storefront is still advertising them before writing "none".
- Never invent fields, and never repeat the old myth that Fluid has no SEO fields or no per-product stock — `seo`, `track_quantity`, `inventory_quantity` and `inventory_levels` all exist on the shapes above. What Fluid has no single field for is a product-level stock count independent of variants.
- Don't use `/api/products` (legacy). It answers 200 but embeds the entire country configuration blob per product and will exhaust context on the second page.
- Keep the chat short. The report is the output; don't narrate the checks as you run them.
