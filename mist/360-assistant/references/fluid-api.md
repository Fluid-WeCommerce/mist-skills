# API reference — the only calls the assistant may make

Every logical tool in SKILL.md maps to exactly one request below. If a request you want isn't here,
the answer is **R11 handoff**, not a guessed path. Shapes come from the published Fluid OpenAPI
specs; items marked **verified** were additionally confirmed against a live store during a real
build.

## Hosts — get this right first

| Surface | Host |
|---|---|
| Storefront reads (products, collections, pages, posts) | `https://{shop}.fluid.app` — **host-scoped: the subdomain *is* the storefront selector** |
| Cart, checkout, account | `https://api.fluid.app` |
| The cart/checkout link itself | `https://checkout.<apex>` — **not** the storefront host |

**Verified:** calling a storefront read on `api.fluid.app` returns
`404 {"error":{"message":"Storefront not found"}}`. This is the single most common wiring bug.

**Derive host pairing, never configure it.** Take the apex off `STOREFRONT_HOST` and build the API
and checkout hosts from it:

| storefront apex | API | checkout |
|---|---|---|
| `fluid.app` | `api.fluid.app` | `checkout.fluid.app` |
| `<other apex>` | `api.<apex>` | `checkout.<apex>` |

Three separately-configured hosts can drift; a derived pair cannot. This is what stops a staging
storefront ever emitting a production checkout link, or vice versa. **Add the checkout host to the
outbound URL allowlist** — it is not the storefront host, so a naive allowlist will silently drop
the one link that matters.

---

## Storefront reads — PUBLIC, no token

```
GET https://{shop}.fluid.app/api/v202604/products
      ?q=&country=&lang=&page[limit]=          # max 100
      &filter[availability]=in_stock           # always send for shopper-facing search
      &filter[collection_ids]=                 # comma-separated
GET https://{shop}.fluid.app/api/v202604/products/{slug}?country=&lang=
GET https://{shop}.fluid.app/api/v202604/collections/{slug}/products?country=&lang=&page[limit]=
GET https://{shop}.fluid.app/api/v202604/pages?q=        ·  /pages/{slug}
GET https://{shop}.fluid.app/api/v202604/posts?q=        ·  /posts/{slug}
GET https://{shop}.fluid.app/api/v202604/enrollment-packs
```

**Fields the assistant may quote** (trim everything else before it reaches model context):
`id · title · slug · canonical_url · status · in_stock · is_bundle · has_subscription_plans ·
pricing.display_price · pricing.price · pricing.currency_code · pricing.compare_at ·
default_variant.id · image_url · images.* · description.body · seo.description`

Behaviour that matters:

- **Pricing is country-relative.** `country` selects which per-country variant price and currency
  render. Omit it and you get the company default — a wrong currency in the answer.
- **Show-by-slug is permissive.** Draft, scheduled and inactive products still resolve by direct
  slug (they render `noindex`). Only archived/discarded 404. **So check `status` and `in_stock`
  yourself** — a `200` is not proof a product is sellable.
- 🔴 **Product search is TITLE-ONLY.** It does not read descriptions. Verified live: a query for a
  distinctive word from a product's own description returns **zero results** on a catalogue that
  literally contains it. This is why problem-matching builds its own corpus from detail fetches
  (`needs-and-safety.md`), and it is the first thing to re-verify at a new company.
- 🔴 **It is worse than title-only: an EXACT SUBSTRING of a live product's title can return zero.**
  Verified on a second company — a published, in-stock product whose title contained the searched
  phrase word for word did not come back. **A zero result therefore proves nothing about whether the
  product exists.** Never let the assistant say "we don't sell that" on the strength of an empty
  search (SKILL.md R2).
- **`q` relevance is also unreliable** for named products, not just categories — see
  `catalog-profiling.md`. Resolve through lanes first; search is the fallback, and suppression still
  applies to its results.
- **Result order is frequently descending product id**, not relevance — so the top hit is the newest
  record, which on a sandboxed or migrated catalogue is usually test data.
- **SLUG TRAP:** create/update endpoints ignore a `slug` you send and generate one from the title, so
  a URL composed from your own slug will 404. Quote `canonical_url` from the response.

### 🔴 Bundles: two kinds, and only one of them is cartable

Every product read carries `is_bundle` (boolean) and `bundle_groups[]`.

- **`is_bundle: false`** → an ordinary product, **even if the word "Bundle" is in its title**. Cart
  it normally.
- **`is_bundle: true`** → assembled from `bundle_groups`, and its price is the *configured bundle
  price*, not a variant price.

Each group carries `id · title · description · group_type · min_selections · max_selections ·
selection_type · allow_subscriptions · force_subscriptions · sort_order · pricing_config`, plus
`bundle_group_items[]` (each with `bundled_variant_id` and `quantity`).

**`group_type` is the fast discriminator.** Observed values:

| `group_type` | Meaning | Leaves a choice? |
|---|---|---|
| `included` | Contents come as standard. `min_selections`/`max_selections` are `null`. | No |
| `customizable` | The customer picks. Carries `min_selections`, `max_selections`, `selection_type: "exact"`. | **Yes** |

**Verified live** on a real multi-group bundle: one `included` group of three fixed items, plus a
`customizable` group of "pick exactly 1 of 2", plus another of "pick exactly 3 of 13". **One
customizable group is enough to make the whole product a redirect.** Treat an unrecognised
`group_type` as customizable.

**Treat a bundle as configurable — and therefore not cartable — unless every group provably leaves
no choice.** A group leaves a choice when `max_selections` exceeds `min_selections`, when
`selection_type` implies picking, when `bundle_group_items` holds more options than the group takes,
when subscriptions are selectable on it, or **when you can't tell because the fields are null or
unfamiliar. Unknown means redirect.**

This isn't stylistic. Adding a configurable bundle to a cart means sending `bundled_items[]` — one
`{ variant_id, quantity, product_bundle_group_id }` per selection — which is the assistant choosing
the contents of someone's basket for them. Exactly the guess SKILL.md §3.3 forbids, and §3.9 is the
resulting behaviour.

**`filter[bundle]=true` is the cheap way to enumerate real bundle products.** **Verified:** it
returned **zero** on a catalogue whose "Bundles" collection held three products — all `is_bundle:
false`, each a single SKU with its own default variant — and on a different company it returned
almost the entire catalogue. The collection name is marketing; the flag is structural.

Three more things a bundle does that will bite, all **verified live on one product**:

- 🔴 **A bundle's master variant can be priced `0.0` in every country** while the product-level
  `pricing` shows a real figure. Carting the default variant therefore produces a **$0 cart with a
  normal-looking link** — the $0 guard below is not theoretical, it is the thing standing between you
  and a free order.
- **`pricing_config` on a group can disagree with the product's own price** (product `$10.00`, group
  `country_pricing[US].price` `15`). When the price is ambiguous, that is one more reason to send them
  to the page rather than quote a number.
- **`Untitled Variant` is another placeholder title**, alongside `Default Title`. Strip both — never
  read a placeholder back as if the customer chose it.

Unrelated to bundles but the same family: **`in_stock: true` is not a promise of inventory.** Seen
live with `track_quantity: false` and every warehouse level at zero. It means "purchasable", not "on a
shelf" — so never turn it into a delivery or availability claim.
- **Empty page bodies are common** on imported content. Blank body → treat as not-found.

---

## Cart — PUBLIC, no bearer token

Two surfaces can mint a cart. **Drive any one cart through a single surface** — do not mix.

**A. Checkout surface** (`checkout-v2026-04`, the documented spec)

```
POST https://api.fluid.app/api/checkout/v2026-04/carts
{ "fluid_shop": "{shop}",        // subdomain only, NOT the host
  "country_code": "US",          // required
  "items": [ { "variant_id": 0, "quantity": 1 } ],       // optional seed
  "attribution": { "share_guid": "…" } }

POST   …/carts/{cart_token}/items      { "items": [ … ] }   // quantity 0 removes a line
GET    …/carts/{cart_token}
POST   …/carts/{cart_token}/discount   { "discount_code": "…" }   // NOT idempotent
```

**B. Public commerce surface** (`POST /api/public/v2025-06/commerce/carts`) — **verified** live:
unauthenticated, `origin` header set to the storefront, ~300 ms, builds regular, subscription and
enrollment carts in one call and returns the same `meta.checkout_url`. A reference build used this
one. **Verified:** a **pack-only enrollment cart works** — send the pack with an empty `items`
array and the cart comes back typed as an enrollment.

Both return the cart plus **`meta.checkout_url`** — the link you hand over. It stays valid for the
life of the cart. Store the cart token in the server-side session.

### Guards to apply to every cart response, before handing over the link

Each of these fails **silently** — HTTP 200, normal-looking payload — which is exactly why they
need asserting:

| Guard | Why |
|---|---|
| **$0 total** | A supported country with **no local price** for the variant returns 200 with `price 0.0` and a perfectly normal link. Refuse it; offer a priced alternate. |
| **Wrong checkout host** | Refuse a link whose host isn't the derived checkout host, so a staging link can never surface in production. |
| **Placeholder variant name** | Single-variant products carry a placeholder title (`Default Title`, `Default Variant`, `Untitled Variant`). **The documented set is not exhaustive** — one company's variants were literally titled `a`, `b`, `c`. Derive the list per company (`catalog-profiling.md`) and strip them at source, so one is never read back as if the customer chose it. |
| **`pricing: null`** | Distinct from `$0`, and it means the product cannot be sold at all. Never quote it, never offer it, never count it when answering "cheapest". |
| **Attribution shape** | **Verified:** only top-level `attribution: { fluid_rep_id }` persists. Every other spelling returns 200 with `attribution: null`. Assert it; warn on miss. |
| **Subscription saving** | **Verified:** a subscribe-and-save plan can be configured at **0.00**. Read the live number and let the copy flip automatically — never hardcode "you save". |

