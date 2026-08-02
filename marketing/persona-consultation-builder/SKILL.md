---
name: Persona Consultation Builder
description: Spin up a persona-scoped Liquid consultation for {{company.name}} — 2 questions instead of 19, because the persona pre-answers texture and scalp — plus the rep-facing Portal share screen. Use for "build a consultation for X", "add a persona funnel", "spin up a curly-hair quiz", or when a rep wants a persona-scoped mini-quiz that credits them on conversion.
icon: sparkles
category: Marketing
preview: hero,header,panel,share,cards3,cta
---

# Persona Consultation Builder

{{company.name}}'s brand is personalization, delivered through one long consultation that
gates every product page. Beautiful UX, brutal conversion bottleneck. For any
segment a rep already understands — "curly hair, dry scalp" — the rep does not
need the full interrogation; the persona already answers most of it. This skill
spins up one such **persona consultation** end to end.

**The lever:** the full consultation asks 19 questions because it knows nothing
about the visitor. A rep sharing a link already knows the texture and the scalp.
A persona moves context acquisition from the CUSTOMER to the LINK, so the flow
drops to **2 questions**. Same resolver, same catalog, same cart, a fraction of
the drop-off.

The pitch: instead of one funnel and a 10-minute quiz, {{company.name}} runs 50
persona-targeted 90-second consultations this quarter, each with its own
rep-attributed share link, all feeding the same subscribe economics.

**Honest caveat to lead with, not bury:** this recommends from the existing
catalog. It is a faster funnel into the Salon, not a replacement for the
formulation pipeline.

