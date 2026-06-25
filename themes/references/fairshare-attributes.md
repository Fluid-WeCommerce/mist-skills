# FairShare behavioral attributes — data-fluid-*

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- Naming convention
- Loading the runtime
- The attributes
- Correct usage examples
- Findings to surface
- Quick audit
- Checklist for FairShare-attributed elements


These are the **runtime behavioral attributes** consumed by the FairShare web-widget SDK (loaded from `https://assets.fluid.app/scripts/fluid-sdk/latest/web-widgets/index.js`). Theme authors hand-write them on buttons, links, and elements to wire up commerce behavior — add to cart, open cart drawer, add enrollment packs, etc.

**This is different from `section.fluid_attributes` above.** The editor attributes are emitted by Liquid drops in editor mode. These are static HTML attributes you write into the template that the runtime SDK scans for on `DOMContentLoaded`.

### Naming convention

All FairShare runtime attributes are `data-fluid-*` (kebab-case, `data-` prefix). The SDK is case-sensitive — `data-fluid-add-to-cart` works, `data-fluid-addToCart` and `data-fluid_add_to_cart` do not. The runtime auto-scans the DOM; no init call is required.

### Loading the runtime

```html
<script
  id="fluid-cdn-script"
  src="https://assets.fluid.app/scripts/fluid-sdk/latest/web-widgets/index.js"
  data-fluid-shop="{{ shop.handle }}"
  defer
></script>
```

`data-fluid-shop` is required. Optional script-level attributes: `data-fluid-api-base-url`, `data-fluid-country` (2-letter ISO), `data-fluid-language` (2–3 letter), `data-fluid-rep-id`, `data-share-guid`, `data-debug`.

### The attributes

| Attribute                         | Value shape                                                 | Goes on                                                                           | Notes                                                                                                                                                         |
| --------------------------------- | ----------------------------------------------------------- | --------------------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `data-fluid-cart`                 | `"open"` / `"close"` / `"toggle"`                           | button/link                                                                       | Lowercase only. Strict equality check in the SDK.                                                                                                             |
| `data-fluid-add-to-cart`          | comma-separated variant IDs (integers)                      | button/link                                                                       | Companion for `data-fluid-quantity`, `data-fluid-subscribe`, `data-fluid-subscription-plan-id`, `data-fluid-bundled-items`, `data-fluid-open-cart-after-add`. |
| `data-fluid-quantity`             | positive integer                                            | button/link **with** `data-fluid-add-to-cart` or `data-fluid-add-enrollment-pack` | Defaults to 1.                                                                                                                                                |
| `data-fluid-subscribe`            | `"true"` / `"false"` or comma-separated per item            | button/link **with** `data-fluid-add-to-cart`                                     | Per-item shape mirrors the variant ID list.                                                                                                                   |
| `data-fluid-subscription-plan-id` | **single** integer                                          | button/link **with** `data-fluid-add-to-cart`                                     | **Only one** — comma-separated values are not supported.                                                                                                      |
| `data-fluid-bundled-items`        | JSON string `[{"variant_id": int, "quantity": int}, ...]`   | button/link **with** `data-fluid-add-to-cart`                                     | Invalid JSON is logged and silently dropped.                                                                                                                  |
| `data-fluid-open-cart-after-add`  | `"true"` / `"false"`                                        | button/link **with** add-to-cart or enrollment-pack                               | Defaults to `"true"`. Set `"false"` to keep shopping.                                                                                                         |
| `data-fluid-add-enrollment-pack`  | enrollment pack ID (integer)                                | button/link                                                                       | Can combine with `data-fluid-add-to-cart` for pack + items in one click.                                                                                      |
| `data-fluid-bundle-selections`    | JSON string `[{"variant_id": int, "bundled_items": [...]}]` | button/link **with** `data-fluid-add-enrollment-pack`                             | For packs whose products take variant/bundle config.                                                                                                          |
| `data-fluid-add-combined`         | `"{enrollmentPackId}+{variantId1},{variantId2},..."`        | button/link                                                                       | Alternative to setting both `data-fluid-add-to-cart` and `data-fluid-add-enrollment-pack`.                                                                    |

### Correct usage examples

