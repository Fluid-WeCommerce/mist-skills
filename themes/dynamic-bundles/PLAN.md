# Universal Dynamic Bundles Skill — Research & Implementation Plan

Status: **IMPLEMENTED AND FIELD-VERIFIED.** Planned 2026-08-05; built and exercised against a live company 2026-08-06.
Author: Mist. Date: 2026-08-05, revised 2026-08-06. Reference corpus: the 18 docs now shipped alongside this skill at `reference/*.md` (originally read from `fluid-dynamic-bundles copy/`).

> **Read PART 7 before trusting PART 1.** Parts 1–6 are the pre-build research record and are
> preserved deliberately, including the questions that were open at planning time. PART 7 records
> what changed once the writes actually ran — including **two claims in PART 1 that live testing
> disproved**. Where the two disagree, PART 7 wins. The operational form of PART 7 is
> `playbooks/08-api-write-recipe.md`; this part exists to show the evidence behind it.
Primary test company: **Chipotle** (`980243433`) — confirmed live: `GET /api/v2025-06/bundles` → `[]`, active theme `57123` "Chipotle Onboarding Theme", sibling theme `57124`. Clean slate, exactly as the readiness doc predicts.

---

# PART 1 — What I actually learned

## 1.1 The model, in one page

A bundle is **a Product** with `products.bundle = true`, a shadow `Bundle` row (1 live row per product, unique index), and N `ProductBundleGroup` rows each holding N `BundleGroupItem` rows. Three layers, and which layer owns a setting determines what it can influence:

```
BUNDLE  (products.* + products.bundle_config + bundles.settings)
  └ GROUP (product_bundle_groups.* + .pricing_config)   group_type = included | customizable
      └ ITEM (bundle_group_items.* + .config)           one variant, in one group
```

Load-bearing consequences:

- **`group_type` is a stored NOT-NULL column**, not emergent. The *bundle's* static/dynamic nature is emergent (`static?` = all groups included).
- **Static/`included` groups are reconstituted server-side** and must **not** be sent in `bundled_items` — with exactly one exception: an included group that is a member of an exclusive pair *must* be sent, because the server cannot know which branch was chosen.
- **Bundle-level flat pricing collapses the layers.** When on, group and item prices become display-only; nothing beneath can move the charge. It is *illegal* to combine with a `dynamic_price` group (model validation), so a theme never has to reconcile those two.
- Almost everything a theme cares about lives in four schemaless JSONB bags: `bundles.settings`, `products.bundle_config`, `product_bundle_groups.pricing_config`, `bundle_group_items.config`. Unknown keys round-trip verbatim and are never rejected — a typo returns 200 with the key missing.

## 1.2 Detection — the only gate worth writing

```liquid
{% if product and product.product_bundle_groups.size > 0 %}
```

Valid in every scope. `is_bundle` is API-only and nil everywhere in Liquid. `slug`/`handle` are nil in page and section scope. `product.bundle` *does* work (contrary to the old skill) but is absent from the enrollment product hashes and can be `true` with zero visible groups. `bundle_in_stock` is `true` on non-bundles — never a detector.

## 1.3 Three "product" shapes, and the one that matters

| Scope | Producer | Keys | Has `mutually_exclusive_groups`? |
|---|---|---|---|
| **A** page `product` (a PDP, and any `{% section %}` on it) | `Variables::Product#product_hash` | 50 | ❌ **no** |
| **B** `section.settings.<product-typed setting>` | `ProductDrop#as_json` | 40 | ✅ yes |
| **C** live `ProductDrop` (`products[i]`) | Drop object, every public method | — | ✅ yes |

A section **inherits the page scope verbatim** — inside `sections/*.liquid` on a product template, `product` is always scope A. So on the deployment shape we want (one shared bundle template, no pinning), **exclusivity data is only reachable at `product.bundle_config.mutually_exclusive_groups`**. And that value holds **`sort_order`s, not group ids**, in two possible shapes (`[{ids:[…],default:…}]` or a bare `Array<Integer>`), and is `null` — not `[]` — on older bundles.

## 1.4 The three moving parts (and the two that are missing by default)

| Part | Default on a new company |
|---|---|
| The `product_bundle` section | ✅ free everywhere — one global row unioned into every theme, byte-identical across 33 themes / 6 companies, renders on companies with zero bundle infrastructure |
| A host `product` template containing it | ❌ **no seed ships one** |
| Routing (product → that template) | ❌ **no auto-assignment exists** |

Routing is not a column — it is a `template_resources` join **scoped to the currently-active theme**. So: switching or cloning a theme silently un-routes every bundle; and a bundle created via API with no explicit `application_theme_template_id` comes back `null` and renders as an ordinary product.

**A bundle on a bundle-unaware theme is a silent revenue hole**: normal-looking product page, working native add-to-cart, hard failure at checkout (`orchestrator.rb` `validate_bundle_configuration`). Nothing surfaces to the merchant.

## 1.5 The trilemma that decides the architecture

Global sections **never resolve typed `{% schema %}` settings** (`section_templates_for_template` omits the global union — defect **P3**). Measured, all four combinations:

| Setup | Data blob | exclusivity | schema settings | scales? |
|---|---|---|---|---|
| Global section, no pin | 50-key page hash | ❌ | ❌ inert | ✅ one template |
| Global section + `bundle_product` pinned | ❌ **dead shell** | — | — | ❌ |
| Local clone, no pin | 50-key page hash | ❌ | ✅ | ✅ one template |
| Local clone + pin | 40-key drop | ✅ | ✅ | ❌ **one template per bundle** |

**No stock configuration gives both exclusivity and scale.** Pinning is also actively *destructive* on a global-only install (a raw integer is non-blank, suppresses the page-product fallback, emits no blob). And a theme-local clone **shadows the global permanently and never receives updates** (`auto_upgradeable?` is hardcoded `false`; two Chick-fil-A clones are already 15.7 KB stale).

