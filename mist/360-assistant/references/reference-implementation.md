# Reference implementation — what a real build learned

Architecture and hard-won traps from building this skill into a live storefront assistant. Read
before writing code. Nothing here is company-specific; every item shipped as a bug first.

## Shape

```
Storefront page
  └─ loader script → launcher + iframe        (public, no secrets; OWNS THE SDK BRIDGE)
        │  POST /api/assistant/chat  { message, thread_id }   ← SSE stream back
        ▼
Mist app (Next.js, Fluid hosting) + Postgres
  ├─ /api/assistant/chat      SSE: session | delta | tool | ui | violation | done | error
  ├─ /api/assistant/session   cookie mint
  ├─ /embed                   the chat panel (server half = first paint, client half = stream)
  ├─ /assistant               local harness with probe buttons
  ├─ /<loader>-test           hit-testing harness: the real loader over a grid of tap targets
  └─ lib/assistant/
       config.ts        env + boot invariants — THROWS if the assistant name is unset
       profile.ts       THE ONLY FILE WITH COMPANY FACTS
       greeting.ts      the opening line — shared by the panel AND the chat route
       storefront.ts    public reads + field allowlist (the only serialiser)
       cart.ts          the only module that talks to the cart API
       basket.ts        pure basket ops — the source of truth for cart composition
       offers.ts        typed standing offers + the clarify marker
       needs.ts         problem → product, matched against DESCRIPTIONS
       intent.ts        buy / edit / swap / repair / account / affirmation detection
       tools.ts         tool specs + dispatcher — POLICY IS ENFORCED HERE
       prompt.ts        system prompt (MODEL PATH ONLY — see §1)
       guard.ts         outbound refusal + off-brand scans
       session.ts       signed cookie
       repository.ts    tenant-scoped persistence
```

## Two answer paths, one dispatcher

With a model key configured, the model plans. Without one, a deterministic rules planner does —
through the **same dispatcher, the same suppression list, the same allowlist, the same guards**. The
stream reports which path served the turn, so no surface can pass the rules engine off as a model.

Worth the extra module: the whole pipeline is testable before a key exists, and the fallback is
honest rather than silent. **Production should refuse rather than fall back.**

## 1. 🔴 Anything that lives only in the prompt does not affect live behaviour

The prompt is read by **the model path only**. With no model key the rules planner is live and never
sees it. Brand voice was injected into the prompt and nowhere else, so the company's guide was applied
exclusively to the code path that wasn't running — while live copy read like a support macro.

**Rule: voice and policy must reach the dispatcher or the planner.** A rule in the prompt is a
suggestion; a rule in the dispatcher is a rule.

Corollaries:

- **Hand-written copy bypasses every guard** unless a **test** runs the guard over it. This has caught
  a refusal phrase four times.
- Run a **tone guard** (off-brand vocabulary from the profile) in parallel with the refusal guard,
  over the same canned strings.
- **Word-boundary match the off-brand list.** A brand's own coinage can contain a banned substring —
  one brand's playful compound contained "optimal", which its guide bans.
- **Never run the off-brand guard over the prompt itself** — the prompt deliberately quotes the
  off-brand counter-example in order to reject it.

## 2. Boot invariants, and how the name is wired

- **Throw if the assistant-name env var is unset.** Never default to "Assistant" — that ships to a
  customer. A missing name is a broken install, and the loud failure is the feature.
- **Refuse to serve chat if the company profile is missing or still the template.** An assistant
  without a profile has no lanes and no suppression list; it will recommend spare parts and invent a
  personality. A loud failure beats a plausible one.
- **One module owns the name** (`config.ts`, a single exported constant). Every surface imports it:
  launcher label, chat header, avatar alt text, the greeting module, the system prompt, the handoff
  email subject. **Never interpolate the literal into a template** — a hardcoded name is invisible
  until the day it's wrong on exactly one surface.
- **Renaming is one env var plus a redeploy** (production env changes don't apply until the app is
  rebuilt) — plus one decision that must be made consciously: the introduce-once flag is already set
  for returning people, so either clear it for a fresh introduction or acknowledge the change in the
  greeting. **Never rewrite past transcripts**; they record what was actually said.
- 🔴 **Assert the literal name in exactly one test** — the one that renders every surface and checks
  each shows the configured name. Use the constant everywhere else. That test is the rename canary:
  it fails on a rename (update one expected value), and **any other failure is a surface that
  hardcoded the name**.

## 3. Offers are data, not prose

The single highest-value structural change in the build. Every closed question the assistant asks gets
a **typed** offer written to the thread when made, and parsed when affirmed:

```
cart:<slug> · configure:<slug> · fit:<slug> · compare:<slug> · lineup · enroll · human
```

- **An audit found 7 of 10 offers unarmed.** Assume yours are too until you enumerate them.
- **Define each answer once**, shared by the branch that offers it and the resolver that honours it,
  so promise and delivery can't drift.
- **`parse("cart")` with no slug returns null.** Building a cart for a product nobody named is the
  worst available outcome.
- **The offer moves with the subject.** An out-of-stock reply that says "want that one instead?" must
  rearm to the *alternative*.
