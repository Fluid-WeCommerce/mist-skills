---
name: Replenishment Revenue Recovery
description: Audit and repair a durable-goods catalog's consumables engine — subscription SKUs with no plan attached, $0.00 placeholders, and devices with no purchasable replacement path.
icon: refresh-cw
---

# Goal

Durable-goods brands make their money twice: once on the device, then for years
on the consumable. Filters, pods, blades, cartridges, refills, strips.

The device catalog is small and gets all the attention. The consumable catalog
is larger, duller, and is where the recurring revenue actually lives — so it is
reliably the half that arrives broken after a migration or an import. The
storefront looks finished because the hero products look finished.

This skill finds the breaks and repairs them.

**Run it whenever a catalog contains devices plus their consumables** — after an
import, after a platform migration, or as a standalone revenue audit. It is
read-only until it asks permission to write.

---

## What "broken" means here

Five specific failures, in descending order of revenue impact. Each one is
individually invisible on a storefront that otherwise renders perfectly.

| # | Failure | Why it costs money |
|---|---------|--------------------|
| 1 | **Subscription SKU with no plan attached** | Product titled "…Subscription" with `has_subscription_plans: false`. The customer subscribes to nothing. No recurring revenue is created, ever. |
| 2 | **$0.00 purchasable product** | `price: "0.0"` with `buyable: true`. Free consumables — direct margin leak, and it reads as a pricing error to the customer. |
| 3 | **Device with no replacement path** | Nothing in the data links the device to its consumable, so the owner cannot find the refill without already knowing its name. Replenishment depends on the customer doing your merchandising for you. |
| 4 | **Orphaned consumable** | A refill that maps to no device in the catalog. Either dead inventory or a missing device — both worth knowing. |
| 5 | **Replenishment cadence undeclared** | The copy states a replacement interval ("every three months", "six months of clean air") but nothing in the data captures it, so no reminder, no subscription default, and no lifecycle email can read it. |

---

## Step 1 — Read the catalog

Enumerate every product:

```
GET /api/v202604/company/products?page[limit]=100
```

Follow `meta.pagination.next_cursor` until exhausted. (If `fluid_catalog_index`
is available in this build, it does the same enumeration and writes a local
evidence file — prefer it.)

The list payload omits the fields this audit turns on, so read each product's
full record:

```
GET /api/company/v1/products/{id}
```

The fields that matter: `title`, `price`, `has_subscription_plans`,
`product_subscription_plans`, `product_bundles`, `metafields`, `tags`,
`category`, `collections`, `description`, and each variant's
`variant_countries[].{price, buyable}`.

Do not infer any of these from the list response. `has_subscription_plans` in
particular is absent from list payloads, and assuming `true` is exactly the
mistake this skill exists to catch.

## Step 2 — Classify every product

Sort the catalog into **devices** and **consumables**, using in order:

1. **Category / collection membership** — most reliable when the import created
   them (a "Filters" or "Accessories" category).
2. **Price band** — consumables cluster well below devices. Compute the catalog
   median; a product an order of magnitude below the device band is almost
   always a consumable.
3. **Title tokens** — `filter`, `refill`, `cartridge`, `pod`, `replacement`,
   `pack`, `subscription`, `2-pack`.

Show the classification as a table and ask the user to confirm it before
changing anything. A misclassified device becomes a bad relationship write, and
relationship writes are the part of this skill that touches live merchandising.

## Step 3 — Build the compatibility map

For each device, determine which consumables fit it. Evidence, best first:

- **SKU structure.** Device and consumable SKUs usually share a prefix or model
  token (`MN1-…` / `MN2-…` for one model line, `SQ1-…` / `SQ2-…` for another).
  Strongest signal, and machine-checkable.
- **Title model tokens.** "Air Mini / Mini+ PECO-Filter" names its devices.
- **Description text.** Often states compatibility outright.
- **The source website.** `crawl` the source PDP — most consumable pages carry an
  explicit "compatible with" block.

Produce an explicit device → consumables table with the evidence for each row and
show it to the user. **Do not guess a compatibility relationship.** A wrong one
ships the customer a part that does not fit their machine, which costs a return,
a support ticket, and the replenishment relationship you were trying to create.
An unresolved pairing is reported as unresolved.

