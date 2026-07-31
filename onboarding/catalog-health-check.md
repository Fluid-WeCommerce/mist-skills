---
name: Catalog Health Check
description: Audit a Fluid catalog after an import and return three scored health reports — products (prices per market, duplicate SKUs, missing images, empty descriptions, SEO gaps, currency mismatches, orphan variants), taxonomy (empty or duplicated categories and collections), and enrollment packs (fees, agreements, pack contents). Reads the Fluid API only; never fetches the storefront. Use when the user asks "check my catalog", "did the import work", "catalog health", "are my products ready", "are my collections set up", "what's missing in my products", or right after any product-import workflow finishes.
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

Audit a company's catalog after an import and hand back a scored report: what's broken, how much it matters, and what to do about it. Read-only — this skill never writes. The point is that a client migrating to Fluid finds their own gaps in one pass, instead of discovering them when a customer hits a product with no price.

Three populations are audited and scored **separately**, because they fail independently and a blended number hides whichever one is broken:

1. **Products** — the catalog itself.
2. **Taxonomy** — categories and collections, the browsing surfaces.
3. **Enrollment packs** — the paid signup tiers, when the company has any.

## Scope: Fluid data only

This skill reads the **Fluid API and nothing else**. It never fetches the storefront, never parses rendered HTML, and never reports on the theme. Every finding is a statement about data in Fluid, which makes the audit fast, cheap, deterministic, and re-runnable.

That boundary is deliberate, and it has a real consequence worth stating once in the report when it matters: **a product can be perfectly healthy here and still render wrong to a customer**, because the theme is a separate system with its own bugs. If the user asks why a page looks broken when this audit is clean, say plainly that rendering is out of scope and point them at the theme skills (`themes/theme-review`, `themes/iterative-theme-refine`) — do not start fetching pages from inside this skill.

**Trigger** whenever the user asks about catalog quality or has just finished an import: "check my catalog", "did the import work", "catalog health", "are my products ready", "what's missing in my products", "I just migrated from Shopify". Also offer it unprompted right after any import workflow you ran finishes.

Ask nothing up front. The default market is the company's default country; only ask which market if the company sells in several AND the user's request is market-specific.

Write the report in the user's own language (Spanish request → Spanish report). The section headers below are the shape, not literal English strings.

# Step 0 — Gather

Every call is a GET on `fluid_api`. Nothing here fetches a web page.

- **First, in parallel:** 1 (markets), 2 (taxonomy), 3 (products), 7 (enrollment packs). Nothing depends on anything else.
- **Then, in parallel:** 4 (variant detail), 5 (taxonomy membership), pack detail from 7.
- **Only if needed:** 6 (warehouses, only when stock problems appear), 8 (import reconciliation, only when a manifest exists).

Budget: the fixed part is about ten calls — markets, the two taxonomy lists, the first product page, the two `filter[status]` probes, packs, `filter[bundle]=true`, `filter[availability]=in_stock`, plus one more per extra product cursor page. Everything after that **scales with the catalog**: one detail call per product audited for variants (step 4, hard-capped at 150) and one limit-1 call per category and per collection (step 5). A 40-product store with 15 taxonomy resources is therefore ~65 calls, not 20 — the per-product detail fetch dominates, and the 150 cap is what keeps a large catalog bounded, not the membership sweep. If the user is watching, the one-line "checking…" note below is all they should see until the report.

1. **Markets** — `GET /api/settings/company_countries`.
   Each row carries `country.id`, `country.iso`, `country.currency_code`, and `default`. Pick the row with `default: true`. If **no** row is flagged default, choose using only data this skill already has: when exactly one open market's `country.currency_code` matches the currency most products carry in `pricing.currency_code`, audit that market; otherwise take the first row. Either way, name the choice and its reason as one line under *Informational (unscored)* — a company with no flagged default market is itself a configuration finding worth naming, not a fallback to take silently.
   **Do not justify the choice with entity registration, settlement currency, or tax setup.** This skill never fetches any of it, and building a rationale out of fields you did not read is exactly the failure the scope rule exists to prevent — it reads as authoritative and is unverifiable. If the currency test does not decide it, say the choice was arbitrary and that a default market should be flagged. Keep the full ISO list — you need it for the orphan-variant check, and to offer the other markets at the end.
   `GET /api/countries` is only needed if a row's `country` object is missing a currency.

2. **Taxonomy** — `GET /api/v202604/company/categories?page[limit]=100` and `GET /api/v202604/company/collections?page[limit]=100`.
   These are **not** just a lookup for the no-category check: each one is a browsing resource with its own page, image, description and `seo` block, and together they are audited as their own population (see *Taxonomy checks*). Keep the full records — `id`, `title`, `slug`, `status`, `active`, `publish_at`, `has_children`, `image_url`, `images`, `description`, `seo`, `canonical_url` — not just `id` and `title`.
   The lists do **not** contain product ids — membership comes from step 5.