```html
{%- comment -%} Open cart drawer {%- endcomment -%}
<button data-fluid-cart="open">Cart ({{ cart.item_count }})</button>

{%- comment -%} Add one item {%- endcomment -%}
<button data-fluid-add-to-cart="{{ product.first_variant.id }}">
  Add to cart
</button>

{%- comment -%} Add with quantity + subscription {%- endcomment -%}
<button
  data-fluid-add-to-cart="{{ variant.id }}"
  data-fluid-quantity="2"
  data-fluid-subscribe="true"
  data-fluid-subscription-plan-id="{{ section.settings.default_plan_id }}"
>
  Subscribe &amp; save
</button>

{%- comment -%} Add a bundle product with its bundled items {%- endcomment -%}
<button
  data-fluid-add-to-cart="{{ bundle_variant.id }}"
  data-fluid-bundled-items='[
    {%- for item in selected_items -%}
      { "variant_id": {{ item.variant_id }}, "quantity": {{ item.qty }} }{%- unless forloop.last -%},{%- endunless -%}
    {%- endfor -%}
  ]'
  data-fluid-open-cart-after-add="false"
>
  Add bundle
</button>

{%- comment -%} Add an enrollment pack {%- endcomment -%}
<button data-fluid-add-enrollment-pack="{{ section.settings.starter_pack.id }}">
  Join with starter pack
</button>
```

### Findings to surface

The reviewer should flag these on any element that uses `data-fluid-*`:

#### Wrong attribute names (typos / wrong casing)

**`blocker`** — the SDK only recognizes the exact kebab-case forms listed above.

| You see                                                     | Severity  | Fix                                              |
| ----------------------------------------------------------- | --------- | ------------------------------------------------ |
| `data-fluid-addToCart="..."`                                | `blocker` | `data-fluid-add-to-cart="..."`                   |
| `data-fluid_add_to_cart="..."` (underscores)                | `blocker` | Kebab-case only.                                 |
| `datafluid-add-to-cart="..."` (missing hyphen after `data`) | `blocker` | Must be `data-fluid-*`.                          |
| `fluid-add-to-cart="..."` (missing `data-` prefix)          | `blocker` | Add `data-`.                                     |
| `data-fluid-cart="Open"` / `"OPEN"`                         | `blocker` | Lowercase: `"open"` / `"close"` / `"toggle"`.    |
| `data-fluid-cart="show"` / `"display"`                      | `blocker` | Only `open` / `close` / `toggle` are recognized. |

#### Missing required companions / dangling modifiers

**`blocker`** — modifier attributes are inert without their owner.

| You see                                                                                                        | Severity  | Fix                                                     |
| -------------------------------------------------------------------------------------------------------------- | --------- | ------------------------------------------------------- |
| `data-fluid-quantity` on an element with neither `data-fluid-add-to-cart` nor `data-fluid-add-enrollment-pack` | `blocker` | Either pair it with one of the add-actions or remove.   |
| `data-fluid-subscribe` without `data-fluid-add-to-cart`                                                        | `blocker` | Subscribe is meaningful only in an add-to-cart context. |
| `data-fluid-subscription-plan-id` without `data-fluid-add-to-cart`                                             | `blocker` | Same.                                                   |
| `data-fluid-bundled-items` without `data-fluid-add-to-cart`                                                    | `blocker` | Bundled items modify the add-to-cart action.            |
| `data-fluid-bundle-selections` without `data-fluid-add-enrollment-pack`                                        | `blocker` | Only meaningful when adding a pack.                     |
| `data-fluid-open-cart-after-add` on an element with no add-action                                              | `should`  | Inert — remove or pair with an add-action.              |

#### Wrong value shapes

| You see                                                                                    | Severity  | Fix                                                                                                           |
| ------------------------------------------------------------------------------------------ | --------- | ------------------------------------------------------------------------------------------------------------- |
| `data-fluid-subscription-plan-id="4,5"` (comma-separated)                                  | `blocker` | Single integer only. If the items need different plans, that's not supported — drop down to single-item rows. |
| `data-fluid-quantity="2.5"` / `"0"` / `"-1"`                                               | `blocker` | Positive integer.                                                                                             |
| `data-fluid-subscribe="yes"` / `"1"` / `"on"`                                              | `blocker` | String `"true"` or `"false"` only.                                                                            |
| `data-fluid-bundled-items='[{"variant_id":"39325", "quantity":1}]'` (variant_id as string) | `blocker` | `variant_id` and `quantity` must be JSON numbers.                                                             |
| `data-fluid-bundled-items='{...}'` (object, not array)                                     | `blocker` | Must be a JSON array.                                                                                         |
| Single-quote-wrapped JSON without escaping inner double quotes                             | `blocker` | Use `'[...]'` outer + `"..."` inner per the examples. Mismatched quoting breaks parsing silently.             |
| `data-fluid-country="USA"` (3-letter) on the script tag                                    | `blocker` | 2-letter ISO. `"US"`, not `"USA"`.                                                                            |
| `data-fluid-language="english"` on the script tag                                          | `blocker` | 2–3 letter code: `"en"`, `"es"`, `"fil"`.                                                                     |

