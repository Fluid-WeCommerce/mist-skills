---
name: Product Quiz
description: Build an AI-driven product quiz for any Fluid company — a Mist backend that generates questions and picks products from the live catalog, a native theme section, and a storefront page.
icon: list-checks
---

# Goal

Build an **AI-driven product quiz** for whatever Fluid company this skill is run in: a
"answer 5–8 questions, get a personalized product/bundle recommendation" experience that
lives on a real storefront page, is styled by the company's own active theme, and is
powered by that company's own live catalog.

Nothing in this playbook is company-specific. Every product, price, question, colour and
word is **discovered at run time** from the company you are running in. If you find
yourself typing a product name, a promo code, a hex colour or a category word into code,
you have made a mistake — that value belongs in settings, in theme tokens, or in the
model prompt's catalog projection.

Use this skill when someone asks for a product quiz, product finder, "help me choose",
recommendation quiz, or personalized bundle builder.

## Architecture (decide this first, then build)

Three pieces, in this order:

1. **A Mist app (Next.js) = the quiz brain.** Reads the catalog, generates questions,
   scores answers, picks products, stores sessions/leads/analytics. It is the only place
   with a model API key.
2. **A native Liquid section in the active theme = the quiz face.** Fetches from the Mist
   app at run time and renders with the theme's own tokens. **Not an iframe.**
3. **A storefront Page** that hosts the section, plus entry points that drive traffic to it.

Why a native section and not a drop zone / iframe: the storefront is not a Fluid iframe
surface, and a native section inherits brand fonts, gets SEO-indexed, and loads instantly.

The exact endpoint payloads, catalog response shape, and AI provider config live in
`references/backend-contract.md`. Fluid-specific failure modes that will bite this build
live in `references/fluid-gotchas.md`. Read both before step 1.

---

# Steps

## 0. Recon — never assume, always look

Do all of this before writing a line of code:

1. `list_projects` — is there already a quiz Mist app and which theme project is live?
2. `fluid_api GET /api/application_themes/active` — the active theme id + its
   `global_stylesheet`. Read the CSS custom properties it defines (`--clr-*`, `--ff-*`,
   `--fs-*`, `--space-*`, `--rounded-*`). **These are your design tokens.**
3. `fluid_api GET /api/v202604/company/pages?page[limit]=50` — does a quiz Page already
   exist? Read its real `slug` and `canonical_url` from the response.
4. Read the company's `brand.md` (it is in your context as `<brand_voice>`) — this is the
   voice the AI must write in.
5. Hit the public catalog once (step 2) and eyeball what the company actually sells. A
   quiz for a supplement brand asks different questions than one for coffee; the AI will
   work this out, but you need to know whether the catalog is big enough to be worth a
   quiz (fewer than ~6 sellable products → tell the user a quiz is overkill and stop).

## 1. The backend Mist app

If a quiz Mist app already exists, extend it. Otherwise propose one with
`human_in_the_loop` (source `agent`, fresh `project-create:mist:<name>:<suffix>` id), end
your turn, and create it with `create_project` after the Approve click. Creating a Mist
provisions a real vendor stack — never speculatively.

Endpoint contract — **freeze these shapes before the theme work starts**, because the
theme is built against them in parallel:

| Endpoint | Purpose |
| --- | --- |
| `GET /api/quiz/config` | questions to render + the live offer |
| `POST /api/quiz/score` | answers in → `{ shareToken, result }` out |
| `GET /api/quiz/result/:token` | replay a saved result verbatim |
| `POST /api/quiz/lead` | optional email capture — never a gate |
| `POST /api/quiz/event` | fire-and-forget analytics |

Full request/response JSON is in `references/backend-contract.md`. Unknown answer ids are
ignored, never fatal. `bundle` is `null` when fewer than 2 items.

Write this contract into `docs/theme-quiz-section-spec.md` in the Mist project with **real
captured responses**, not invented examples. That file is the handoff to the theme agent.

## 2. Catalog wiring — use the PUBLIC storefront endpoint

```
GET https://<shop>/api/v202604/products?country=US&page[limit]=100
```

- **No auth at all.** The company is resolved from the subdomain. It returns only live
  products with an active variant in that country — exactly what a quiz should recommend.
- Do **not** use the admin catalog endpoint (`/api/v202604/company/products`) with the
  Mist's `FLUID_COMPANY_PRIVATE_TOKEN`: it 403s (authenticated but not authorized).
- The response shape differs from the admin endpoint in ways that will silently break a
  naive mapper — see `references/backend-contract.md`.
- Cache the snapshot per company with a TTL (~15 min) and a content hash. Every derived
  artifact (classifications, generated questions) must be keyed by that hash **and** by a
  `VERSION` constant you bump whenever the derivation logic changes meaning — otherwise
  stale output is served for the whole TTL.

## 3. The AI layer

### 3a. Provider-agnostic client, no new dependency

Plain `fetch` against an OpenAI-compatible chat-completions endpoint with a JSON-schema
`response_format`. Provider resolution order and env var names are in
`references/backend-contract.md`. Set them with `set_mist_env_var`; tell the user a
redeploy is required. If the company has no model key, **ask for one** — do not invent a
value — and ship with the deterministic path working in the meantime.

**No key, non-200, timeout, or malformed JSON ⇒ log once and return `null`** so the caller
falls back. Hard `AbortController` timeouts: ≤8s on config, ≤6s on score. The quiz must
never 500 or hang because of a model.

### 3b. AI generates the questions

Input to the model: company name, brand voice from `brand.md`, and a **compact projection**
of the live catalog — titles, collection slugs, price band, derived signals. Never the raw
payload.

