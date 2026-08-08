# 09 — Pricing patterns: how to get upgrade pricing

The skill documents fixed vs dynamic group pricing as a *data field*. That is not the same as
knowing **how to price a bundle so that picking a dearer option costs more** — which is what
most operators actually want. This playbook is that missing piece.

Confirmed on two companies: Chipotle (2026-08-06) and a second conversion (2026-08-07,
~13 live carts). Written for the general case — an **anchor** item plus one or more **choice
groups**, whether that is a gift set, a starter kit, a build-your-own PC, a treatment
regimen, or a meal.

---

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **anchor group** | The `included` group holding the thing the bundle is named after. Usually carries the headline price. |
| **choice group** | A `customizable` group the shopper selects from. |
| **headline price** | What the bundle is advertised at in its default configuration. |
| **base** | The `fixed_price` you put on the anchor group. |

---

## 2. The trap: flipping choice groups to `dynamic_price` double-charges

Under `dynamic_price`, **each selected item contributes its own full variant price**. If the
anchor group still holds the whole headline price, the total becomes

```
headline + Σ(full component prices)
```

and the customer pays twice for what the headline already covered. Observed: an $11.19
bundle would have charged **$16.27**.

This is the same failure mode as the earlier variant→bundle double-charge (playbook 08 §3),
arriving from a different direction.

---

## 3. The pattern that works — **rebalanced base**

```
anchor_group.fixed_price = headline_price − Σ(default component price, one per choice group)
every choice group       = dynamic_price
is_default: true         = the intended default member of each choice group
```

The default configuration lands exactly on the headline price, and **every upgrade is a true
delta**. Verified on live carts:

| Selection | Total |
|---|---|
| default | $11.19 |
| one tier up (+$0.60 component) | $11.79 |
| cheaper option (−$1.80 component) | $9.39 |

This is the only supported route to upgrade pricing. Document it as *the* pattern; treat
anything else as a smell.

### 3a. Guard — the base can go negative, and that is normal

Value and discounted bundles are frequently priced **below** the sum of their standard
components. That is the entire point of a bundle. A $5.00 value bundle minus a $2.79 side
minus a $2.29 drink yields a base of **−$0.08**.

Resolution order — do not improvise past step 2:

1. **Honour the source's own declared default** for each group. Value bundles usually default
   to a smaller or cheaper component, which fixes it: `5.00 − 1.19 − 2.29 = +1.52`.
2. Still negative → **stop and escalate.** Do not clamp to zero. Do not pick a different
   default to make the arithmetic work. A negative base means the intended pricing cannot be
   expressed this way, and a human has to decide.

**Compute the base per bundle and assert `base >= 0` before writing anything.**

---

## 4. Approaches that do NOT work

| Attempt | What happens |
|---|---|
| **Per-item deltas** — base component `0.00`, upgrades `+delta` | A `0.00` item price is treated as **unset** and falls back to the variant's own price. Same double-charge. |
| **`config.country_prices`** to force a genuine zero | HTTP **500** when sent as an object; **silently dropped** when sent as an array. Broken. Do not spend time here. |
| **`fixed_price: "0.00"` on a group** to make it free | Ignored — behaves as unset, components fall back to their own variant prices (playbook 08 §4a). |

The common root: **the platform cannot represent "this component is free *here*" via a zero.**
Zero means unset everywhere it appears. Only a genuinely $0 variant is genuinely free.

---

## 5. What `price_range` actually reports — and how it lies

`price_range` / `bundle_price_range` sums each item's **`config.price`**. It does *not* read
the group's `fixed_price`.

Consequences, both confirmed:

- **All-fixed bundle** (anchor holds the price, every item priced `0.0`) → `price_range`
  reads **`$0.00`** on a fresh GET, while the cart charges the headline price correctly.
  This is *not* a reader defect: it is an accurate sum of items that are all zero. It is
  also useless as a verification signal, and actively dangerous on any storefront surface
  that renders it (see playbook 03 §price-surfaces).
- **Dynamic choice groups** → the range is correct and arithmetically checkable
  (e.g. `$8.09 – $14.69`), and *is* a good verification signal.

> A suspicious constant in a read is more often a true report of a degenerate configuration
> than a broken reader. Check the configuration before filing a defect.

### 5a. A PATCH echo is not proof — this bit us

On 2026-08-06 an all-fixed kit (Chipotle 89901, anchor group `fixed_price: "52.00"`) was
recorded as `price_range: $52.00` **from the `update_bundle_product` response echo**. A fresh
`GET` on 2026-08-08, with the stored group config byte-identical and `updated_at` unchanged,
returns:

```
bundle_price: "0.0"    price_range: { min: "0.0", max: "0.0" }
```

The echo reflected the values just submitted; the persisted read computes them differently.
The cart was and remains correct at **$52.00** — that was verified with a real
`POST /api/checkout/v2026-04/carts`, not an echo.

**Rule: never verify a write from the response to that write. Always re-`GET`.** Every
"verified" price in a report must trace to a fresh read or a real cart.

---

## 6. Choosing the shape

| Situation | Shape |
|---|---|
| One price, fixed contents, nothing to choose | Single `included` group, `fixed_price` = headline. Accept that `price_range` reads `$0.00`; render the headline from the anchor group, never from `price_range`. |
| Shopper chooses, all options same price | Choice groups `fixed_price: "0.00"`… **no** — see §4. Use `dynamic_price` with every item priced equal, and rebalance the base. |
| Shopper chooses, options differ in price (the common case) | **Rebalanced base**, §3. |
| Optional paid add-ons on top | Allowed, but an optional `dynamic_price` group raises the advertised floor by its cheapest item (playbook 08 §4b). Get explicit sign-off. |

---

## 7. Pre-write checklist

- [ ] Source's declared default identified for **every** choice group
- [ ] `base = headline − Σ(defaults)` computed **per bundle**
- [ ] `base >= 0` asserted; negatives escalated, never clamped
- [ ] `is_default: true` set **inside `config`** on the intended default of each choice group
- [ ] Every choice group is `dynamic_price`; the anchor group is `included` + `fixed_price: base`
- [ ] Planned default total == headline, arithmetic shown
- [ ] Post-write: fresh `GET` (not the echo) + at least one real cart at the default
