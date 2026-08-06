# 01 — Discovery: classify, never assume

Read-only. Output is `bundle-discovery.json` plus a written answer to
**"how do this company's bundles work, and *why*?"** — not a config dump.

---

## 1. Preflight (gate G0)

| Check | How | Fail action |
|---|---|---|
| Active theme | `GET /api/application_themes` → the single `status:"active"` row | Stop. Only the active theme renders. |
| Templates | `GET /api/application_theme_templates?application_theme_id=<id>` (root key `templates`, includes globals — `application_theme_id: null` means global, not the company's) | — |
| Countries / currency / decimals | company countries + `localization` | Never assume USD/2 |
| Subscription plans | plan inventory per product | Multi-plan is unproven upstream |
| SDK boots | fetch a storefront product page, assert the `fluid-cdn-script` tag | P17: no SDK = perfect page, dead button, no console error |
| Storefront host | `<slug>.fluid.app` or custom domain | Needed for every later verification |

---

## 2. Catalog scan

`GET /api/company/v1/products?per_page=50` — **never 100**, which returns zero products with
no error. Page to exhaustion. For each product keep: `id`, `title`, `slug`, `status`, `bundle`,
`product_bundle_groups[]` (ids, types, selection rules, pricing), `product_bundles[]`,
`variants[].variant_countries[]`, `application_theme_template_id`, images.

Cross-check with `GET /api/v2025-06/bundles` — **read only**. It has no pagination and omits
`product_id`, so **match bundle → product by `product_bundle_groups[].id`**, never by slug
(slug matching resolved the wrong bundle on ≥3 known fixtures, one of which reports empty
`country_pricing` while the product actually charges $25).

Flag, do not fix: orphan `Bundle` rows (storefront 302s to /404), products with
`bundle: true` and zero groups, bundles with `status: draft`, bundles with
`application_theme_template_id: null`.

---

## 3. Theme scan

Pull every template and section of the **active** theme and grep for:

| Signal | Means |
|---|---|
| `{% section 'product_bundle' %}` | a canonical host exists |
| a theme-local `sections/product_bundle` | a clone — diff it against the global; it will never auto-update |
| `dynamic_bundle_picker`, `data-dbp-`, `data-fluid-dbp` | hand-authored picker (Archetype B) |
| the picker injected into `product/default` | must be un-injected |
| `data-fluid-bundled-items` | declarative cart path — 4 silent-failure modes |

Also record, because they decide how the generated CSS is written: the token lineage
(`--clr-*` vs `--color-*`), the `.container` mechanism (or a per-section container keyed to
`section.id`), the `button, .btn {}` reset, the input `-webkit-appearance` reset, the
`ul, li { list-style: none }` reset, radius and type scale.

---

## 4. Live storefront probe

For one representative product, compare all three render paths — this is how you tell a
platform bug from a theme bug:

```
plain:     https://<co>.fluid.app/home/products/<slug>
canonical: …?preview=true&theme_template_id=<canonical host>
picker:    …?preview=true&theme_template_id=<hand-authored host>
```

Markers: canonical → `data-bundle-section`; hand-authored → `data-dbp-*`; ours → `data-bb-root`.

Parse the data blob directly — key count is diagnostic: **50 = page scope** (exclusivity is
only in `bundle_config`), **40 = `ProductDrop#as_json`** (top-level exclusivity present,
hidden groups dropped).

---

## 5. Archetypes

Classify with a confidence score and the evidence that produced it.

| # | Archetype | Signals | Action |
|---|---|---|---|
| **A** | Already dynamic bundles | products with `product_bundle_groups.size > 0` | Audit + re-theme + fix routing/pricing gaps. No data migration. |
| **B** | Hand-authored picker | picker section in the theme; `data-dbp-*` on live pages | The picker's own rule/pricing/submit logic **is** the behavioural spec — read it, port it, then un-inject from `product/default`. |
| **C** | Legacy flat `ProductBundle` | `product_bundles[]` non-empty, `product_bundle_groups` empty | Convert to one `included` group (split by `display_externally` into visible + hidden). Preserve `quantity`. **Capture pricing intent first** — these price from the master variant like a normal product. |
| **D** | Convention-based "fake" bundles | kit/combo/bundle titles with multi-variant options; descriptions enumerating components; a component catalog with a parent SKU pattern | **Propose, never auto-convert.** Present candidates with evidence; the user confirms each. |
| **E** | Greenfield | zero bundles, zero infrastructure | `playbooks/06-greenfield.md` |
| **F** | External source page | a reference URL that is a configurator or a fixed bundle page (§6) | Translate the page's own option model into groups. |
| **G** | **Mis-modelled variant product** | a multi-variant product whose option encodes COMPONENT choice, not item attributes — see the test below | **Adjust the existing product in place.** Never create a parallel "Build Your Own X" beside it. Propose, with the price consequence stated. |

A company can be several at once. Classify per product, not per company.

Archetype G is common on any store whose catalog was imported or built by an earlier automated
pass: a menu, a configurator or a kit gets flattened into one product with one option axis,
because that is what a plain product importer can express. It is the single most likely thing
this skill will find on a company that has already been through onboarding — and it is the case
a naive read dismisses as "just variants".

---

## 5a. What a bundle looks like, by vertical

Most companies sell ordinary products. **A configurator is the hardest case, not the common
one.** Rank your expectations accordingly: the single most frequent real bundle on the platform
is a fixed kit with one flat price and no shopper choice whatsoever.

| Vertical | How the bundle usually presents | Group shape |
|---|---|---|
| **Any** — the baseline | "Bundle & save", gift set, starter pack | all `included`, bundle-level flat price |
| Supplements / wellness | "Starter stack", "3-month supply", "build your stack" | `included` base + `max_only` add-ons; subscription often forced |
| Beauty / skincare | "Build your routine", custom kit, "pick 3 shades" | `exact N` over shade/size variants, `dynamic_price` |
| Apparel | "Build a set", "3 for $99", "complete the look" | `exact N` or `min_and_max`, group `fixed_price` |
| Food / QSR | meal builder, "make it a combo" | `included` base + `exact 1` protein + `max_only` toppings |
| Electronics / hardware | "Configure", "kit with accessories" | `included` core + `exact 1` config + `max_only` accessories; **exclusive pairs common** |
| Pet | variety pack, "pick your flavours" | one `exact N` group |
| Coffee / beverage | "choose 3 bags", subscription bundle | `exact N` + subscription |
| Home goods / furniture | room bundle, matching set | all `included`, flat price |
| Direct sales / MLM | business builder kit, **enrollment pack** | catalog bundles fine; **enrollment bundles are UNSUPPORTED — refuse** |

**Variant-dimension trap, most visible in apparel and beauty.** A bundle item is a *variant*,
not a product. So "pick a shirt, then pick its size" is two-dimensional, and the platform has
only one dimension: you enumerate the variants you want selectable. Either the group lists one
representative variant per style (and size is handled elsewhere), or it lists every
style×size variant and gets large fast. Surface this to the user rather than silently choosing —
it changes the shopper experience materially.

### Variants vs bundles — run this test on every multi-variant product

Do **not** dismiss a product just because it has options. Options are how a mis-modelled
bundle looks. Ask what the option *means*:

| The option varies… | Verdict |
|---|---|
| attributes of one indivisible item (size, colour, length, scent) | **variants** — leave alone |
| **which components the item is made of** (protein, base, configuration, add-on) | **archetype G** — a bundle modelled as variants |

**The mechanical test: do the option's values correspond to things that exist, or could exist,
as their own catalog products?** A Large is not a product. Steak is.

Run these three checks and record the result per product:

1. **Value↔product match** — normalise each option value and look for a catalog product with
   that title. A high match rate means the option is component selection.
2. **Shared option object** — is the same option `id` attached to several parent products? A
   real variant axis is usually product-specific; a shared axis is a menu/category-wide
   component choice.
3. **Price-delta correspondence** — do the variant price gaps equal the price gaps between
   those standalone components? Then the variant price is carrying a component upcharge.

Genuinely **not** bundles, decline with a reason: a quantity break, a multipack with its own
SKU, a "frequently bought together" upsell, a subscription of one product.

> **Observed live (Chipotle, 2026-08).** `Burrito` (89585) and `Burrito Bowl` (89586) each had
> one option — `"protein or veggie"`, **option id 1144, shared between them** — with 7 variants
> priced $9.35–$11.35, and every value (Chicken, Steak, Sofritas, Veggie…) also existing as a
> standalone product. No rice, beans or topping modelling anywhere, so a shopper could choose a
> protein and nothing else. All three signals fired. These are archetype G, and the first run
> of this workflow missed them because the rule then in force excused "flavour" options.

---

## 6. Archetype F — recognising a bundle from a source page

**The agent should not need to be told a page is a bundle.** Crawl the URL with
`formats:['markdown','html']` and `only_main_content:false`, then score the signals below.

There are **two** shapes to recognise, and the simpler one is more common:

**Shape 1 — fixed bundle page.** "What's included" / "In this kit" / "This set contains" plus
an itemised component list, ONE price (often struck through against a higher "value" figure),
and a plain add-to-cart. No selection UI at all. ⇒ all `included` groups, flat price. Do not
invent choice groups for a page that offers none.

**Shape 2 — configurator.** Signals below. This is the harder case and the rarer one.

**Strong (any two ⇒ configurator):**
- Repeated option cards in labelled sections, where the section heading is an instruction —
  "Choose your…", "Pick 2", "Add…", "Select up to…".
- A running total or price that updates as options change, and a single terminal CTA
  ("Add to bag", "Add to order") rather than one CTA per card.
- Cards carrying a per-item price delta (`+ $2.00`, "Free", "Included").
- A quantity stepper or an "extra / double" affordance on individual cards.
- Radio-like exclusivity within a section (one selection replaces another) versus
  checkbox-like multi-select in another.

**Supporting:**
- URL shape: `/build`, `/builder`, `/customize`, `/configure`, `/create-your-own`, `/bundle`.
- A step/progress indicator, or a persistent summary panel.
- Structured data (`ProductGroup`, `hasVariant`, `AggregateOffer`) with more members than a
  normal PDP.

**Extraction → group model.** For each section of the page:

| Read from the page | Becomes |
|---|---|
| Section heading text | `group.title` |
| "Choose 1" / a radio group | `customizable`, `selection_type: exact`, `min_selections: 1` |
| "Pick 2" / "Choose 3" | `exact`, `min_selections: N` |
| "Add up to N" / optional checkboxes | `max_only`, `max_selections: N` |
| "Choose at least N" | `min_only` |
| No limit stated, multi-select | `max_only` with `max_selections` = the item count, flagged for confirmation |
| Cards with a `+$` delta | `pricing_type: dynamic_price` |
| Cards all free / no deltas shown | `fixed_price` with `fixed_price: "0.0"` **explicitly set** |
| An always-present component, no picker | `included` group — **and it must get an explicit price** |
| Two sections where choosing one hides the other (bowl vs burrito) | an exclusive pair |
| "Extra"/"Double" on a card | item `max_quantity: 2` |
| A card pre-highlighted on load | item `config.is_default: true` |

**Then map each extracted option to a real catalog product** by normalised title, then SKU,
then fuzzy match. Report three buckets: matched, ambiguous (≥2 candidates — ask), missing
(no catalog product — offer to create, or exclude). **Never invent a variant id.**

### JS-gated pages — the general rule

Configurators are frequently client-rendered and bot-protected (Kasada, Cloudflare, Akamai, or
simply a hydrated SPA). When the crawl returns a shell with no option cards:

1. Say so explicitly and name the reason. **Report it as a capture limitation, never as an
   empty result** — "no options found" and "could not read the page" are different findings and
   conflating them is the failure mode here.
2. Ask the user to paste the rendered HTML (DevTools → Elements → copy outer HTML). Option
   cards in a modern configurator almost always carry stable hooks — a `data-*` item name/id,
   an `aria-label` with price, a background-image URL — so a paste is deterministic to parse.
3. Fall back to a plain-language description from the user only if the paste is unavailable,
   and mark every derived group as **needs confirmation**.

> **Worked example (food/QSR, the test company).** `chipotle.com/order/build/burrito` is a
> Kasada-protected Vue app fed by `services.chipotle.com`. On the pasted HTML every
> `.meal-builder-item-selector-card-container` carries `data-qa-item-name`, `data-qa-item-id`,
> an `aria-label` with price + calories, an optional `.item-tagline`, and a `background-image`
> pointing at the official DAM PNG — and 47 of those components already exist as individual
> products, so the matching stage resolves against the live catalog rather than creating
> anything. The *shape* of that recovery generalises; the selectors are that site's.

---

## 7. Output — `bundle-discovery.json`

```jsonc
{
  "company": { "id": 0, "slug": "", "storefront": "", "countries": ["US"], "currency": {} },
  "theme":   { "activeId": 0, "tokenLineage": "clr|color", "containerMechanism": "",
               "resets": { "button": true, "inputAppearance": true, "listStyle": true },
               "hasCanonicalHost": false, "hasLocalSectionClone": false, "pickerSections": [] },
  "archetypes": [ { "kind": "A|B|C|D|E|F", "confidence": 0.0, "evidence": [], "productIds": [] } ],
  "bundles":  [ { "productId": 0, "bundleId": 0, "matchedBy": "group_id", "groups": [],
                  "routedTemplateId": null, "issues": [] } ],
  "candidates": [ { "productId": 0, "why": [], "proposedGroups": [] } ],
  "sourcePages": [ { "url": "", "captured": "html|blocked", "sections": [], "matching": {} } ],
  "blockers": []
}
```

**G1 passes when:** every candidate is classified with evidence; no product is both "bundle"
and unclassified; enrollment bundles are flagged unsupported and excluded; every source-page
option is matched, ambiguous, or missing — never silently dropped.
