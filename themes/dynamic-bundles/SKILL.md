---
name: dynamic-bundles
description: Use when configuring, migrating, or theming Fluid Dynamic Bundles for ANY company — recreating an existing bundle implementation as Dynamic Bundles, building a reusable bundle theme from scratch, translating a source site's configurator/meal-builder page into a bundle, or diagnosing a bundle that renders wrong, won't add to cart, or charges the wrong price. Triggers - "dynamic bundles", "build your own", "bundle builder", "make <company> bundle-ready", "turn this page into a bundle", "migrate bundles", "bundle picker", "bundle won't add to cart", "bundle price wrong", "configurator page".
---

# Fluid Dynamic Bundles — universal build & migration skill

> **This skill is a platform, not a migration.** Its output is one theme implementation
> that renders *every* current and future bundle for a company with zero per-bundle code,
> plus correctly-configured Dynamic Bundle records. Nothing it generates may contain a
> bundle id, product id, group id, or group title.

**The spec is `reference/00-BEHAVIOUR-MAP.md`** (every admin setting → renders → responds →
cart → checkout). This file is the operating procedure; the reference corpus is the truth.
Claims here are already reconciled against it — where this file and a reference doc disagree,
the reference doc wins and this file is a bug.

---

## Where this sits — it runs AFTER onboarding, and replaces nothing

This is a **follow-on capability**, not an alternative to the onboarding workflow. It assumes
a company that already exists and already has a store.

| This skill DOES | This skill does NOT |
|---|---|
| Read an existing catalog and classify how bundles work today | Import or create a catalog |
| Configure Dynamic Bundle records on existing products | Scrape or clone a storefront |
| Add a bundle section + host template to an **existing** theme | Create or seed a theme, or build a homepage / PDP / shop page |
| Route bundle products to that template | Set up brand, domains, payments, countries |

**Prerequisites, checked in G0 and stopped on:** the company has an active theme, and the
catalog contains the products the bundle will be built from. If either is missing, say so and
point at the onboarding workflow — do not start doing onboarding's job inside this one.

Typical order: **onboarding (store + catalog + theme) → this (bundles on top)**. It is also
correct to run this standalone, months later, on a mature store — that is the common case.

---

## Applies to every vertical, not just configurators

Most companies sell ordinary products. A build-your-own configurator is the **hardest** case,
not the typical one — do not treat it as the default shape and do not over-engineer toward it.

The three shapes that cover the large majority of real bundles:

1. **Fixed kit** — "Bundle & save", a gift set, a starter pack. Every component is
   `included`; one flat price. No shopper choice at all. *This is the most common bundle on
   the platform.*
2. **One pick-N group** — "Choose any 3 flavours", "pick 2 shades". A single `customizable`
   group over a set of variants.
3. **Base + options** — an `included` core plus one or more choice groups. Configurators are
   just this shape with more groups.

Per-vertical patterns are in `playbooks/01-discovery.md` §5a, and the recipes for building
each from scratch are in `playbooks/06-greenfield.md`. Food/QSR meal builders appear there as
**one worked example among several**, because that is the test company — not because the skill
is food-shaped.

### Variants vs bundles — the distinction that decides everything

Both are "a product with choices", and getting this backwards is the most expensive
classification error in the skill. **Options do not settle it. What the option MEANS does.**

| The option varies… | It is | Example |
|---|---|---|
| one indivisible item's own attributes | **variants** — leave alone | size, colour, length, scent of a single item |
| **which components the item is composed of** | **a bundle** | protein, base, add-ons, configuration |

The decisive, mechanical test: **do the option's values correspond to things that exist (or
could exist) as their own catalog products?** A Large is not a product. Steak is. If the values
map onto standalone products, the option is encoding *component selection* and the product is
a bundle that was modelled as variants.

Three corroborating signals, all checkable:

1. The option's values match existing product titles in the catalog.
2. The same option object is **shared across several parent products** — a real variant axis is
   usually product-specific, whereas one "protein" option reused across burrito / bowl / tacos
   is a menu-wide component axis.
