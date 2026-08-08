# 08 — The verified write recipe

Every rule here was confirmed live against Chipotle (company 980243433) on 2026-08-06 while
converting six menu items to bundles, building four fixed catering kits, and reproducing a real
add-to-cart failure. Each one exists because a request failed or a read-back was wrong. Nothing
here is inferred.

Read this **after** `02-translation.md` (shape decisions) and alongside `05-validation.md`.

---

## 1. Classify the shape before you write anything

The most expensive mistake available is applying one pattern to products that merely *look*
uniform. It happened three times in one session.

Chipotle had 7 "menu item" products. They split three ways:

| Products | Option | What the values are | Correct shape |
|---|---|---|---|
| Burrito, Bowl, Tacos, Salad, Quesadilla, Kid's | **1144** | components of *one* item (Chicken, Steak…) | **bundle** — component axis |
| Chips & Sides 89593 | **1145** | 24 values that each already exist as their own product | **category** — a flattened collection |
| Build-Your-Own 89584, High Protein 89587 | **1143** | distinct menu items at $3.50–$16.10 | **category** (89587) / **bundle** (89584) |

So the test is never "do these share an option?" It is:

> **Are the option values components of a single sellable thing, or are they separate sellable
> things?** Components → bundle. Separate things → category/collection. Converting a category
> into one bundle destroys a browsable listing and advertises one wrong price.

Check the **option id** per product. Do not generalise from a sibling.

### Fixed kit vs configurable — and the case where it is BOTH

- **Fixed kit** (shape 1, the most common): the card names its full contents and has one price.
  Model as a bundle with a single `included` group at `fixed_price`.
- **Configurable**: the shopper chooses. `customizable` groups.
- **Both**: a category page of fixed kits where each card *also* has a **CUSTOMIZE** link into a
  builder. Chipotle's Family Meals is this. The correct model is **N fixed-kit products *plus* one
  configurable bundle**, all in one collection — not one or the other. The kit and builder prices
  legitimately differ (Chipotle: $52/$52/$63 kits vs $53/$53/$64 builder, a flat +$1 to
  customize). **Do not "reconcile" them.**

### Never trust imported prices as source of truth
The importer had the catering proteins at $50/$50/$61; the live page said **$52/$52/$63**. The
catalog was wrong before anyone touched it. Deriving deltas from existing variants is correct when
*preserving* prices and wrong when *matching a source*. Read the source.

---

## 2. The endpoint, and the two calls

```
POST  /api/company/v1/products/create_bundle_product
PATCH /api/company/v1/products/{id}/update_bundle_product
```

Body wrapped in `product`. Plain `PATCH /api/company/v1/products/{id}` **silently ignores**
`product_bundle_groups_attributes` and still returns 200 — the classic false success.

**`title` is required even on an update.** Omitting it → 422 `{"product":{"title":["is missing"]}}`.

### Create = ONE call. Convert = TWO.

Verified on three creates and six conversions:

| | `bundle: true` + groups in one request |
|---|---|
| `POST create_bundle_product` | ✅ persists — `is_bundle: true`, `bundle_price` correct, Bundle row synced |
| `PATCH update_bundle_product` | ❌ groups are created but `is_bundle` stays **false**, `bundle_config: {}`, **no Bundle row** |

So a conversion needs a second, **groups-free** flag call:

```jsonc
// CALL 1 — structure (teardown + groups, see §3)
// CALL 2 — flag only
{ "product": { "id": 89585, "title": "Burrito", "bundle": true, "status": "active" } }
```

Between the two calls the product has groups but no bundle record, and if unrouted its PDP renders
$0.00 with no picker. **Route immediately after (§5), per product — never batch routing to the end.**

---

## 3. Teardown and groups go in the SAME call

A variant priced $9.95 already contains its component. Adding a priced component group while the
priced variant axis still exists charges the shopper twice. Never leave that state, not even
between two requests.

```jsonc
"option_attrs": [],
"variants_attributes": [
  { "id": <master>, "option_attrs": [],
    "variant_countries_attributes": [ { "id": <country_row_id>, "price": "0.0" } ] },
  { "id": <variant_2>, "_destroy": true }
]
```

