# 03 — Theme generation

Five artefacts. One job each. No bundle-specific anything in any of them.

```
sections/bundle_builder/index.liquid   presentation + the data blob + {% schema %}
assets/bundle-builder.js               normalize | rules | render | cart
assets/bundle-builder.css              tokens only, scoped, + the compat layer
product/bundle/index.liquid            host template, self-gating, with a fallback
theme/bundle-manifest.json             provenance, routing map, contract revision
```

Source lives in `templates/` in this skill. Generation = copy + adapt to the host theme.

---

## 1. Adapt to the host theme (from discovery §3)

The shipped CSS is already lineage-agnostic — every colour is a layered `var()` fallback that
resolves on `--clr-*`, on `--color-*`, or on neither. So adaptation is small and specific:

| Observed | Do |
|---|---|
| Per-section container keyed to `section.id` (newest PDPs) | leave the section container-less; it inherits the host template's width. **Never add `.container`** — that is the guaranteed-visible misalignment. |
| `.container`-based PDP | wrap `{% section %}` in the host template, not inside the section |
| `button, .btn {}` hijack | already handled by `.bb button { all: unset }` |
| `-webkit-appearance: none` on inputs | already handled — custom check markers, no native chrome |
| `ul, li { list-style: none }` | already handled — the section styles its own lists |
| Theme radius / type scale | set `card_radius` and, if the theme has a distinctive scale, adjust `.bb-card__title` / `.bb__heading` sizes only |
| Brand accent | leave `accent_color` unset so it inherits `--clr-primary`; set it only if the brand guide names a specific bundle accent |

Nothing else. Resist restyling into a bespoke design — the whole point is that it inherits.

---

## 2. Push and publish

```
fluid theme push          # NEVER --force (it pushes to the LIVE theme with delete=true)
```

If writing via the API instead: **updates need an explicit publish.** The renderer serves
`theme_template.published`, so a `PUT` alone changes nothing on the storefront —
`POST /api/application_theme_templates/<id>/publish`.

Creating a new template is additive: `CreateAction` sets `status: :active` and publishes, and
does **not** set `default: true`, so it cannot hijack the default product page.

---

## 3. Zero-hardcoding check (mechanical, and it fails the run)

Grep every generated file for every live bundle id, product id, group id, variant id, and
group title in the company's bundle set. **Any hit fails G3.** The one legitimate exception is
`bundle-manifest.json`, which is provenance, not code.

Also assert: `bundle_product` is **not** set on any `product/*` template.

---

## 4. What must be true after generation

- The section renders **nothing** on a non-bundle product (`data-bb-root` absent).
- The data blob is present and escaped — zero raw `<` inside the `<script>`.
- Group shells and included rows exist in the **server-rendered** HTML (progressive
  enhancement — no blank-until-JS, no layout shift).
- `[data-bb-ready="true"]` appears after JS runs.
- Zero console errors; no horizontal overflow at 390 px.

---

## 5. Extending it later

| Want | Change | Don't touch |
|---|---|---|
| Different card layout | `<template data-bb-tpl="card">` + CSS | JS |
| New rule type the platform adds | `selectionBounds()` + `rules()` | render, cart |
| New drop field | `normalize()` only | everything else |
| New cart field | `buildCartPayload()` only | everything else |
| Different copy / language | `{% schema %}` settings | all code |

`model.unknownFields` logs any group/item key the normalizer did not understand (dev mode
only). That is how a future platform feature surfaces instead of silently doing nothing.

---

## 6. Parity mode (non-default)

If byte-parity with the platform section is genuinely required, clone the global
`product_bundle` into the theme instead and apply the 5-site exclusivity patch from
`reference/02-hosting-and-routing.md` §3a (read `bundle_config.mutually_exclusive_groups` as a
fallback). Accept the consequences: ~11 inherited client defects, 46 inline styles that
outrank your CSS, 31 leaked utility class names, and a copy that will never receive upstream
updates (`auto_upgradeable?` is hardcoded `false`). Record the source revision — the deployed
global row is **not** the repo file, so fetch and diff before debugging.