#### Wrong element type / placement

| You see                                                                 | Severity                                              | Fix                                                                                                                   |
| ----------------------------------------------------------------------- | ----------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `data-fluid-add-to-cart` on a `<div>` with no click semantics           | `should` (`blocker` for accessibility-critical pages) | Use `<button type="button">` or `<a href="...">`.                                                                     |
| `data-fluid-add-to-cart` on a parent that wraps multiple buttons        | `blocker`                                             | Move to the specific clickable child — the SDK click handler fires once per click, on the element with the attribute. |
| `data-fluid-shop` missing from the `<script id="fluid-cdn-script">` tag | `blocker`                                             | Required for SDK init. Without it, none of the `data-fluid-*` attributes do anything.                                 |
| Multiple `<script>` tags with `id="fluid-cdn-script"`                   | `blocker`                                             | The SDK uses this ID for self-discovery; duplicates pick a random one.                                                |

#### Liquid-side mistakes

| You see                                                                                        | Severity                           | Fix                 |
| ---------------------------------------------------------------------------------------------- | ---------------------------------- | ------------------- | -------------------------------------------------------------------------------------------------------------------- |
| `data-fluid-add-to-cart="{{ variant }}"` (drop, not `.id`)                                     | `blocker`                          | `{{ variant.id }}`. |
| `data-fluid-quantity="{{ section.settings.default_qty                                          | default: 1 }}"` rendering to empty | `should`            | Always provide a `default:` filter for settings that are required by the SDK to be integers.                         |
| `data-fluid-bundled-items` JSON built with un-escaped Liquid (commas/quotes from user content) | `blocker`                          | Render through `    | json` or hand-craft only with sanitized numeric IDs. User-controlled strings inside JSON attributes are an XSS path. |

### Quick audit

From the theme repo root:

```bash
# Wrong attribute prefixes
grep -rE 'datafluid-|data-fluid_|[^a-z-]fluid-add-to-cart|[^a-z-]fluid-cart=' --include='*.liquid' . 2>/dev/null

# Common camelCase typos
grep -rE 'data-fluid-(addToCart|openCartAfterAdd|subscriptionPlanId|bundledItems)' --include='*.liquid' . 2>/dev/null

# Modifier attributes without an owner action in the same element
# (heuristic — manual review still needed)
grep -rln 'data-fluid-quantity' --include='*.liquid' . 2>/dev/null | while read -r f; do
  if ! grep -q 'data-fluid-add-to-cart\|data-fluid-add-enrollment-pack' "$f"; then
    echo "POSSIBLE_ORPHAN  $f"
  fi
done

# Wrong cart action values
grep -rE 'data-fluid-cart="(?!(open|close|toggle)")' --include='*.liquid' . 2>/dev/null
```

### Checklist for FairShare-attributed elements

- [ ] Attribute name is exact kebab-case with `data-fluid-` prefix
- [ ] `data-fluid-cart` value is `open` / `close` / `toggle` (lowercase)
- [ ] Modifier attributes (`quantity`, `subscribe`, `subscription-plan-id`, `bundled-items`, `open-cart-after-add`) are paired with an add-action attribute
- [ ] `data-fluid-subscription-plan-id` carries a single integer
- [ ] `data-fluid-bundled-items` / `data-fluid-bundle-selections` are valid JSON arrays with numeric IDs and quantities
- [ ] Attributes live on a `<button>` or `<a>` (or have appropriate ARIA + click semantics)
- [ ] Script tag has `id="fluid-cdn-script"` and `data-fluid-shop` set, and there is exactly one

---
