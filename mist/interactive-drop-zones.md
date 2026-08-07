---
name: Interactive Drop Zone Experiences
description: Build games and ambient interactive widgets into Fluid checkout and order-confirmation drop zones — placement, install-time zone registration, tenant-safe token verification, and the rendering traps that only appear inside the embed.
icon: gamepad-2
---

# Goal

A drop zone is a short, fixed-height iframe that Fluid mounts inside its own
checkout and order-confirmation pages. You declare the height in pixels — think
a band of 180 to 360px. There is no fullscreen, no takeover, no scroll of your
own, and no way to grow when your content does not fit.

That constraint decides the whole design. What fits is a **one-thumb,
one-glance** experience: a single gesture repeated, or nothing to do at all. A
game with levels, a leaderboard, or a second screen does not fit and should not
be attempted here.

**Run this skill whenever you are asked to put anything interactive into a
checkout or order-confirmation drop zone** — a game, a quiz, a product matcher,
a reveal, an animation. It covers placement, install-time registration,
tenant-safe identity, and the rendering failures that only appear once the code
is inside the iframe.

---

## The placement rule, before anything else

**Games belong on `order_confirmation`. Never in checkout.**

The buyer on the confirmation page has already paid. Their dwell time costs you
nothing, and it is the highest-intent moment you will ever get for a consumable
or subscription cross-sell — they just bought the device, and you are the only
thing on the page.

Checkout is the buyer's critical path. Every millisecond of load and every
eyeball you pull off the payment fields is measured in abandoned carts. A
checkout drop zone may therefore be **ambient only**:

- no input handlers, and `pointer-events: none` on the whole surface
- no cart mutation, no writes, no navigation
- tight timeouts on anything upstream
- on any failure, render a **zero-height band** — not a broken box, not an
  error message, not a spinner next to the card fields

If you are asked to put a minigame in checkout, stop and re-place it on
`order_confirmation`. Say why. Do not build it and note the concern afterward.

### The slot catalog, and the column-background rule

Checkout is two columns with different background colours. Your embed must paint
the colour of the column it lands in, or it reads as bolted-on regardless of how
good the content is.

| Page | Slot | Column background |
|------|------|-------------------|
| checkout | `above_order_items`, `below_order_items`, `below_discount_code`, `below_total` | LEFT order summary — `#f9fafb` |
| checkout | `above_fast_checkout`, `below_contact`, `below_shipping_address`, `below_shipping_method`, `below_payment_method`, `below_terms` | RIGHT form column — `#ffffff` |
| order_confirmation | `above_order_details`, `below_order_details`, `below_total` | — |

`product_detail`, `order_detail` and `customer_detail` are **admin** pages, not
storefront. A quiz on the customer-facing PDP is a theme section and a different
build entirely — do not reach for a drop zone to do it.

---

## What "broken" means here

Each of these ships silently. The deploy is green, the code is correct in
isolation, and the buyer sees something wrong.

| # | Failure | What it costs |
|---|---------|---------------|
| 1 | **Zones never register** — attach fired `droplet.installed` against a build with no secret; the webhook answered 500, the one-time exchange token burned, and nothing registered | The feature does not exist on the store. Recovery needs the irreversible reinstall path. |
| 2 | **Token accepted as identity** — `company_id` or the resource token trusted as proof of who is asking | Cross-tenant read. One buyer's order data served to another company's embed. |
| 3 | **Dark-mode slab** — the scaffold honours `prefers-color-scheme: dark` and paints `body #0a0a0a` | A black rectangle inside white checkout for every dark-mode buyer. Reads as a broken page during payment. |
| 4 | **Blank canvas** — `requestAnimationFrame` is suspended in a backgrounded document, so frame one never paints | An empty white box next to the card fields. |
| 5 | **Relative outbound link** — `href="/filters"` resolves against the app origin | 404 on the app domain. The buyer you just converted lands on nothing. |
| 6 | **Client-reported score** | The reward code is farmable in the console. Free product, at scale, on your margin. |
| 7 | **Invented reward code** | A code that fails at the register is worse than no code. You turned a gift into a complaint. |
| 8 | **CTA to a page that renders empty** | The link returns 200 and the destination says "No products in this collection yet". Highest-intent buyer, empty shelf. |
| 9 | **Unreviewed inline copy** in a regulated vertical | A disease claim or an unqualified stat on a checkout page. Regulatory exposure, not a bug. |