- **A clarifying question is marked, and is deliberately NOT an offer**, so a bare "yes" fires
  nothing. Two consecutive clarifiers → escalate to a human.
- **`configure:<slug>` exists because some products can't be carted** (SKILL.md §3.9). Any branch
  that surfaces a configurable bundle must arm *that* kind, so a bare "yes" opens the product page
  instead of building a cart the assistant had no right to build. Resolve cartability where the
  product is serialised, so every lane inherits it rather than each branch remembering.
- **New closed question in the copy ⇒ new offer kind, with a round-trip test.**

## 4. The basket is the source of truth

`basket.ts` holds pure operations (add / remove / set quantity / swap option), and **every edit sends
the whole basket through one cart call**. Consequences:

- The link, the rendered card and the sentence can't drift out of sync.
- **Never patch a remote cart line-by-line** — that's how other lines silently vanish.
- **Re-price through the API** on every edit; options within one product differ in price.
- **Persist quantity and cadence** so a swap can't silently change either.
- **Cap it** (lines, and per line). A runaway basket is a misparse, not an order.
- A quantity edit needs an actual **number**; a stray number must never reprice.
- **A configurable product never enters the basket** (§3.9) — the add path rejects it and opens its
  page, leaving the existing basket untouched.

## 5. Intent detection — the asymmetry that matters

Missing a purchase is friction; **inventing** one hijacks someone who wanted to read. So:

1. An explicit **learn** phrase beats a buy phrase → product page, never a cart.
2. A cart is built only on **explicit** purchase intent, or a stored offer that says so.
3. A **price question is not a purchase.**
4. **Membership/enrollment is a third purchase kind**, checked *before* subscription intent.
5. **A superlative is a product reference, not a question.**
6. 🔴 **Lanes that live inside a gate must be checked against the gate.** The swap ("I'd rather have
   the brushed one") and add-more ("also add the smaller one") phrasings carry **no purchase verb**,
   so the buy gate never opened and the branch inside was unreachable. Both shipped broken. When you
   add a lane inside a gate, verify the gate opens for its phrasing.

Pin ~40 buy phrasings plus the learn / subscribe / enroll / swap / repair vocabularies in tests.

## 6. The two-cart bridge

See `fluid-api.md` for the protocol. The implementation notes:

- The panel is a **cross-origin iframe** and cannot reach the storefront SDK. The loader owns it.
- **Resolve success from the SDK's success event, not the promise** — it resolves `undefined` on
  failure by design. A no-op emits nothing, so you need a timeout that reports failure.
- **Never render "in your cart" on a failure or timeout.** Fall back to the checkout link.

## 7. 🔴 Identity can't hang off a third-party cookie

The panel is a third-party iframe, so Safari blocks its cookie by default. Every request then mints a
fresh visitor — and "introduce once, ever" fires on the first message of **every** conversation.

**Fix:** seed the greeting the panel already painted as the thread's first assistant message when the
thread is created. That records something which genuinely happened and needs no cookie. Share one
`openingGreeting()` between the panel and the chat route — two copies of that string silently break
it.

Same reasoning moves conversation memory (`last_offer`, the basket) from the visitor row to the
**thread**, whose id the client echoes on every request.

⚠️ When probing the API directly, **absence of the introduction is the PASS condition**, not a
regression.

Cookie details that cost a cycle: `SameSite=None; Secure` in production because the chat is an
iframe; `SameSite=Lax` and insecure in local dev — **a `Secure` cookie is rejected over
`http://localhost`**, which silently breaks session persistence and looks exactly like a prompt bug.

## 8. Keeping data out of model context

Prompt rules are the second line of defence; the first is that the model never receives the data.

- **One serialiser, with a field allowlist.** Trim ~40 product fields to the ~12 quotable ones. Cost,
  supplier, internal ids, metafields and warehouse data never leave the server.
- **Stock is a boolean.** Drop numeric inventory in the trimmer. The model can't leak a number it
  never saw.
- **No admin token on the chat path.** Public reads and the cart API only.
- **Server-side tool allowlist.** Only known tool names dispatch; a model-emitted URL is never
  fetched.
- **Design tool signatures so hallucination is structurally impossible:** an "open this page" tool
  takes a *slug* and the server resolves the canonical URL; a "show the cart" tool takes **no
  argument** and the server injects the stored link.
- **Confirmation is a code gate, not a prompt rule.**

## 9. 🔴 The launcher: the wrapper must never be bigger than what you can see

The bug that broke an entire storefront on mobile, and read to the merchant as *"the theme isn't
responsive."*

A floating launcher is `position: fixed` at a huge z-index, and the closed panel usually stays in the
box (faded to `opacity: 0` so it can animate). **A fully transparent div with no background still
wins hit-testing.** On a 390×844 phone that dead zone measured ~358×692 — 92% of the viewport width —
killing add-to-cart, option pills, filter pills and footer links.

**Two guards, in this order:**

1. **Structural (the real fix):** make the panel and any teaser `position: absolute`, anchored above
   the button, so the root's box *is* just the button.
2. **`pointer-events: none` on the root**, re-armed to `auto` on the real controls only. Belt and
   braces, so a future in-flow child can't reintroduce it.

Two details that each cost a cycle:

- **Arm the teaser on its visible-state class, not the base class.** A card appended on every page
  load but only *shown* to first-time visitors leaves a permanent invisible blocker for everyone else
  if you arm the base class.
- 🔴 **One `position` per rule.** A second declaration later in the same block wins, silently putting
  the element back in flow *and* turning `bottom: 72px` from an anchor into a 72px offset.

**Acceptance test:** at a phone viewport, tap a control underneath the closed launcher box (a product
page's add-to-cart is sharpest) and confirm it fires; then confirm the launcher still opens and
closes.

Cosmetic notes worth copying: take an existing SDK slot rather than adding a third floating bubble;
copy the SDK's entrance keyframe verbatim and apply it to the **root**, never the button (a
`forwards` fill locks the transform and kills the hover state); equal boxes aren't equal perceived
weight, so a sparse glyph needs a larger size and heavier stroke than a dense one beside it.

### 9a. The attention pulse — scoped, not permanent

A soft ring expanding out of the launcher, drawn as a **pseudo-element** on the button so it adds no
node to the tree:

```css
.btn::after { content:''; position:absolute; inset:0; border-radius:9999px;
              border:2px solid <brand>; opacity:0; pointer-events:none; }
.root.has-teaser .btn::after { animation: ring 2.4s ease-out infinite; }
@keyframes ring { 0%{opacity:.7;transform:scale(1)} 70%{opacity:0;transform:scale(1.45)}
                  100%{opacity:0} }
```

Three decisions in that, and the middle one is the point:

1. 🔴 **The pulse is armed by the first-visit state, not by the base class.** It runs *while the
   greeting card is up* and then stops forever. A launcher that pulses on every page view, for every
   visitor, for the life of the site is not an invitation — it is a nag, and people learn to ignore
   it. Scope the animation to the moment you have something to say.
2. **`pointer-events: none` on the ring.** A pseudo-element scaled to 1.45 extends ~13px past its
   host's box on a 60px button, and it will happily take clicks out there — silently widening the
   launcher's hit area beyond anything visible. Same family as the §9 bug, one layer down.
3. **`opacity: 0` in the resting state**, so the ring is invisible when the animation isn't running
   rather than relying on the animation's `0%` frame to hide it.

### 9b. The first-visit greeting card

A small card above the launcher, shown **once per browser**, that introduces the assistant by name
and offers one CTA that opens the chat.

**State lives in `localStorage` on the storefront origin — deliberately, and this matters.** That is
first-party storage, so it survives the third-party cookie blocking that breaks the chat iframe's own
cookie (§7). The launcher is the one part of this system that *can* remember something reliably.
Wrap the reads and writes: private mode throws.

**Version the key** (`..._seen_v1`). Redesign the card later and you can re-show it once without
inventing a migration.

Six rules, each of which was a decision rather than a default:

- 🔴 **Mark it seen on DISPLAY, not on dismiss or open.** Otherwise "once per browser" quietly means
  "every page load until they interact", which is the most annoying possible reading.
- **Delay it (~1.8s).** Greeting after the page settles reads as a welcome; appearing instantly reads
  as an interruption.
- 🔴 **Auto-hide it (~12s), and treat that as a correctness rule rather than polish.** On a narrow
  screen the card overlaps the hero's primary CTA — **a greeting must never sit on top of the buy
  button.** If it can't be dismissed automatically, it shouldn't be shown.
- **Remove it from the DOM after its transition**, not just fade it, so it can't trap focus or
  clicks.
- **`role="status"` + `aria-live="polite"`** — announced to a screen reader without stealing focus.
  It's an aside, not a dialog.
- **Escape dismisses it** — and Escape while the panel is open closes the panel instead. One key,
  two states, most-recent-first.

🔴 **The card does NOT consume the server-side introduction.** It is client-side, easily missed,
dismissible without being read, and per-browser rather than per-person — so the conversation's own
first line still has to introduce the assistant when they actually open it (§7, `introduced_at`).
Two surfaces, two jobs: the card is a poster, the greeting is a conversation. Wiring the card into
the introduce-once flag produces a person who never says hello to anyone who ignored a poster.

**And honour `prefers-reduced-motion`:** kill the entrance slide, the card's transition **and the
pulse ring**. A permanently-animating ring is exactly what that setting exists to stop.

### 9c. Let the page open it

Two small affordances that cost nothing and get used immediately:

- **A data attribute** (`data-<name>-open`) wired on mount, so any link, button or banner the theme
  already has can open the assistant without touching this script.
- **A global** with `open()`, `close()` and — genuinely useful — **`resetTeaser()`**, which clears the
  first-visit key so the greeting can be demonstrated on demand. You will want this within an hour of
  shipping.

### 9d. Launcher implementation notes, app side

- **Ship the loader as a static `.js` file**, not a route returning a template literal. Two
  documented traps disappear at once: a backtick anywhere in loader prose closes the string
  (typecheck passes, dev server 500s), and a `# Reference implementation — what a real build learned

Architecture and hard-won traps from building this skill into a live storefront assistant. Read
before writing code. Nothing here is company-specific; every item shipped as a bug first.

## Shape

```
Storefront page
  └─ loader script → launcher + iframe        (public, no secrets; OWNS THE SDK BRIDGE)
        │  POST /api/assistant/chat  { message, thread_id }   ← SSE stream back
        ▼
Mist app (Next.js, Fluid hosting) + Postgres
  ├─ /api/assistant/chat      SSE: session | delta | tool | ui | violation | done | error
  ├─ /api/assistant/session   cookie mint
  ├─ /embed                   the chat panel (server half = first paint, client half = stream)
  ├─ /assistant               local harness with probe buttons
  ├─ /<loader>-test           hit-testing harness: the real loader over a grid of tap targets
  └─ lib/assistant/
       config.ts        env + boot invariants — THROWS if the assistant name is unset
       profile.ts       THE ONLY FILE WITH COMPANY FACTS
       greeting.ts      the opening line — shared by the panel AND the chat route
       storefront.ts    public reads + field allowlist (the only serialiser)
       cart.ts          the only module that talks to the cart API
       basket.ts        pure basket ops — the source of truth for cart composition
       offers.ts        typed standing offers + the clarify marker
       needs.ts         problem → product, matched against DESCRIPTIONS
       intent.ts        buy / edit / swap / repair / account / affirmation detection
       tools.ts         tool specs + dispatcher — POLICY IS ENFORCED HERE
       prompt.ts        system prompt (MODEL PATH ONLY — see §1)
       guard.ts         outbound refusal + off-brand scans
       session.ts       signed cookie
       repository.ts    tenant-scoped persistence
```

## Two answer paths, one dispatcher

With a model key configured, the model plans. Without one, a deterministic rules planner does —
through the **same dispatcher, the same suppression list, the same allowlist, the same guards**. The
stream reports which path served the turn, so no surface can pass the rules engine off as a model.

Worth the extra module: the whole pipeline is testable before a key exists, and the fallback is
honest rather than silent. **Production should refuse rather than fall back.**

## 1. 🔴 Anything that lives only in the prompt does not affect live behaviour

The prompt is read by **the model path only**. With no model key the rules planner is live and never
sees it. Brand voice was injected into the prompt and nowhere else, so the company's guide was applied
exclusively to the code path that wasn't running — while live copy read like a support macro.

**Rule: voice and policy must reach the dispatcher or the planner.** A rule in the prompt is a
suggestion; a rule in the dispatcher is a rule.

Corollaries:

- **Hand-written copy bypasses every guard** unless a **test** runs the guard over it. This has caught
  a refusal phrase four times.
- Run a **tone guard** (off-brand vocabulary from the profile) in parallel with the refusal guard,
  over the same canned strings.
- **Word-boundary match the off-brand list.** A brand's own coinage can contain a banned substring —
  one brand's playful compound contained "optimal", which its guide bans.
- **Never run the off-brand guard over the prompt itself** — the prompt deliberately quotes the
  off-brand counter-example in order to reject it.

## 2. Boot invariants, and how the name is wired

- **Throw if the assistant-name env var is unset.** Never default to "Assistant" — that ships to a
  customer. A missing name is a broken install, and the loud failure is the feature.
- **Refuse to serve chat if the company profile is missing or still the template.** An assistant
  without a profile has no lanes and no suppression list; it will recommend spare parts and invent a
  personality. A loud failure beats a plausible one.
- **One module owns the name** (`config.ts`, a single exported constant). Every surface imports it:
  launcher label, chat header, avatar alt text, the greeting module, the system prompt, the handoff
  email subject. **Never interpolate the literal into a template** — a hardcoded name is invisible
  until the day it's wrong on exactly one surface.
- **Renaming is one env var plus a redeploy** (production env changes don't apply until the app is
  rebuilt) — plus one decision that must be made consciously: the introduce-once flag is already set
  for returning people, so either clear it for a fresh introduction or acknowledge the change in the
  greeting. **Never rewrite past transcripts**; they record what was actually said.
- 🔴 **Assert the literal name in exactly one test** — the one that renders every surface and checks
  each shows the configured name. Use the constant everywhere else. That test is the rename canary:
  it fails on a rename (update one expected value), and **any other failure is a surface that
  hardcoded the name**.

## 3. Offers are data, not prose

The single highest-value structural change in the build. Every closed question the assistant asks gets
a **typed** offer written to the thread when made, and parsed when affirmed:

```
cart:<slug> · configure:<slug> · fit:<slug> · compare:<slug> · lineup · enroll · human
```

- **An audit found 7 of 10 offers unarmed.** Assume yours are too until you enumerate them.
- **Define each answer once**, shared by the branch that offers it and the resolver that honours it,
  so promise and delivery can't drift.
- **`parse("cart")` with no slug returns null.** Building a cart for a product nobody named is the
  worst available outcome.
- **The offer moves with the subject.** An out-of-stock reply that says "want that one instead?" must
  rearm to the *alternative*.
- **A clarifying question is marked, and is deliberately NOT an offer**, so a bare "yes" fires
  nothing. Two consecutive clarifiers → escalate to a human.
- **`configure:<slug>` exists because some products can't be carted** (SKILL.md §3.9). Any branch
  that surfaces a configurable bundle must arm *that* kind, so a bare "yes" opens the product page
  instead of building a cart the assistant had no right to build. Resolve cartability where the
  product is serialised, so every lane inherits it rather than each branch remembering.
- **New closed question in the copy ⇒ new offer kind, with a round-trip test.**

## 4. The basket is the source of truth

`basket.ts` holds pure operations (add / remove / set quantity / swap option), and **every edit sends
the whole basket through one cart call**. Consequences:

- The link, the rendered card and the sentence can't drift out of sync.
- **Never patch a remote cart line-by-line** — that's how other lines silently vanish.
- **Re-price through the API** on every edit; options within one product differ in price.
- **Persist quantity and cadence** so a swap can't silently change either.
- **Cap it** (lines, and per line). A runaway basket is a misparse, not an order.
- A quantity edit needs an actual **number**; a stray number must never reprice.
- **A configurable product never enters the basket** (§3.9) — the add path rejects it and opens its
  page, leaving the existing basket untouched.

## 5. Intent detection — the asymmetry that matters

Missing a purchase is friction; **inventing** one hijacks someone who wanted to read. So:

1. An explicit **learn** phrase beats a buy phrase → product page, never a cart.
2. A cart is built only on **explicit** purchase intent, or a stored offer that says so.
3. A **price question is not a purchase.**
4. **Membership/enrollment is a third purchase kind**, checked *before* subscription intent.
5. **A superlative is a product reference, not a question.**
6. 🔴 **Lanes that live inside a gate must be checked against the gate.** The swap ("I'd rather have
   the brushed one") and add-more ("also add the smaller one") phrasings carry **no purchase verb**,
   so the buy gate never opened and the branch inside was unreachable. Both shipped broken. When you
   add a lane inside a gate, verify the gate opens for its phrasing.

Pin ~40 buy phrasings plus the learn / subscribe / enroll / swap / repair vocabularies in tests.

## 6. The two-cart bridge

See `fluid-api.md` for the protocol. The implementation notes:

- The panel is a **cross-origin iframe** and cannot reach the storefront SDK. The loader owns it.
- **Resolve success from the SDK's success event, not the promise** — it resolves `undefined` on
  failure by design. A no-op emits nothing, so you need a timeout that reports failure.
- **Never render "in your cart" on a failure or timeout.** Fall back to the checkout link.

## 7. 🔴 Identity can't hang off a third-party cookie

The panel is a third-party iframe, so Safari blocks its cookie by default. Every request then mints a
fresh visitor — and "introduce once, ever" fires on the first message of **every** conversation.

**Fix:** seed the greeting the panel already painted as the thread's first assistant message when the
thread is created. That records something which genuinely happened and needs no cookie. Share one
`openingGreeting()` between the panel and the chat route — two copies of that string silently break
it.

Same reasoning moves conversation memory (`last_offer`, the basket) from the visitor row to the
**thread**, whose id the client echoes on every request.

⚠️ When probing the API directly, **absence of the introduction is the PASS condition**, not a
regression.

Cookie details that cost a cycle: `SameSite=None; Secure` in production because the chat is an
iframe; `SameSite=Lax` and insecure in local dev — **a `Secure` cookie is rejected over
`http://localhost`**, which silently breaks session persistence and looks exactly like a prompt bug.

## 8. Keeping data out of model context

Prompt rules are the second line of defence; the first is that the model never receives the data.

- **One serialiser, with a field allowlist.** Trim ~40 product fields to the ~12 quotable ones. Cost,
  supplier, internal ids, metafields and warehouse data never leave the server.
- **Stock is a boolean.** Drop numeric inventory in the trimmer. The model can't leak a number it
  never saw.
- **No admin token on the chat path.** Public reads and the cart API only.
- **Server-side tool allowlist.** Only known tool names dispatch; a model-emitted URL is never
  fetched.
- **Design tool signatures so hallucination is structurally impossible:** an "open this page" tool
  takes a *slug* and the server resolves the canonical URL; a "show the cart" tool takes **no
  argument** and the server injects the stored link.
- **Confirmation is a code gate, not a prompt rule.**

## 9. 🔴 The launcher: the wrapper must never be bigger than what you can see

The bug that broke an entire storefront on mobile, and read to the merchant as *"the theme isn't
responsive."*

A floating launcher is `position: fixed` at a huge z-index, and the closed panel usually stays in the
box (faded to `opacity: 0` so it can animate). **A fully transparent div with no background still
wins hit-testing.** On a 390×844 phone that dead zone measured ~358×692 — 92% of the viewport width —
killing add-to-cart, option pills, filter pills and footer links.

**Two guards, in this order:**

1. **Structural (the real fix):** make the panel and any teaser `position: absolute`, anchored above
   the button, so the root's box *is* just the button.
2. **`pointer-events: none` on the root**, re-armed to `auto` on the real controls only. Belt and
   braces, so a future in-flow child can't reintroduce it.

Two details that each cost a cycle:

- **Arm the teaser on its visible-state class, not the base class.** A card appended on every page
  load but only *shown* to first-time visitors leaves a permanent invisible blocker for everyone else
  if you arm the base class.
- 🔴 **One `position` per rule.** A second declaration later in the same block wins, silently putting
  the element back in flow *and* turning `bottom: 72px` from an anchor into a 72px offset.

**Acceptance test:** at a phone viewport, tap a control underneath the closed launcher box (a product
page's add-to-cart is sharpest) and confirm it fires; then confirm the launcher still opens and
closes.

Cosmetic notes worth copying: take an existing SDK slot rather than adding a third floating bubble;
copy the SDK's entrance keyframe verbatim and apply it to the **root**, never the button (a
`forwards` fill locks the transform and kills the hover state); equal boxes aren't equal perceived
weight, so a sparse glyph needs a larger size and heavier stroke than a dense one beside it.

### 9a. The attention pulse — scoped, not permanent

A soft ring expanding out of the launcher, drawn as a **pseudo-element** on the button so it adds no
node to the tree:

```css
.btn::after { content:''; position:absolute; inset:0; border-radius:9999px;
              border:2px solid <brand>; opacity:0; pointer-events:none; }
.root.has-teaser .btn::after { animation: ring 2.4s ease-out infinite; }
@keyframes ring { 0%{opacity:.7;transform:scale(1)} 70%{opacity:0;transform:scale(1.45)}
                  100%{opacity:0} }
```

Three decisions in that, and the middle one is the point:

1. 🔴 **The pulse is armed by the first-visit state, not by the base class.** It runs *while the
   greeting card is up* and then stops forever. A launcher that pulses on every page view, for every
   visitor, for the life of the site is not an invitation — it is a nag, and people learn to ignore
   it. Scope the animation to the moment you have something to say.
2. **`pointer-events: none` on the ring.** A pseudo-element scaled to 1.45 extends ~13px past its
   host's box on a 60px button, and it will happily take clicks out there — silently widening the
   launcher's hit area beyond anything visible. Same family as the §9 bug, one layer down.
3. **`opacity: 0` in the resting state**, so the ring is invisible when the animation isn't running
   rather than relying on the animation's `0%` frame to hide it.

### 9b. The first-visit greeting card

A small card above the launcher, shown **once per browser**, that introduces the assistant by name
and offers one CTA that opens the chat.

**State lives in `localStorage` on the storefront origin — deliberately, and this matters.** That is
first-party storage, so it survives the third-party cookie blocking that breaks the chat iframe's own
cookie (§7). The launcher is the one part of this system that *can* remember something reliably.
Wrap the reads and writes: private mode throws.

**Version the key** (`..._seen_v1`). Redesign the card later and you can re-show it once without
inventing a migration.

Six rules, each of which was a decision rather than a default:

- 🔴 **Mark it seen on DISPLAY, not on dismiss or open.** Otherwise "once per browser" quietly means
  "every page load until they interact", which is the most annoying possible reading.
- **Delay it (~1.8s).** Greeting after the page settles reads as a welcome; appearing instantly reads
  as an interruption.
- 🔴 **Auto-hide it (~12s), and treat that as a correctness rule rather than polish.** On a narrow
  screen the card overlaps the hero's primary CTA — **a greeting must never sit on top of the buy
  button.** If it can't be dismissed automatically, it shouldn't be shown.
- **Remove it from the DOM after its transition**, not just fade it, so it can't trap focus or
  clicks.
- **`role="status"` + `aria-live="polite"`** — announced to a screen reader without stealing focus.
  It's an aside, not a dialog.
- **Escape dismisses it** — and Escape while the panel is open closes the panel instead. One key,
  two states, most-recent-first.

🔴 **The card does NOT consume the server-side introduction.** It is client-side, easily missed,
dismissible without being read, and per-browser rather than per-person — so the conversation's own
first line still has to introduce the assistant when they actually open it (§7, `introduced_at`).
Two surfaces, two jobs: the card is a poster, the greeting is a conversation. Wiring the card into
the introduce-once flag produces a person who never says hello to anyone who ignored a poster.

**And honour `prefers-reduced-motion`:** kill the entrance slide, the card's transition **and the
pulse ring**. A permanently-animating ring is exactly what that setting exists to stop.

### 9c. Let the page open it

Two small affordances that cost nothing and get used immediately:

- **A data attribute** (`data-<name>-open`) wired on mount, so any link, button or banner the theme
  already has can open the assistant without touching this script.
- **A global** with `open()`, `close()` and — genuinely useful — **`resetTeaser()`**, which clears the
  first-visit key so the greeting can be demonstrated on demand. You will want this within an hour of
  shipping.

 before an interpolation vanishes silently.
- **Derive the app origin from `document.currentScript.src`.** A hardcoded origin is how a staging
  panel ends up on production.
- 🔴 **CSS specificity beats intent.** `#root .btn svg {display:block}` (id+class+type) silently
  out-specifies `#root .ico-close {display:none}` (id+class), so **both icons render at once**. Give
  both icon states equal specificity and let source order decide.
- **`z-index` ~9990, not the maximum.** Above page content, **below** the cart drawer and the mobile
  menu, so the bubble never floats over an open drawer or nav.
- 🔴 **`getBoundingClientRect()` includes transforms.** An SDK button with `animation-delay` and
  `fill-mode: both` has its `0%` keyframe translate applied **backwards** during the delay — and
  **permanently** when animations are suppressed (headless, or `prefers-reduced-motion`). Subtract
  the element's own matrix, or measure `offsetWidth`/`offsetHeight`.
- **Bounded retries are not enough for an SDK-injected custom element.** A 4s cap missed the widget
  entirely and failed *silently*. Poll until found.
- **Make invisible failures observable.** Writing the outcome to a `data-*` attribute on the root
  collapsed three rounds of guessing into one read. Do this for anything that can silently decline to
  act — and expose harness-only overrides for timed behaviour (a teaser delay, an auto-hide) so tests
  reach a state deterministically instead of racing a timer.
- 🔴 **The panel's metadata pollutes the host page.** A crawler reads a framed document's metadata as
  the host's, so a storefront's description absorbed the app's default template title. Own the embed
  route's metadata and mark it `noindex` — and it must be a **route layout**, because a client
  component cannot export metadata and the Pages-Router head API silently does nothing.
- **postMessage exact origins in both directions.** The loader passes its own origin into the panel
  as a query param; never guess from `referrer`, never use a wildcard.

## 10. Testing floor

Every behavioural change needs a test that would fail without it. Then typecheck, lint **and build**.

⚠️ **Typecheck is not enough when the prompt is a template literal.** A backtick anywhere in the
prose — **including inside a CSS comment** in the loader — closes the string. Typecheck passes; the
dev server 500s. **Only a full build catches it.** This bit three times. Never use backticks in
prompt or loader prose.

⚠️ **A `$` immediately before an interpolation does not survive an edit reliably.** The literal `$`
gets dropped and the sentence still reads fine — "costs about 40 a month" — so nothing looks broken.
Use a **pre-formatted display constant** and pin it to the number with a test.

⚠️ **Canned strings bypass the outbound guards**, which only see model output. Run both guards over
hand-written copy in tests.

⚠️ **New test files must set env in `beforeAll`** — the config module throws on import by design.

⚠️ 🔴 **The harness must carry EVERY piece of state the route carries.** A multi-turn helper that
threads the offer and the basket but not the newest field will pass whatever you write and prove
nothing. This bit **three separate times in one build**.

⚠️ **Never hardcode a fixture id in an assertion.** Twice a typed-from-memory variant id failed a
test whose behaviour was correct. Read the id from the fixture, or assert the observable fact —
quantity, subtotal, the option name.

⚠️ **Two-message tests are not optional.** Anything involving conversational memory — the subject, a
standing offer, a delta against a ledger — is invisible to a single-message suite. Every one of those
bugs shipped with a green test run.

**Other toolchain traps, each of which cost a round trip:**

| Trap | Detail |
|---|---|
| `CREATE TABLE IF NOT EXISTS` | Adds **no columns** to an existing table. New columns need their own idempotent `ALTER … ADD COLUMN IF NOT EXISTS`. |
| Adding a route `layout.tsx` | Makes typecheck fail against a **stale** generated route validator. Run a full build once to regenerate — not a real error. |
| Synchronous timers | A timer implementation may fire synchronously. Declare the handle with `let` **before** the closure that clears it, or hit a temporal dead zone. |
| Unconfigured lint rules | An `eslint-disable-next-line` for a rule that isn't configured is **itself** a lint error. Don't write the disable comment. |
| Cross-project reach | A Mist project cannot write to a sibling theme project, and cannot read a skill project's files at all. **`run_skill` returns SKILL.md plus every file in `references/`** — that is how a build project reads the playbook. |

⚠️ **Don't assert on raw wrapped prose** from a template literal; a line break can land between any
two words. Collapse whitespace first.

## 11. Verification discipline

The habits that caught real bugs, and the traps that hid them.

- **Run the negative control.** A check that would also pass for deliberately invalid input is not
  verification. (A `return_to` parameter appears on a login page for a nonsense route too.)
- **Fetch a URL yourself before telling another agent to rely on it.** An upload that returns an id
  is not proof the URL serves, with the right content type, un-truncated.
- **Ship a sha256 with any file you hand over**, so the receiver can prove the write wasn't lossy —
  and say explicitly which copy is stale when you supersede one.
- **HEAD the URLs the deployed app emits.** A well-formed URL is not a resolving one — this is how a
  404 image rendition on the best seller was found.
- **Reproduce before fixing.** Every operator report in one build was reproduced against production
  first; twice that changed the diagnosis.
- **Say what the tooling cannot prove.** Two honest gaps worth copying verbatim: a crawler cannot
  reproduce a layout that depends on an SDK's compiled stylesheet, so it cannot verify corner
  auto-stacking; and the add-to-real-cart round trip needs a real browser, because the panel is a
  cross-origin iframe. Report those as **unverified** rather than claimed.

### 🔴 Fix the mechanism, not the sentence

Four separate "it can't find an obvious product" reports were filed on one build. The first three were
patched at the **phrase** level — add a pattern, special-case a wording — and each time the next
phrasing broke. All four had one cause: a scoring threshold that discarded the top-ranked candidate.

**If the same class of complaint arrives twice, stop patching and go read the mechanism.** The
operator said *"we're running into too much of this"* before that was worked out, and they were
right.

Corollary, which appeared **four times** in one build: **when a helper is reused for a different
question than it was written for, its permissive default becomes a bug.** Standing offers, safety
routes, option resolution and quantity parsing were all instances.
- **Measure, don't eyeball.** A ~60px placement shift is invisible at thumbnail scale. Crop the
  *same* region from before/after captures and compare.
- ⚠️ **A network-frozen isolated preview does not execute injected scripts** — the launcher is simply
  absent, so every synthetic tap test passes. Test loader behaviour against the deployed URL.
- ⚠️ **Automation can't reliably click a toggle.** A double-dispatched click nets zero on
  `setOpen(!open)` while an idempotent `setOpen(true)` works fine. Prefer an idempotent control when
  verifying; otherwise expect a false negative and ask a human.
- ⚠️ **Interaction tooling refuses mutation controls**, so add-to-cart and cart cards are verified by
  payload plus documented contract, never by pixels. **Say so plainly** rather than implying they
  were clicked.
- **Two identical screenshot hashes** across runs is a useful signal that page state didn't change.

## 12. Deploy: a push that succeeds is not a deploy that happened

Seen live: the watch flag printed *"Locating deployment for commit X… still waiting"* until it timed
out, and **no build was ever created** — the push landed on the remote and the build hook never fired.
Distinguish three states before reacting:

| Symptom | Meaning | What to do |
|---|---|---|
| `git log` shows the commit at HEAD, push output shows the ref update | the code IS on the remote | do **not** re-commit |
| the deployments list shows the commit as `error` | the build ran and failed | read the log, fix, push |
| the deployments list does not list the commit **at all** | the build was never triggered | nothing client-side to retry |

In the third case a re-run of push is a **no-op** (nothing new to commit), and so is a lifecycle
retry — it exits 0 having done nothing. The fix is to give the hook something new to react to: **make
a trivial follow-up commit** (a doc line is ideal — real content, zero runtime risk) and push that.
Confirm the new commit appears as ready before claiming anything shipped.

Then **probe production directly** — post a message to the chat endpoint, read the streamed text,
check the violations array is empty, and echo the thread id to exercise multi-turn behaviour (offers,
basket edits, swaps). Local success is not deployment success.

## 13. Observability

Per turn: tenant, thread, surface, intent, tools called, error kind, whether the confirmation gate
fired, latency. Then watch:

- **cart rate** — turns that produced a cart, split by add-to-cart vs link
- **handoff rate**, and the reason split
- **not-found / refused rate** — usually a stale profile
- **banned-phrase hits** (refusal *and* off-brand) — should be zero; alert otherwise
- **re-introduction rate** — also zero, and the canary for the cookie trap in §7
- **unresolved-affirmation rate** — a bare "yes" that resolved to nothing is an unarmed offer (§3)

The last three are the cheapest possible guards on the rules a customer actually feels.

## 14. Authoring rules that bite once each

🔴 **A build log has two places it can be destroyed, and they are not obvious.**

1. **`references/*.md` is appended to the skill body at run time.** A build log, status report or
   findings dump left there is injected into the assistant's system prompt — silently, and forever.
2. **The project root is replaced when the skill is updated.** Verified the hard way: a log written
   to the root was **gone** after the operator updated the skill. `references/` and the catalogue
   index survived; the root `.md` did not.

**So write build logs to `docs/`** — outside the runtime prompt, and outside the blast radius of an
update. Keep `references/` to exactly what the runtime needs.

🔴 **When you add a section to a numbered reference, grep for stale cross-references.** Inserting a
new §14 pushed "Build order" to §15, and a pointer in `SKILL.md` kept saying §14 — so a handoff sent
a build agent to the wrong section. Numbered headings are an interface: renumbering one is a breaking
change to every file that cites it. `rg '§1[0-9]'` across the bundle takes two seconds.

**Ship empty guard lists rather than invented ones.** Where a company has no brand guide, the
off-brand vocabulary guard should ship as **real code with an empty word list** — not with bans you
made up and attributed to the brand. Adding words later becomes configuration; inventing them now
becomes a fake constraint nobody can trace. Same reasoning for a `parts` lane on a catalogue with no
spare parts: wire it inert, mark the tests **N/A, and never fake a fixture to make one pass.**

## 15. Build order

1. Session + thread store + chat loop with catalogue and UI tools → substance and safety tests.
2. Cart + both cart controls → the purchase tests.
3. Offers-as-data + the affirmation resolver → the offer tests.
4. Problem-matching and the medical guard → the needs and safety tests.
5. The parts lane → the repair tests.
6. Account signposting with verified UI copy and verified destinations → the reach tests.
7. Verified customer auth, then account reads, then mutations behind the confirmation gate.

Do not skip step 7's gate: a mutation shipped before the confirmation gate is the one bug here that
costs a real customer real money.