⇒ The scalable shape is: **theme owns the section source, never pin `bundle_product` on `product/*`, read exclusivity from `bundle_config`.**

## 1.6 Write surfaces — one is safe, one is not

**Surface A — `POST /api/company/v1/products/create_bundle_product` / `PATCH …/{id}/update_bundle_product`** (what the admin Bundle Builder uses). Only this surface can:
- write `products.bundle_config` — *the place the cart validator and cart pricer actually read* `mutually_exclusive_groups`
- set `products.bundle`, `track_inventory_on_bundle_items`, variants, `variant_countries`, images, SEO
- run `BundleConfigValidation` (exclusive-pair arity/uniqueness + the `hidden`-flag rules)
- do surgical nested deletes via `_destroy`

**Surface B — `/api/v2025-06/bundles`** is a trap: no pagination, `per_page`/`page` silently ignored, **omits `product_id`** (you cannot get from bundle to product), skips `BundleConfigValidation` entirely, writes `bundles.settings` *without* mirroring to `products.bundle_config` (so exclusivity written here is honoured by the portal and **silently ignored by the cart**), returns **500 not 422** on any schema violation, `items[].is_default` 500s on update and is dropped on create, `sort_order` is overwritten by array position, `groups: []` destroys all groups, and it is entirely undocumented and untested upstream.

⇒ **The skill writes bundles exclusively through Surface A**, reads through `GET /api/company/v1/products/{id}`, and uses Surface B only as a *read* cross-check (never as the source of truth, never for bundle→product resolution).

Two more write rules learned the hard way:
- `is_default` must be sent **inside `config`** on both surfaces.
- **Match bundle → product by `product.product_bundle_groups[].id`, never by slug.** Duplicate/orphan Bundle rows share a title and the later row often owns the uniquified slug — slug matching resolved the *wrong* bundle on ≥3 fixtures, one of which reports empty `country_pricing` while the product actually charges $25.
- **Delete the Bundle before the Product.** Reverse order leaves an orphan whose `DELETE` then 500s forever (nine such orphans exist on CrashTest).

## 1.7 The cart contract

```js
window.FairShareSDK.addCartItems(PARENT_VARIANT_ID, {
  quantity: 1,
  bundled_items: [{ variant_id, quantity, product_bundle_group_id, subscription?, subscription_plan_id? }]
});
```

- **Always send `product_bundle_group_id`.** Schema-optional, load-bearing: omitting it changes `bundle_selection_key` (`1527:56794x1|…` vs `56794x1|…`), so the same bundle added tagged once and untagged once produces **two lines and a double charge**. Mixing tagged/untagged for one variant is a hard 422.
- **Never send included/static items** — except exclusive-set members (§1.1).
- `quantity: 0` entries are **dropped before rule counting**, not rejected.
- **Duplicates are not de-duplicated** — counting is over *entries*, not distinct variants. One entry per click ⇒ silent over-charge. Collapse into `quantity` yourself.
- A cold cart is **two** HTTP calls for a bundle (create empty, then `…/items`); non-bundles are one.
- Re-adding **sets** quantity, it does not increment. In-place edits via `POST` + `cart_item_id` are silently ignored; `PATCH …/bundled_items` works but leaves a stale selection key. **Use delete-then-re-add.**
- **The promise never rejects.** `swallowErrors: true` ⇒ resolves `undefined` on 4xx/5xx/network, and `performAddCartItems` replaces the server body with a generic `"Failed to add items to cart"`. A theme `.catch()` never runs. The stock section's `.then()` therefore opens an unchanged cart drawer *after a failed add*.
- **HTTP 200 is not success.** A country-unavailable child returns 200, prices the bundle at **$0.00**, and (finding D) leaves `items[].errors` **empty** — no programmatic signal at all. `valid_for_checkout` is `false` on every bare cart, so it is not a guard. Out-of-stock is *skippable*: the line is dropped and reported in a top-level `skipped_items` array that is **not** on the resolved Cart object (only on the event detail).

## 1.8 Pricing — the chains a theme must implement

- **Item:** `country_prices[ISO]` → `item.price` → `variant.variant_countries[ISO].price`. `item.price` is `"0.0"` on **100%** of fixtures, and a zero here means *unset*, not free.
- **Group:** `pricing_config.country_pricing[ISO]` → `pricing_config.fixed_price`. `group.fixed_price` reads `"0.0"` when unset — indistinguishable from a real zero unless you check `pricing_config.fixed_price` for key presence. `min_price`/`max_price`/`compare_at_price` are effectively dead (`"0.0"` on every live group).
- **Bundle:** `bundle_config.bundle_pricing_config.country_pricing[]` (values are **strings**). `product.bundle_price` is empty even with bundle pricing on. `primary_price`/`primary_currency` are admin echo — **never read by Rails**.
- `product.price` in the Liquid drop **is** correct and country-resolved (`"$50.00"`, or a `"$30.00 - $70.00"` range when any group is dynamic). Top-level `price`/`display_price` from *both* JSON APIs are computed with `country_code: nil` and read `$0.00` — unusable. But **`price_range`/`bundle_price_range` are correct and country-resolved**, and are the primary write-verification signal (verified 2026-08-06 on nine bundles, including one *wrong* `$55.75–$66.75` that exposed a real pricing defect — see `playbooks/08-api-write-recipe.md` §4).
- **Mode behaviour, verified three-way (display == cart == checkout):** `dynamic_price` sums selections and scales with quantity ✅; `fixed_price` group ignores picks *and* quantities ✅; bundle-level flat ignores everything below ✅; mixed = dynamic sum + fixed group price ✅. Two exceptions, both real money: an `included` group with **no** `fixed_price` displays as its item sum and **charges $0.00** (P11/finding C); a child with no priced country row **zeroes the whole bundle** (P6/finding D).
- **CV/QV only flow from `dynamic_price` groups.** Fixed-price / flat bundles credit 0/0 unless CV/QV is re-entered on the group or bundle `country_pricing` row. A theme that sums `variant_countries[].cv` to promise "you'll earn N CV" **overstates every non-dynamic group**.
- **Compare-at**: only render when `compare_price > price`, else you advertise an increase.
- Type traps in one object: `variant_countries[].price`/`wholesale`/`compare_price` are **floats**, `subscription_price` is a **string**; `cv`/`qv` are Integers in Liquid and **strings** in both APIs; `display_*` carries a `" (USD)"` suffix; drop prices can be BigDecimal engineering notation (`"0.4999e2"`) — `parseFloat` survives it, `{{ item.price }}` in Liquid does not.

