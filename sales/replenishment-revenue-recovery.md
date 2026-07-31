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
| 2 | **$0.00 purchasable product** | `price: "0.0"`, `buyable: true`, `status: published` — the PDP is live and its add-to-cart works, so anyone can order it for free today. Not a data smell; an open till. Treat as the most urgent finding. |
| 3 | **Device with no replacement path** | Nothing in the data links the device to its consumable, so the owner cannot find the refill without already knowing its name. Replenishment depends on the customer doing your merchandising for you. |
| 4 | **Orphaned consumable** | A refill whose device line has no device in the catalog. Either dead inventory or a missing device — both worth knowing, and easy to miss because the product itself looks healthy. |
| 5 | **Replenishment cadence undeclared** | The copy states a replacement interval ("every three months", "six months of clean air") but nothing in the data captures it, so no reminder, no subscription default, and no lifecycle email can read it. |

---

## Step 1 — Read the catalog

Enumerate every product:

```
GET /api/v202604/company/products?page[limit]=100
```

Follow `meta.pagination.next_cursor` until exhausted. (If `fluid_catalog_index`
exists in this build, it does the same enumeration and writes a local evidence
file — prefer it.)

The list payload omits the fields this audit turns on, so you also need each
product's full record:

```
GET /api/company/v1/products/{id}
```

**Do not fetch details for the whole catalog.** One detail call per product is
fine at 13 products and abusive at 300. From the list payload, shortlist:
every product whose title matches subscription/refill/filter/pod/cartridge
language, every product with a zero or missing price, and every product in a
consumable-looking category or collection. Fetch details for the shortlist plus
all devices. Say how many you fetched.

The fields that matter: `title`, `sku` (on each variant, not the product),
`price`, `has_subscription_plans`, `product_subscription_plans`,
`product_bundles`, `metafields`, `metafields_collection`, `tags`, `category`,
`collections`, `description`, and each variant's
`variant_countries[].{price, buyable}`.

> **Read trap — metafields live in two places.** On
> `GET /api/company/v1/products/{id}`, existing metafields come back in
> **`metafields_collection`** (as `{key, value}` pairs) while **`metafields` is
> an empty array**. The v202604 PATCH *response* returns them under
> `metafields`. Read both keys and merge, or the audit will report its own
> successful writes as missing and rewrite them on every run.

Never infer any of these from the list response. `has_subscription_plans` in
particular is absent from list payloads, and assuming `true` is exactly the
mistake this skill exists to catch.

## Step 2 — Classify every product

Sort the shortlist into **devices** and **consumables**, using in order:

1. **Category / collection membership** — most reliable when the import created
   them (a "Filters" or "Accessories" category). Note that `category` is
   frequently `null` on bundle and option products; treat null as unknown and
   fall through, never as "device".
2. **SKU model tokens** — see step 3; the prefix that identifies a device line
   usually classifies the product too.
3. **Title tokens** — `filter`, `refill`, `cartridge`, `pod`, `replacement`,
   `pack`, `subscription`, `2-pack`.

**Price band is a weak last resort, not a primary signal.** Broken subscription
SKUs sit at $0.00, *below* the consumable band, and bundle products sit in the
device band with no category. Ranking by price alone misclassifies exactly the
products this audit exists to find.

Show the classification as a table and ask the user to confirm it before
changing anything. A misclassified device becomes a bad relationship write, and
relationship writes are the part of this skill that touches live merchandising.

## Step 3 — Build the compatibility map

Compatibility lives in the **variant SKU**, not the product record. Read
`variants[].sku`.

Derive a **device-line prefix** for every product — the leading token of the SKU
before the first separator (`SQ2PH-US` → `SQ`, `MN1-PHFL-US` → `MN`,
`MH1-NF1-PF3` → `MH`). Then:

- A consumable fits every device sharing its prefix.
- Collect the set of prefixes that have **at least one device**. Any consumable
  whose prefix is not in that set is an **orphan** (failure 4) — it serves a
  device this catalog does not sell. This is the check that finds dead
  inventory, and nothing else in the audit surfaces it.

Corroborate every pairing against a second source before writing it — title
model tokens ("Air Mini / Mini+ PECO-Filter" names its devices), description
text, or a `crawl` of the source PDP, which usually carries an explicit
"compatible with" block.

Produce an explicit device → consumables table with the evidence per row and
show it to the user. **Do not guess a pairing.** A wrong one ships the customer a
part that does not fit their machine — a return, a support ticket, and the lost
replenishment relationship. An unresolved pairing is reported as unresolved.

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

All product writes go through `PATCH /api/v202604/company/products/{id}`. Four
things about that endpoint decide whether this step is safe:

