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
- **`q` relevance is unreliable** for both categories and named products — see
  `catalog-profiling.md`. Resolve through lanes first.
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
| **Placeholder variant name** | Single-variant products carry a placeholder title (e.g. `Default Title`). Strip it at source so it is never read back as if the customer chose it. |
| **Attribution shape** | **Verified:** only top-level `attribution: { fluid_rep_id }` persists. Every other spelling returns 200 with `attribution: null`. Assert it; warn on miss. |
| **Subscription saving** | **Verified:** a subscribe-and-save plan can be configured at **0.00**. Read the live number and let the copy flip automatically — never hardcode "you save". |

**Options within one product are frequently different prices.** Changing the selected option is
therefore a cart *rebuild*, not a label swap: create the cart again and quote the figure the new
response returns. Carrying the previous total across a swap misquotes the order. Persist the
quantity and the cart kind (one-off / subscription / membership) so the rebuild cannot silently
change either.

**Money is quoted, never computed.** Especially for enrollment: a joining fee is charged *on top
of* pack contents, so keep fee / contents / total as three separate strings taken verbatim from the
cart. **Verified:** the enrollment-pack *list* endpoint carries no formatted price block at all, so
the cart is the only authoritative source of a currency string.

### Not your job

`…/complete`, `…/shipping`, `…/address`, `…/points`, and anything under the payment surfaces belong
to the hosted checkout page. The assistant's involvement ends at the link, which is also why the
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