The surviving master **must** be repriced to 0 on every country row, addressed by
`variant_countries_attributes[].id` — not by writing `price` on the variant. If a `_destroy` is
refused for order history, deactivate instead and say so in the report.

---

## 4. Pricing — the part that silently costs money

### 4a. `fixed_price: "0.00"` is IGNORED
A group priced at zero does **not** zero its contents. Each item's `resolved_price` falls back to
the component variant's own price, even when `config.price` is explicitly `"0.0"`.

Live proof: Large Chips ($2.75) inside a `fixed_price: "0.00"` **included** group pushed
`price_range` from **$53–$64 to $55.75–$66.75**. Removing that one item restored it.

⇒ **A nonzero `fixed_price` pins a group total. `0.00` behaves as unset.** Only components whose
underlying variant is genuinely $0 belong in a free group.

### 4b. What each group type adds to the advertised floor

| Group | Contribution to `price_range.min` |
|---|---|
| `included` | **sum of ALL its components'** resolved prices |
| optional `fixed_price` (`max_only`) | **nothing** |
| optional `dynamic_price` | **its cheapest item** — even when `min_selections: nil` |

That last row is the trap. An optional paid "Add Guac or Queso" `dynamic_price` group moved the
burrito's floor from **$9.35 → $12.30**, so every collection tile advertised "from $12.30" for a
burrito buyable at $9.35. There is no theme-side fix; the value is computed server-side.

⇒ **Never add an optional priced `dynamic_price` group to a product whose "from" price is
customer-facing** unless the client accepts the inflated floor.

### 4c. A fixed-price `included` group prices the bundle exactly
`bundle_price` / `price_range` equal the group's `fixed_price`, ignoring components' own prices
(items still echo their real `pc_price`). This is the correct primitive for a fixed kit, and it
means the kit price cannot drift when a component's à-la-carte price changes.

### 4d. Compare `price_range` before → after — but know what it measures
It sums each item's `config.price`; it does **not** read the group's `fixed_price`. So it is a
strong signal for **dynamic** groups (a moved minimum means you changed the shelf price — that
check caught both 4a and 4b), and reads **`$0.00`** for an **all-fixed** bundle even though the
cart charges correctly. Do not read a zero as a defect, and do not read it as verification.
Full semantics: `09-pricing-patterns.md` §5.

### 4e. Upgrade pricing needs a rebalanced base
Flipping choice groups to `dynamic_price` alone **double-charges**: each item contributes its
full variant price on top of an anchor group that already holds the headline. Use
`base = headline − Σ(default component prices)` on the anchor, `dynamic_price` on every choice
group, `is_default: true` inside `config` on each intended default. Assert `base >= 0`.
See `09-pricing-patterns.md` — this is the single biggest gap the first version of this
playbook had.

---

## 5. Route immediately, per product

```
PATCH /api/company/v1/products/{id}   { "product": { "application_theme_template_id": <id> } }
```

Confirm with `GET /api/application_theme_templates/{id}/available_themeables?per_page=200`. This is
a `template_resources` join **scoped to the active theme** and is silently dropped on a theme
switch or clone — re-run after either.

Loop shape: `call 1 → call 2 → read back → route → verify`. Per product, not per phase.

---

## 6. Other mutation gotchas

- **`images_attributes` APPENDS on PATCH.** It does not replace. Swapping an image without
  `_destroy` for the old id leaves two rows both at position 1. Send `_destroy`.
- **Collection membership REPLACES.** `PATCH /api/v202604/company/collections/{id}`
  `{collection:{product_ids:[…]}}` overwrites the whole set, and the response does **not** echo
  products. Read current members first (v1 GET returns `product_collections[]`), then re-GET to verify.
- **A `draft` / `public: false` collection still renders publicly.** Verified by fetching a live
  draft collection page. Do not "fix" draft status to make a collection reachable.
