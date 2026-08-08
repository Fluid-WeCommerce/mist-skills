# 02 — Translation: existing behaviour → Dynamic Bundle records

Output is `bundle-plan.json`. Nothing writes until the plan is approved.

**Preservation priority, in order.** When two cannot both be preserved, the higher one wins
and the conflict is surfaced, never silently resolved:

1. charged price → 2. selection semantics → 3. subscription semantics → 4. exclusivity →
5. defaults & quantity caps → 6. copy & imagery.

---

## 1. The mapping table

| Source concept | Target | Trap |
|---|---|---|
| "always included" component | `included` group, item `quantity` = component qty | **Must set an explicit `fixed_price`** — an included group with no price displays as its item sum and charges **$0.00** (finding C). If it really is free, set `"0.0"` deliberately and record that. |
| "pick exactly N" | `customizable`, `selection_type: exact`, `min_selections: N` | `exact` collapses `max` to `min`; a stale persisted `max_selections` is normalized by the drop but **not** by the raw API |
| "pick up to N" | `max_only`, `max_selections: N` | `min_selections` is forced `nil` → guard the client comparison (P16) and allow a zero submit (P14) |
| "pick at least N" | `min_only`, `min_selections: N` | `max_selections` forced `nil` — same nil guard |
| "pick N–M" | `min_and_max` | progress denominator is max, completion is judged at min |
| either-A-or-B branch | two groups + `bundle_config.mutually_exclusive_groups` | pairs of **sort_order**, max 2 per set, a group in at most one set — **Surface A only**, or the cart ignores it |
| per-component price | group `dynamic_price` | the **only** mode where CV/QV flows from items |
| one flat kit price | group `fixed_price`, or bundle-level flat for the whole bundle | credits **0/0 CV/QV** unless re-entered on the group/bundle country row — surface this, it is a commissions decision |
| per-country price | `country_pricing[]` at the right layer | values are **strings**, ISO **UPPERCASE**, `enabled` strict `== true` |
| pre-selected option | item `config.is_default: true` | **clamp to `max_selections`** and skip out-of-stock (P19) |
| "max 2 of this" | item `config.max_quantity` | counters count **units**, not lines |
| subscribe option / required | item `config.allow_subscription` / `force_subscription` (+ plan id) | a forced item needs ≥1 active plan on **its own** product; check the group level too — real fixtures force at item level with the group flag false |
| hidden internal component | `included` group + `pricing_config.hidden: true` | legal only on static groups outside an exclusive pair |
| legacy `ProductBundle` row | one `included` group; `display_externally: false` → a second `hidden` group | preserve `quantity`; these previously priced from the master variant |

---

## 2. Write shape (Surface A only)

```jsonc
PATCH /api/company/v1/products/{id}/update_bundle_product
{ "product": {
    "bundle": true,
    "status": "published",
    "bundle_config": {
      "mutually_exclusive_groups": [ { "ids": [1, 2], "default": null } ],   // SORT ORDERS
      "bundle_pricing_enabled": false
    },
    "product_bundle_groups_attributes": [
      { "id": 0, "title": "", "group_type": "customizable", "sort_order": 0,
        "selection_type": "exact", "min_selections": 1,
        "pricing_config": { "pricing_type": "dynamic_price" },
        "bundle_group_items_attributes": [
          { "variant_id": 0, "quantity": 1, "sort_order": 0,
            "config": { "is_default": true, "max_quantity": 2, "allow_subscription": false } }
        ] } ] } }
```

Rules the shape encodes:

- `is_default` goes **inside `config`** — there is no column, and on Surface B it 500s.
- `sort_order` is meaningful because exclusivity references it. Set it explicitly.
- Omit `id` to create, include it to update, add `"_destroy": true` to remove.
- Unknown keys are silently dropped with a **200**. Read back and diff, always.
- Create returns **200**, not 201.
- On the **create** path, `bundle_pricing_enabled: true` + a `dynamic_price` group passes
  validation (the bundle saves before its groups) and then fails on the next update. Never
  emit that combination.

---

## 2b. Archetype G — converting a variant-encoded product into a bundle