3. **Products** — `GET /api/v202604/company/products?page[limit]=100`.
   Pagination is **cursor-based**, not page numbers: follow `meta.pagination.next_cursor` into `?page[limit]=100&page[cursor]=<cursor>` until `next_cursor` is null. A health score computed on page one is a lie.

   **Do not filter this endpoint by market — and understand why, because the obvious "fix" breaks the audit.** There is no `country_id` param, but there *is* `filter[country]=<ISO>`, and it does not narrow the market view of each product: `apply_country` in the products Browser resolves the ISO to a company country and then returns only products that have a `variant_countries` row for it. Passing it therefore **excludes from the response exactly the products this audit is looking for** — the ones with no price in the audited market — and it does so on the authenticated surface too, with no visibility gate to save you. The market is audited by *reading* `variant_countries[ISO]` off every product, never by filtering on it. Filter by market here and the 20-point *No price in market* check returns a silent, permanent zero.
   For catalogs over ~300 products, use the `fluid_catalog_index` tool instead to enumerate the roster without burning context, then detail-fetch from its output.

   **Then probe the non-published states explicitly — do not trust the unfiltered list to contain them.** An audit whose whole purpose is finding what the import broke must not silently miss the products the import left unpublished:
   ```
   GET …/company/products?filter[status]=draft&page[limit]=100
   GET …/company/products?filter[status]=archived&page[limit]=100
   ```
   Two extra calls, and they are the difference between "measures what already works" and "finds what went wrong". Never infer emptiness from the default list: if the unfiltered count equals the `filter[status]=active` count you have learned nothing about drafts, because you cannot tell a catalog with no drafts from a list that hides them.

   There is no third call for scheduled products: `scheduled` is a resolved response value, not a filter value, so they arrive inside `filter[status]=active` and you separate them by reading `status` off each record.

   **Status vocabulary trap — three different vocabularies, one word.** On products, `filter[status]` takes the raw enum keys `active` | `draft` | `archived`, while the product objects come back with a *resolved* status of `published` | `draft` | `archived` | `scheduled`. So `filter[status]=active` returns products whose `status` reads `published` or `scheduled`, and there is no value you can pass that literally matches what you read. Filter with `active`; branch on the resolved value.

   Two neighbours use the same word differently, and mixing them up is easy: **enrollment packs** take `draft` | `scheduled` | `published` on `filter[status]` — the resolved vocabulary, not the product one, and with no `archived` at all — and the legacy `/api/company/v1/products` returns `status: "active"` for the very same record a v202604 call calls `published`. Three vocabularies: pick per endpoint, never carry one across.

   Archived products stay outside every population. Drafts are reported as the informational line, never scored.

4. **Variants** — the list payload has **no** `variants` array. Variant-level checks need `GET /api/v202604/company/products/{id}` per product (5 in parallel at a time), which also returns `media` and `bundle_groups`.
   Cap this at **150 products**. If the catalog is larger, run product-level checks on everything, run variant-level checks on the first 150 by `-created_at`, and label those rows `partial` with their real denominator.

5. **Taxonomy membership** — this call does double duty, so make it **once per category and once per collection, individually**, never as one combined OR query:
   `GET /api/v202604/company/products?filter[category_ids][]=<id>&page[limit]=1` (same for `filter[collection_ids][]`).
   - Union of all returned ids → the set for the product-level *No category* check.
   - Per-id result → whether that category/collection is **empty**, which is the highest-value taxonomy finding.

   Use `page[limit]=1`, not 100: **`meta.pagination` carries no `total_count`**, so there is no cheap way to ask "how many products are in here". With limit 1 the answer is unambiguous and the payload is one product instead of a hundred:
   - `products: []` → empty (a dead page)
   - one product, `next_cursor: null` → exactly one (thin, informational only)
   - one product, `next_cursor` present → two or more (fine)

   Only re-fetch a collection at `page[limit]=100` if you actually need its full membership for the union. For a catalog of any size, prefer building the union from the limit-1 sweep plus one combined `filter[collection_ids][]` OR query, and keep the per-id calls purely for emptiness.

   **Shortcut worth knowing for large catalogs.** The legacy `GET /api/company/v1/products` returns, per product, an embedded `category` object and a full `collections` array — plus `meta.pagination.total_count`, which v202604 does not provide. On a big catalog that collapses this entire sweep into the product fetch itself and gives exact membership counts for free. Costs: page-based pagination (`per_page` defaults to 10, so pass it explicitly), a much heavier payload per product, and the `status: "active"` vocabulary above. Use v202604 as the default because it is the documented, supported surface; reach for v1 deliberately when the membership sweep would otherwise cost dozens of calls, and say in the report which one you used.

