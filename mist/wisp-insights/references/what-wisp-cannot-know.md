# What Wisp cannot know

Read this before you write a causal sentence, and whenever a question starts drifting toward
something the recording does not contain. Every limit below is a design decision with a reason, not a
gap waiting to be filled — which means the honest move is to state the limit, not to work around it.

## Checkout is not recorded (v1)

Fluid's checkout runs on a **different origin** (`checkout.fluid.app`), and the storefront's
head-injection mechanism does not extend to it. There is no embed, script tag, or setting that
reaches checkout today; the only company-specific surface there is a sandboxed cross-origin iframe
which by construction cannot record its parent.

Consequences you must respect:

- The funnel's last measurable step is **reaching the checkout doorway**, not buying. Whenever you
  quote it, say which one it is. "42% reached checkout" is true; "42% converted" is false and the
  merchant will act on it.
- Abandonment *inside* checkout is invisible. If a merchant asks "where in checkout do people drop?",
  the answer is that Wisp cannot see it — say so, and point at their payment/analytics data.
- A session that ends at the checkout exit is **not** a failed session. It may be their best one.

## Typed input is unknowable, permanently and by design

Masking happens in the browser at capture time, before anything is serialized. Real characters never
reach the server; a keystroke becomes a `*` and a count. There is no unmask, there is no admin
override, there is no "just this once" — the data does not exist to be revealed.

So these questions have no answer and never will:

- "What did they search for?" / "What did they type in the form?"
- "Which email address abandoned the cart?"
- "What was in the field when it errored?"

What you *can* say: how many characters, in which field, in what order, and how long they hesitated.
Behaviour is fully recorded. Content is not. That distinction is usually enough — "they typed 14
characters into the discount field, deleted it, and left" is an actionable finding without knowing
the code.

**Never speculate about content.** If the merchant needs it, they need a different tool, and telling
them so is the correct answer.

## Correlation is not cause, and the corpus cannot settle it

Wisp observes; it does not experiment. Two things being true of the same sessions is not evidence
that one caused the other, and a session corpus contains no counterfactual.

Write "sessions with X also show Y" and let the merchant supply the mechanism, or state your
hypothesis **as** a hypothesis. The one honest causal claim available is a before/after over a known
change — and even then, say what else changed in the window (traffic mix, campaign, season) or you
have built a post-hoc story.

## What a "session" is, and is not

- A session is consecutive pageviews from one visitor with gaps under **30 minutes**. A shopper who
  returns after lunch is two sessions; one who leaves a tab open is one long one.
- The same human on phone and laptop is **two visitors**. There is no cross-device identity.
- Bots that execute JavaScript may be recorded. Obvious automation is refused at the loader, but a
  determined crawler looks like a fast, shallow, signal-free session — if a path shows implausible
  volume with no interactions, suspect that before you report a trend.

## Sessions that cannot be replayed, or lack metadata

- A pageview whose first chunk never arrived has **no DOM snapshot** and cannot be replayed. The
  player labels it "recording started mid-page". Its signals are still valid; its replay is not
  available. Never send a merchant to a `playerUrl` you have not reasoned about.
- Sessions recorded before certain fixes may show **"unknown device"** or a missing entry path.
  That is historical metadata loss, not a device that could not be identified. Do not build a
  device-mix claim on a window that spans it.
- A **`degraded`** session hit the recorder's circuit breaker: mutations stopped being recorded to
  protect the merchant's page. Interactions are intact, the DOM after that point is not, and
  `dead_click` is suppressed for it. Exclude degraded sessions from any mutation-dependent claim.

## Sampling and retention shape the corpus

- If the merchant's sampling rate is below 1, you are looking at a **fraction** of traffic. Rates are
  still valid; absolute counts are not the truth about their business. Check the setting before
  quoting a total.
- Chunks are reaped past the retention window. Signals and summaries survive, replays do not — so a
  question about last quarter may be answerable in aggregate while none of the evidence is watchable.
  Say that rather than linking to recordings that will 404.

## The rule this all reduces to

State the limit in the same breath as the finding. A merchant who learns from you that checkout is
invisible trusts the rest of the answer more, not less — and a merchant who discovers it *after*
acting on your conclusion does not come back.
