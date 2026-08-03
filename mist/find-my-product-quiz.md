# Goal

Create a quiz for your company that users can take to get a personalized item
recommendation that they can then add directly to their cart.

Five questions, one per screen, a personalized product result, and a path into
the cart. Ships as a Mist app embedded on the storefront as a dismissible modal,
and optionally as a PDP drop zone.

Works for any Fluid company — "Find My Flavor", "Find My Shade", "Find My
Blend". Derived from the OLIPOP build (2026-07-31); every **DO NOT** below is a
bug that actually happened, so don't re-derive them.

# Steps

1. **Interview the company before building anything.** Don't guess these:
   - **The noun.** Use the company's own word for its product family.
   - **The 5 questions.** Offer the default axes (step 2) as a starting point and
     let them rewrite the copy. Their wording beats yours.
   - **Fulfillment reality** — online only, retail only, or both? This drives Q5
     and the closing CTA.
   - **Email capture?** Optional, or none. It must never gate the result.
   - **Where it appears** — home-page modal, dedicated page, PDP drop zone, or
     several.

2. **Fix the question axes.** Q1–Q3 pick the product, Q4 picks the COPY ONLY,
   Q5 picks the variant + CTA.

   | # | Drives | Shape |
   |---|--------|-------|
   | Q1 | habit | "What do you usually reach for?" — include an "open to anything" option |
   | Q2 | family | the company's own product families (4–5) |
   | Q3 | intensity | a 3-point scale (light / middle / bold) |
   | Q4 | messaging | what the shopper cares about → drives the framing paragraph |
   | Q5 | line + CTA | ship / in store / both |

   Keep Q4 out of the winner calculation except as a small nudge. It exists so
   the result can speak to a motivation, not to re-rank products.

3. **Enumerate the catalog — never hand-write product data.** Run
   `fluid_catalog_index` to produce `fluid-catalog-index.json`, then generate the
   config from it. Hard rules, each of which broke something on the OLIPOP build:
   - **Every product URL must be the verbatim `canonical_url` from the API.**
     Fluid regenerates slugs and ignores a slug you send, so a URL you compose
     WILL 404.
   - **Verify product-line claims against real SKUs.** OLIPOP has 24 flavors but
     only 10 exist in the shelf-stable line. Where a line is unconfirmed, make NO
     claim rather than guessing.
   - **Exclude non-consumables** — merch, apparel, gift cards, accessories.
     Collect their ids in one `EXCLUDED_PRODUCT_IDS` array and filter in one
     place.
   - **Briefs lie.** OLIPOP's said "Watermelon" and "Peach Please"; the catalog
     had "Watermelon Lime" and "Peaches & Cream", and "Mint Chip" didn't exist.
     Match the catalog, not the brief.

4. **Write the config so a MERCHANDISER can edit it.** One file, editing rules
   commented at the top, and no product id referenced from component code. Per
   product: `key`, `name`, `enabled`, matching Q1 answers, families, intensity
   1–3, Q4 tags, optional manual `boost`, one short second-person `blurb`, and a
   `lines` map of purchasable forms.

5. **Build a pure scoring engine and test it.** One pure `recommend(answers)` —
   no React, no DB, no network — called by BOTH client and server, so the result
   paints instantly and survives the analytics call failing. Tests must assert:
   - every configured URL equals the catalog's `canonical_url`
   - the product-line claim set is exactly the real ids
   - no excluded product can ever be recommended
   - **all 720 answer combinations** (5×4×3×4×3) return a valid product
   - unknown option ids are rejected by the validator

   If one fails after a config edit, the CONFIG is wrong. Don't fix the test.

6. **Build the quiz route.** Public, anonymous, frame-able: no session, no PII,
   no identity from the query string. The tenant key is resolved SERVER-SIDE from
   config, never from the request body.
   - One question per screen, client state, no reloads. Progress bar + "Question
     N of 5". Title on every question; intro paragraph on Q1 only.
   - `?answers=q1.q2.q3.q4.q5` deep-links straight to a result. This is also how
     you QA result states, since a network-frozen harness won't hydrate React.
   - Two tables: one row per completed run (answers + recommendation, no PII),
     one for opt-in emails. Both keyed and indexed on the tenant column.
   - Analytics is fire-and-forget: if the insert fails, return 200 with
     `runId: null` and let the UI carry on.