## Step 4 — Report before you write

Present the findings as a table: every failure, the affected product, and the
revenue consequence in the client's own terms. Lead with the subscription and
$0.00 failures — they are unambiguous and they are money.

Then propose the repairs with `human_in_the_loop`, one suggestion per failure
class, using a deterministic id:

```
replenishment:{company}:{failure-class}
```

Catalog writes are merchandising changes on a live store. They get sign-off.

## Step 5 — Repair the approved items

**Subscription plans.** Attach a real plan to each subscription SKU. Confirm the
current subscription-plan write shape in the Fluid API docs before calling —
do not assume the body wrapper. Verify by re-reading the product and confirming
`has_subscription_plans` flipped to `true` and `product_subscription_plans` is
non-empty.

**Pricing.** A $0.00 buyable product is either mispriced or should not be
buyable. Ask which — never invent a price. Write with
`PUT /api/company/v1/variants/{id}` (PUT, not PATCH; body `{ variant: { … } }`)
so a single-field price change does not round-trip the whole product.

**Compatibility.** Express the device → consumable relationship in whatever the
company's catalog actually supports, in this order of preference:

1. **Metafields** on both sides (`compatible_with`, `fits_devices`) — queryable
   from Liquid, survives re-import, no merchandising side effects.
2. **A per-device collection** ("Filters for Air Mini+") — immediately usable as
   a PDP rail and browsable on its own.
3. **Bundles** — only where the company genuinely sells device + consumable
   together, not as a compatibility hack.

**Cadence.** Where the copy states a replacement interval, capture it as a
metafield (`replacement_interval_days`) so subscriptions, reminders, and
lifecycle email all read one number instead of re-parsing prose.

## Step 6 — Surface it on the storefront

Data nobody sees earns nothing. In the theme, add to each device PDP a
**"Keep it running"** rail listing compatible consumables, and to each consumable
PDP a **"Fits these devices"** line.

Build both from the relationship written in step 5 — never from a hardcoded
product list, which silently rots the next time the catalog changes. Follow the
theme's existing section conventions, put every user-facing string through `| t`
with keys in `locales/*.json`, and keep `data-fluid-add-to-cart` intact on any
buy button so attribution and cart behavior keep working.

## Step 7 — Prove it

Verification is re-reading live state, not asserting success:

- Re-fetch every mutated product and confirm the field actually changed.
- Load a device PDP and a consumable PDP in the preview; confirm both rails
  render with real products.
- `fluid theme lint --json` clean, plus the local server log and the browser
  console — a clean lint alongside a broken render is not a pass.

Close with a before/after table: failures found, failures fixed, failures left
open and why. Record the outcome against each approved suggestion with
`human_in_the_loop` in `record_outcome` mode.

---

## Reporting the value

The point is a number the executive already believes. Frame the result in their
model of the business, not in catalog terms:

> *N* devices had no purchasable replacement path. *M* subscription SKUs created
> no recurring revenue. Every device now has a compatible-consumable rail and a
> working subscription, so the second purchase has somewhere to happen.

If order history exists, quantify it: replenishment rate (customers with ≥2
orders where the later one contains a consumable), before and after. If the store
has no order history yet — a fresh migration — **say so plainly and report the
structural fix instead.** A fabricated projection is worse than an honest
structural finding, and an executive will test the number.

---

## Notes and traps

- **`has_subscription_plans: false` on a product named "Subscription Plan"** is
  the signature failure. Search titles for subscription language and check the
  flag on every match; the name is not the plan.
- **A $0.00 price with `buyable: true`** is live. Treat it as urgent.
- **Compatibility is a two-way relationship.** Writing it on the device only
  means the customer who lands on the filter still cannot tell what it fits —
  and consumable pages take heavy search traffic from owners who already have
  the device.
- **Variant-level country pricing** means a product priced correctly in the
  default country can still be $0.00 in a second market. Check
  `variant_countries` per country, not just the top-level `price`.
- **Re-imports overwrite.** Prefer metafields and collections over anything the
  next import will clobber, and re-run this audit after any catalog import.