6. **Warehouses** — `GET /api/settings/warehouses`, only if stock problems appear, to say where inventory should have landed.

7. **Enrollment packs** — `GET /api/v202604/company/enrollment-packs?page[limit]=100` (same cursor pagination). These are the paid signup tiers: on a direct-sales company the pack is how a rep joins, so a broken pack costs a recruit, not just a sale. Detail is `GET /api/v202604/company/enrollment-packs/{id}` for `member_enrollable_products`, `subscription_enrollable_products`, and `enrollment_pack_agreements` (all SHOW-only).
   Audit them as their own population, running **both** the pack-specific checks and every shared product check (see *The same checks, on packs*) — never fold them into the product score, and never skip them just because the product catalog looks clean.
   Two filters on this endpoint are worth using rather than reimplementing: `filter[country]=<ISO>` proves per-market availability, and `filter[status]=published` separates live tiers from drafts. Compare filtered against unfiltered counts instead of interpreting the `countries` array by hand.
   **An empty list ends this population immediately.** Most companies are not direct-sales and have no packs; that is the normal case, not a finding. Do not fetch pack detail, do not fetch compliance, do not mention enrollment anywhere in the report.

8. **Import reconciliation** — every check above is internal-consistency only, so a product that never arrived is invisible to all of them and a half-imported catalog can still score 100. If the company has an import manifest or a `fluid-catalog-index.json` in the project, compare its product count and titles against the live catalog and report anything missing as its own line. If neither exists, say plainly that arrival could not be verified and that the score covers only what is in Fluid.

Tell the user what you're auditing in one line, naming the populations you actually found ("Checking 412 products / 1,180 variants, 15 categories and collections, and 3 enrollment packs against the US market…"), and then go quiet until the report.

## The real field shapes (do not guess these)

- `status` is **resolved server-side and has four values**: `archived` | `draft` | `scheduled` | `published`. `scheduled` means a future `publish_at`, so the API already tells you that — never re-derive it by comparing `publish_at` to today. **Skip `archived` entirely** — an archived product with no description is not a problem to fix.
- `active` is **not** the inverse of draft. It is computed as `!archived && public`, so the two fields are orthogonal, not two readings of the same thing: a `draft` product that is public returns `active: true`, and `active: false` means *archived or non-public* — it never means draft. Branch on `status` for lifecycle and treat `active` purely as the archived-or-hidden signal. Counting drafts off `active` under-reports them.
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

**Packs get the same treatment as products, not a lighter one** — but each fact is counted once. The table below holds the product checks plus the two that exist *only* for packs (pack no agreements, pack empty contents). Everything else a pack is checked for is a shared check re-run against the pack's own field names, defined in *The same checks, on packs* right after. Run both tables; skipping the second is the most common way this skill under-reports, and duplicating a row across the two is the most common way it over-reports.

