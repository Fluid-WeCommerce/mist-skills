# Replenishment classes

Term lists for classifying a catalog into replenishable, durable and bundle. A product
is a subscription candidate when it **runs out and gets rebought** — not merely when it
is bought often.

## Two matching rules that are load-bearing

**Word boundaries are required.** Naive substring matching flagged a lip tint as a
medical device because `TENS` sits inside "sof**tens**", "brigh**tens**" and
"mois**tens**". Bound every term against non-alphanumeric characters or string edges;
`\b` alone is not enough because it fails around punctuation and hyphens.

**Acronyms are case-sensitive.** Same root cause. `TENS` must match `TENS`, never
`tens`.

**An ingredient mention is not a category.** A topical serum whose description lists
vitamin E is not an ingestible supplement. Terms must describe the product's *format or
category*, never a single ingredient it contains.

## Replenishable

Cadence in the right-hand column is a **category convention, not a measurement**. It is
a placeholder until repeat-purchase data replaces it, and it must be labelled as an
assumption every time it is shown. See `measuring-cadence.md`.

| Class | Terms | Assumed cadence |
|---|---|---|
| `blade_refill` | refill blades, razor refill, refill cartridge, cartridge refill, replacement blades, refill pack, blade refill, refills | ~42d |
| `shave_prep` | shave cream, shaving cream, shave gel, shave glaze, shave butter, shave oil, shaving foam | ~60d |
| `body_cleanser` | body wash, shower gel, body cleanser, bar soap, hand wash, cleansing gel | ~45d |
| `moisturizer` | body lotion, moisturizer, moisturiser, body cream, body butter, hand cream, balm, salve, body oil | ~60d |
| `deodorant` | deodorant, antiperspirant | ~60d |
| `haircare` | shampoo, conditioner, dry shampoo, hair mask, hair oil, leave-in | ~60d |
| `wipes` | wipes, cleansing cloths, cotton rounds, cotton pads | ~30d |
| `treatment` | serum, treatment, skin solution, toner, essence, spot treatment, exfoliant, peel | ~75d |
| `hair_removal_consumable` | wax kit, wax strips, hard wax, sugar wax, depilatory | ~60d |
| `oral_care` | toothpaste, floss, mouthwash, toothbrush head, brush head | ~45d |
| `supplement_consumable` | capsules, softgels, tablets, gummies, powder sachets, daily pack, monthly supply | ~30d |

`blade_refill` is the recurring half of a razor-and-blades model and is usually the one
product already on subscription. Its *absence* from the plan list is a red flag rather
than an opportunity — check whether the merchant removed it deliberately.

`supplement_consumable` is replenishable for subscription purposes. Whether it may be
*advertised or sold in social commerce* is an entirely separate question with different
rules; do not conflate the two.

## Not replenishable

| Class | Terms |
|---|---|
| `durable` | handle, holder, travel case, carrying case, stand, dock, magnetic holder, applicator, device, tool, brush, sponge, buffer, mitt, bag, pouch |
| `set_or_bundle` | starter kit, gift set, value set, discovery set, sample set, full routine, kit, set, bundle, trio, duo, collection, starter, routine, regimen |

**Durables** are bought once and occasionally replaced. Never a subscription unit on
their own — but a durable is very often the *entry device* whose refill should be. A
durable with no matching refill product anywhere in the catalog is its own finding: an
entry purchase that can never generate a second order.

**Sets and bundles** are acquisition units, not replenishment units. Putting one on a
schedule re-ships the durables inside it that the customer already owns, which is how a
subscription earns a cancellation rather than a renewal. Split it instead: subscribe the
consumables it contains, sell the bundle once.

## Precedence

Structure beats text. `is_bundle`, `bundle`, `product_bundles` and `bundle_config` are
authoritative when populated, and no wording overrides them.

Where structure is absent, score matches rather than ordering the classes by hand:

```
score = (term matched in the TITLE ? 1000 : 0) + length of the matched term
```

Hand-ordering fails in both directions at once, and it did: an earlier version ranked
`set_or_bundle` above every consumable class, which classified both of a merchant's wax
kits as bundles — hiding real recurring revenue — while a genuine multi-product set
called "Smooth Operator", carrying no bundle word at all, fell through to `treatment` and
would have been offered as a subscription.

## When to refuse

If nothing in the **title** decided the class, and either two or more replenishable
classes matched or a bundle term appeared anywhere, return **NEEDS REVIEW**. Do not place
it in the gap and do not silently exclude it — name it and let a human rule on it. That
combination is precisely how an unflagged multi-product set reads.