**Options within one product are frequently different prices.** Changing the selected option is
therefore a cart *rebuild*, not a label swap: create the cart again and quote the figure the new
response returns. Carrying the previous total across a swap misquotes the order. Persist the
quantity and the cart kind (one-off / subscription / membership) so the rebuild cannot silently
change either.

🔴 **A price belongs to the object you read it from.** The same product can be represented in four
places with four different numbers — verified live on one drink: the **product** said `$3.39`, its
own **default variant** said `$0.55`, a row for it nested in a **bundle group** said something else
again, and a **completed order** said `$0.50`. Lifting the nested figure and calling it the product
price shipped a wrong "cheapest" answer. Read the price off the product, or off the cart. Never out
of `bundle_group_items[]`, an order line, or a plan.

**Other price fields that lie:**

- **`buyable: true` is not a price check.** It is set even on `active: false` rows priced `0.0`.
- **A per-country row can hold a figure in the wrong currency.** Verified: a JP row carrying `9.29`
  rendered as `¥9 (JPY)` — a USD number displayed in yen. **Quote `display_price` verbatim and never
  do FX arithmetic.**
- **A variant's subscription price can exceed its one-off price** while the plan reports a discount.
  Read the plan, and if the two disagree, don't claim a saving.
- **Subscription plans on one product can disagree with each other** — one at 10% off, another at
  exactly zero. Read the specific plan you're about to name.
- **Duplicated option axes:** a variant can return the same option twice, in both orders
  (size/soda-type, then soda-type/size). Read the variant `title` rather than reassembling options.

**Money is quoted, never computed.** Especially for enrollment: a joining fee is charged *on top
of* pack contents, so keep fee / contents / total as three separate strings taken verbatim from the
cart. **Verified:** the enrollment-pack *list* endpoint carries no formatted price block at all, so
the cart is the only authoritative source of a currency string.

### 🔴 There are TWO carts, and only one of them is the shopper's

The cart built through this API is a **separate record**, reachable only by its own checkout link.
The shopper's storefront cart — the one the site's badge counts — is **untouched**. Telling them
"I've popped one in your cart" is a falsehood they can see.

To actually add to their real cart you must go through the storefront SDK, which lives on the
storefront page, not in the chat iframe. So a cross-origin `postMessage` bridge is required:

```
panel  --postMessage 'add_to_cart'-->  loader (on the storefront, owns the SDK)
       <--postMessage 'cart_result'--  SDK.addCartItems([...])
```

Three details, each of which fails silently otherwise:

- 🔴 **Resolve success from the SDK's success EVENT, not the promise.** `addCartItems` resolves
  `undefined` on failure by design, so awaiting it proves nothing. A documented no-op emits no event
  at all — hence a timeout that reports failure rather than spinning forever.
- **Use the array form** for a multi-line basket: one call, one success event. Line-by-line makes
  partial failure indistinguishable from success.
- **The loader passes its own origin** so the panel targets `postMessage` exactly, never a wildcard.

**A failure never renders "in your cart"** — fall back to the checkout link.

**Cap the basket** (a limit on lines, and per line). A runaway chat basket is far more likely a
misparse than a real order, and it lands on someone's card.

### Not your job

`…/complete`, `…/shipping`, `…/address`, `…/points`, and anything under the payment surfaces belong
to the hosted checkout page. The assistant's involvement ends at the cart, which is also why the
app has **no PCI surface**.

---

## Customer account

Reading a customer's orders or subscriptions requires a **verified customer session**. Two
implications the prompt cannot fix:

1. **Without one, the assistant cannot see any account data** and must signpost instead (SKILL.md
   §2, R6). Stating an order status you cannot read is fabrication.
2. **A user id passed into an embed is a lookup hint, never proof of identity.** Some embed hosts
   append an identifier to the frame URL. Trusting it would let anyone read anyone's orders. Only a
   cryptographically verified session counts.
3. **Not every hosted account surface is linkable.** One can return `200` to a logged-out visitor
   and render an empty shell with no sign-in form at all — see `platform-limits.md`. Verify a
   destination serves a login *before* the assistant is ever allowed to emit it.

Where a verified session exists, the customer-scoped reads and subscription actions are IDOR-safe —
scoped to the token's own customer — and each mutation should be followed by a re-read so the
assistant reports the **new** state from the response rather than its own intent.

---

## Explicitly out of bounds at runtime

- **Any admin path.** Those are staff surfaces with a company token. The assistant is a *customer*
  surface, and **no admin token should exist in its runtime at all** — an admin token turns every
  prompt-injection attempt into a real risk.
  **Setup is different:** Part A profiling legitimately reads admin catalogue endpoints with an
  operator's token, once, offline, in the setup chat — never from the chat path.
- Order mutation, refunds, cancellations, fulfilment → R11.
- Creating customers or reps.
- Payment tokenisation of any kind.