Company: {{company.name}} · Theme: Prose Onboarding Theme (#56810) · API: {{company.api_base}}

---

## Architecture — read this before touching anything

The consultation is a **Liquid theme section**, not a Fluid Form, not a Droplet.
It is server-rendered, SEO-visible, first-party (so FairShare cookies and the
`/:credit/` path work), and it renders no iframe.

> Verified: Drop Zones only exist for Admin, checkout, and order_confirmation
> (`settings.page` enum is `checkout, order_confirmation`). **There is no
> storefront-page drop zone**, so a Droplet cannot own a consultation route.

Files that matter:

| File | Role |
|---|---|
| `sections/prose_hair_quiz/index.liquid` | Markup, persona/mode resolution, `[data-quiz-config]` JSON, schema |
| `assets/prose-quiz.js` | All runtime logic. Reads config JSON. **Contains no Liquid.** |
| `assets/prose-quiz.css` | Styles, scoped to `.prose-quiz` |
| `locales/en.json`, `locales/fr.json` | Every user-facing string under `quiz.*` |
| `page/default/index.liquid` | Fallback routing for a Page with no assigned template |
| `sections/product_hero/index.liquid` | PDP consultation CTA + its link settings |

**Keep CSS and JS in `assets/`.** A single-file version of this section grew
past 150KB and a `fluid theme pull` merge duplicated its tail — see Gotchas.

### How the persona is chosen (precedence)

1. **Explicit setting in the Page's own theme template** — what actually runs
   for every Page created by `create_page`. Deterministic.
2. **Title keywords in `page/default`** — fallback only, for a Page with no
   assigned template. Currently unreachable for all live Pages.
3. **Section schema default** (`persona: none`) → the full 19-question flow.

Always set the persona **explicitly** in `template_content`. Do not rely on
title matching.

### Existing presets

`curly_dry` · `fine_oily` · `postpartum` · `color_damage`, plus
`mode: haircare | skincare`. Each preset supplies a texture, a scalp, and one
signature product that always makes the routine.

---

## 0. Ask ONCE, then wait

Before any tool call, ask these three in one short message. Keep it to three —
the whole premise is that a persona replaces interrogation, so a builder
interview that runs long contradicts the product.

1. **Who is this audience?** Hair type (or skin type) plus their situation, in
   the rep's own words. "curly hair, dry scalp", "fine hair that goes flat by
   lunch", "six months postpartum", "bleached blonde, straightens daily",
   "acne-prone but dry".

2. **What do they actually complain about?** Two or three concerns in the
   words the audience uses — "frizz", "no definition", "breakage at the ends",
   "shedding at the temples", "flat roots", "flakes", "dullness".

   **This is the load-bearing question — do not let it be skipped.** Concerns
   are what pick the signature product, what a triage page routes on for
   unattributed traffic, and what a Mist app would store as `prose.concerns`.
   A persona without concerns is a label with no mechanism behind it. If the
   answer comes back vague ("dry hair"), ask ONE follow-up: dry where — scalp,
   lengths, or ends? They resolve to different products.

3. **Sharing model** — (a) reps share via Portal, (b) linked from the public
   storefront, or (c) both. Both is the default; the Page is public either way.
   The answer only sets whether you prioritize the Portal screen or the nav link.

**Do NOT ask for the texture token, the scalp token, or which product to
feature.** Derive all three from answers 1 and 2 using the mapping in step 2,
then confirm your derivation in one line — "Reading that as curly texture, dry
scalp, curl cream as the signature product; say the word if that's off."
Asking a builder to fill in `p_texture: curly` is asking them to do your job.

Then **END YOUR TURN and wait.** Do not read files or draft anything yet.

## 1. Read memory

Check `memory.md` for **"Persona consultation preferences"** — quiz length,
question tone, bundle rules, CTA copy the user already refined. Honor them.

Also read the **persona registry** table (step 8) if one exists. It tells you
which personas are already live and what concerns each one claims — so you can
catch an overlap before building a near-duplicate funnel. If the new concerns
substantially overlap an existing persona, say so and ask whether they want a
separate funnel or a tweak to the existing one.

## 2. Derive the preset, then confirm or add it

### 2a. Turn the answers into the three values the section needs

**Texture** — from answer 1. Must be one of the four families the token tables
in `assets/prose-quiz.js` understand:

| They said | `p_texture` |
|---|---|
| straight, fine, poker-straight, no bend | `straight` |
| wavy, loose S, beachy | `wavy` |
| curly, ringlets, spirals, 3a–3c | `curly` |
| coily, kinky, 4a–4c, tight zig-zag | `coily` |

**Scalp** — from answer 1 or 2. One of `oily | balanced | dry | notsure`.
"Greasy by day two" → `oily`. "Flaky, itchy, tight" → `dry`. Nothing said about
the scalp → `balanced`, and say that you assumed it.

**Signature product** (`p_extra`) — from answer 2. This is the product the
persona exists to sell, and it is ALWAYS in the routine:

| Concern in their words | `p_extra` |
|---|---|
| frizz, no definition, curls fall flat, shape | `custom-curl-cream` |
| breakage, split ends, damage, snapping, bleached | `custom-hair-mask` |
| shedding, thinning, density, postpartum, temples | `custom-scalp-serum` |
| flat roots, oily roots, limp, second-day hair | `custom-dry-shampoo` |
| dry lengths, dullness, no shine, straw-like | `custom-hair-oil` |
| flakes, itch, sensitivity, irritation | `custom-scalp-mask` |

Two or more concerns pointing at different products: pick the one they named
FIRST — reps lead with the complaint that actually loses them the sale — and
note that the others are still reachable through the goal question in the flow.

**If a concern maps to a product this catalog does not have, say so plainly**
rather than substituting a near-match. A persona whose signature product is
missing is worth surfacing, not papering over.

### 2b. Confirm or add the preset

Read `sections/prose_hair_quiz/index.liquid` and check whether the derived
persona already exists in the `{%- if persona == ... -%}` chain.

**If it exists**, note its texture / scalp / signature product and move on.

**If it does not**, add it — four coordinated edits:

1. The persona chain in the section: `p_texture`, `p_scalp`, `p_extra`,
   plus `persona_eyebrow` and `persona_heading` translation keys.
2. The `persona` select's `options` array in `{% schema %}`.
3. `locales/en.json` — `quiz.persona_<key>_eyebrow` and `_heading`.
4. `locales/fr.json` — the same two keys. **Never leave a locale missing**, or
   `/?locale=fr` renders raw key names.

Write the eyebrow and heading from the audience's OWN words, not from the token
names. `curly_dry` renders "Curly hair · dry scalp" / "Curly hair, dry scalp —
let's finish the formula". If they said "flat by lunchtime", the heading should
sound like that, not like "fine_oily".

Then `fluid theme lint --json` and `fluid theme push`.

### 2c. Keep the concerns durable

Put the concerns verbatim in the Page `description` in step 3. They then survive
outside the theme, are readable by a future triage page or Mist app, and are
what makes "which consultation for frizz?" answerable later. Record them in
memory in step 8 too.

## 3. Create the Page

**Use `create_page`. Never `fluid_api`** — Page mutations are refused there
("Page mutations must use create_page").

```
create_page(
  title: "<Persona> Consultation",
  slug: "<persona-kebab>-consultation",
  template_name: "<persona-kebab>-consultation",
  description: "For <audience in their words>. Concerns: <concern, concern, concern>.
                Pre-answers texture and scalp, so it asks 2 questions instead of 19.",
  template_content: <the Liquid below>
)
```

**Put the concerns in `description` verbatim** — that is the only place they
persist outside this chat, and it is what a triage page or a Mist app reads
later to answer "which consultation for frizz?".

`template_content` — set the persona explicitly:

```liquid
{% section 'prose_hair_quiz', id: '<short>_quiz' %}

{% schema %}
{
  "sections": {
    "<short>_quiz": {
      "type": "prose_hair_quiz",
      "settings": { "persona": "<persona_key>" },
      "blocks": {}
    }
  }
}
{% endschema %}
```

Two rules that cost real time when broken:

- **`{% section %}` takes the section TYPE** (`prose_hair_quiz`, the directory
  name), **not its display name**. `'Prose Hair Quiz'` renders absolutely
  nothing — no wrapper, no error, blank body. `fluid theme lint` DOES catch it
  as a missing section reference, so trust lint over the page looking fine.
- **Do NOT set `full_quiz_url` here.** A template setting beats the schema
  default, and pointing it anywhere other than the full consultation makes the
  "Not quite you?" escape hatch loop the shopper back into a product grid.

### `create_page` errors while succeeding — do not retry

It has failed with `Object has been destroyed` on **every** call observed, and
**created the Page record anyway** every time. Naively retrying produced FOUR
duplicate Pages.

On error, do this instead:

```
GET /api/v202604/company/pages?per_page=50
```

Find your title. If it is there, the Page exists — proceed. Note its `id` and
`slug` from the response.

**Slugs are derived from the title.** Every Page created came back
`custom_slug: false` with a slug generated from the title, ignoring the one
supplied. "Curly Hair, Dry Scalp" became `curly-hair-dry-scalp-consultation`.
**Quote `canonical_url` from the response — never compose a URL from a slug you
chose.**

## 4. Verify by DRIVING it, not by looking at it

Lint passing and the page loading prove nothing about the resolver. Drive the
real flow and assert the outcome:

```
crawl(url: <canonical_url>, formats: ["html"], only_main_content: true,
  actions: [
    { wait 2500 },
    { click "[data-quiz-start]" },
    { click "[data-quiz-answer=\"goal\"][data-quiz-value=\"hydration\"]" },
    { wait 700 },
    { click "[data-quiz-answer=\"fragrance\"][data-quiz-value=\"corsica\"]" },
    { wait 700 },
    { click "[data-quiz-skip]" },
    { wait 1500 }
  ])
```

Request `formats: ["html"]`, not markdown — markdown strips attributes and you
lose the evidence.

Then assert, from the returned HTML:

- **`data-quiz-variant`** on each `.prose-quiz__item` is the resolved variant.
  **Predict it from the token tables first, then compare.** A resolver that is
  quietly broken returns each product's FIRST variant every time — so check the
  variant's POSITION in the product's list, not just that a value is present.
- The routine contains the persona's signature product.
- The profile line (`[data-quiz-profile]`) reads the expected
  `texture · scalp · goal`.
- Run a SECOND persona with different answers and confirm the products and
  variants actually differ.

Known catalog limit, state it rather than overclaiming: `custom-hair-mask`,
`custom-scalp-serum` and `custom-hair-oil` have only ONE variant each, so
answers decide *whether* they appear, never *which*.

## 5. Point the PDPs at it

The PDP is consultation-first: no add-to-cart on `custom-*` formulas, "Get your
formula" instead (see brand.md). Set the relevant link in `product_hero`'s
settings so the CTA reaches the new funnel:

- `consultation_url` — the full consultation (all formula PDPs)
- `consultation_url_skincare` — cleanser / serum / moisturizer
- `consultation_url_curly` — curl cream (curly-only product)

A single-hair-type product may point at its persona funnel. Anything ambiguous
goes to the FULL consultation: a PDP does not know who the shopper is, and
guessing a persona builds a formula on someone else's hair.

**After any Page rename, re-check these** — a stale default 404s. Verify by
fetching the PDP and reading the CTA href.

## 6. Portal share screen — the rep-facing artifact

This is where a rep grabs their attributed link, and it is the piece most likely
to be missing. Follow `portal-page-authoring` for the rules you must not violate
(one single-column LayoutWidget wrap, columns via sectionLayout, string px
heights on CarouselWidget, publish a version after any change).

```
GET  /api/company/fluid_os/definitions
POST /api/company/fluid_os/definitions/{def_id}/screens
     { "screen": { "name": "<Persona> consultation — share",
                   "slug": "<persona-kebab>-share",
                   "component_tree": {} } }
```

Then PUT the tree — sections top to bottom:

1. **CarouselWidget** — hero: `"Share the <persona> consultation."`
2. **LayoutWidget (single-column)** — eyebrow `SHARE THE QUIZ`, title
   `"Your unique link — every answer credits you"`.
3. **QuickShareWidget** — carries the rep-attributed URL:
   ```json
   { "id": "share-consultation", "type": "QuickShareWidget",
     "props": { "shareableType": "Page", "shareableId": <page.id>,
                "showBuyButton": false, "showResourceType": true,
                "showShareActions": true } }
   ```
   `showBuyButton: false` — this is lead-gen, not a product card.
4. **LayoutWidget (3c-equal)** — three TextWidget cards previewing the products
   the persona routine lands on, so the rep sees what they are sharing.
5. **LinkWidget** — `linkType: "external"` to the Page's `canonical_url`, so the
   rep can preview the prospect's view.

Add a nav item, then publish:

```
POST /api/company/fluid_os/definitions/{def_id}/navigations/{nav_id}/navigation_items
     { "navigation_item": { "label": "<persona> quiz — share",
        "slug": "<persona-kebab>-share", "position": <n>,
        "screen_id": <id>, "source": "user" } }
POST /api/company/fluid_os/definitions/{def_id}/versions   {}
```

## 7. Report both flows, then LEARN

Hand back both URLs — the Page's `canonical_url` quoted from the response, and
the Portal share screen. Say which persona resolved and which products the
routine produced, with the variant evidence from step 4.

Explain the two paths in one line each:

- **Rep-shared:** rep opens the Portal screen → QuickShareWidget mints a unique
  URL → prospect clicks → attribution cookie set → takes the consultation on the
  storefront Page → cart carries the rep → order settles → rep gets credit.
  Attribution is sticky per session, so the whole flow keeps the credit path.
- **Public:** prospect lands directly (nav, ad, SEO) → no attribution → same
  Page, same quiz, same checkout → settles as a house customer.

Then ask ONE question: "This routine lands on <N> products. Want a tighter map
(top 2), the full 4-product Salon, or different closing copy?" **END YOUR TURN.**

## 8. Remember, then offer the next

On their answer, `update_memory` under "Persona consultation preferences" —
quiz length, tone, bundle default, CTA copy that worked. Be specific and lasting.

**Also record a PERSONA REGISTRY line** — one per funnel, in a stable shape, so
later runs and a future triage page can read it without re-deriving anything:

```
| persona_key | Page slug | concerns (verbatim) | texture | scalp | signature product |
```

e.g. `| curly_dry | curly-hair-dry-scalp-consultation | frizz, no definition,
dry scalp | curly | dry | custom-curl-cream |`

That table IS the routing map. When someone later asks "which consultation for
breakage?", it answers in one lookup instead of a judgement call — and it is the
seed data for a triage page or a Mist `personas` table.

Then offer the next persona. The second should need almost no input: the preset
work is done, memory holds the preferences, and it is one `create_page` plus one
Portal screen. That is where "50 funnels this quarter" becomes real.

---

## Unattributed traffic — the gap this skill does NOT close

Persona selection is **the rep picking a link**. Correct for we-commerce, and it
breaks in two places: a shopper arriving from an ad or SEO with no rep, and a rep
who guesses wrong.

Mitigations, cheapest first:

1. **Triage page** — one question, "what's your main concern?", six answers
   routing to the right funnel (frizz → curly, flat roots → fine/oily, shedding
   → postpartum, breakage → color-damage). ~30 lines of Liquid, no API.
2. **PDP implication** — already partly built (curl cream → curly). Extendable.
3. **Page metafields** — `PageWrite` accepts `metafields_attributes`
   (`namespace`, `key`, `value`, `value_type`), and `PageBase` returns
   `metafields`, so `prose.persona = curly_dry` is expressible.
   **Two things are UNVERIFIED — do not build on them without testing:**
   whether Liquid can read `page.metafields` (the page drop is only partially
   populated — `page.slug` and `page.handle` come back BLANK while `page.title`
   works), and whether a non-admin token may write them.
   **And there is no metafield filter on any documented list endpoint**, so
   metafields can never be the query layer — they are a durable label, and an
   index belongs in a Mist DB.

---

## Gotchas — all verified the hard way

**`create_page` errors but creates.** `Object has been destroyed` every time,
Page created every time. Never retry; `GET .../company/pages` and check. Four
duplicate Pages came from retrying.

**`{% section %}` takes the section type, not the display name.** A bad
reference renders NOTHING — no wrapper, no error, blank body. Lint catches it.

**Slugs are derived from the title.** `custom_slug` came back `false` on every
Page created. Quote `canonical_url` from the response; never compose a URL.

**`page.slug` and `page.handle` are BLANK in Liquid.** Only `page.title` is
populated. Any `page/default` routing must match on title.

**`fluid theme pull` can DUPLICATE a large section file.** It reported "merged
cleanly" while appending copies of the file's tail past `{% endschema %}`, which
Fluid renders as **visible page text** — raw JavaScript appeared on the
storefront. Lint stayed green.
- Earliest symptom: `edit_file` failing with **"old_string appears 2 times"** on
  a string that should be unique. Treat that as corruption, not as needing more
  context.
- Detect: `search_files` for `endschema` in the section. More than one match =
  corrupted. Repair = rewrite the file; surgical edits are impossible.
- Prevent: keep CSS/JS in `assets/`. When local is known-good, use
  `fluid theme push --force` rather than pull — the pull caused the damage.

**`write_file` dies on ~50KB+ payloads.** Split into several smaller files
instead of retrying the giant write.

**Never `data-fluid-add-to-cart` for runtime-resolved variants.** FairShare
binds that attribute when it scans the DOM at load; quiz variant ids do not
exist until the shopper finishes, so the attribute may never bind — a button
that looks perfect and does nothing. Use `FairShareSDK.addCartItems()`. Never
both, or every item is added twice.

**Only mark products that have a plan as subscriptions.** The cart returns 422
for an invalid subscription line, and the whole routine is added in ONE
`addCartItems()` call — one bad line loses all of it. Products without a plan
add one-time, and the UI says so.

**Currently only Custom Shampoo has a subscription plan** (of 21 products). A
routine therefore shows "One-time purchase" on most items. That is live data, not
a bug — flag it, since the funnel asks "Subscribe and save 15%?" and then mostly
cannot deliver it. Fix is per-product in admin.

**Never show the resolved variant name to a shopper.** "Shampoo dry v4" is the
consultation's OUTPUT; a version number in front of a customer is what this whole
flow exists to remove. Keep it in `data-quiz-variant` for QA only.

**Play the answers back.** A consultation that asks 19 questions and reflects 3
feels decorative. The results screen carries a collapsed recap built by reading
option labels out of the DOM — so it needs no new locale strings and cannot drift
from the wording the shopper saw.

**QuickShareWidget `shareableType`** is exactly `Product | Page |
EnrollmentPack | Medium | Library`. `Page` is what carries rep attribution to a
storefront consultation.

**Portal `component_tree` — POST hash, PUT array.** Create with `{}`, then PUT
the array-shaped tree. Publish a version after every screen change.

**{{company.name}} has ZERO reps today** (`GET /api/checkout/v2026-04/reps` → `total_count:
0`; one admin user with `username: null` and `share_guid: null`). Attribution
code paths are correct but untestable until a real rep exists — do not claim a
share link was verified to credit anyone.