3. Variant price differences equal the price differences between those standalone components —
   the variant price is carrying a component upcharge.

Genuinely **not** bundles: a quantity break ("buy 3, save 10%"), a multipack with its own SKU,
a "frequently bought together" upsell, a subscription of one product. Those are pricing and
merchandising features.

**A mis-modelled product is adjusted, not duplicated.** Creating a second "Build Your Own X"
next to the existing X leaves the company with two products for one thing, one of them wrong.
See `playbooks/02-translation.md` §5.

---

## 0. The 60-second model

A bundle is a **Product** (`products.bundle = true`) + a shadow `Bundle` row + N
`ProductBundleGroup`s each holding N `BundleGroupItem`s (one variant each).

```
BUNDLE   products.* · products.bundle_config · bundles.settings
  └ GROUP   group_type = included | customizable   (a stored NOT-NULL column)
      └ ITEM   one variant + config jsonb
```

- The **group's** type is stored. The **bundle's** static/dynamic nature is emergent
  (`static?` = every group `included`).
- Everything the client can act on crosses **one tag**:
  `<script type="application/json" data-bundle-product>{{ bp | json }}</script>`.
  What the drop serializes is the entire client contract, whatever the REST API returns.
- Bundle-level flat pricing **collapses the layers** — group and item prices become
  display-only. It is illegal to combine with a `dynamic_price` group (model validation),
  so a theme never has to reconcile those two.

---

## 1. The nine rules that prevent essentially every bug

1. **Detect with `product.product_bundle_groups.size > 0`.** Nothing else. `is_bundle` is
   API-only; `slug`/`handle` are nil in page and section scope; `bundle_in_stock` is `true`
   on non-bundles.
2. **Write bundles only through Surface A** —
   `POST /api/company/v1/products/create_bundle_product` /
   `PATCH /api/company/v1/products/{id}/update_bundle_product`. It is the only surface that
   writes `products.bundle_config` (*where the cart reads exclusivity*) and the only one that
   validates. `/api/v2025-06/bundles` is READ-CROSS-CHECK ONLY (§5).
3. **Never send included/static items** in `bundled_items` — the server reconstitutes them.
   *Exception:* an included group inside an exclusive set **must** be sent, because the
   server cannot know which branch was chosen.
4. **Always send `product_bundle_group_id`** on every entry. Omitting it changes
   `bundle_selection_key` (`1527:56794x1|…` vs `56794x1|…`) → duplicate lines → double charge.
   Mixing tagged and untagged for one variant is a hard 422.
5. **Read exclusivity from `bundle_config.mutually_exclusive_groups`.** It holds
   **`sort_order`s, not group ids**, in two shapes (`[{ids:[…],default:…}]` or a bare
   `Array<Integer>`), and is `null` — not `[]` — on older bundles.
6. **Collapse duplicate variants into `quantity`.** The server counts **units**, and does
   **not** de-duplicate entries. One entry per click = silent over-charge.
7. **HTTP 200 is not success.** The SDK promise resolves `undefined` on failure and destroys
   the server's message. A country-unavailable child returns 200, prices the bundle at
   **$0.00**, and leaves `items[].errors` **empty**. Verify by reading the cart back.
8. **Every price is a chain.** `item.price` is `"0.0"` on 100% of fixtures and a zero there
   means *unset*, not free. See §4.
9. **Match bundle → product by `product_bundle_groups[].id`, never by slug.** Duplicate and
   orphan `Bundle` rows share a title and the later row often owns the uniquified slug.
   And **delete the Bundle before the Product** — reverse order leaves an orphan whose
   `DELETE` then 500s forever.

---

## 2. The three moving parts — two are missing by default

| Part | Default on a new company |
|---|---|
| A bundle-rendering section | ✅ the platform's `product_bundle` is free everywhere (one global row unioned into every theme) |
| A `product` template hosting it | ❌ **no seed ships one** |
| Routing (product → that template) | ❌ **no auto-assignment exists** |

Routing is not a column — it is a `template_resources` join **scoped to the currently-active
theme**. Consequences:

- **Switching or cloning a theme silently un-routes every bundle.**
- A bundle created via API with no explicit `application_theme_template_id` comes back `null`.
- **A bundle on a bundle-unaware theme is a silent revenue hole**: normal-looking product
  page, working native add-to-cart, hard failure at checkout. Nothing surfaces to the merchant.

---

## 3. Architecture decision — generate, don't clone

This skill generates a **theme-owned** section (`bundle_builder`) implementing the platform's
data + cart contract exactly, and owning its own presentation. It does **not** clone the
platform's `product_bundle`. Five reasons, in order of weight:

1. **"Match the brand" is unachievable with the platform section.** 46 inline `style=`
   attributes and 18 hardcoded hex colours outrank any stylesheet.
2. **A clone inherits ~11 client-side defects** (P2, P5, P10, P14, P15, P16-client, P17, P19,
   P20, P21, P1's escaping) that we can simply not write.
3. **A clone never receives updates anyway.** `auto_upgradeable?` is hardcoded `false` and a
   theme-local copy shadows the global permanently. Cloning *guarantees* the drift it is
   supposed to avoid — two Chick-fil-A clones are already 15.7 KB stale.
4. **The stable part of the platform is the contract, not the UI.** The drop shape and cart
   schema are documented and are what we build against.
5. **Collision safety.** The platform section emits 31 generic utility class names
   (`.btn`, `.container`, `.text-sm`, `.flex` …) into whatever theme hosts it.

A patched clone remains available as documented, non-default **parity mode**
(`playbooks/03-theme-generation.md` §9).

### 3a. The trilemma this avoids

Global sections never resolve typed `{% schema %}` settings (defect **P3**), so pinning
`bundle_product` on a global install yields a **dead shell**; and exclusivity is top-level
only in the 40-key drop shape, not the 50-key page shape a PDP gives you. No stock
configuration gives both exclusivity and scale. Owning the source + reading exclusivity from
`bundle_config` gives both.

**Never pin `bundle_product` on a `product/*` template.** It hard-wires one bundle and drops
hidden groups. Pin only on `home_page`/`page` templates, where there is no page product.

---

## 4. Price and type traps

- **Item:** `country_prices[ISO]` → `item.price` (>0) → `variant.variant_countries[ISO].price`.
- **Group:** `pricing_config.country_pricing[ISO]` → `pricing_config.fixed_price`.
  `group.fixed_price` reads `"0.0"` when unset — check `pricing_config.fixed_price` for **key
  presence** to distinguish unset from a real zero. `min_price`/`max_price`/`compare_at_price`
  are dead (`"0.0"` on every live group).
- **Bundle:** `bundle_config.bundle_pricing_config.country_pricing[]` (values are **strings**,
  `country_code` UPPERCASE, `enabled` strict `== true`). `product.bundle_price` is empty even
  with bundle pricing on. `primary_price`/`primary_currency` are admin echo, never read by Rails.
- `product.price` in the Liquid drop **is** correct and country-resolved (`"$50.00"`, or a
  `"$30.00 - $70.00"` range when any group is dynamic). Top-level `price` and `display_price`
  from the JSON APIs are computed with `country_code: nil` and read `0.0` / `$0.00` — unusable
  (every live bundle reports `display_price: "$0.00 (USD)"`).
- **`price_range` / `bundle_price_range` sum each item's `config.price`. They do NOT read the
  group's `fixed_price`.** So:
  - **dynamic** choice groups → the range is correct and arithmetically checkable. Use it.
  - **all-fixed** bundle (anchor holds the price, items all `0.0`) → the range reads **`$0.00`**
    on a fresh GET while the cart charges correctly. Not a reader defect — an accurate sum of
    zeros. Useless for verification, and dangerous on any storefront surface that renders it.
- **A PATCH echo is not proof.** On 2026-08-06 an all-fixed kit was recorded at `$52.00` from
  the `update_bundle_product` echo; a fresh `GET` on 2026-08-08, stored config byte-identical
  and `updated_at` unchanged, returns `0.0`. The cart was correct at `$52.00` throughout
  (verified with a real cart POST). **Never verify a write from the response to that write —
  always re-`GET`, or prove it with a cart.** See `playbooks/09-pricing-patterns.md` §5.
- In one object: `price`/`wholesale`/`compare_price` are **floats**, `subscription_price` is a
  **string**. `cv`/`qv` are Integers in Liquid, **strings** in both APIs. `display_*` carries a
  `" (USD)"` suffix. Drop prices can be BigDecimal engineering notation (`"0.4999e2"`) —
  `parseFloat` survives it, `{{ item.price }}` in Liquid does not.
- **Compare-at**: render only when `compare_price > price`, else you advertise an increase.
- **CV/QV only flow from `dynamic_price` groups.** Fixed-price and flat bundles credit 0/0
  unless CV/QV is re-entered on the group or bundle `country_pricing` row. Never sum
  `variant_countries[].cv` into a "you'll earn N CV" promise.

---

## 4a. Planning rules learned in the field

1. **Variants must exist before groups are built.** A group built while its component
   products were single-variant points at the only variant available; once real variants are
   added that pointer is *wrong* and the group must be repointed. A second group built too
   early had 43 items where the source offered 117 (43 products × sizes) and needed a full
   rebuild. **Assert in preflight: every product that will become a component already carries
   its full variant set.** If not, fix the catalog first — this is a G0 check, alongside
   active-theme and non-empty-catalog.

2. **Group membership comes from the source, per bundle — never derived from the component
   product.** Different bundles offer different subsets of the same product's variants; one
   bundle offered three sizes of a component, another offered a smaller size the first did
   not. Deriving from the parent product's full variant list silently adds options the
   merchant does not sell. Where the source declares a default member, honour it; where it
   declares none, use the cheapest.

3. **Upgrade pricing needs a rebalanced base**, not just `dynamic_price` — see
   `playbooks/09-pricing-patterns.md`. Compute `base = headline − Σ(defaults)` per bundle and
   assert `base >= 0` before writing. A negative base is normal for value bundles and is
   resolved by honouring the source's default; if it is still negative, **escalate**.

4. **Bundles are not interchangeable — census before any batch.** Flag any candidate whose
   computed base is negative or zero, that carries an explicit price-increment mechanism,
   whose group count or min/max differs from the proven shape, or that has more than one
   anchor candidate (or none). Anything unresolved is **skipped and named**, never guessed.
   Convert in batches behind a human gate, then cart-verify a sample spanning the *kinds* of
   bundle — premium, value, and any odd shape — not just the easy ones.

---

## 5. Write surfaces

**Surface A — `create_bundle_product` / `update_bundle_product`** (what the admin Bundle
Builder uses). The only surface that can set `products.bundle`, `bundle_config`,
`track_inventory_on_bundle_items`, variants, `variant_countries`, images, SEO, group
`images_attributes`, `_destroy` nested deletes — and the only one that runs
`BundleConfigValidation`. **Use this exclusively for writes.**

**Surface B — `/api/v2025-06/bundles`** — a trap. No pagination (`per_page`/`page` silently
ignored), **omits `product_id`** (you cannot get from bundle to product), skips validation,
writes `bundles.settings` without mirroring to `products.bundle_config` (so exclusivity
written here is honoured by the portal and **silently ignored by the cart**), returns **500
not 422** on schema errors, `items[].is_default` 500s on update and is dropped on create,
`sort_order` is overwritten by array position, and `groups: []` destroys all groups.

### 5a. The write contract — inline, as the safety net

A workflow step chat does not inherit the launching skill's materialized files, so
`playbooks/`, `templates/` and `reference/` have repeatedly come back ENOENT. Every step of
the `dynamic-bundles` workflow now calls `run_skill("themes/dynamic-bundles")` first, which
materializes them — but if that call fails, this table is all you have. Do not go looking for
the write recipe elsewhere and do not improvise it.

| Rule | Detail |
|---|---|
| Surface A only | `POST create_bundle_product` / `PATCH /api/company/v1/products/{id}/update_bundle_product`. Never `/api/v2025-06/bundles` for writes. |
| `product.title` required on **every** call | Omitting it → `422 product.title is missing`, even when updating only pricing. |
| Nested keys | `product_bundle_groups_attributes` / `bundle_group_items_attributes`. |
| `is_default` goes **inside `config`** | At top level it is silently dropped. |
| **Create = 1 call, convert = 2** | `bundle: true` persists on `create_bundle_product`; on `update_bundle_product` it does not — a second groups-free `{id, title, bundle: true, status}` call is required. |
| Items are **append-only** | Omitted existing items are kept, not removed. |
| Uniqueness on (group, variant) | Re-sending an existing variant `422`s the **whole request**, atomically. Useful as a cheap non-mutating membership oracle. |
| Group-level `_destroy` **does not work** | Returns 404 even for a group that exists. Do not plan delete-and-recreate around it. Item-level and variant-level `_destroy` DO work. |
| Item updates by `id` work | Including repointing `variant_id` in place — this is how you fix a group pointing at the wrong variant. |
| `images_attributes` **appends** | It does not replace. Send `_destroy` with the old image id when swapping. |
| Reads cap at 51,200 bytes | A large bundle cannot be read whole. Page it by PATCHing visible items' `sort_order` into a high block and re-reading. |
| Unknown keys silently dropped, 200 | Always read back and diff. |
| **A PATCH echo is not proof** | The echo can show values a fresh GET does not. Always re-`GET`. |

Cart writes need **both** `fluid_shop` and a top-level **`country_code`** — omitting the
latter is `422 country_code is missing`.

---

## 6. The workflow

Run the **`dynamic-bundles` workflow** — it is this skill's execution engine, with per-step QA
and bounded rework. Everything before `write-bundles` is read-only.

**You are the launcher. Collect these before calling `run_workflow`** — the workflow cannot
recover from any of them being wrong, because a step chat only ever sees the start context:

| Context key | Why it must come from you |
|---|---|
| `theme_id` | **Required.** Mist picks the project for a theme-targeted step from `context.theme_id`. Absent, it takes the first local theme checkout or scaffolds one — so the run can silently build into a theme nobody asked for. `preflight` stops the run if this is missing or disagrees with the active theme. |
| `approved` | Gates the entire mutating tail via `runIf`. Absent or falsy, steps 5–9 are condition-skipped and the run still completes, reporting a plan and no writes. |
| `source_url` | Optional. Present → `source-analysis` runs; absent → it is condition-skipped, which satisfies its dependents, so the run proceeds without it. |

`approved: true` says *this run may write*. It is **not** consent to a plan that does not exist
yet when `run_workflow` is called. `write-bundles` therefore calls `human_in_the_loop` with the
plan's real numbers and gets approval for **that** before its first write.

| # | Step | QA on fail |
|---|---|---|
| 1 | `preflight` — company, `fluid_shop`, active theme vs `context.theme_id`, variant completeness (**G0, blocking**) | **stop** |
| 2 | `study-company` — catalog, shapes, anchors, theme token lineage | continue |
| 3 | `source-analysis` — the source configurator (`runIf: source_url`) | continue |
| 4 | `plan-translation` — `bundle-plan.json` + the base arithmetic, `base >= 0` | **stop** |
| 5 | `write-bundles` — Surface A; `human_in_the_loop` on the plan, then write; fresh-GET verify | **stop** |
| 6 | `picker-section` — the one reusable section | continue |
| 7 | `price-surfaces` — inventory and wire every surface that shows a price | continue |
| 8 | `route-and-render` — per product, on the ACTIVE theme | continue |
| 9 | `cart-and-money` — default / upgrade / downgrade / **negative case** through the cart API | continue |
| 10 | `reusability-and-report` — proof, manifest, four-part report | continue |

Steps 5–9 carry `runIf: {flag: "approved"}`. Step 10 deliberately does not, so an unapproved
run still ends with a report saying what it would have written.

Greenfield collapses 2–4 to "no existing implementation" and builds **one real bundle from
the live catalog** as the proving fixture.

Playbooks: `01-discovery` · `02-translation` · `03-theme-generation` · `04-routing` ·
`05-validation` · `06-greenfield` · `07-troubleshooting` · `08-api-write-recipe` ·
`09-pricing-patterns` · `10-ui-and-price-surfaces`.
(`09` and `10` supersede `02`/`03` where they overlap — they are field corrections.)

**The workflow may not exist in this company.** The skill catalog and the workflow library
sync separately and per-company; a skill can be present with no matching workflow. Check
first. If `dynamic-bundles` is absent, either author it from the table above with
`create_workflow` — carrying the acceptance criteria, not just the step names — or run the
steps directly in order. Do not assume it arrived with the skill.

**If you run the steps directly instead**, you are running them in one chat, so `run_skill` and
the `runIf` gating do not apply — but the two gates they encode still do. Do not write until a
human has seen the actual plan, and confirm which theme you are editing before the first file
write.

---

## 7. Beliefs to discard

| Belief | Reality |
|---|---|
| Group type is emergent from config | `group_type` is a stored NOT-NULL column |
| Products sharing an option share a pattern | Check the **option id per product**. Option values that are *components of one item* → bundle; values that are *separate sellable items* → category/collection. Converting a category into one bundle destroys a listing and advertises one wrong price (hit 3× in one session) |
| A group priced `fixed_price: "0.00"` is free | `0.00` behaves as **unset** — components fall back to their own variant price and inflate the bundle floor |
| Flipping choice groups to `dynamic_price` gives upgrade pricing | It double-charges unless the anchor base is rebalanced. `base = headline − Σ(defaults)`. See `09-pricing-patterns.md` |
| A `$0.00` read means the platform is broken | It usually means every item genuinely resolves to zero. Check the configuration before filing a defect |
| A PATCH echo confirms the write | It does not. Re-`GET`, or prove it with a real cart |
| Group-level `_destroy` removes a group | Returns 404. Only item- and variant-level `_destroy` work |
| Sending the full item list replaces the group's items | Items are **append-only**; omitted items are kept |
| An optional group can't affect the advertised price | An optional `dynamic_price` group adds its **cheapest** item to `price_range.min` regardless of `min_selections: nil` |
| `product.bundle` is nil in section scope | It works. Only `is_bundle` / `slug` / `handle` are nil |
| Legacy `ProductBundle` is retired | Still writable, still read, still rendered |
| Send every selected item to the cart | Included/static items must NOT be sent — except exclusive members |
| Use `data-fluid-bundled-items` (declarative) | Call the SDK imperatively; the declarative path has 4 silent-failure modes |
| Child clicks on the CTA are ignored (`e.target`) | **Fixed** — the SDK uses `closest()` |
| The section self-gates on non-bundles | It doesn't. Only the data blob is gated |
| Bundles auto-route to a bundle template | No auto-assignment exists. Manual, per product, per active theme |
| `product.bundle_price` gives the price | Empty even when bundle pricing is on |
| Exclusivity via `product.mutually_exclusive_groups` | Absent from page scope, silently no-ops |
| `include_parent_in_orders` changes order lines | No effect in Rails; advisory only |
| Group `allow_subscriptions` gates subscriptions | Never read server-side — check the item too |
| Add-to-cart errors surface to the theme | Promise resolves `undefined`; errors swallowed |
| MutationObserver freeze / hiding the native CTA | Only ever needed for the hand-authored picker |

---

## 8. Assumptions that do NOT hold across companies

Every one was observed varying. This list is why "universal" is hard.

1. **Two CSS token lineages** — `--clr-*` (7 themes) vs `--color-*` (chewy, where `--clr-*` is
   an alias shim). Resolve with layered `var()` fallbacks, never a hardcoded token name.
2. **Three `.container` widths, two mechanisms**, and the **newest PDPs bypass `.container`
   entirely** for a per-section container keyed to `section.id`. A section that wraps itself
   in `.container` misaligns with the rest of the PDP on those themes — guaranteed, visible.
3. `button, .btn {}` is **hijacked on 6 of 8 themes** into a black flex box;
   `-webkit-appearance: none` makes **native radios and checkboxes invisible on every theme**;
   `ul, li { list-style: none }` kills bullets on 7 of 8. Ship a scoped compat layer.
4. `!important` density ranges 0 → 16, plus 7 more inline.
5. **One currency / 2 decimals is not safe** — read `localization.country.currency.symbol`
   and `.decimal_places`.
6. **One subscription plan is not safe** — the multi-plan picker has never been exercised
   upstream. Treat it as unproven and degrade cleanly.
7. **Hidden-group filtering differs by scope** — the drop rejects `pricing_config.hidden`, the
   page path does **not**. Filter yourself.
8. `description` on a group can be `""` *or* `null`. Some fixtures have **no image anywhere**.
9. **API traps that fake theme bugs:** `per_page=100` on `/api/company/v1/products` returns
   **zero** products with no error (50 works); ignored filters return an unfiltered page;
   `?country=CA` is ignored, `?country_id=<numeric>` works.
10. **Enrollment bundles are not supported.** The drop exposes the same data; there is zero
    rendering support anywhere. Refuse honestly.

---

## 9. Before you file a bug

A bundle rendering wrong is **more often theme, routing, or data than a platform defect** — in
the source campaign three bundles showed "no bundle UI" and only **one** was a real fault (the
others were a draft product and a product with zero groups). Work
`reference/12-theme-health-check.md` first, then `reference/13-defect-triage.md`.
**8 of 21 reported defects were downgraded.** Do not file P7, P12, P4 (by design) or
P11, P13, P16, P18 (fixture artifacts the Bundle Builder cannot produce).

The two worth acting on: **P2** (exclusivity — shopper charged for a branch they never
receive, $60 confirmed) and **P19** (defaults over max → unrecoverable `3 / 1` in one click).

---

## 10. Where things are

**Everything this skill needs ships inside the skill's own directory.** Paths below are
relative to the directory holding this `SKILL.md`, so they resolve the same way for every
company — there is no dependency on any particular workspace.

| What | Path |
|---|---|
| These playbooks | `playbooks/*.md` |
| The `bundle_builder` section | `templates/sections/bundle_builder/index.liquid` |
| The four-layer JS engine | `templates/assets/bundle-builder.js` |
| Token-only CSS | `templates/assets/bundle-builder.css` |
| Host template | `templates/product/bundle/index.liquid` |
| Manifest schema | `schemas/bundle-manifest.schema.json` |
| The reference corpus (the spec) | `reference/*.md` |

**Assume you may not be able to read any of them.** Workflow step sandboxes have repeatedly
failed with ENOENT on `playbooks/`, `templates/` and `reference/`. `SKILL.md` is written to be
sufficient on its own — §5a carries the full write contract for exactly this reason. If a
playbook is unreachable, say so in the report and proceed from this file; do not stall, and
do not silently reverse-engineer a contract that is already written down here.

If `reference/` is missing the skill still runs — it is the evidence behind the rules, needed
only when triaging a suspected platform defect (§9) or checking a claim.

Copy the artefacts into the theme and **adapt only what `01-discovery.md` §3 recorded about the
host theme** — they are already lineage-agnostic. A step running inside a theme project that
cannot see the skill directory can be handed the four artefact files by the operator; nothing
else needs to travel.

| Need | Read |
|---|---|
| The spec | `reference/00-BEHAVIOUR-MAP.md` |
| Model, APIs, validators | `reference/01-model-and-backend.md` |
| Hosting & routing procedure | `reference/02-hosting-and-routing.md` |
| The Liquid drop contract | `reference/03-data-contract.md` |
| Cart / checkout contract | `reference/07-cart-contract.md` |
| Pricing & subscriptions (empirical) | `reference/06-pricing.md` |
| Admin control → data field | `reference/08-admin-reference.md` |
| Per-company readiness & theme variance | `reference/09-company-readiness.md` |
| Defects + triage | `reference/10-known-defects.md`, `reference/13-defect-triage.md` |
| Health check first | `reference/12-theme-health-check.md` |
| Proof | `reference/14-verification.md` |