---

## Step 1 — Choose the slot and the interaction class

Decide two things, in this order, and write them down before any code:

1. **Which page.** Interactive → `order_confirmation`. Ambient → checkout. There
   is no third case.
2. **Which slot**, from the catalog above, and therefore **which background
   colour** the shell must paint.

Then declare the height in pixels and design to it. Pick a number in the 180 to
360 band and treat it as a hard ceiling: the iframe does not grow, and content
that overflows is content the buyer never sees. Nothing in the experience may
depend on scrolling inside the zone.

Confirm the placement with the user before building. Re-placing a game from
checkout to confirmation after it is built means redoing the identity layer,
because the token you are handed changes with the page.

## Step 2 — Register the zones at install, and prove it

Drop zones are registered **at install time**, from the scaffold's
`lib/config/droplet.config.ts`. A code push does not register them. Getting this
sequence wrong is the single most expensive mistake in this build, because the
recovery is irreversible.

Do it in this order, without reordering:

**1. Attach the Droplet.**

```
fluid mist attach-droplet <Name> <slug> --json
```

This is idempotent. If a Droplet with that slug already exists — including one
you created by hand — it adopts it and reports `surfaceCreated: false`. It will
not duplicate.

**2. Redeploy immediately.** Not "before you test". Immediately, as the next
action.

**3. Verify.** See below.

Two facts drive that ordering, and both cost real debugging time:

**The Mist-managed env vars only exist once the Droplet is attached.**
`FLUID_WEBHOOK_AUTH_TOKEN`, `FLUID_DROPLET_SECRET` and `FLUID_DROPLET_UUID` are
provisioned by attach, not by creating the Droplet record. `set_mist_env_var`
refuses them with `422 managed_var` — you cannot set them yourself, and trying is
a sign the attach has not happened yet.

**Attach installs immediately, so `droplet.installed` fires against the build
that is live right now.** If that build predates attach, it has no secret. Its
webhook handler answers `HTTP 500 "Webhook authentication not configured"`, the
delivery is dropped, and token exchange never runs. No zones register. The
exchange token is **one-time**, so retrying the webhook does not help — recovery
requires `repair_and_reinstall_droplet`, which is irreversible and therefore
needs a dry run plus explicit user approval before you call it.

The cheap probe for which state you are in — an unsigned POST to the deployed
app:

```
POST /api/webhooks
```

- `500` → the secret is missing from the running build. **Redeploy before
  anything installs.**
- `401 "Missing X-Fluid-Signature"` → the secret is live and the handler is
  reachable. Safe to proceed.

Run this probe before the attach if the app is already deployed, and again after
the redeploy.

**Patch `settings.height` into the create payload.** Checkout's drop-zone
component consumes `settings.height`, and the scaffold's `CreateDropZonePayload`
type omits it. If you do not patch the client, every zone registers at the
default height and your carefully-sized band is silently wrong.

**Verify side-effects, never a status field.** A `replacement_operations` record
sat at `state: queued`, `stage: revoking`, with `updated_at` frozen for over 45
minutes — while its delivery had already succeeded and both zones were
registered. The status field was simply wrong. Verify with:

```
GET /api/drop_zones
```

and by loading the actual rendered route. A record that says "queued" is not
evidence of anything.

**Repair a registered zone in place.** Use `PATCH /api/drop_zones/{uuid}` to
change a height, a slot, or a URL. Do not delete and recreate: the install's
`registeredIds` cleanup tracks the original uuid, and a recreated zone is
orphaned from it.

## Step 3 — Build the identity module before the experience

Fluid mounts your iframe as:

```
<embed_url>?token=<resource_token>&company_id=<id>
```

The token is the **cart** token on checkout zones and the **order** token on
`order_confirmation`. **Neither parameter is identity.** Both are attacker-supplied
strings in a URL.

Write one module that every page and every API route goes through. No route may
read `company_id` or `token` directly.

That module must:

- use `company_id` **only** to select which install row to load. Unknown or
  deactivated installation → refuse. It never grants anything by itself.
- resolve the token against the checkout API **using that install's stored
  credentials** — so the token is validated by a party that already knows the
  tenant.