The product already exists, already ranks, already has a URL, and its variants already carry
the full price. Three rules, in order of importance:

**1. Adjust in place. Do not create a parallel product.** Shipping "Build Your Own Burrito"
next to "Burrito" leaves two products for one menu item, splits the URL and any SEO, and
guarantees the wrong one gets ordered. Convert `89585`, do not create `89898`.

**2. The double-charge trap.** A variant priced $9.95 already includes its component. Bolt a
priced component group onto that product and the shopper pays for the protein twice. So
conversion is not additive — the variant layer must be dismantled as the group layer goes in:

```
BEFORE  product 89585  option "protein or veggie" → 7 variants @ $9.35–$11.35
AFTER   product 89585  one master variant, options cleared
                       + group "Protein or Veggie", customizable, exact 1
```

**3. Where the money goes is a decision, not a default.** Two legal shapes, and they price
differently:

| Shape | How | Consequence |
|---|---|---|
| **Component-priced** | one `customizable` group, `dynamic_price`, each item priced at the component's own price | total = sum of picks; CV/QV flows; the menu price is only reproduced if component prices happen to add up to it |
| **Base + upcharge** | an `included` group at an explicit base price + a `customizable` group whose items carry only the *delta* ($0 chicken, +$1.40 steak) | reproduces the original variant prices exactly; the fixed base credits 0/0 CV/QV unless re-entered |

Derive the deltas from the variants you are replacing — that is the only source that preserves
the prices the merchant actually set. **Never infer the menu price from ingredient add-on
prices**; a burrito is not the sum of its toppings' à-la-carte prices.

Mechanics that bite:

- Clearing `option_attrs` to `[]` at product and variant level drops the option display, but a
  variant retains its stale `option_ids` — verify by re-reading, not by the 200.
- Removing a variant is `variants_attributes: [{ id, _destroy: true }]`. Removing every
  non-master variant is the goal; the master survives as the bundle parent.
- A bundle parent's master variant is normally priced 0 and does **not** contribute to the
  bundle total — the base must live in a group, not on the parent.
- Deleting a variant that has order history may be refused. If so, deactivate it
  (`variant_countries.active: false`) and say so rather than forcing it.
- **A shared option object** (the same option `id` on several products) means converting one
  product does not free the others. Convert the set together, or state which remain.

Always report the before/after price for at least the cheapest and dearest original variant, so
the merchant can see whether the conversion moved any price.

---

## 3. Judgement calls that must be surfaced, not decided silently

Each of these changes money or commissions. Put them in the plan with the consequence spelled
out, and let the human choose:

1. **dynamic vs fixed group pricing** → CV/QV flows or doesn't.
2. **an included group's price** → an unset price ships the contents free.
3. **defaults** → which options are pre-selected, and the resulting starting price.
4. **bundle-level flat pricing** → collapses every layer beneath it and forbids dynamic groups.
5. **subscription forcing** → a forced item that loses its plan makes the bundle unbuyable.
6. **a component with no catalog match** → create the product, or drop the option.

---

## 4. `bundle-plan.json`

```jsonc
{
  "sourceArchetype": "B",
  "bundles": [{
    "productId": 0, "action": "create|update|adopt",
    "groups": [{ "title": "", "type": "", "selectionType": "", "min": 1, "max": 1,
                 "pricingType": "", "price": null, "sortOrder": 0,
                 "items": [{ "variantId": 0, "quantity": 1, "maxQuantity": null,
                             "isDefault": false, "allowSubscription": false }] }],
    "exclusiveSets": [[0, 1]],
    "assertions": [
      { "kind": "price", "selection": [], "expected": "50.00" },
      { "kind": "selection", "group": 0, "rule": "exact 1" },
      { "kind": "cart", "expects": "included group absent from bundled_items" }
    ],
    "judgementCalls": [{ "id": "", "question": "", "chosen": "", "consequence": "" }]
  }]
}
```

`assertions[]` is the point of the file — gates G5 and G6 replay them against the real cart,
so "preserved the original behaviour" becomes a machine check rather than a claim.