Output: 5–8 questions. One concept per question. `single` unless a multi-pick genuinely
helps. `optional: true` on anything a shopper can skip. Copy in the brand's voice. Option
ids are stable slugs.

**Every question must discriminate between products that actually exist in this catalog.**
Reject a generated set whose options map to no candidate. Validate hard against a schema;
on any failure, serve the deterministic fallback set.

Cache per company + catalog hash + `PROMPT_VERSION`, TTL ~24h. On a cache miss, serve the
deterministic set **immediately** and warm the cache in the background — never make a cold
shopper wait on a model call.

### 3c. AI picks the products — from a shortlist it cannot escape

This is the part that keeps the quiz honest:

1. A **deterministic scorer** ranks the whole catalog against the answers and takes the
   top ~20. This is the candidate generator, and it is also the fallback.
2. The model sees **only those candidates** (id, variantId, title, price, signals) plus the
   answers.
3. The model returns 2–4 picks, a `role` for each, plus `headline`, `blurb`, and a one-line
   `reason` per item in brand voice.
4. **Validate every returned `variantId` against the shortlist.** Drop anything else. If
   fewer than 2 valid items survive, use the deterministic result unchanged.
5. Prices, URLs, images and titles come from the catalog record — **never** from the model.
   Bundle math (subtotal/discount/savings/total) is server-side arithmetic, never model
   output.

Persist the **final result object**, not the prompt, so `GET /result/:token` replays
identically forever.

## 4. Tenancy + security gate — this is a gate, not a nicety

- Resolve company/install through the app's verified-context path. The `shop` query param
  is bootstrap/lookup material, **never** trusted identity.
- Every cache row, session, lead, event and idempotency key carries the tenant key, and it
  is enforced in the SQL predicate — not just in UI props.
- A Mist can serve its own company with no droplet install ("single-company mode") by
  verifying the shop against Fluid rather than trusting the request. Keep the install path
  first so the same code goes multi-tenant later.
- Negative tests before you claim success: no context → 401; wrong company → 403; two
  tenants cannot read each other's cached questions or results; a hallucinated variantId is
  rejected; the no-key path falls back.

## 5. The Page + its ApplicationTheme template

- Create it with **`create_page`**, never `fluid_api`. It creates the Page, the dedicated
  ApplicationTheme template, links them, and publishes.
- The Page template is **versioned separately from the theme**. A plain `fluid theme push`
  does not replace it. Iterate with `update_page_template` (`publish:false` while
  iterating, `true` only after preview is clean).
- `create_page` has three sharp edges — a slug it derives from the title rather than
  honouring, an error it can report *after* a successful write, and no delete path. Read
  `references/fluid-gotchas.md` before calling it, and never blind-retry it.

## 6. The Liquid section

`sections/quiz_flow` — native Liquid + vanilla JS.

- Fetch `/api/quiz/config` at run time. **Do not hardcode the questions and do not assume a
  fixed count** — they are AI-generated per catalog snapshot. Progress reads
  "Question 3 of N" from the fetched length.
- One question per screen. Large tap targets. `role="radiogroup"`, arrow-key navigation,
  visible focus ring. `kind:"multi"` → checkboxes + Continue. `optional:true` → a Skip /
  "No preference" control.
- Result screen heroes the `role:"primary"` item, then addition/accessory/gift, each with
  its `reason` under the title. Bundle box shows subtotal, savings, total, promo code.
- Add to cart via `window.FairShareSDK.addCartItems([{ variant_id, quantity }])` for all
  bundle items, then apply `bundle.promoCode`. Also offer **"Add just the primary"**. Fire
  the `add_to_cart` event (it suppresses the abandoned-quiz follow-up).
- Share: copy `<page-url>?r=<shareToken>`; on load, if `?r=` is present hydrate from
  `/result/:token` and skip the questions. Remember the result in `localStorage` with a
  prominent **Retake**.
- Loading state on `/score`; on a non-200 show a friendly retry plus a link to the all-
  products collection. Never leave the shopper stuck.
- **Styling comes from the theme, not from you.** Use the `--clr-*` / `--ff-*` / `--fs-*` /
  `--space-*` / `--rounded-*` custom properties the active theme defines, and reuse the
  existing product-card / button / heading patterns from the theme's own product sections.
  Expose copy and colour choices as `{% schema %}` settings. Literal hex values in a quiz
  section are a bug.
- 390px is the primary target.

## 7. Entry points

A quiz nobody can find is worthless. Wire all four:

1. The quiz Page itself — the destination for email/social campaigns.
2. A homepage teaser section linking to it.
3. A main-nav link.
4. An empty-cart prompt — invite them to the quiz instead of showing a dead end.

## 8. QA gates — evidence, not assertions

Backend:
- `pnpm typecheck && pnpm lint && pnpm test`, then `fluid mist push --watch`.
- Call the **live** endpoints and paste the real responses: `/config` returns questions for
  this shop; `/score` returns 2–4 items whose `variantId`s all exist in the live catalog;
  `/result/:token` replays identically.

Theme:
- `fluid theme dev`, then `screenshot_preview` at **390x844 and 1440x900** on the quiz route.
- `interact_preview` through the whole flow — answer, skip, back, submit, retake.
- `read_preview_console` for fetch/JS errors.
- Confirm result cards render real product images and prices from the live response.
- If local edits appear to have no effect, you are probably hitting the
  `?theme_template_id=` trap in `references/fluid-gotchas.md`.

Report what you observed. "It should work" is not QA.

## 9. Hand back

Tell the user: the live quiz URL (copied verbatim from the API response), which model
provider is wired, what the fallback does when the model is unavailable, and anything a
human still has to do (add a model key, remove a duplicate page, publish the theme).
