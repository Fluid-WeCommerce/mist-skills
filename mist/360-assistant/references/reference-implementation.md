# Reference implementation — what a real build learned

Architecture and hard-won traps from building this skill into a live Mist app. Read before writing
code. Nothing here is company-specific.

## Shape

```
Storefront page
  └─ loader script → launcher + iframe        (public, no secrets)
        │  POST /api/assistant/chat  { message }   ← SSE stream back
        ▼
Mist app (Next.js, Fluid hosting) + Postgres
  ├─ /api/assistant/session   cookie mint + one-time introduction claim
  ├─ /api/assistant/chat      SSE: session | delta | tool | ui | violation | done | error
  ├─ /embed                   the chat panel
  ├─ /assistant               local harness with probe buttons
  └─ lib/assistant/
       config.ts        env + boot invariants — THROWS if ASSISTANT_NAME is unset
       profile.ts       THE ONLY FILE WITH COMPANY FACTS
       storefront.ts    public reads + field allowlist (the only serialiser)
       cart.ts          the only module that talks to the cart API
       session.ts       signed cookie
       repository.ts    tenant-scoped persistence
       tools.ts         tool specs + dispatcher — POLICY IS ENFORCED HERE
       prompt.ts        system prompt
       guard.ts         outbound banned-phrase scan
       intent.ts        buy / account / superlative / affirmation detection
```

## Two answer paths, one dispatcher

With a model key configured, the model plans. Without one, a deterministic rules planner does —
through the **same dispatcher, the same suppression list, the same outbound guard**. The stream
reports which path served the turn, so no surface can pass the rules engine off as a model.

This is worth the extra module: the whole pipeline is testable before a key exists, and the
fallback is honest rather than silent. **Production should refuse rather than fall back** — a
deterministic planner is a development harness, not a degraded model.

## Boot invariants

- **Throw if `ASSISTANT_NAME` is unset.** Never default to "Assistant" — that ships to a customer.
- **Refuse to serve chat if the company profile is missing or still the template.** An assistant
  without a profile has no lanes and no suppression list; it will recommend spare parts and invent
  a personality. A loud failure beats a plausible one.

## Identity and the introduce-once rule

One row per **person**, unique on `(company_id, visitor_id)`, carrying `introduced_at`. That column
is how "introduce yourself once, ever" is enforced — in data, not by hoping the model remembers.
Every row carries `company_id` (from server env, never from a request) and **every query filters on
it**; a missing tenant predicate is a cross-company data leak.

If both a public and a signed-in surface ever exist, merge threads on verified identity only, and
never across tenants.

## Cookie

`SameSite=None; Secure` in production, because the chat is an iframe on the storefront.
`SameSite=Lax` and insecure in local dev — **a `Secure` cookie is rejected over `http://localhost`**,
which silently breaks session persistence and makes the assistant re-introduce itself on every
message. That looks like a prompt bug and is not.

## Keeping data out of model context

Prompt rules are the second line of defence; the first is that the model never receives the data.

- **One serialiser, with a field allowlist.** Trim ~40 product fields to the ~12 quotable ones
  before anything enters context. Cost, supplier, internal ids, metafields and warehouse data never
  leave the server.
- **Stock is a boolean.** Drop any numeric inventory figure in the trimmer. The model cannot leak a
  number it never saw.
- **No admin token on the chat path.** Public reads, cart token, customer session — nothing else.
- **Server-side tool allowlist.** Only known tool names dispatch; a model-emitted URL is never
  fetched.
- **Design the tool signatures so hallucination is structurally impossible:** a "open this page"
  tool takes a *slug* and the server resolves the canonical URL; a "show the cart link" tool takes
  **no argument** and the server injects the stored URL; a verify-code tool takes only the code,
  with the challenge id held server-side.
- **Confirmation is a code gate, not a prompt rule.** Any mutation requires a `pending_write` row
  matching tool + args, created on a *previous* turn.

## Intent detection — the asymmetry that matters

Missing a purchase is friction; **inventing** one hijacks someone who wanted to read. So:

1. An explicit **learn** phrase beats a buy phrase → product page, never a cart.
2. A cart is built only on **explicit** purchase intent.
3. A **price question is not a purchase** — quote, offer, wait.
4. A bare **"yes"** only buys when the assistant just offered that exact cart (store `last_offer`).
5. **Membership/enrollment is a third purchase kind**, checked *before* subscription intent, so
   "sign up for the club" isn't read as an autoship while "sign me up for monthly delivery" still is.
6. **A superlative is a product reference, not a question.** "Your most popular one" means *pick
   for me*; bouncing it back is the bug.
7. **An accepted offer needs its own lane, ahead of the buy gate.** The sentence that takes up "say
   the word and I'll swap it" carries no purchase verb — "I'd rather have the other finish" — so buy
   detection misses it entirely. Match the option, rebuild the cart, re-quote. Fall through
   untouched when nothing matches, so "actually, tell me more" stays a learn request.

Pin ~40 buy phrasings plus the learn/subscribe/enroll vocabularies in tests. Conversation context
(`last_product_slug`) is what makes "I'll take it" resolve instead of guess.

### The most expensive bug class: copy that offers what no lane implements

This shipped once and is worth internalising. The assistant offered a variant swap in its own
words — *"say the word and I'll swap it"* — and the phrasing that naturally accepts that offer hit
no intent lane, so it fell through to a generic clarifier. The customer said yes and the product
said "sorry, what?".

**Any copy that invites a follow-up is a promise, and it needs a matching lane plus a test.** Add
the lane in the same change as the invitation. Then audit the invitations already in your copy for
the same gap — there is usually more than one.

Cheap to get wrong alongside it: a swap must **persist quantity and cart kind** (`last_quantity`,
`last_cart_kind` beside `last_offer`). Turning a 2-unit order into 1, or a subscription into a
one-off, while "just changing the colour" is a money bug.

## Testing floor

Every behavioural change needs a test that would fail without it. Then typecheck, lint **and
build**.

⚠️ **Typecheck is not enough if the system prompt is a template literal.** A stray backtick in the
prose closes the string: typecheck passes, the dev server 500s. **Only a full build catches it.**
This bit twice. Never use backticks inside prompt text.

⚠️ **Canned strings bypass the outbound guard**, which only ever sees model output. Run the guard
over hand-written copy in tests.

⚠️ **Interaction-testing tools may refuse harness probe buttons** as mutation controls, so verify
cart and account cards by inspecting the response payload rather than pixels — and get a human
glance before shipping.

## Deploy and verify

Push, then **probe production directly** rather than assuming: post a message to the chat endpoint,
read the streamed text, and check the violations array is empty. Local success is not deployment
success.

## Observability

Per turn: tenant, thread, surface, intent, tools called, error kind, whether the confirmation gate
fired, latency. Then watch six numbers — **cart-link rate**, **handoff rate**, **not-found /
refused rate** (usually a stale profile), **auth-failure rate**, **banned-phrase hits** (should be
zero; alert otherwise), and **re-introduction rate** (also zero).

The last two are the cheapest possible guard on the two rules a customer actually feels.

## Build order

1. Session + thread store + chat loop with catalogue and UI tools → the substance and safety tests.
2. Cart + link → the purchase tests.
3. Account signposting with verified UI copy → the reach tests.
4. Verified customer auth, then any account reads.
5. Mutations, behind the confirmation gate.
6. Handoff + the banned-phrase regex in CI.

Do not skip step 5's gate: a mutation shipped before the confirmation gate is the one bug here that
costs a real customer real money.
