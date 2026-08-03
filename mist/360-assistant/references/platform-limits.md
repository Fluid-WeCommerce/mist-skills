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
sitewide (see the launcher hit-testing section in `reference-implementation.md`), which is a
merchant-visible outage rather than a
cosmetic bug.

Three details worth copying:

- **Take an existing slot rather than adding a third control.** Commerce SDKs often already render
  their own floating buttons. Hiding a lower-value one (a lead-capture bubble) and taking its place
  keeps the corner at two controls instead of three. Hide it with **CSS, not DOM removal**, so it
  holds however late the widget mounts — and so removing the script restores the original launcher.
- **Match the host's own motion.** Copy the SDK's entrance keyframe so the launcher arrives the way
  the cart does. Apply it to the root element, never the button — a `forwards` fill on the button
  locks its transform and kills the hover state.
- **The launcher is the one piece of this system with reliable memory.** It runs on the storefront
  origin, so its `localStorage` is first-party and survives the third-party cookie blocking that
  breaks the chat iframe's own cookie. That is what makes a genuinely once-per-browser first-visit
  greeting possible (`reference-implementation.md` §9b).

### The theme install, and the collision you ship with it

The install is **one line** in the active theme's layout, immediately before the single `</body>`:

```html
<script src="https://<app-host>/assistant.js" defer></script>
```

Non-negotiables, each of which someone will try to "improve": **absolute URL, not an asset helper**
(the app serves the file) · **`defer` stays** · **`<body>`, never `<head>`** · no raw-block wrapper,
no style/script tag wrapper, no comment.

🔴 **Do the corner-collision fix in the SAME edit as the script line.** The launcher defaults to the
bottom-right corner — the floating cart's *exact* corner — and hides it completely. Shipping the
script line alone **is** the "chat button is covering the cart" bug report.

Numbers derived rather than guessed, for a 60px cart button at a 16px margin:

- **`bottom: 92px`** = 76 (the cart's top edge) + 16 (the SDK's own margin rhythm).
- **`right: 18px`, not 16** — a 56px launcher against a 60px cart, so `18 + 28 == 16 + 30` and both
  circles share one vertical centre line. 16px leaves them 2px off-axis, which is visible.
- `!important` on **geometry only** — the launcher injects its stylesheet at runtime, so it lands
  after the theme's inline block and wins ties.
- Cap the panel's headroom: lifting the root eats the space above it.

**Fetch the entrance animation, don't eyeball it.** The values are not in crawl-retained page CSS —
read the published SDK stylesheet. One slid in **horizontally from 100px off the right with a fade**,
`.3s ease-out` after a `.3s` delay — *not* a slide-up. **Re-declare the keyframes under your own
name** so it survives the cart widget being switched off and its stylesheet no longer loading.

**Three walls in local theme QA, none of which are bugs:**

1. 🔴 **An isolated / network-frozen preview never executes the loader at all.** No root element, no
   bubble, clean console — and every synthetic tap test passes against a launcher that was never
   there. Use mounted-pane screenshots, then a crawl with actions against the **live** URL as the real
   gate.
2. **Automation cannot click a runtime-injected element.** Don't try to prove open/close locally.
3. **A blank panel locally is a CSP, not a bug.** `frame-ancestors` excludes localhost, so the browser
   blocks the frame outright — blank panel, console-only error, indistinguishable from a broken panel.
   Fixable only in the **app**, by appending a localhost origin under a dev flag. Production is
   unaffected.

🔴 **Never hit-test on a bundle product.** The bundle picker correctly **blocks** add-to-cart until
the required selections are made; reading that as a failed hit test cost two rounds. Use a plain
single-variant product, click the real add-to-cart with the launcher closed, and confirm the count
increments. **Reading the CSS is not the test.**

**Layout-file landmines:**

- **Never write literal template-tag syntax in prose** — including inside a CSS comment. The parser
  tokenizes it anyway, opening a block that never closes, and **every route 404s**.
- **External stylesheet assets can silently not apply** on some stores' render path. Put polish CSS in
  the existing inline style block.
- ⚠️ **The dev server may serve assets from a different theme id than the one you push to.** "I
  verified it locally" says nothing about the asset path production uses.

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