- **cross-check the resolved resource back against the install**, so an attacker
  cannot pair someone else's order token with their own `company_id` and have
  both halves pass independently.
- refuse a payload with no verifiable company signal. Never fall back to "the
  only install" or "the first company".

Handling rules that are not optional:

- Tokens are **never** persisted, logged, or echoed into markup or error copy.
  When you need a stable per-order key, store an **HMAC salted per
  installation** — not the token.
- Every owned row carries the installation uuid **in the SQL predicate**. The
  repository layer should offer no lookup that omits it; a function that can be
  called without a tenant is a function that will be.

**Require negative tests.** These are the tests that catch the regression, so
write them with the feature, not after:

- no context → 401 or redirect
- wrong company for a valid token → 403
- two tenants cannot read each other's rows
- a production build cannot reach the dev fixture

**The dev fixture pattern:** `MIST_DEV=1` *plus* an explicit `?fixture=1`. The
fixture replaces the **identity source** only — never the verifier. Missing
context in dev is still a refusal. A fixture that short-circuits verification
teaches you nothing and eventually ships.

## Step 4 — Score on the server, reward from config

The client reports **raw events** — particles cleared, taps registered. It does
not report a score.

The server bounds those events against elapsed time, decides the score, and
decides any reward. Anything else is a reward code farmable from the browser
console, which is free product at whatever scale someone feels like. On replay,
keep the **best** score.

The reward itself comes from a merchant-configured env var (`*_REWARD_CODE`).
**Never invent a code string.** A fabricated code that fails at the register is a
worse customer experience than no code at all — you promised a discount and then
took it back in front of the payment form. When the var is unset, degrade to a
CTA with no code attached.

## Step 5 — Make outbound links absolute, and prove the destination renders

Your iframe is served from the app's own origin. A relative `href="/filters"`
resolves to `<mist-app>.wecommerce.dev/filters` and 404s.

Every buyer-facing link must be:

- an **absolute storefront URL**
- `target="_top"` — otherwise it opens inside your 200px band
- `rel="noopener"`

Derive the origin from the **verified resource**, in this order:

1. `order.primary_domain_hostname`
2. `meta.shop_url`
3. the install row's `fluid_shop`

Never hardcode it. A public droplet with a hardcoded shop sends every tenant's
buyers to the first company's storefront. Validate any env override before using
it: reject non-http schemes and protocol-relative paths. If none of the three
sources resolves, **render no button** — a dead CTA is worse than an absent one.

**Then verify the destination renders, not that it returns 200.** A collection
whose API product count was 3 rendered "No products in this collection yet",
because its three members were $0.00 subscription-plan products that the template
does not list. Every automated check passed. The CTA "worked" and dropped
high-intent buyers on an empty shelf.

`crawl` the rendered destination page and confirm real products are visible on
it. Status codes prove routing, not merchandising.

## Step 6 — Fix the rendering traps before you style anything

Each of these produced a visibly broken embed with correct-looking code.

**Pin the colour scheme.** The scaffold's `globals.css` honours
`prefers-color-scheme: dark` and paints `body` `#0a0a0a`. Fluid checkout is
always light, so a dark-mode buyer got a black slab inside white checkout. Pin
embed routes to `color-scheme: light`, make the document surfaces transparent,
and let **each shell** paint its host column colour (Step 1) while filling
`min-height: 100vh`.

**Paint frame one synchronously.** `requestAnimationFrame` is suspended in a
backgrounded or headless document, so a canvas that waits for the first rAF
callback never paints — an empty white box. Draw the initial frame directly,
then let the loop schedule itself from there.

**Honour `prefers-reduced-motion`** with a static end-state — the finished
scene, not a frozen first frame — and pause the loop on `visibilitychange`.

**Give every `<button>` an explicit `type="button"`.** The default is `submit`.
Inside a checkout iframe, a button without a type is a button that can submit a
host form.

**Use a `globalThis` singleton for the database.** The scaffold's `lib/db.ts`
caches PGlite in a module-level `let`. Next compiles page bundles and
route-handler bundles separately, so both open a database over the same file: an
insert "succeeds" in the route handler while the page reads zero rows. This looks
exactly like a persistence bug and is not one.

## Step 7 — Gate the copy when the vertical is regulated