- **Cross-group duplicate variants are legal.** Cheese sits in both the protein group ("Cheese
  Only", $9.90) and the toppings group ($0) on Quesadilla. Different `product_bundle_group_id` ⇒
  distinct cart keys. This is why rule 4 (always tag the group) is load-bearing.
- **Sequencing: never archive or delete a product the storefront still links to.** Retire only
  after the referring tile/nav has been repointed and that change is confirmed.
- **Bundle items are append-only.** Omitting an existing item from
  `bundle_group_items_attributes` keeps it; it does not remove it.
- **(group, variant) is unique.** Re-sending a variant already in that group `422`s the
  **whole request**, atomically — nothing is written. This makes it a cheap, non-mutating
  membership oracle: send a candidate and read the error.
- **Group-level `_destroy` does not work** — returns 404 even for a group that exists. Do not
  plan a delete-and-recreate around it. Item-level and variant-level `_destroy` DO work.
- **Item updates by `id` work**, including repointing `variant_id` in place. That is how you
  fix a group pointing at the wrong variant — no rebuild needed.
- **Reads cap at 51,200 bytes.** A large bundle cannot be read whole. Page it by PATCHing the
  visible items' `sort_order` into a high block and re-reading.
- **Cart creation needs a top-level `country_code`** as well as `fluid_shop`. Omitting it is
  `422 country_code is missing`.

---

## 7. Read-back checklist, per product

Do all of this from a **fresh `GET`**. A PATCH echo can show values the persisted read does
not — an all-fixed kit echoed `$52.00` and reads `0.0` two days later with its stored config
byte-identical (`09-pricing-patterns.md` §5a). The echo is not evidence.

| Assert | Where |
|---|---|
| `is_bundle: true` | fresh GET after the flag call |
| `price_range` matches intent (dynamic groups) — or is a knowing `$0.00` (all-fixed) | fresh GET |
| `option_attrs: []`, no priced variants remain | product response |
| Bundle row exists with the expected group count | `GET /api/v2025-06/bundles` (read-only) |
| `application_theme_template_id` set | `available_themeables` |
| **Add-to-cart actually succeeds** | §8 — the only test that matters |

Report actual values, never the word "verified".

---

## 8. Prove add-to-cart through the checkout API

**Config being valid says nothing about whether the storefront can sell it.** A six-group bundle
read back perfectly from `/api/v2025-06/bundles` and still failed for shoppers.

Reproduce with the real endpoint:

```
POST /api/checkout/v2026-04/carts
{ "fluid_shop": "<sub>", "country_code": "US", "items": [ { "variant_id": <master>, "quantity": 1,
  "bundled_items": [ { "variant_id": …, "quantity": 1, "product_bundle_group_id": … } ] } ] }
```

**The failure this catches** — sending a selection for an `included` group:

```
400  "product_bundle_group_id 1771 must reference a customizable group
      or an exclusive included group"
```

This is SKILL.md rule 3 violated by the client. The cart attaches included components itself: the
successful response listed Cheese / Romaine / Tortillas under group 1771 although they were **not**
in the request.

Two shapes verified 200 with correct totals:

```jsonc
// configurable — customizable groups ONLY (protein, rice, beans). Included group omitted.
{ "variant_id": 343601, "quantity": 1, "bundled_items": [
  {"variant_id":344039,"quantity":1,"product_bundle_group_id":1765},
  {"variant_id":344022,"quantity":1,"product_bundle_group_id":1769},
  {"variant_id":344023,"quantity":1,"product_bundle_group_id":1770} ] }   // → $53.00

// pure fixed kit — NO bundled_items at all
{ "variant_id": 344077, "quantity": 1 }                                   // → $52.00
```

Expect on the cart line: `is_bundle: true`, `bundle_group_base_price`, and a
`bundle_selection_key` listing **only** the customizable picks
(`1765:344039x1|1769:344022x1|1770:344023x1`; empty string for a pure fixed kit).

**Corollary for the theme:** an all-`included` product has nothing to select, so any UI that gates
add-to-cart on "all required groups chosen" leaves every fixed kit permanently unclickable — and
the API side looks perfectly healthy. Test a fixed kit in the browser, not just in the API.

---

## 9. Cost of the write phase

Each `update_bundle_product` response is a full ~50 KB product payload. Six conversions ≈ 600 KB
across 12 calls plus read-backs. Budget for it: convert in small batches or run it as a workflow
step with its own context, or the agent runs out of room mid-conversion and leaves products
converted-but-unrouted — the exact broken state §5 warns about.