| Check | What counts as a problem | Level |
|---|---|---|
| No price in market | The variant has **no** `variant_countries[ISO]` entry for the audited market, or that entry exists with a `price` of null / `"0.0"`. A row that exists and carries a real price but is switched off (`active: false`) is **not** counted here — that is *Unbuyable in market*. One fact, one deduction: this check is about a **missing or unpriced** row | variant |
| Orphan variants | A variant with no `sku` **and** empty `option_ids`; or a `variant_countries` key for an ISO the company has not opened | variant |
| Missing SKU | A variant whose `sku` is null or blank **but which has `option_ids`** — a real, selectable variant with nothing to identify it in inventory or fulfillment. This is distinct from an orphan and the orphan rule does not catch it | variant |
| Duplicate SKUs | The same SKU on more than one variant, compared trimmed and case-insensitively (include `default_variant.sku`). Ignore null/blank SKUs here — they belong to Missing SKU, and treating them as duplicates of each other is a false positive | variant |
| Inconsistent currencies | `variant_countries[ISO].currency_code` differs from that market's own `currency_code` | variant |
| Missing images | Product `image_url` empty **and** `images` empty/null | product |
| Broken images | Any URL in `image_url`, `images.*.url` or `seo.image_url` that is empty or does not start with `http`. Do **not** fetch the URLs — a health check that issues a thousand requests is a different, slower tool. Say that unreachable-but-well-formed URLs are out of scope | image |
| Missing description | `description.body` empty per the rule above | product |
| Weak SEO | `seo.title` empty, or `seo.description` empty, or `seo.block_crawler: true` (the product is deliberately hidden from search engines — call that out by name) | product |
| Boilerplate SEO | A non-empty `seo.description` that is byte-identical to another product's, or to the company's default storefront blurb. Fluid falls back to a generic company description when a product has none, so this passes an emptiness check while search engines see duplicate meta descriptions. Detect it by grouping products by exact `seo.description` and flagging every group with more than one member. When the boilerplate is inherited by a product whose `description` is empty, the *shared-cause rule* under Scoring applies: report it, deduct once | product |
| No category | Product id absent from the category ∪ collection membership set | product |
| Unbuyable in market | Every variant's market row **exists and is priced**, but each one is `buyable: false` or `active: false` — the product is switched off for this market rather than missing a price. A **configuration** fault, and it is scored. Never count a product both here and under *No price in market*: a missing or unpriced row is that check, a present-but-switched-off row is this one, and `active: false` belongs to this row alone | product |
| Out of stock | **Informational only — never scored.** `in_stock: false`, or `track_quantity: true` with `inventory_quantity` 0/null and `keep_selling: false`. Cross-check the count for free with `filter[availability]=in_stock`: the in-stock population plus your out-of-stock count should equal the non-archived total, and if it doesn't, your stock logic is wrong — say so rather than reporting the number anyway. Being out of stock is a business state, not an import defect: a genuinely sold-out product is correctly marked sold out, and scoring it punishes a catalog for telling the truth. Report it as a count below the scored issues so the user can confirm it is genuine | product |
| Pack no agreements | An active pack whose detail returns an empty `enrollment_pack_agreements`. A rep is signing up with nothing to accept — a compliance exposure, not a cosmetic gap. Say so plainly and point at the country's required agreements | pack |
| Pack empty contents | An active pack where `member_enrollable_products` and `subscription_enrollable_products` are both empty: the buyer pays the fee and receives nothing | pack |
| Bundle integrity | **Informational only — never scored. Ask the API, do not read titles.** Request `filter[bundle]=true` (one extra call) to get the products Fluid itself considers bundles, then flag any of them whose `bundle_groups` is empty: a declared bundle with no component groups. That is a fact from two fields, not an inference. **Do not** detect bundles by a title that joins two other product titles — every product with "&" or "and" in its name is a false positive, and `pricing.compare_at` above `pricing.price` is not evidence either, it is just a product on sale. The inverse case (a de-facto pair sold as one simple SKU, never flagged as a bundle) is *not* detectable from the API and is a legitimate merchandising choice — do not guess at it. When this fires, state it as an observation with its consequence (stock will not decrement for the components) and let the user decide | product |

## Taxonomy checks — categories and collections

Categories and collections are browsing surfaces: each one backs a public page. They fail in their own way and are audited as **one combined population** (categories + collections together), because a shopper cannot tell them apart and both break identically. Everything below is read from the API records fetched in step 2 plus the membership sweep in step 5 — no page is fetched.

