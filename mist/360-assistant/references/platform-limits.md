# Platform limits — where an embedded assistant can and cannot live

Findings from a real build. Each was attempted, verified, and in one case reverted. They are
platform constraints, not company quirks, so check them before promising a surface — and re-check
them before assuming they still hold, because platforms change.

## Storefront: works

A theme with a `content_for_header` (or equivalent global script slot) can load a launcher on every
page. That is what makes a persistent, cross-page assistant possible at all.

⚠️ **Installing the launcher edits a production theme, so it needs explicit operator sign-off** —
identify the *active* theme rather than assuming, and don't push to it as part of setup. A
badly-built launcher covers most of a phone viewport with a transparent div and kills add-to-cart
sitewide (`reference-implementation.md` §9), which is a merchant-visible outage rather than a
cosmetic bug.

Two details worth copying:

- **Take an existing slot rather than adding a third control.** Commerce SDKs often already render
  their own floating buttons. Hiding a lower-value one (a lead-capture bubble) and taking its place
  keeps the corner at two controls instead of three.
- **Match the host's own motion.** Copy the SDK's entrance keyframe so the launcher arrives the way
  the cart does. Apply it to the root element, never the button — a `forwards` fill on the button
  locks its transform and kills the hover state.

## Account destinations: verify one serves a sign-in before you link it

A hosted "manage my account" surface can return **200 to a logged-out visitor and render an empty
shell** — placeholder company name, blank name and email, empty addresses and payment methods, and
**no sign-in form anywhere in the HTML**. Adding a shop query parameter changes nothing. Verified on
Fluid's `checkout.<apex>/manage` surface.

Since every visitor an unauthenticated assistant talks to is logged out, linking such a page strands
**100%** of them: they land somewhere that looks like their account, shows them nothing, and offers
no way in.

Two rules follow, and both belong in code rather than prose:

1. **A destination qualifies only if a logged-out request serves a real sign-in** — or redirects to
   one that preserves the destination. Fetch it and look for the form. A `200` proves nothing.
2. **Pin the disqualified hosts and paths in a regression test**, so a later refactor cannot
   reintroduce them.

The tenant portal (`<shop>.portal.<apex>`) behaves correctly by comparison: `/orders`,
`/subscriptions` and `/profile` are real per-page URLs, and a logged-out deep link self-redirects
through login while preserving the destination.

### 🔴 "The path resolves" is not "this is the destination to send people to"

The most instructive correction from a real build, because the verification was **accurate and
irrelevant**.

Deep links into a tenant portal (`/orders`, `/subscriptions`) were verified to work: each served a
real login and preserved the destination through it. Both facts true. The operator still corrected
it — their convention is that the assistant links the **portal root** and nothing deeper.

Which one is right is not something you can discover from the API. **Where to send a customer is an
operator convention; what technically resolves is an implementation detail.** Confusing the second
for the first produces a change nobody asked for that passes every test you thought to write.

**So ask.** One question during setup: *"when the assistant sends someone to their account, should
it link the portal root, or deep-link the exact screen?"* Record the answer in the profile and pin it
with a test asserting the shape of every emitted account URL — root-only, or deep-linked.

Two consequences for walkthrough copy, and **which applies depends on that answer**:

- **If you deep-link**, don't name a tab — the person is already standing on that page, so naming it
  is confusing. Describe what's *on* the screen instead.
- **If you link the root**, the copy **must** name where to go once inside. A root link with no
  onward directions dead-ends the customer on a login page, which is worse than either alternative.
- **Either way, keep exactly one steps table per destination.** When a destination changes, the
  walkthrough describing it must change with it or it becomes a confidently-wrong instruction. A real
  example: a steps list written for an SPA said *"there's no order number in this list, match by date
  and total"* — accurate there, actively false on the portal that replaced it, which has both an
  order number and a search box.

Also verify **how** sign-in works before describing it. One platform's portal is email-code, not
password, with exactly three pieces of visible copy (`Login`, `Continue with email`,
`Email address`). Name no control you haven't read, and never ask for a password.

⚠️ **Open question worth asking the platform team:** whether a retail (non-member) customer can sign
in to a tenant portal at all, where that portal is a member programme. It is strictly better than a
surface with no login — but if retail buyers have a different sign-in, that is what to point them at.

## Logged-in portal: verified impossible (at time of writing)

Attempted, verified, reverted. Four independent blockers, any one of which is fatal:

1. **Widgets cannot cross screens.** Typically only the Home screen is editable; other destinations
   are rendered by the SDK and expose no widget tree. A widget lives on one screen, so it cannot be
   a persistent assistant.
2. **Nav items cannot hold a URL.** The nav item schema is a destination reference — icon, label,
   position, screen id, slug — with no URL field. Putting the assistant in the nav therefore means
   creating a *screen*, and clicking it **navigates the user away from whatever they were doing**,
   which is strictly worse than the storefront overlay.
3. **No global script slot.** There is no portal-level equivalent of `content_for_header`.
4. **The embed iframe sandbox has no `allow-top-navigation`.** So `target="_top"` is silently
   blocked inside a portal embed: a link can only open a *second tab of the portal the user is
   already in*. Inside such an embed, **name the nav item instead of rendering a link** — a link
   that cannot work is worse than no link.

**Real SSO into an embed is a separate blocker.** Session-token *verification* may be undocumented,
and the token-exchange endpoint can be host-only (returning 404 to a company token). Until you can
verify a token's signature, any identifier the host appends to the frame URL is **a lookup hint,
never proof of identity** — trusting it is an authentication bypass.

To unblock, in order: create and install the app registration so you have a client id and secret;
capture a real token from a logged-in session; read its header to learn the algorithm; then write
the verifier. Ask the platform team the precise question — *"for this embed type with app-bridge
configured, how does the embedded app verify the session token: which algorithm, and shared secret
or JWKS?"* — rather than guessing.

## Consequence for the skill

Design the **thread/identity join** as if both surfaces will exist (it is cheap, and it is the
thing that makes an assistant feel like one person rather than two bots sharing a name), but
**ship storefront-first** and be honest in copy about what the assistant can currently see.

An assistant that says "open the Orders tab, then here's exactly what you'll find" is genuinely
useful. An assistant that implies it is reading the account when it is not is a liability.