7. **Choose the cart path deliberately.** The shopper is inside an iframe; this
   is where the OLIPOP build lost the most time.

   **Option A — escape the frame.** Every outbound link gets `target="_top"`. The
   whole tab goes to the PDP, the modal falls away, and the storefront's own cart
   and checkout behave normally.

   > **DO NOT ship these links without `target="_top"`.** Without it the IFRAME
   > navigates to the product page, so the shopper shops inside a 640×760 box.
   > Add-to-cart appears to work, then Checkout loads `checkout.fluid.app` inside
   > that frame and throws "Application error: a client-side exception has
   > occurred" — a framed checkout can't reach the storage it needs.

   With Option A, **don't label the button "Add X to cart"** — it's a link to a
   PDP. Say "Shop X". If the PDP defaults to a different pack size than the label
   claims, the label is lying.

   **Option B — real add-to-cart, then hand off.** Server-side, create a cart and
   add the recommended VARIANT via the documented checkout API
   (`/api/checkout/v2026-04/carts` + its `/items` sub-resource — look the schema
   up with `query_docs`, don't guess the body), then navigate `_top` to the
   returned checkout URL. This is the honest "add result to cart" and the better
   conversion path; it costs one server round-trip and needs the variant id, not
   the product id.

   Either way: **top-level navigation, always.** Checkout must never render
   framed.

8. **Embed it.**
   - **Storefront modal is THEME work.** Fluid publishes no storefront-page
     drop-zone slot. Build a theme section with an iframe: opens on load,
     closable via X + backdrop + Esc, full-screen on mobile, frequency in
     `sessionStorage` (expose "session / visitor / always" as a theme setting,
     plus `?quiz=open` and `?quiz=off` for QA).
   - **Frame permissions live in `proxy.ts`.**

     > **DO NOT set `frame-ancestors` via `next.config.ts` headers.** `proxy.ts`
     > (Next 16's renamed middleware) runs on every UI request and SETS
     > `Content-Security-Policy` itself, silently overriding it — the config
     > block looks applied and does nothing. Include `http://localhost:9292` so
     > theme devs can see the modal under `fluid theme dev`.

   - **Host handshake** — if the modal needs to know the shopper finished, post a
     message meaning *mark seen, leave open*:
     `window.parent.postMessage({ type: "<app>:seen" }, "*")`

     > **DO NOT name it `:complete` or give it close semantics.** OLIPOP's modal
     > closed on the same tick the result rendered and the shopper never saw
     > their match. Dismissal belongs exclusively to the host's close control.

     `targetOrigin: "*"` is correct here only because the payload is a constant
     type string with no answers, no result and no PII, and the host origin
     legitimately varies across storefront / admin / theme dev.

   - **Droplet + drop zone** — reuse an existing droplet if there is one;
     duplicates leave the company with two of everything. `active` is NOT
     writable: a PATCH returns 200 and silently keeps `false`. Don't chase it,
     and don't recreate the droplet to force it — that orphans the install. A
     storefront modal doesn't need it.

   - **The postcss trap** — if a stray Tailwind `postcss.config.js` sits in a
     PARENT directory, Turbopack walks up, finds it, and every route 500s with
     "Cannot find module 'postcss-import'". Drop an empty `postcss.config.js` at
     the project root BEFORE trying to render anything.

9. **Never link a page you haven't verified exists.** Fluid returns **200 with
   fallback content** for a missing page, not a 404 — so a dead link looks like
   "it goes to the shop page". Confirm the slug is in
   `GET /api/v202604/company/pages` before wiring any CTA to it. OLIPOP's store
   locator was referenced in four places and existed in none. If it's missing,
   get it built first or drop that branch of the flow.

10. **Verify, and be honest about what you couldn't.**
    - `pnpm typecheck && pnpm lint && pnpm test` before every push.
    - Deep-link each interesting result state and read the rendered DOM: confirm
      every outbound anchor carries `target="_top"`.
    - `fluid mist push --watch`, then fetch the public URL and confirm the new
      build is serving (`data-dpl-id` changes).
    - **State plainly what you could NOT verify.** A network-frozen QA harness
      never hydrates React, so clicking through five questions, the cross-iframe
      handshake, and the cart/checkout hand-off all need a human in a real
      browser. Ask for that explicitly instead of implying it passed.