| Check | What counts as a problem |
|---|---|
| Empty collection / category | The per-id membership call returns `products: []` while the resource itself is `published` and `active`. A published taxonomy resource with no members is a dead end for anyone who reaches it, and it is the highest-value taxonomy finding — name it by title and say it is published and holds nothing. State it as a data fact; do not claim the nav links to it, since you have not looked at the nav |
| Missing image | `image_url` empty **and** `images` empty/null. Category tiles and collection cards are the main navigation art on most themes; empty ones render as blank frames in a grid |
| Broken image | Any URL in `image_url`, `images.*.url` or `seo.image_url` that is empty or does not start with `http`. Same rule as products and packs, and the same out-of-scope note: do **not** fetch the URLs, so a well-formed but unreachable URL is not a finding here |
| Missing description | `description` empty or null. Unlike a product, this is also the only body copy the category page has |
| Weak SEO | `seo.title` empty, `seo.description` empty, or `seo.block_crawler: true` |
| Boilerplate SEO | Group all categories AND collections by exact `seo.description` and by exact `seo.image_url`; flag every group with more than one member. Fluid falls back to one company-wide blurb and one brand-default image, so a freshly imported store typically has every single taxonomy page sharing both — report it once as a group, not once per resource. Almost always these resources also have an empty `description`, so the *shared-cause rule* under Scoring applies: the shared blurb is already paid for under *Missing description* and only the shared `seo.image_url` half deducts here |
| Unavailable | `status` is anything other than `published` (`draft` or `scheduled` — the API resolves a future `publish_at` to `scheduled` for you, so don't compare dates yourself), or `active: false` — remembering that `active` means archived-or-non-public and is not the draft flag. The resource exists in the admin but is not live |
| Duplicate title or slug | Two categories, two collections, or a category and a collection sharing a title or slug — usually an importer that created both kinds from the same source taxonomy. Say which pair, since the shopper sees two identical entry points. **Population is affected resources, not pairs:** three duplicated pairs are six affected resources, so `10 × 6/15`, never `10 × 3/15`. Counting pairs halves the deduction and makes the score depend on who ran the audit |

**Thin, not broken:** a category or collection holding exactly one product is worth a single informational line (`• 2 collections hold only one product each (Hatch Rest, Hatch Grow)`) but is **not** scored. A one-item collection is often deliberate staging for a range that is still arriving.

**Not applicable:** no price, no SKU, no stock, no variants, no currency — taxonomy resources carry none of these. Do not invent equivalents.

## The same checks, on packs

Run every row of this table. The left column is the product check already defined above; the middle column is how it is evaluated on a pack. Same counting, same proportional scoring, separate population.

| Product check | On a pack | Why it matters here |
|---|---|---|
| Missing images | `image_url` empty **and** `images` empty/null | The join page is the conversion page; an empty frame there costs a recruit |
| Broken images | Any URL in `image_url`, `images.*.url`, `seo.image_url` that is empty or not `http`-prefixed. Do not fetch | Same rule, same out-of-scope note |
| Missing description | `description` empty — remember it is `string` OR `object` (`.body`) OR `null`, so handle all three before deciding it is empty | A tier with no copy is an unfinished import |
| Weak SEO | `seo.title` empty, `seo.description` empty, or `seo.block_crawler: true` | Packs have a full `seo` object exactly like products |
| Boilerplate SEO | Group packs by exact `seo.description`; flag every group with more than one member, and flag any that equals the company default blurb. Subject to the *shared-cause rule* under Scoring when the pack's own `description` is empty | Tiers are the likeliest place to inherit the same generic text |
| No price in market | `enrollment_fee` null or `"0.0"`, **or** the pack absent from `GET …/enrollment-packs?filter[country]=<ISO>` while present unfiltered | Verify availability with the API's own filter rather than interpreting `countries` yourself — it is authoritative and cheap |
| Out of stock / unavailable | **Not a scored check on a pack — it is the lifecycle exclusion.** A `status` of `draft` or `scheduled` (packs have no `archived`), or `active: false`, takes the pack *out of* the scored population and onto the informational line, exactly as it does for a draft product. There is no inventory on a pack either, so the unscored out-of-stock case cannot apply | A pack cannot be both outside the population and deducted from it. Excluding wins; a join flow where *no* tier is published is caught by the *Ready to sell* line instead |
| Duplicate SKUs | **No pack equivalent** — packs carry no SKU. The nearest failure is two packs sharing a title or slug; flag that instead if you see it | — |
| No category | **Product-only.** `…/enrollment-packs` accepts no `filter[category_ids]`, and live categories carry `source_type: "product"`, so packs are not categorized. Do not report packs as uncategorized | — |
| Orphan / missing SKU / inconsistent currencies | **Product-only** — variant-level concepts. `enrollment_fee` is a single value in the company's base currency, so there is no per-market currency to disagree | — |

Population and lifecycle work *almost* the same way, with one difference: **packs have no `archived` state.** Their statuses are `draft` | `scheduled` | `published`, full stop — so there is nothing to skip as archived here, and a rule about archived packs is a rule for a state that cannot occur. Exclude `draft`, `scheduled` and inactive packs from the score and report those as the same informational line products get (`• 2 packs still in draft — the join page shows no tiers`). **This exclusion is the only way lifecycle touches the pack score** — there is no separate scored `unavailable` deduction, because a pack that has left the population cannot also be deducted from it. Packs are few enough that the 150-item detail cap never bites: fetch `…/enrollment-packs/{id}` for every one of them so the agreements and contents checks run on the whole population, and label nothing `partial` unless a call actually failed.

**False-positive guards — obey these or the report is noise:**

- A variant with `image_url: null` **inherits the product image**. That is normal Fluid behaviour. Only count a variant as image-less when the parent product has no image either.
- `compare_at: "0.0"` and `subscription_price: "0.0"` mean "not set", not "priced at zero". Never report them as a zero price.
- `cv` / `qv` of `"0"` are normal for a company that doesn't run a comp plan. Never flag them.
- On a pack, an **empty `countries` array means available in every market the company sells in** — unrestricted, not unavailable. Reporting it as a gap inverts the meaning of the field.
- `additional_volume` of 0 or null is normal, as are `membership_optional` / `membership_after_one_month` in either state. None of them are health findings.
- A category with `has_children: true` is a parent node and may legitimately hold no products of its own — its children hold them. Check `has_children` before reporting a category as empty, and never flag a parent whose children are populated.
- Utility collections that exist to drive theme behaviour rather than browsing — a `default-suggested-items` / "Recommended Products" set, a `non-commission-products` set — are frequently and correctly empty or partial. Name them if empty, but say plainly that they may be internal rather than treating them as broken navigation.
- Products that are not live are **not scored** — intentional drafts exist. But these are three *orthogonal* conditions, not three ways of spotting one: `status: draft` is unfinished, `status: scheduled` is finished and dated for later, and `active: false` is archived-or-non-public (`!archived && public`) and can be true of a *published* product. Exclude on `status` (`draft`, `scheduled`, `archived`) and separately on `active: false`, then report the counts as one informational line each where they differ, because a post-import catalog stuck in draft is invisible to customers and is often the real finding. Do not collapse them into a single "not live" bucket — the fix differs: a draft needs publishing, a non-public product needs its visibility flipped.

## Scoring

Each check costs its full weight only when it affects the whole catalog, and proportionally otherwise — one bad product in a thousand must not read like a catalog on fire, and half the catalog with no price cannot be shrugged off.

```
deduction(check) = weight × (affected / population)
score            = round(100 − Σ deductions), floored at 0
```

Weights: no price in market 20, orphan variants 20, unbuyable in market 20, missing SKU 15, missing images 15, duplicate SKUs 15, inconsistent currencies 15, missing description 10, weak SEO 10, boilerplate SEO 10, no category 10, broken images 10.

No price in market, orphan variants and unbuyable in market lead at 20 because they are the only three that make a product genuinely unsellable rather than merely untidy.

**Shared-cause rule — report twice, deduct once.** Fluid derives `seo.description` from `description`, so an empty description *causes* the boilerplate meta description that follows it. When a boilerplate `seo.description` is the documented fallback for a `description` you have already counted under *Missing description*, **report both lines** — the SEO consequence is worth naming and the user fixes it in one edit — but deduct only under *Missing description*, and say so on the SEO line (`• 1 product on the boilerplate meta description — 86807, caused by the empty description above, not scored again`). This applies to all three populations, and it bites hardest on taxonomy, where every resource typically has both. The same holds when `seo.description` comes back **empty** instead of boilerplate — that fires *Weak SEO* rather than *Boilerplate SEO*, from the identical cause, and is deducted the same single time.

What still deducts independently, because nothing else caused it: a duplicate `seo.description` on a resource that *has* a real description, an empty `seo.title`, `block_crawler: true`, and a shared `seo.image_url`. That last one matters on taxonomy — a brand-default OG image is its own fallback, unrelated to the description — so when the boilerplate finding is part description and part image, the description half is already paid for and the image half is not. Deduct the row once for the independent half.

The general form of this rule is the one at the end of the pack section: if two checks fire because one field is empty, the score moves once. Two lines in the report, one deduction.

**Out of stock and bundle integrity carry no weight** — both are observations about how the business is running, not defects the import introduced. They are reported below the scored issues and never move a score. Scoring out-of-stock in particular is the fastest way to make a healthy catalog look broken: a seasonal or sold-out product is *correctly* flagged, and deducting for it means the score drifts with inventory instead of measuring import quality.

**Enrollment packs score separately.** Give them their own line — `Enrollment Packs: 40/100 (3 packs)` — computed the same proportional way over the pack population. Only two weights are pack-specific:

```
pack no agreements 20 · pack empty contents 20
```

Every other pack check is a shared check from the product table and **carries the exact same weight there as it does on a product** — no price in market 20, missing images 15, missing description 10, weak SEO 10, boilerplate SEO 10, broken images 10. (There is deliberately **no** `unavailable` weight here: draft, scheduled and inactive packs leave the population under the lifecycle rule above. A pack has no variants and no inventory either, so neither the scored *unbuyable in market* nor the unscored *out of stock* case has a pack equivalent.) Do not invent separate pack weights, and **count each check once**: a pack with no `enrollment_fee` is one *no price in market* hit, not that plus a separate "missing fee". If you find yourself deducting twice for the same fact, you have double-counted. A pack population of three means each failing pack moves the score by a third of the weight, so state the pack count next to the score. Two scores beat one blended number here, because a company can have a spotless product catalog and a completely broken join flow; averaging them hides exactly the thing the user needs to see.

**Taxonomy scores separately too**, on the same rule: one line, `Taxonomy: 64/100 (4 categories · 11 collections)`, over the combined population, with weights: empty collection/category 30, missing image 15, missing description 10, weak SEO 10, boilerplate SEO 10, broken images 10, unavailable 10, duplicate title/slug 10. Empty outranks everything because it is the only one that produces a page a shopper can land on and get nothing from. When the company has no categories and no collections at all, omit the line entirely — same rule as packs.

**When the company has no packs, say nothing about enrollment at all** — no score line, no "n/a", no mention in Issues. Most companies are not direct-sales and have no packs; a line explaining an absence is noise. Same for taxonomy: no categories and no collections means no taxonomy line. Only report on populations that exist.

Population is that check's own denominator: non-archived products for product-level checks, variants of those products for variant-level ones, image count for broken images. Archived products are outside every population.

# Step 2 — The report

Exactly this shape, nothing else:

```
Catalog Health Score: 99/100
Taxonomy: 61/100 (4 categories · 11 collections)
Enrollment Packs: 80/100 (3 packs)
Ready to sell: NO — 12 products unbuyable in the US market
412 products · 1,180 variants · United States (USD)

Issues

• 15 taxonomy pages have no image and no description of their own
• 3 packs with no agreements attached (Starter, Pro, Elite)
• 15 taxonomy pages share one boilerplate meta description and one default image
• 2 published pages hold no products — Refurbished Devices (collection),
  Sleep Audio & Membership (category)
• 12 products with no price in the US market (86811, 86814, 86820)
• 8 products missing descriptions (86808, 86809, 86811)
• 2 products blocked from search engines (seo.block_crawler)

Informational (unscored)

• 14 products still in draft — not published, so not for sale
• 3 products are marked out of stock — confirm that's genuine

Recommendations

• …
```

Every number there follows the formula, and two things about it are worth reading twice. The Issues block is ordered by **what each line actually cost**, not by weight: the taxonomy image and description gaps hit the whole 15-resource population and cost 25 points between them, while the twelve unpriced products cost `20 × 12/412 ≈ 0.6` against a 412-product population, and the two empty pages cost `30 × 2/15 = 4` despite carrying the heaviest single weight in the skill. And that is exactly why *Ready to sell* is a separate blunt line — this catalog scores 99 and still cannot sell twelve products. If your issue order and your scores disagree, recheck the arithmetic before reordering.

That example is a store with real problems. A healthy one looks like this — and **this is the expected outcome, not a failure to find anything.** Do not go hunting for findings to fill the block:

```
Catalog Health Score: 100/100
Taxonomy: 100/100 (6 categories · 4 collections)
Ready to sell: YES — with cosmetic gaps
412 products · 1,180 variants · United States (USD)

Issues

• 2 products missing descriptions (86806, 86807)

Recommendations

• description.body also feeds seo.description, so this costs twice — worth
  writing before the next crawl.
```

The 100 next to a real finding is not a rounding bug and not a contradiction: `10 × 2/412 = 0.05` rounds to zero, so a genuine gap affecting two products out of four hundred correctly costs nothing. Report the finding and leave the score at 100. **Never invent a deduction to make the number look earned** — proportional scoring means a large catalog absorbs small defects, and that is the whole point of it.

The **Ready to sell** line is a blunt yes/no above the scores, because 88/100 reads like a pass while a product sits in the catalog that nobody can buy. It is NO whenever a product is unsellable for a **configuration** reason — no `variant_countries` row for the market, that row inactive, a null/zero price, or every variant `buyable: false` — or whenever the company has enrollment packs but **not one of them is published**, because a join flow whose every tier is draft or scheduled cannot take a recruit today. That last one is a population-level fact read off the pack list, not a per-pack deduction: the packs themselves stay out of the score. The count is of products, not issues. Otherwise YES, optionally with "with cosmetic gaps".

**Being out of stock does not make it NO.** A sold-out catalog is configured correctly and simply has nothing to ship; that is a business state, not a launch blocker. Mention the out-of-stock count on its own line instead.

It answers "can this catalog transact?", judged from Fluid data. It is **not** a claim that the storefront renders correctly — that is the theme's job and outside this audit. Never widen it into one.

List pack issues in the same Issues block as product issues, in the same one-line format, prefixed so the population is unambiguous (`• 3 packs missing agreements (Starter, Pro, Elite)`). Name packs by title rather than id — there are only ever a handful and the title is what the user sees in the admin. Do not give packs a separate Issues section; one ordered list of everything wrong, worst first, is the point of the report.

Order issues by how much they cost the score, not by the order you checked them. One line each: the count, the thing, and up to three example ids in parentheses. Say "none" under Issues when the catalog is clean, and use Recommendations to point at the next market instead.

Below the Issues block, add an **Informational (unscored)** section for the states that are business facts rather than defects — drafts (`• 14 products still in draft — not published, so not for sale`), out of stock, thin one-product collections, bundle-integrity observations, the audited-market choice when no market was flagged default, and any population you could not verify. Keep it clearly separated so nobody reads these as things to fix.

Everything you want to say goes in one of those four blocks. **Do not add a free-standing paragraph between the header and Issues** — a finding parked outside every list is ordered by nothing and counted by nothing, which is how the market-default note ends up being the one thing in the report with no home.

Recommendations are per issue found, one line, concrete and specific to Fluid:

- **No price in market** — price lives per market on `variant_countries`, so an importer that created the variant without a row for this country leaves it unsellable there. Fix first; it is the only issue that makes a product literally unbuyable.
- **Orphan variants** — variants with no SKU and no options are usually an interrupted import; they break cart pricing rather than merely looking untidy.
- **Duplicate SKUs** — deduplicate before re-importing; a repeated SKU makes inventory and reporting ambiguous.
- **Inconsistent currencies** — align each `variant_countries` entry with its market's own currency before any order lands; mixed currencies corrupt every total that sums across variants.
- **Missing images** — re-run the image step of the import; some themes render an empty frame.
- **Broken images** — re-upload through the DAM rather than patching URLs.
- **Missing description** — `description.body` also feeds `seo.description`, so this costs twice.
- **Pack no agreements** — a rep enrolling with no agreement to accept. Flag it as compliance, not polish, and offer to run the country compliance skill for the required list.
- **Pack empty contents** — name the pack by title, since there are usually only a handful: the recruit pays the fee and receives nothing. A pack with no `enrollment_fee` is the *no price in market* line rather than a separate "missing fee" one, and draft or scheduled packs belong under Informational — neither gets its own recommendation here.
- **Missing SKU** — a selectable variant with no SKU cannot be picked in a warehouse or reconciled in reporting. Common on imported bundles, where the parent got a SKU and the option rows did not.
- **Bundle integrity** — one neutral line, below the scored issues: name the product, say stock will not decrement for its components, and ask whether that was intentional. Do not phrase it as something to fix.
- **Weak SEO** — set `seo.title` / `seo.description` per product; `block_crawler: true` removes the product from search results entirely, so confirm that was deliberate.
- **Boilerplate SEO** — these products are inheriting the company's default blurb; write a real `seo.description` per product. Name the shared text once instead of repeating it per product.
- **No category** — the product is reachable only by direct link or search.
- **Empty collection / category** — fix first among taxonomy issues: either assign products to it or unpublish it, because a published taxonomy page with no members is a dead end for anyone who reaches it. Name each one by title and say which kind it is; a collection and a category look the same to a visitor but live in different admin screens.
- **Taxonomy missing image / description** — these are the tiles and the body copy of the browse pages, not metadata. Report them as a count across the combined population rather than resource by resource.
- **Taxonomy boilerplate SEO** — say it once for the whole group and quote the shared blurb a single time: "15 taxonomy pages share the same meta description and the same default OG image." Repeating the same sentence fifteen times is the fastest way to make this report unreadable.
- **Duplicate title or slug** — name the pair and which kind each is; usually an import created a category and a collection from the same source taxonomy, giving the storefront two identical doors.
- **Out of stock** — one neutral line below the scored issues, with the count and up to three ids: "3 products are marked out of stock — confirm that's genuine." Name the warehouse from `GET /api/settings/warehouses` when there is only one. Do not frame it as a defect and do not let it affect the score; a sold-out product is doing its job.
- **Unbuyable in market** — this one *is* a defect and it is scored: the market row exists but is switched off (`buyable: false` on every variant, or `active: false` on the row), so the product cannot be sold in the audited market no matter how much stock exists.
- **Drafts** — publishing is a bulk action in the admin; ask before assuming they should go live.

Close with a single next step, not a menu: the highest-weight issue, phrased as an action. If the company has other open markets, add one line offering to run the same audit for them.

## Optional deep pass — only if asked

If the user asks *why* copy is weak, or asks about claims/compliance, run `GET /api/v202604/company/products/{id}/compliance` on at most 25 products — and `GET /api/v202604/company/enrollment-packs/{id}/compliance` on every pack, since pack copy is where income and earnings claims live and it is the higher-risk surface of the two. Both are API endpoints, so this stays inside scope. It returns a pre-computed `score` (0–10), `status`, `summary` and `compliance_issues[]` with `severity` and a concrete `recommendation`. Report it as a separate block with its own 0–10 scale — never fold it into the 0–100 health score. For acting on those findings, hand off to the `themes/suggested-changes` skill rather than editing anything here.

# Rules

- Read-only. Every call is a GET. Never offer to fix anything by writing — if the user asks, tell them what to change and where, and let them decide.
- Never guess a number. If pagination stopped early, a detail fetch failed, or an endpoint errored, say which part of the catalog you could not see, give the score for what you did see, and label it `partial`. A confident score over half a catalog is worse than an honest gap.
- One market per report. Prices, currencies and availability are per market, so a single blended score across markets means nothing.
- **Fluid data only.** Never `web_fetch` a storefront page, never parse rendered HTML, never report on the theme. Every number in the report must trace to an API response you received in this run. If you find yourself wanting to look at a page, that is a different skill — say so and stop.
- Never read a price, title, or product off a rendered page and report it as company data. Theme demo content looks exactly like real content, and repeating it back as real is the worst failure this skill can have. The corollary of the scope rule: since you never fetch a page, this can only happen if you go outside scope.
- A clean report is a statement about the data, not about the customer's experience. Do not write "the store looks good" or imply pages render correctly — you did not look. Say the catalog data is sound.
- Never invent fields, and never repeat the old myth that Fluid has no SEO fields or no per-product stock — `seo`, `track_quantity`, `inventory_quantity` and `inventory_levels` all exist on the shapes above. What Fluid has no single field for is a product-level stock count independent of variants.
- Don't use `/api/products` (legacy). It answers 200 but embeds the entire country configuration blob per product and will exhaust context on the second page.
- Keep the chat short. The report is the output; don't narrate the checks as you run them.
