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

⚠️ **Don't assert on raw wrapped prose** from a template literal; a line break can land between any
two words. Collapse whitespace first.

## 11. Verification discipline

The habits that caught real bugs, and the traps that hid them.

- **Run the negative control.** A check that would also pass for deliberately invalid input is not
  verification. (A `return_to` parameter appears on a login page for a nonsense route too.)
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

## 14. Build order

1. Session + thread store + chat loop with catalogue and UI tools → substance and safety tests.
2. Cart + both cart controls → the purchase tests.
3. Offers-as-data + the affirmation resolver → the offer tests.
4. Problem-matching and the medical guard → the needs and safety tests.
5. The parts lane → the repair tests.
6. Account signposting with verified UI copy and verified destinations → the reach tests.
7. Verified customer auth, then account reads, then mutations behind the confirmation gate.

Do not skip step 7's gate: a mutation shipped before the confirmation gate is the one bug here that
costs a real customer real money.