## 1.9 Subscriptions

Precedence: bundle-wide `subscription: true` **suppresses** per-item forced-subscription checks. Item `force_subscription` ⇒ must send `subscription: true` (422 otherwise); `allow_subscription: false` ⇒ must not (422). Group `force_subscriptions` / `allow_subscriptions` apply the same way — but note group `allow_subscriptions` is **never read server-side**, and on real fixtures the forcing lives on the *item* while the group flag is false, so **check both levels**. A missing plan id with `subscription: true` gets the company default. `force_subscription` requires the item's product to have ≥1 active plan (model validation).

**P7 (by design, not filable): renewal price comes from the BGI variant's own `variant_country`, deliberately not the parent** — so a $35 bundle can renew at $100/mo or $0/mo depending only on which child was ticked, and **the PDP shows nothing**. The only theme-side remedy is disclosure.

## 1.10 What the platform section actually is

3063 lines. Lines 1–839 are inlined static CSS (there is no separate stylesheet to port). Lines 863–1148 are markup: 5 `<template>` blocks + 2 JSON `<script>` payloads + an empty `<div data-bundle-groups>`. Lines 1150–2966 are two IIFEs. **The visible DOM is built entirely by JS cloning templates.** The whole client contract crosses one tag:

```liquid
<script type="application/json" data-bundle-product>{{ bundle_product | json }}</script>
```

So *what the JS can act on is exactly what the drop serializes* — nothing the drop omits can be rendered, whatever the REST API returns.

Surface area: 5 templates, ~50 `data-*` hooks, 79 `bundle-*` classes, **plus 31 generic utility classes** (`.btn`, `.container`, `.text-sm`, `.flex`, `.font-bold`, `.mt-lg` …) that collide with any theme defining the same names, **46 inline `style=` attributes**, and **18 hardcoded hex colours**. It also emits a nested double `<section>`, a dead step-indicator subsystem, and a hardcoded green `#059669` progress fill that overrides the `progress_bar_color` setting. It reads three CSS tokens (`--clr-black`, `--clr-white`, `--text-sm`) that happen to exist on all 8 surveyed themes but are an alias shim on one, and `--text-sm` is `0.875rem` in one lineage and `14px` in the other.

The deployed global row is **not** the repo file (3058 vs 3063 lines; missing one merged commit) — so never assume a company's hosted section equals master; fetch and diff.

## 1.11 The defect surface a generated theme has to survive