> **`title` is required on every PATCH.** The endpoint documents PATCH semantics
> ("only keys present in the payload are updated") but rejects a body without
> `title` — `422 {"product":{"title":["is missing"]}}`. Send the product's
> **current title, byte-for-byte**, alongside whatever you are changing.
>
> **Resending an unchanged title is slug-safe; changing one is not.** Slugs
> regenerate from the title, and imported catalogs are full of products whose
> slug does not derive from their current title (`mini-ala-carte-live` for "Air
> Mini / Mini+ PECO-HEPA Tri-Power Filter"). Resending the identical title
> leaves the slug alone even when `custom_slug` is `false` — verified. Altering
> the title in the same call would move the slug and break the live URL, the
> theme's links, and any page that references it. **Never change a title from
> inside this skill.**
>
> **Every successful PATCH triggers a fresh Lighthouse + compliance scan.** A
> bulk write across a large catalog kicks off one scan per call. Batch by
> product (all of a product's metafields in a single PATCH), and warn the user
> before a run that touches dozens.
>
> **Verify on a low-risk product first.** Pick one whose slug already derives
> from its title, confirm the write lands and the slug holds, then proceed.

### Subscription plans — the guided path

`product_subscription_plans_attributes` is a **join row**, not a plan:

```jsonc
{ "product": {
  "title": "<exact current title>",
  "product_subscription_plans_attributes": [
    { "subscription_plan_id": 4410, "default": true, "active": true }
  ]
}}
```

It attaches a plan that **already exists**. No endpoint in any published Fluid
spec creates one — `/api/company/v1/subscription_plans` 404s, and
`/api/checkout/v2026-04/subscriptions/*` manages a customer's subscription
*instances*, not the store's plan catalog. Plans are created in Fluid admin.

That does **not** mean stopping at "found, not repairable." Work the ladder.

**(a) Discover what plans exist.** There is no plan index, but plans are
readable where they're referenced. Union these two:

1. **Attached to any product** — `product_subscription_plans[]` and
   `variants[].variant_countries[].subscription_plans[]` on every product you
   already fetched in step 1. A store with working subscriptions elsewhere in
   the catalog will surface its plans here.
2. **On existing subscriptions** — `GET /api/checkout/v2026-04/subscriptions`
   returns each subscription with a nested `subscription_plan` object carrying
   `id`, `name`, `billing_interval`, `billing_interval_unit`,
   `billing_frequency_in_words`, `price_adjustment_type`,
   `price_adjustment_amount`, and `company_default`. Note this endpoint is
   IDOR-scoped to the authenticated customer, so it may return nothing under an
   admin token — treat it as a bonus source, not the primary one, and never
   read an empty response as proof the store has no plans.

Say explicitly that this union is what's *visible*, not a guaranteed-complete
plan list, and that admin is the authority.

**(b) If plans exist — ask which one, per SKU.** Open a `steps` panel with one
`single_select` per broken subscription SKU, options being the discovered plans
labelled by `billing_frequency_in_words` (e.g. "Every 3 months — Subscribe &
Save 15%"). Pre-select the plan whose `billing_interval` matches that product's
`replacement_interval_days` when one exists; that mapping is the whole reason
step 5 captures cadence. Offer a "none of these" option that routes to (c).

**(c) If no plan fits — derive the spec and walk the user through admin.** Do
not send them away with "create a subscription plan." Collect the missing
decisions in a `steps` panel — billing cadence, subscribe-and-save discount,
and the real price for any $0.00 SKU — seeding each option from evidence you
already hold:

- **Cadence** from `replacement_interval_days`, or from the source PDP copy.
- **Discount** from the source site's own subscribe-and-save language, quoted
  back ("the source homepage advertises up to 40%").
- **Price** from the equivalent one-time consumable's current price. Never
  invent one; offer the à-la-carte figure as a default and let the user confirm.

Then emit a filled-in spec they can type straight into admin — one block per
plan, with name, billing interval, shipping interval, price-adjustment type and
amount — and name the exact screen (Fluid admin → Products → Subscription
Plans). State that the skill will finish the job once the plan exists.

**(d) Resume and attach.** After the user says the plan is created, re-run the
discovery in (a), match the new plan by name and interval, attach it with the
join-row payload above, and verify per step 7. Only now is failure class 1
repaired.

If the user declines or defers, report class 1 as **found, awaiting a plan** —
with the derived spec attached to the report so the work isn't lost. Never
claim the subscription is fixed while `has_subscription_plans` is still false.

### Pricing — a $0.00 live product is an open till

Handle this **before** the subscription work. Do not fold it into a generic
"confirm pricing" question. When a product has `price: "0.0"`, an `active: true`
country row, and `status: published`, it is **orderable at zero cost right now**.

**Prove it, then warn, then ask.** Fetch the product's `canonical_url` and
confirm the page returns 200, displays the zero price, and renders an
add-to-cart control. Open the report with the count, the product names, the
affected countries, and one plain sentence: *these can be checked out for $0.00
until this changes.* This outranks every other finding — a missing plan forgoes
future revenue; a live $0.00 SKU gives away stock today.

**Then ask how to handle it, and do not presume the answer is "set a price."**
For a placeholder an import invented, pulling it out of the storefront is usually
right and is instantly reversible. Offer these in a `steps` panel — one select
per product, or one for all when they're uniform:

| Option | The write | When it's right |
|---|---|---|
| **Unpublish** | `{ product: { title, status: "draft" } }` | Placeholder never meant to sell. Stops exposure immediately, fully reversible. `status` accepts `draft`, `scheduled`, `published`, `archived`. |
| **Archive** | `{ product: { title, status: "archived" } }` | The SKU is genuinely dead and should leave the working catalog. |
| **Block checkout, keep the page** | `variants_attributes: [{ id, variant_countries_attributes: [{ id, active: false }] }]` | Preserve the URL for SEO or a "coming soon" state while making it unbuyable. Per country — `buyable` is derived from the country row's `active`, not writable directly. |
| **Set a real price** | `variants_attributes: [{ id, variant_countries_attributes: [{ id, price: "174.99" }] }]` | Genuinely for sale; the price was lost in migration. |
| **Leave it, knowingly** | nothing | The user accepts the risk. Record the acknowledgement verbatim in the report — never leave a live $0.00 SKU silently. |

Prefer that nested write on `PATCH /api/v202604/company/products/{id}` (still
sending `title`) over `PUT /api/company/v1/variants/{id}`: it's the documented
path and it addresses per-country rows, which is where checkout reads the price.

Never invent a price. Offer the equivalent one-time consumable's current price as
the default, say where it came from, and make the user confirm. If a subscription
SKU has **no à-la-carte twin** in the catalog, say so and ask for that one figure
instead of guessing from a sibling.

**Check every country.** A product priced correctly in the default market can
still be `0.0` with an active row in another. Fix every affected row or none — a
half-fixed product is still an open till in one market.

**A plan does not fix a price.** Attaching a subscription plan to a SKU that is
still $0.00 leaves it free: `price_adjustment_amount` applies to a base of zero.
Classes 1 and 2 must both be resolved on the same product, and the report must
say so, or someone will read "subscription attached" as "revenue restored."

`subscription_only` appears on the variant read payload but is **not** in the
documented variant write contract. If the user wants a SKU to exist purely as a
recurring purchase, put that toggle in the admin spec rather than attempting it
over the API.

**Compatibility.** Prefer metafields — queryable from Liquid, survive re-import,
no merchandising side effects:

```jsonc
{ "product": {
  "title": "<exact current title>",
  "metafields_attributes": [
    { "namespace": "custom", "key": "compatible_consumable_ids",
      "value": "86816,86819", "value_type": "single_line_text_field",
      "description": "Product IDs of consumables that fit this device." }
  ]
}}
```

`namespace`, `key`, `value`, and `value_type` are all required;
`single_line_text_field` is the safe `value_type` for ids, lists, and numbers.
Omitting `id` creates a new entry, so **read the existing metafields first**
(both keys — see step 1) and only write the ones that are genuinely missing or
changed, or repeat runs will pile up duplicates.

Write the relationship **in both directions** — `compatible_consumable_ids` on
the device, `fits_device_ids` on the consumable. Also write the derived
`device_line` on both, and `orphaned_consumable` on any orphan, so the next run
and the theme can both read the classification instead of re-deriving it.

A per-device collection ("Filters for Air Mini+") is a fine second choice when
the merchant wants a browsable page. Reach for bundles only where the company
genuinely sells device + consumable together, never as a compatibility hack.

**Cadence.** Where the copy states an interval, capture it as
`replacement_interval_days` so subscriptions, reminders, and lifecycle email
read one number instead of re-parsing prose.

## Step 6 — Surface it on the storefront

Data nobody sees earns nothing. In the theme, add to each device PDP a
**"Keep it running"** rail listing compatible consumables, and to each consumable
PDP a **"Fits these devices"** line.

Build both from the metafields written in step 5 — never from a hardcoded product
list, which silently rots the next time the catalog changes. Follow the theme's
existing section conventions, put every user-facing string through `| t` with
keys in `locales/*.json`, and keep `data-fluid-add-to-cart` intact on any buy
button so attribution and cart behavior keep working.

If the theme lives in a different project from the one running this skill, hand
the rail off rather than editing across the boundary.

## Step 7 — Prove it

Verification is re-reading live state, not asserting success:

- Re-fetch every mutated product and confirm the field actually changed —
  reading **`metafields_collection`**, not `metafields`.
- Confirm every mutated product's `slug` and `canonical_url` are unchanged.
- For a price fix, re-fetch the **live PDP** and confirm the new figure renders.
  **Add a cache-busting query param** (`?v=recheck`) when you do: a crawl of a
  URL fetched earlier in the same session can return the pre-write page and make
  a successful fix look like a failure. Verified — a plain re-crawl showed
  `$0.00` while the API already reported `109.99`; the busted URL showed
  `$109.99`. The API is authoritative, but the rendered page is what the customer
  sees, so check both and never conclude from one stale read.
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
> no recurring revenue. Every device now has a compatible-consumable rail, so
> the second purchase has somewhere to happen.

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
  and consumable pages take heavy search traffic from owners who already own the
  device.
- **Variant-level country pricing** means a product priced correctly in the
  default country can still be $0.00 in a second market. Check
  `variant_countries` per country, not just the top-level `price`.
- **Re-imports overwrite.** Prefer metafields and collections over anything the
  next import will clobber, and re-run this audit after any catalog import.