For supplements, medical devices, financial products, or anything touching income
claims: **every user-visible string lives in one module**, with a test asserting
each string against banned patterns.

At minimum, that test rejects:

- "FDA approved" — the compliant phrasing is **FDA cleared**
- `diagnose`, `treat`, `cure`, `prevent disease`
- unqualified `kill`, and "chemical-free"
- income, earnings, or guarantee language

And requires that any numeric performance stat travels with its independent-lab
attribution — and appears nowhere else unreviewed.

Inline strings in components are unreviewed copy on a checkout page. That is the
whole reason for the rule: the review step exists only if the strings are
somewhere a reviewer can read them all at once.

## Step 8 — Verify at real height, and report what you could not prove

Preview each zone in the pane's **"As Drop Zone"** mode, at its real declared
height, with a test cart. A zone that looks right at full-window height and wrong
at 220px has not been previewed.

Then fetch the deployed embed URL directly with a real cart or order token, and
confirm the rendered output.

State the limits plainly rather than implying coverage you do not have:

- **`interact_preview` refuses game canvases.** Gameplay frames cannot be
  verified automatically. Hand this to the user to verify and say so.
- **A local `MIST_DEV` preview proves layout and fixture behaviour only.** It
  does not prove a production app-bridge exchange, the scopes actually granted,
  or the real shape of the resource. Do not report a fixture pass as a
  production pass.

Report both limitations in the summary. An honest gap is usable; an inferred
success is not.

---

## Experience patterns that fit the band

Concrete shapes at the right scale. Each is one gesture, under 30 seconds, and
readable at a glance.

| Pattern | Slot | Why it fits |
|---------|------|-------------|
| **One-tap 30-second clear-the-room game** | `order_confirmation` | Single repeated gesture, server-scored, ends in a consumable reward CTA. Dwell time is free after payment. |
| **Four-tap quiz** | `order_confirmation` | It is a segmentation survey wearing a quiz costume. Four taps is the honest ceiling for post-purchase attention. |
| **Drag-your-rooms product matcher** | `order_confirmation` | Turns a device purchase into a sized cross-sell. Drag is one gesture and needs no text entry. |
| **Scratch-to-reveal** | `order_confirmation` | One gesture, instant payoff, and the reward comes from `*_REWARD_CODE` — never an invented string. |
| **Ambient purchase visualiser** | checkout, LEFT column | Names the purchased product from the cart and animates around it. No handlers, `pointer-events: none`, zero-height on failure. The only interactive-feeling thing checkout may carry. |

---

## Reporting the value

Frame the result in the merchant's model of their business, not in drop-zone
terms:

> Confirmation-page dwell time — previously dead — now carries a one-gesture
> experience that ends on a compatible-consumable CTA, so the second purchase has
> somewhere to happen while intent is still highest.

If order history exists, quantify it: post-purchase CTA click-through and the
share of orders followed by a consumable reorder, before and after.

If the store has no order history yet, **say so plainly and report the structural
work instead.** A fabricated conversion projection is worse than an honest
structural statement — the merchant will test the number, and a number that does
not survive contact costs you the rest of the report.

---

## Notes and traps

- **Attach installs immediately.** The redeploy is not a follow-up task; it is
  part of the attach. Anything between the two runs against a build with no
  secret.
- **A one-time exchange token means there is no retry.** The unsigned-POST probe
  costs one request and saves an irreversible reinstall.
- **`422 managed_var` is not an error to work around.** It means the attach has
  not happened. Fix the ordering, not the call.
- **A status field is not evidence.** `queued`/`revoking` sat frozen for 45
  minutes over an operation that had already succeeded. Check `GET
  /api/drop_zones` and the rendered route.
- **`settings.height` is missing from the scaffold's payload type**, so the
  compiler will not tell you. Patch the client.
- **`company_id` selects; it never grants.** Every owned query carries the
  installation uuid in its predicate, and the repository exposes no lookup that
  omits it.
- **Delete-and-recreate orphans a zone** from the install's `registeredIds`
  cleanup. Repair with `PATCH /api/drop_zones/{uuid}`.
- **The iframe cannot grow.** Content that overflows the declared height is
  content no buyer will ever see, and there is no scrollbar to discover it with.
- **200 is not "renders".** Crawl the destination and confirm products are
  actually on the page.
