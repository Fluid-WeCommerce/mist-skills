# What each signal actually means

Do not improvise these. Every detector is a deterministic function with a fixed threshold, and the
merchant will act on your explanation. If you describe `dead_click` as "a click that didn't do
anything" when the detector means "no DOM mutation *anywhere* within 2 seconds", you have quietly
changed what the number counts and the merchant will chase the wrong fix.

Source of truth: `docs/06-signals.md` in the Wisp repo. This file is the analyst's summary of it.

## The confidence column is the point

`confidence` is not decoration. It is how much weight a finding can carry on its own.

| Signal | Confidence | Fires when | What it actually tells you |
| --- | --- | --- | --- |
| `rage_click` | **1** | ≥3 clicks on the same element (or within 30px) inside 1500ms | Someone is hitting a thing that is not responding the way they expect. Unambiguous. |
| `js_error` | **1** | Any captured JS error or unhandled rejection | An engineering fault, with a timestamp. Unambiguous. |
| `quickback` | **1** | Pageview under 4000ms, followed by a return to the *previous* path | The page did not match the promise of the link that led to it. Fires on the page they left — that is the page with the problem. |
| `error_click` | **0.9** | A click within 3000ms of a JS error or failed request | The shopper *felt* the error, not just the log. Pair it with `js_error`: one is the experience, one is the fault. |
| `dead_click` | **0.8** | Click on an interactive-looking element with **no DOM mutation anywhere and no navigation** within 2000ms | The highest-value signal in the product. A control that looks clickable and does nothing. |
| `excessive_scroll` | **0.7** | Total scroll ≥ 3× the scrollable content height | Hunting. **Currently dormant — see below. Never report it as zero-meaning-good.** |
| `thrashed_cursor` | **0.6** | Within 2000ms: path ≥900px and path-to-displacement ratio ≥6 | Long distance travelled, little net progress. Hunting or agitation — *or* someone who moves the mouse while reading. |

**Rules that follow from the confidence:**

- **Confidence 1 signals can carry a claim by themselves.** "Rage clicking on the size selector" is a
  finding at n=8.
- **0.8–0.9 can carry a claim with the sessions to back it.** Watch two before you assert it.
- **`thrashed_cursor` at 0.6 cannot carry a story alone.** Plenty of people move the mouse while they
  read. Use it as corroboration for something else, never as the headline.

## Reading a path by its signal mix

The *mix* routes the fix to a different person, which is usually the most useful thing you can tell a
merchant:

- Heavy in **`dead_click`** → a broken or fake-looking control. Front-end.
- Heavy in **`quickback`** → the page fails to deliver what its inbound link promised. Merchandising
  or copy, not engineering.
- Heavy in **`js_error` + `error_click`** → an engineering bug the shopper is colliding with. Route it
  to a developer with the session and the error message.
- Heavy in **`rage_click`** with no `js_error` → the control works but is not perceived as working:
  no loading state, no feedback, a slow response. Design.

## Two traps

**`dead_click` deliberately under-reports.** Any DOM mutation anywhere in the 2-second window
suppresses it — including an unrelated carousel animating. That bias is intentional: it is a signal
merchants act on, so a false positive costs more than a miss. Never present a `dead_click` count as
exhaustive; it is a floor.

**`dead_click` never fires on a degraded pageview.** When the recorder's circuit breaker trips,
mutations stop being recorded, so *every* click would look dead. Sessions flagged `degraded` are
excluded from this detector by design. If a merchant asks why a busy page shows no dead clicks, check
whether it is degrading the recorder first.

## `excessive_scroll` is implemented and dormant

It returns nothing on today's recordings, because the recorder emits no content height — rrweb's
metadata carries the *viewport*, and scroll records carry only an offset. Turning it on is a
pixel-contract change, not a detector change.

**So: a zero for `excessive_scroll` means "not measured", not "no problem."** Never let it appear in
an answer as evidence of absence. If scroll-hunting is the merchant's actual question, say the signal
is not yet collected and reach for `thrashed_cursor` plus watching a few sessions instead.

## Ecommerce events are not frustration

`reached_cart`, `reached_checkout` and friends are hard-coded from Fluid's URL and cart structure —
they are *milestones*, not problems, and they carry no confidence weight. Use them as funnel
denominators. A session with `reached_cart` and three `dead_click`s is far more interesting than
either fact alone: the shopper wanted to buy and something got in the way.

## The frustration score

The library's ranking is a weighted sum over a session's signals, dampened by session length (the
divisor is floored at 1, so a short session is never inflated). Treat it as a **sort order, not a
measurement**. "Score 29 vs 3" means "look at this one first", not "9.7× worse". Never quote the
number to a merchant as though it were a unit.