Filable platform bugs relevant to us: **P2** exclusivity no-ops on the page path (shopper charged for a branch they never receive, $60 confirmed) · **P1** stored XSS via product title into an inline `<script>` (bundle-section-only; root cause `JsonFilter#json` using bare `JSON.generate`) · **P3** global schema settings · **P5** swallowed cart errors · **P6** silent $0.00 · **P10** bundle-wide subscribe shows $77 charges $70 · **P14** `max_only` cannot submit zero · **P16** **HTTP 500** when a selection bound is nil (nils are created by the platform's own `normalize_selection_bounds`, and the CTA *enables*) · **P17** no SDK ⇒ perfect-looking page, dead button, no console error · **P19** defaults pre-select past `max_selections` ⇒ `3 / 1`, CTA permanently dead, message says add *more* · **P20** phantom Add on a card disabled by an exclusive switch · **P21** contradictory out-of-stock wording.

Explicitly *not* bugs (don't design around them as if they were): **P4** the section doesn't self-guard (by design — a section renders where you put it; the trap is real, the fix is hosting) · **P7**/**P12** by design, named verbatim in their originating commits · **P11/P13/P16-fixture/P18** are API-only states the Bundle Builder cannot produce · **P8** is theme responsibility (send the group id) · the `e.target`-vs-`closest()` dead-click bug is **fixed** and the `pointer-events:none` / MutationObserver workarounds are unnecessary.

## 1.12 Assumptions that do NOT hold across companies

This list is the actual reason a "universal" skill is hard. Every item was observed varying:

1. **Two CSS token lineages** — `--clr-*` (7 themes) vs `--color-*` (chewy, where `--clr-*` exists only as an alias shim). Namespace must be *detected*.
2. **Three `.container` widths and two mechanisms** (1360 `width:` / 1280 `max-width:` / 1328), and the **newest PDPs bypass `.container` entirely** in favour of a per-section container keyed to `section.id`. A section that wraps itself in `.container` misaligns with the rest of the PDP on those themes — guaranteed, visible.
3. **`button, .btn {}` is hijacked on 6 of 8 themes** into a black flex box; `input, button, textarea, select { -webkit-appearance: none }` makes **native radios and checkboxes invisible on every theme**; `ul, li { list-style: none }` kills bullets on 7 of 8.
4. `!important` density ranges 0 → 16 plus 7 more inline.
5. **One currency / 2 decimals is not safe** — read `localization.country.currency.symbol` and `.decimal_places`.
6. **One subscription plan is not safe** — CrashTest has exactly one (618 Monthly), so the multi-plan picker has *never been exercised*. Plans attach company-wide.
7. **Hidden-group filtering differs by scope** — the drop rejects `pricing_config.hidden`, the page path does **not**. Filter yourself.
8. `mutually_exclusive_groups` shape varies and may be `null`; it references `sort_order`.
9. `description` on a group can be `""` *or* `null` (both occur live).
10. Some fixtures have **no image anywhere** — the placeholder path must work.
11. API traps that fake theme bugs: `per_page=100` on `/api/company/v1/products` returns **zero** products with no error (50 works); ignored filters return an unfiltered page; `?country=CA` is ignored, `?country_id=35` works.
12. Enrollment bundles expose the same data and have **zero** rendering support anywhere. Genuinely unsupported.

---

# PART 2 — Design decisions

## D1. Generate a theme-owned section, not a clone of `product_bundle`

**Decision:** the skill generates a theme-native section (working name `bundle_builder`) that implements the platform's *data contract and cart contract exactly*, and owns its own presentation layer. A patched clone of `product_bundle` is offered as a documented, non-default "parity mode".

Why, in order of weight:

1. **The brand requirement is unachievable with the platform section.** 46 inline `style=` attributes and 18 hardcoded hex colours outrank any stylesheet on specificity. "Match the company's branding" would mean `!important` warfare or editing the template anyway — at which point you own the source and the clone bought you nothing.
2. **A clone inherits ~11 client-side defects** (P2, P5, P10, P14, P15, P16-client, P17, P19, P20, P21, and P1's escaping) that we can simply not write.
3. **A clone never receives updates regardless.** `auto_upgradeable?` is hardcoded `false` and `prefer_theme_specific` makes a local copy shadow the global permanently. The "stay in sync with upstream" argument for cloning is *false* — cloning guarantees the drift it's supposed to avoid, and two CFA clones already prove it.
4. **The stable part of the platform is the contract, not the UI.** The drop shape and the cart schema are what upstream changes cost you; both are documented, both are what we build against. The 3000 lines of inlined CSS+JS are the volatile, unmaintainable part.
5. **Collision safety.** The platform section emits 31 generic utility class names into whatever theme hosts it. Ours emits only `data-*` hooks plus a single scoped namespace.

Cost, and how it's paid: we re-implement ~2000 lines of interaction logic. That is bounded because the behaviour is fully specified in `00-BEHAVIOUR-MAP.md` (98 scenarios) + `05a-behavior-verified.md` (31 verified) + `11-edge-cases.md` (25 adverse), and we validate against the platform section side-by-side using the bench (same product, two `theme_template_id`s) as the differential oracle.

## D2. Layered architecture for the generated implementation

Five artefacts, each with one job. This is the maintainability answer.

```
sections/bundle_builder/index.liquid   presentation only: <template>s + {% schema %} + the data blob.
                                       No pricing logic. No rule logic. Escaped blob (fixes P1).
                                       Server-renders included rows + group scaffold (no blank-until-JS, no CLS).
assets/bundle-builder.js               one pure normalizer + one state machine + one cart adapter.
                                       No markup strings, no company constants, no bundle ids.
assets/bundle-builder.css              tokens only, zero hex, scoped under [data-bundle-root],
                                       + a compat layer that neutralises the host theme's button/input/list resets
                                         *inside the section only*.
product/<name>/index.liquid            host template. Gates on product_bundle_groups.size > 0 and
                                       falls through to the theme's normal product body when false.
theme/bundle-manifest.json             provenance + routing map + applied-defect list + contract revision.
```

The JS splits into four named layers so a future change lands in exactly one:

| Layer | Responsibility | Why separate |
|---|---|---|
| `normalize(rawProduct, ctx)` | drop JSON → a flat, typed, country-resolved `BundleModel`. Every price chain, every string→number coercion, every `null` vs `""` guard, hidden-group filtering, `sort_order` sorting, exclusivity read from `bundle_config` **and** the top-level key, both mutex shapes, nil-bound repair. | This is where 100% of the platform's data traps live. One function, unit-testable, and the *only* thing that changes when the drop changes. |
| `rules(model, selection)` | pure function → `{ perGroup: {count, min, max, satisfied, blocked, reason}, complete, violations[] }`. Mirrors `CartBundleValidator` exactly, including nil-bound guards and `max_only`-zero. | Turns swallowed 422s into inline messages *before* the request. |
| `render(model, state, refs)` | clones `<template>`s, sets text/attrs. Knows nothing about pricing or rules. | Restyling and re-layout never touch logic. |
| `cart(model, selection)` | builds `bundled_items` (tag every entry, drop included groups except exclusive members, collapse duplicates into quantity, omit zero-qty), calls the SDK, treats resolved-`undefined` as failure, reads the cart back, inspects `items[].errors` and `skipped_items`. | The money path, isolated and assertable. |

## D3. Zero bundle-specific hardcoding — mechanically enforced

The generator emits no bundle id, product id, group id, group title, item count, or price anywhere in the theme. A validation gate greps every generated file for every live id in the company's bundle set and **fails the run** on a hit. `bundle_product` is never set on a `product/*` template (it hard-wires one bundle, drops hidden groups 3→2, and is destructive on a global install). Group *labels* come from `group.title`; rule *copy* comes from schema settings with `{count}`-style placeholders, so it localises without code.

## D4. Routing, done deliberately

Per bundle product: `PATCH /api/company/v1/products/{id} { product: { application_theme_template_id } }` → then **fetch the plain storefront URL** (no `preview` param) and assert our marker is present and the old implementation's markers are gone. Verified end-to-end in the reference campaign; a plain PATCH is sufficient and takes effect immediately.

Because routing is a per-active-theme join, `bundle-manifest.json` records `{theme_id, template_id, product_ids[]}` so re-routing after a theme switch or clone is a single idempotent replay — and the skill *warns* about this explicitly, since it's the #1 real-world fault (`byob-undle` was rendering bundle-less purely because the join was null).

## D5. Discovery: classify, don't assume

The skill never assumes an architecture. It gathers evidence and classifies the company into one of five archetypes, with confidence, and writes `bundle-discovery.json`.

| Archetype | Signals | Action |
|---|---|---|
| **A. Already dynamic bundles** | products with `product_bundle_groups.size > 0` | audit + re-theme + fix routing/pricing gaps. No data migration. |
| **B. Hand-authored picker** | theme source contains `dynamic_bundle_picker`, `data-dbp-*`, `data-fluid-dbp`; often injected into `product/default` | read the picker's own rule/pricing/submit logic as the behavioural spec; port to the generated section; un-inject from default. |
| **C. Legacy flat `ProductBundle`** | `product_bundles[]` non-empty and `product_bundle_groups` empty | convert to one `included` group (split by `display_externally` into included + hidden if needed). Preserve `quantity`. Note: these price from the master variant like a normal product — pricing intent must be captured *before* conversion. |
| **D. Convention-based "fake" bundles** | multi-variant kit/combo/bundle titles; option-driven builders; products whose description enumerates components; a catalog of component products with a parent SKU pattern | **propose, never auto-convert.** Present candidates with evidence and let the user confirm each. |
| **E. Greenfield (Chipotle)** | zero bundles, zero infrastructure | generate the implementation; optionally build one *real* bundle from the live catalog as the proving fixture. |

Evidence sources: `/api/company/v1/products` (paged at **50**, never 100), the active theme's template list + section sources, `/api/v2025-06/bundles` as a read cross-check only, `variant_countries` for pricing intent, subscription plans, `company_countries` for the country/currency matrix.

## D6. Translation rules (existing → dynamic), table-driven

Every conversion is a declarative row, so it's reviewable and extensible rather than buried in code. The contract is *preserve*, in this order of priority: **charged price** → **selection semantics** → **subscription semantics** → **exclusivity** → **defaults/quantity caps** → **copy/imagery**.

| Source concept | Target | Notes / trap |
|---|---|---|
| "always included" component | `included` group, item `quantity` = component qty | **must set an explicit `fixed_price`** or it displays as the item sum and charges $0.00 (P11) |
| "pick exactly N" | `customizable` + `selection_type: exact`, `min_selections: N` | `exact` collapses `max` to `min`; a stale persisted `max` is normalized by the drop but not the raw API |
| "pick up to N" | `max_only`, `max_selections: N` | `min_selections` is forced `nil` → **guard the client comparison** (P16) and allow zero-submit (P14) |
| "pick at least N" | `min_only` | `max_selections` forced `nil` — same guard |
| "pick N–M" | `min_and_max` | progress denominator is max, completion is judged at min |
| either-A-or-B branch | two groups + `bundle_config.mutually_exclusive_groups` (pairs of **sort_order**, max 2 per set, a group in at most one set) | write via **Surface A only**, else the cart ignores it |
| per-component price | group `dynamic_price` (sums, scales with qty, **credits CV/QV**) | the only mode where volume flows from items |
| one flat kit price | group `fixed_price`, or bundle-level flat for the whole bundle | fixed/flat credit **0/0 CV/QV** unless re-entered on the group/bundle country row — surface this to the user, it's a commissions decision |
| per-country price | `country_pricing[]` at the right layer | strings, UPPERCASE ISO, `enabled` strict `== true` |
| pre-selected option | item `config.is_default: true` | **clamp to `max_selections`** and skip out-of-stock (P19) |
| "max 2 of this" | item `config.max_quantity` | counters count *units*, not lines |
| subscribe option / required | item `config.allow_subscription` / `force_subscription` (+ plan id) | forced items need an active plan on their own product; check group level too |
| hidden internal component | `included` group + `pricing_config.hidden: true` | legal only on static groups outside an exclusive pair |

## D7. Self-validation gates

Every gate reads state back. None trusts the screen. A failed gate either auto-repairs (idempotent, bounded) or stops with an actionable message naming the exact resource and field.

| Gate | Proves |
|---|---|
| **G0 preflight** | token scope; exactly one `status:"active"` theme identified; `product_bundle` global resolves; countries + currency + decimals; subscription plan inventory; SDK boot tag present on the storefront |
| **G1 discovery** | every candidate classified with evidence; no product both "bundle" and unclassified; enrollment bundles flagged as unsupported and excluded |
| **G2 config write-back** | re-`GET` each product and diff field-by-field against intent; `products.bundle_config` non-empty; every mutex tuple references an existing `sort_order`; `is_default` present *inside* `config`; no group left with a nil surviving selection bound; every `included` group has an explicit price or an explicit $0 decision |
| **G3 render** | blob present + key count as expected; post-JS `[data-group-id]` count == expected (excluding `<template>`s); zero console errors; **a non-bundle product on the default template is byte-untouched**; 390 px with no horizontal overflow |
| **G4 interaction** | each `selection_type` gates correctly; defaults ≤ max; at-max gives a real disabled affordance or swaps; `max_only` can submit zero; nil bounds don't enable a doomed CTA; subscribe controls appear only where allowed and are locked where forced; a **real scrolled mouse click** on the CTA *and on a child of it* |
| **G5 cart** | captured request body: every entry tagged with `product_bundle_group_id`, included items **absent** (exclusive members **present**), duplicates collapsed; cart read back with one line, `metadata.is_bundle`, every expected child incl. server-reconstituted ones; `items[].errors` and `skipped_items` inspected **even on 200**; resolved-`undefined` surfaces our error UI; add-twice produces the expected lines |
| **G6 money** | displayed total == cart total == checkout total in **every pricing mode the company uses**; recurring subtotal read from `cart.recurring[0]` and disclosed on the PDP; no $0.00 accepted silently; CV/QV expectation matches the mode |
| **G7 reusability** | **the platform proof**: synthesise a second bundle with a *different* shape (extra group, nested exclusivity, per-item max, a subscription-forced item) and confirm it renders and adds to cart with **zero code changes** and no new template |

## D8. Improvements beyond the brief (and why each earns its place)

1. **Client rule engine mirroring the server validator** — the server's message is destroyed by the SDK, so pre-validation is the *only* way a shopper ever learns why. Also kills P14/P16 client-side.
2. **Real server-error capture** — a narrow `fetch`/XHR interceptor records the last cart error body before the SDK generalises it, surfaced on `CART_OPERATION_ERROR`. Diagnostics stop being guesswork.
3. **$0.00 / country-availability guard** — refuse or warn when a selected child has no positive priced row for the cart country. This is real money and the platform gives *no* signal.
4. **Recurring-total disclosure** — computed from item subscription prices and shown on the PDP. Can't fix P7/P10; can stop hiding a $100/mo surprise until checkout.
5. **Swap-on-click at max + genuine disabled affordance** — P15 is called "the single most likely thing to generate support tickets".
6. **Defaults clamped to max, out-of-stock defaults skipped** — P19 is reachable by a real merchant in one click.
7. **XSS-safe blob** — escape `<`/`>`/`&` in the emitted JSON. We can do in our section what the theme cannot do with the platform's.
8. **Accessibility** — the platform section has none. Real `radiogroup`/checkbox-group semantics, keyboard operability, `aria-live` on tracker and total, focus management on exclusive switches. Also fixes the "native inputs are invisible on every theme" reset problem by not depending on native input chrome.
9. **Capability registry + unknown-field notice** — the model records which group/item flags it understood; an unrecognised flag logs one dev-mode notice instead of silently doing nothing. This is how future platform features surface instead of rotting.
10. **`bundle-manifest.json`** — records routing map, source archetype + evidence, contract revision, applied-defect list, and the global section's fetched digest, so the next agent can re-sync deliberately instead of archaeologically.
11. **Idempotent, resumable writes** — deterministic external keys, read-before-write, converge-not-duplicate on re-run. Bundle-before-product delete order baked in.
12. **Dry-run by default** — a full plan + diff, then `human_in_the_loop` approval before any write. Bundles touch pricing.
13. **Explicit refusal for enrollment bundles** — honest "not supported, here's why" beats a half-working picker.
14. **Locale/currency correctness** — symbol and decimal places from `localization`, thousands separators, never a hardcoded `$`/2 (the *deployed* global section hardcodes 2).
15. **Progressive enhancement** — static rows and group scaffold server-rendered so the page has content and stable layout before JS, unlike the platform section which paints nothing until its IIFE runs.

---

# PART 3 — The workflow the skill will run

Phase 0 and 1 are read-only. Nothing writes before the approval gate in Phase 4.

**Step 1 — Resolve the reference company.** Use the workflow/chat context if a company is already in scope (same pattern as the onboarding workflow's company resolution); otherwise ask once. Resolve: company id, active theme, storefront host, countries + currencies, subscription plans. → **G0**

**Step 2 — Study the reference company.** Catalog scan (paged at 50), theme source scan, existing bundle inventory (matched by group id, never slug), pricing/subscription/CV intent, live storefront probe of one representative product on all three render paths (plain / canonical / any existing picker). Produce `bundle-discovery.json` + a written "how this company's bundles work, and *why*" summary. → **G1**

**Step 3 — Plan the translation.** Emit `bundle-plan.json`: per source bundle, the exact target group/item/pricing/exclusivity/subscription configuration, plus the preserved-behaviour assertions each one must satisfy. Flag every judgement call (fixed vs dynamic pricing → CV/QV consequence; included-group price; defaults) for the user.

**Step 4 — Approve.** `human_in_the_loop` with the plan, the money implications, and the exact write list. Stop.

**Step 5 — Write the Dynamic Bundle records.** Surface A only, idempotent, one product at a time, read-back-and-diff after each. → **G2**

**Step 6 — Generate the theme implementation.** Detect the theme's token lineage, container mechanism, button/input/list resets, typography scale and radius; emit the five artefacts against *those* tokens; `fluid theme push` (never `--force`); publish (updates require an explicit publish — a `PUT` alone changes nothing on the storefront). → **G3**

**Step 7 — Route + verify.** Assign each bundle product; verify on the plain storefront URL. → **G3/G4**

**Step 8 — Prove it.** G4 → G5 → G6 → G7, then write `bundle-manifest.json` and a report: what was built, what was preserved, what differs from the source and why, what needs a human, and which platform defects are worked around versus still live.

**Greenfield branch (Chipotle):** Steps 2–3 collapse to "no existing implementation"; the skill generates the implementation, and builds **one real bundle from the live catalog** as the proving fixture (not a toy), then runs the same G3–G7.

---

# PART 4 — Skill deliverable layout

```
fluid-dynamic-bundles/
  SKILL.md                       trigger + orientation + the 5 rules + the workflow
  reference/                     the existing corpus, kept as the spec (00-BEHAVIOUR-MAP.md remains primary)
  playbooks/
    01-discovery.md              archetype signals, evidence queries, API traps
    02-translation.md            the D6 mapping table + preserved-behaviour assertions
    03-theme-generation.md       token detection, the 5 artefacts, compat layer, push/publish
    04-routing.md                assignment + verification + theme-switch replay
    05-validation.md             G0–G7 as runnable checks
    06-greenfield.md             no-existing-bundles path
    07-troubleshooting.md        health-check → defect-triage decision tree
  templates/                     the generated artefacts as parameterised sources
    sections/bundle_builder/index.liquid
    assets/bundle-builder.js
    assets/bundle-builder.css
    product/bundle/index.liquid
  schemas/
    bundle-discovery.schema.json
    bundle-plan.schema.json
    bundle-manifest.schema.json
```

---

# PART 5 — Edge cases the design explicitly handles

Bundle with zero visible groups (all hidden) · group with zero items · `included` group with no price · nil surviving selection bound · defaults exceeding max · out-of-stock default · variant in two groups (must tag) · duplicate variant across groups · cross-group duplicate submitted naively (the 422 the included-skip prevents) · `max_only` with nothing selected · exclusive pair where one branch is static · exclusive pair with an unavailable item (P20) · older bundle with `mutually_exclusive_groups: null` · legacy bare-array mutex shape · child with no country row · child not sellable in the cart country · parent not sellable (422 at create) · bundle with no image anywhere · engineering-notation prices · `cv`/`qv` type flip between Liquid and API · `description` `""` vs `null` · multi-plan subscription selector (**untested upstream — treat as unproven**) · bundle-wide + per-item subscription coexisting · re-add sets not increments · theme switch un-routing everything · a company whose theme already defines `.btn`/`.container`/`.text-sm` · a company with a non-USD, non-2-decimal currency · orphan Bundle rows · enrollment bundles (refused).

---

# PART 6 — Decisions I need from you before I build

1. **Architecture (the big one).** Generate a theme-native `bundle_builder` section (D1, recommended) — or patch-and-clone the platform `product_bundle` for byte-parity? My recommendation is D1 for the five reasons above; the parity path stays documented as an option.
2. **Chipotle's proving bundle.** Chipotle has 0 bundles but ~47 build-component products already in the catalog (7 proteins, 2 rices, 2 beans, 11 toppings, chips & dips, sides, high-protein cups). A real "Build Your Own Burrito/Bowl" is an unusually good test fixture: an exact-1 protein group, max-1 rice and beans, a many-select toppings group at $0, an included tortilla/base, per-item `max_quantity` for double protein, and a natural exclusive pair (bowl vs burrito). **Confirm this is the fixture you want** (and whether it should be `draft` or published).
3. **Packaging.** One skill that runs end-to-end, or skill + a `dynamic-bundles` workflow (per-step QA + rework, like the onboarding chain)? The validation gates map cleanly onto workflow steps, which would give automatic rework on failure.
4. **Aggressiveness on archetype D.** For convention-based "fake" bundles, my default is *propose, never auto-convert*. Say the word if you'd rather it convert above a confidence threshold.
```

---

# PART 7 — What the live run changed (2026-08-06)

Everything below was observed against **Chipotle (`980243433`)** while converting six menu items,
building four fixed catering kits, and reproducing a real add-to-cart failure. Nine bundles exist
as a result (`1088`–`1095`, plus `1092` rebuilt). Where this part contradicts PARTS 1–6, this part
wins; the earlier text is kept so the correction is visible rather than silently overwritten.

## 7.0 The PART 6 decisions, as resolved

| # | Question | Resolution |
|---|---|---|
| 1 | Architecture | **D1** — theme-native generated `bundle_builder`. Built; the parity-clone path stays documented but non-default. |
| 2 | Chipotle fixture | Went further than a fixture: **six real menu items converted in place** (Burrito 89585, Bowl 89586, Tacos 89590, Salad 89589, Quesadilla 89588, Kid's BYO 89591) plus **four catering products** (89900–89903) and one rebuilt builder (89584). Published, not draft. |
| 3 | Packaging | **Both** — skill *and* `dynamic-bundles` workflow. The gates did map onto steps; the workflow is where the new evidence requirements are enforced. |
| 4 | Archetype D aggressiveness | *Propose, never auto-convert* — **retained, and vindicated.** §7.1 is the reason. |

## 7.1 Shape classification — the failure that recurred three times

The most expensive mistake available is applying one pattern to products that merely *look*
uniform. Seven Chipotle "menu item" products split three ways:

| Products | Option | Values are | Correct shape |
|---|---|---|---|
| Burrito, Bowl, Tacos, Salad, Quesadilla, Kid's | **1144** | components of one item (Chicken, Steak…) | bundle |
| Chips & Sides 89593 | **1145** | 24 values that each already exist as their own product | **category** |
| Build-Your-Own 89584 / High Protein 89587 | **1143** | distinct menu items, $3.50–$16.10 | category (89587) / bundle (89584) |

The test is **not** "do these share an option?" It is: *are the option values components of a
single sellable thing, or separate sellable things?* Components → bundle. Separate things →
category/collection. Converting a category into one bundle destroys a browsable listing and
advertises one wrong price.

Two further shape lessons:

- **Fixed kit vs configurable vs BOTH.** Family Meals is a category page of four fixed-kit cards
  where *each card also has a CUSTOMIZE link* into a builder. The correct model is **N fixed kits
  PLUS one configurable bundle** in one collection — not one or the other. I modelled it as one
  configurable product first, which was wrong, then briefly called 89584 redundant, which was also
  wrong. The kit and builder prices legitimately differ ($52/$52/$63 kits vs $53/$53/$64 builder,
  a flat +$1 to customize) and must **not** be reconciled.
- **Never treat imported catalog prices as source of truth.** The importer had the catering
  proteins at $50/$50/$61; the source page said **$52/$52/$63**. The catalog was wrong before
  anything was touched. Deriving deltas from existing variants is right when *preserving* prices
  and wrong when *matching a source*.

## 7.2 Create is one call; convert is two

| Endpoint | `bundle: true` + groups in one request |
|---|---|
| `POST …/create_bundle_product` | ✅ persists — `is_bundle: true`, `bundle_price` correct, Bundle row synced (3/3 creates) |
| `PATCH …/{id}/update_bundle_product` | ❌ groups created, `is_bundle` stays **false**, `bundle_config: {}`, **no Bundle row** (6/6 conversions) |

A conversion therefore needs a second, groups-free `{id, title, bundle: true, status}` call. Also
confirmed: **`title` is required even on an update** (omitting it → 422 `title is missing`), and
plain `PATCH /api/company/v1/products/{id}` silently ignores
`product_bundle_groups_attributes` while returning 200.

Between the two calls the product has groups but no bundle record; unrouted, its PDP renders
$0.00 with no picker. Hence: route **per product, immediately**, never batched to the end.

## 7.3 Pricing — corrections to PART 1

### 7.3a `price_range` is usable, and is the primary verification signal
**PART 1 (§1.6 bullet) claimed `price_range`/`bundle_price_range` are computed with
`country_code: nil` and read `$0.00`. That is wrong.** Across nine bundles they returned correct,
country-resolved values: `$9.35–$11.35` (×4), `$9.90–$11.90`, `$5.60`, `$52.00`, `$63.00`,
`$53.00–$64.00` — and one *wrong* value, `$55.75–$66.75`, which is how a real pricing defect was
caught (§7.3b). Only top-level `price` / `display_price` are unusable (`$0.00 (USD)` on every
bundle). Compare `price_range` before → after on every write.

### 7.3b `fixed_price: "0.00"` is ignored
A group priced at zero does **not** zero its contents. Each item's `resolved_price` falls back to
the component variant's own price even when `config.price` is explicitly `"0.0"`. Large Chips
(variant 344052, $2.75) inside a `fixed_price: "0.00"` **included** group pushed 89584 from
`$53–$64` to `$55.75–$66.75`; removing that one item restored it. So: **a nonzero `fixed_price`
pins a group total; `0.00` behaves as unset.** Only genuinely $0 variants belong in a free group.
Consequence: Large Chips is named in 89584's copy but is *not* a component of it.

### 7.3c Floor contribution is three-way
| Group | Adds to `price_range.min` |
|---|---|
| `included` | **sum of ALL** its components' resolved prices |
| optional `fixed_price` (`max_only`) | **nothing** |
| optional `dynamic_price` | **its cheapest item** — even at `min_selections: nil` |

The last row supersedes an earlier blanket phrasing of "any dynamic group". An optional paid
"Add Guac or Queso" `dynamic_price` group moved the burrito's floor from **$9.35 → $12.30**, so
every collection tile advertised "from $12.30" for a burrito buyable at $9.35. Computed
server-side; no theme-side fix. Never add one to a product whose "from" price is customer-facing
without explicit client acceptance.

### 7.3d A fixed-price `included` group prices the bundle exactly
`bundle_price` / `price_range` equal the group's `fixed_price`, ignoring components' own prices
(items still echo their real `pc_price`). This is the correct primitive for a fixed kit and means
the kit price cannot drift when a component's à-la-carte price changes.

## 7.4 The add-to-cart root cause

**Valid bundle config is not evidence the storefront can sell it.** 89584 read back perfectly from
`GET /api/v2025-06/bundles` — six groups, correct prices — and failed for every shopper:

```
POST /api/checkout/v2026-04/carts → 400
"product_bundle_group_id 1771 must reference a customizable group
 or an exclusive included group"
```

Group 1771 is `Included Sides`, `group_type: "included"`. This is **SKILL.md rule 3 violated by
the client**, not a platform defect and not a gap in the skill — `bundle-builder.js` `cart()`
already drops included groups. The live theme didn't.

Two payloads verified 200 with correct totals:

```jsonc
// configurable — customizable groups ONLY; included group omitted
{ "variant_id": 343601, "quantity": 1, "bundled_items": [
  {"variant_id":344039,"quantity":1,"product_bundle_group_id":1765},
  {"variant_id":344022,"quantity":1,"product_bundle_group_id":1769},
  {"variant_id":344023,"quantity":1,"product_bundle_group_id":1770} ] }   // → $53.00

// pure fixed kit (89901) — NO bundled_items at all
{ "variant_id": 344077, "quantity": 1 }                                   // → $52.00
```

The cart attaches included components itself: the successful response listed Cheese, Romaine and
Soft Flour Tortillas under group 1771 although they were never sent. Cart metadata carries
`is_bundle: true`, `bundle_group_base_price`, and a `bundle_selection_key` listing **only** the
customizable picks (`1765:344039x1|1769:344022x1|1770:344023x1`; empty string for a pure fixed kit).

**Corollary that matters as much as the fix:** an all-`included` product has nothing to select, so
any UI gating add-to-cart on "all required groups chosen" leaves every fixed kit permanently
unclickable — while the API side looks perfectly healthy. Workflow step 8 therefore demands a cart
call for one configurable bundle **and** one pure fixed kit; testing one shape is an explicit fail.

## 7.5 Mutation gotchas found while writing

- **`images_attributes` APPENDS on PATCH.** No replace. 89900 ended with two gallery rows both at
  position 1. Send `_destroy` for the old image id when swapping.
- **Collection membership REPLACES.** `PATCH /api/v202604/company/collections/{id}`
  `{collection:{product_ids:[…]}}` overwrites the whole set and the response does **not** echo
  products. Read current members first (v1 GET returns `product_collections[]`), then re-GET.
- **A `draft` / `public: false` collection still renders publicly.** Verified by fetching a live
  draft collection page — full `collection_showcase` with pagination. Do not "fix" draft status to
  make a collection reachable.
- **Cross-group duplicate variants are legal.** Cheese (344035) sits in Quesadilla's protein group
  as "Cheese Only" ($9.90) *and* in its toppings group ($0). Different `product_bundle_group_id`
  ⇒ distinct cart keys. This is why tagging every entry (rule 4) is load-bearing.
- **Sequencing.** Never archive or delete a product the storefront still links to; retire only
  after the referring tile/nav is repointed *and* that change is confirmed. Corollary of the
  existing rule that the Bundle row must be deleted before the Product.

## 7.6 Summary of corrections to PARTS 1–6

| Claim in PARTS 1–6 | Status after the live run |
|---|---|
| `price_range`/`bundle_price_range` read `$0.00`, unusable | **Wrong.** Correct and country-resolved; the primary write-verification signal. Only top-level `price`/`display_price` are unusable. |
| (Implied) one write call sets `bundle: true` with groups | **Split.** True for `create_bundle_product`; false for `update_bundle_product`, which needs a second flag call. |
| Products sharing an option share a shape | **Never assume.** Classify per product by option id; components vs separate sellable items. |
| An optional group can't affect the advertised price | **Wrong** for `dynamic_price` — it contributes its cheapest item. |
| A `fixed_price: "0.00"` group is free | **Wrong.** `0.00` behaves as unset. |

Unchanged and re-confirmed: `group_type` is a stored column; Surface A is the only safe write
surface; never send included items (rule 3) and always tag the group (rule 4); routing is a
theme-scoped join that must be re-run after a theme switch or clone; HTTP 200 is not success.
