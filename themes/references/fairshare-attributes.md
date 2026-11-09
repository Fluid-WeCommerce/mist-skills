# FairShare behavioral attributes — data-fluid-*

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Where the attributes are documented

Every `data-fluid-*` attribute the FairShare SDK reads, its value shape, and examples for quantities, subscriptions, bundles, enrollment packs, and combined adds are documented in the [Cart API](https://docs.fluid.app/sdk/cart-api). Look them up with `search_docs` or `query_docs` instead of relying on memory. This file keeps only the review checks.

These are static HTML attributes you write into the template, which the SDK scans for at runtime. They're separate from `{{ block.fluid_attributes }}`, which the Page Editor uses to select blocks.

### The SDK script isn't a theme file

Fluid loads the FairShare SDK from a storefront Global Embed managed in the admin, as a script with the ID `fluid-cdn-script`. The theme must not add, move, or remove it. See [Common theme pitfalls](https://docs.fluid.app/themes/common-pitfalls#leave-the-fairshare-sdk-script-alone).

### Findings to surface

The reviewer should flag these on any element that uses `data-fluid-*`:

#### Wrong attribute names (typos / wrong casing)

**`blocker`** — the SDK recognizes only the exact kebab-case names in the docs.

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
| `data-fluid-subscribe` without an add action                                                        | `blocker` | Subscribe is meaningful only in an add-to-cart context. |
| `data-fluid-subscription-plan-id` without an add action                                           | `blocker` | Same.                                                   |
| `data-fluid-bundled-items` without `data-fluid-add-to-cart`                                                    | `blocker` | Bundled items modify the add-to-cart action.            |
| `data-fluid-bundle-selections` without `data-fluid-add-enrollment-pack`                                        | `blocker` | Only meaningful when adding a pack.                     |
| `data-fluid-open-cart-after-add` on an element with no add-action                                              | `should`  | Inert — remove or pair with an add-action.              |

#### Wrong value shapes

| You see                                                                                    | Severity  | Fix                                                                                                           |
| ------------------------------------------------------------------------------------------ | --------- | ------------------------------------------------------------------------------------------------------------- |
| `data-fluid-subscription-plan-id="4,5"` (comma-separated)                                  | `blocker` | Single integer only. If the items need different plans, that's not supported — drop down to single-item rows. |
| `data-fluid-quantity="2.5"` / `"0"` / `"-1"` | `blocker` | Positive integer. The SDK parses it with `parseInt`, so `"2.5"` adds 2. |
| `data-fluid-subscribe="yes"` / `"1"` / `"on"` | `blocker` | `"true"` or `"false"` only. Anything else adds the item without a subscription. |
| `data-fluid-bundled-items='[{"variant_id":"39325", "quantity":1}]'` (variant_id as string) | `should` | Use JSON numbers, as the docs show. The SDK passes the value to the cart without checking it. |
| `data-fluid-bundled-items='{...}'` (object, not array)                                     | `blocker` | Must be a JSON array.                                                                                         |
| Single-quote-wrapped JSON without escaping inner double quotes                             | `blocker` | Use `'[...]'` outer + `"..."` inner as the Cart API docs show. Mismatched quoting breaks parsing silently.             |

#### Wrong element type / placement

| You see | Severity | Fix |
| --- | --- | --- |
| A `<script>` in the theme that loads the FairShare SDK, or any element with `id="fluid-cdn-script"` | `blocker` | Remove it. The SDK comes from a Global Embed, not the theme. |
| `data-fluid-add-to-cart` on a `<div>` with no click semantics | `should` (`blocker` for accessibility-critical pages) | Use `<button type="button">` or `<a href="...">`. |
| `data-fluid-add-to-cart` on a parent that wraps several buttons | `blocker` | Move it to the specific clickable child. |

#### Liquid-side mistakes

| You see | Severity | Fix |
| --- | --- | --- |
| `data-fluid-add-to-cart="{{ variant }}"` (the drop, not `.id`) | `blocker` | `{{ variant.id }}`. |
| `data-fluid-quantity` built from a setting with no `default:` | `should` | Add `\| default: 1` so an empty setting doesn't render an empty value. |
| `data-fluid-bundled-items` JSON built from unescaped Liquid (commas or quotes from user content) | `blocker` | Output strings with the `json` filter, or build it only from numeric IDs. User-controlled strings inside a JSON attribute are an XSS path. |

### Quick audit

From the theme repo root:

```bash
# A theme-owned copy of the SDK script
grep -rnE 'fluid-cdn-script|fluid-sdk/.*/web-widgets' --include='*.liquid' . 2>/dev/null

# Wrong attribute prefixes
grep -rE 'datafluid-|data-fluid_|[^a-z-]fluid-add-to-cart|[^a-z-]fluid-cart=' --include='*.liquid' . 2>/dev/null

# Common camelCase typos
grep -rE 'data-fluid-(addToCart|openCartAfterAdd|subscriptionPlanId|bundledItems)' --include='*.liquid' . 2>/dev/null

# Modifier attributes in a file with no add action (heuristic; review by hand)
grep -rln 'data-fluid-quantity' --include='*.liquid' . 2>/dev/null | while read -r f; do
  if ! grep -q 'data-fluid-add-to-cart\|data-fluid-add-enrollment-pack' "$f"; then
    echo "POSSIBLE_ORPHAN  $f"
  fi
done

# Cart action values other than open / close / toggle
grep -rnoE 'data-fluid-cart="[^"]*"' --include='*.liquid' . 2>/dev/null | grep -vE '"(open|close|toggle)"$'
```

### Checklist for FairShare-attributed elements

- [ ] The theme doesn't load the SDK itself
- [ ] Each attribute name matches the Cart API docs exactly: kebab-case with the `data-fluid-` prefix
- [ ] `data-fluid-cart` is `open`, `close`, or `toggle` (lowercase)
- [ ] Modifier attributes (`quantity`, `subscribe`, `subscription-plan-id`, `bundled-items`, `open-cart-after-add`) sit on an element with an add action
- [ ] `data-fluid-subscription-plan-id` carries a single integer
- [ ] `data-fluid-bundled-items` / `data-fluid-bundle-selections` are valid JSON arrays with numeric IDs and quantities
- [ ] Attributes live on a `<button>` or `<a>` (or an element with ARIA and click semantics)
