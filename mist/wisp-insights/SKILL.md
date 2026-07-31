---
name: Wisp insights across sessions
description: Turn a vague question about the storefront into a grounded answer across the whole Wisp session corpus — every claim carrying a session the merchant can watch.
icon: telescope
category: mist
---

# Answer a question about {{company.name}}'s storefront, from the sessions

Wisp records every storefront page as a replayable session, detects frustration signals in cron, and
exposes the whole corpus through an MCP server. This skill is the analyst's half of that: it takes a
question a merchant would actually ask — *"why are people bouncing on the product page?"*, *"did last
week's redesign help?"*, *"where is the worst friction?"* — and walks it down to an answer that is
**grounded in many sessions and carries the recordings that prove it.**

The thesis of the whole product, and the standard this skill holds itself to:

> **An insight without a session you can watch is a guess with good grammar.**

Every behavioural claim in your answer carries at least one `playerUrl`. A sentence you cannot attach
a recording to is not a finding — it is a hypothesis, and it gets labelled as one or deleted.

Today is {{today}}. To *install* Wisp on a company that doesn't have it, use the sibling skill
**[`mist/wisp-install`](../wisp-install/SKILL.md)** — this one assumes recording is already live.

**This skill is read-only.** It queries. It never changes a setting, never rotates the write key or
the MCP token, never touches the Global Embed. Rotating a token invalidates a merchant's working
configuration; there is no read-only question worth that.

> ### Safe Mode must be OFF, or this skill cannot run at all
>
> Mist Desktop refuses **every** MCP tool call while Safe Mode is on — not a degraded subset, all of
> them, and the server's *Trusted* checkbox does not override it. Mist treats third-party MCP servers
> as opaque and fails closed
> (`fluid-mono/apps/mist-desktop/src/main/tools/safe-mode-policy.ts:219-223`, which refuses any tool
> whose name starts with `mcp__`).
>
> **The symptom:** every single `wisp` call comes back as a Safe Mode refusal, immediately, with no
> network request — while the rest of Mist keeps working normally. If you see that, do not debug the
> token or the host. Say: *"Safe Mode is on, which blocks all MCP tools. Turn it off in the titlebar
> and I'll re-run."* Then stop and wait. Nothing in this skill works until it is off.

## Before you start

| Reference | Read it when |
| --- | --- |
| [references/connect-and-troubleshoot.md](references/connect-and-troubleshoot.md) | Step 0 — the MCP isn't configured, a call 401s, or the corpus comes back empty |
| [references/signals-and-thresholds.md](references/signals-and-thresholds.md) | Step 3 onward — you need what a signal actually means before you explain it |
| [references/what-wisp-cannot-know.md](references/what-wisp-cannot-know.md) | Step 6 — the question is drifting into a blind spot, or you're about to write a causal sentence |

Do not improvise a definition of "rage click". The detectors are deterministic functions with fixed
thresholds, and a merchant who hears two different definitions in two answers stops trusting both.

---

## Step 0: Connect, and confirm the corpus is real

1. **Check the `wisp` MCP tools are available in this session.** In Mist Desktop, MCP tools are
   namespaced `mcp__<server>__<tool>` — so a server the user named `wisp` surfaces as
   `mcp__wisp__signal_stats`, `mcp__wisp__list_sessions`, `mcp__wisp__get_session`,
   `mcp__wisp__top_friction_paths`, `mcp__wisp__funnel_summary`, `mcp__wisp__compare_periods`,
   `mcp__wisp__daily_rollups`. (The prefix is built by `mcpToolName()` in
   `fluid-mono/apps/mist-desktop/src/main/services/mcp.service.ts:89-91`; the server name is
   lowercased and non-alphanumerics collapse to `_`, so a server named "Wisp Sessions" gives you
   `mcp__wisp_sessions__…`. Read the actual name off the list rather than assuming.)

   Not there? **You cannot add it for them — it is a UI action in Mist Desktop.** Walk them through
   it in one message:

   > **Settings** (gear icon in the titlebar) → **MCP servers** → **Manage MCP servers…** → **Add server**
   >
   > | Field | Value |
   > | --- | --- |
   > | Name | `wisp` |
   > | Scope | *Global*, or *Project* to scope it to this company's project |
   > | Streamable HTTP URL | `https://<mist-host>.wecommerce.dev/api/mcp` |
   > | Authentication | **Bearer token** |
   > | Bearer token | the `wmcp_…` token from the Wisp panel |
   > | Trusted | see step 2 below — recommend ticking it |
   >
   > **Save server**, then click **Test** on the row. Test connects and lists the tools; the row
   > expands to show each `mcp__wisp__…` name it discovered.

   Mist sends the token as `Authorization: Bearer <token>` on the HTTP transport, and stores it in
   the OS keychain (`safeStorage`) under a `secretRef` — never in a plaintext config file, never
   displayed again after you save it. Transport is **Streamable HTTP only**; Mist Desktop has no
   stdio MCP support.

   The token is minted in the Wisp droplet panel (Fluid admin → Droplets → Wisp) and is **shown
   once** — it is stored as a hash, so a lost token is re-minted, never recovered. Full walkthrough,
   including what to do about a `401`, in `references/connect-and-troubleshoot.md`.

2. **Set the approval expectation before you start calling things.** Unless the server is marked
   **Trusted**, Mist prompts the user to approve **every individual tool call** — a modal showing the
   tool name and its arguments, with *Allow once* and *Deny*. There is no "allow for this session"
   button; an unanswered prompt **auto-denies after 60 seconds**. This skill makes a dozen-plus calls
   in a normal run, so on an untrusted server the user will be clicking *Allow once* a dozen-plus
   times and any moment they look away costs you a call.

   So: if the server is untrusted, say so up front — *"Wisp isn't marked Trusted, so you'll get an
   approval prompt for each call. Tick Trusted in Settings → MCP servers to skip them, or stay
   nearby."* Their call, but they should make it knowingly rather than discovering it at call four.

   *From here on this skill writes the tools by their short names — `signal_stats`, `list_sessions`
   and so on — for readability. Call them by whatever fully-namespaced name the session actually
   exposes.*

3. **Probe the corpus before you plan anything.** Call `signal_stats` over the last 7 days and read
   the **denominator** — how many sessions are in scope. This single call tells you whether the
   question is answerable at all:

   - **Healthy denominator** → continue to Step 1.
   - **Zero sessions** → the pixel is not recording, recording is disabled, or the window is wrong.
     **Say that plainly and stop.** Do not answer the merchant's question from the product docs, from
     general ecommerce knowledge, or from anything other than their sessions. An answer Wisp did not
     earn is worse than no answer. Triage table in `references/connect-and-troubleshoot.md`.
   - **A handful of sessions** (single digits) → say so now, before doing the work. The honest
     outcome of this run may be "the corpus is too small to support a conclusion", and the merchant
     should hear that in the first message rather than the last.

4. **Note the sampling rate** if the merchant has one below 1. Everything downstream is a sample of a
   sample, and rates stay valid while absolute counts do not.

---

## Step 1: Pin the question, and pick the baseline before you look

A vague question answered vaguely is the failure mode this skill exists to prevent. Convert it, and
say the conversion out loud so the merchant can correct you:

| They asked | Answer this |
| --- | --- |
| "Why are people bouncing on the product page?" | Which paths under `/products/` carry frustration signals at a rate above the site median, on which device, and what specifically do shoppers do in the seconds before they leave? |
| "Did last week's redesign help?" | Did the frustration rate and the funnel step-through on the changed paths move between the two weeks either side of the deploy, by more than the two weeks before it drifted on their own? |
| "Where is the worst friction?" | Which paths rank highest by frustration **density** — signals per session, not signals — over a window long enough to have a denominator? |

Then fix **two windows** and write them down:

- **Focus window** — what you're being asked about.
- **Baseline window** — the equivalent period immediately before it, same length, same days of week.

**A number without a baseline is not evidence.** "47 rage clicks last week" is unreadable; "rage
clicks on `/products/*` went from 0.04 to 0.11 per session week over week" is a finding. Choose both
windows *before* you pull data, so you cannot drift into the window that tells the nicer story.

**One hard constraint on the baseline: replay chunks are reaped at `retention_days`, default 30.**
Past that a session goes `expired` — its metadata, signals and AI summary survive, but the recording
is gone and its `playerUrl` will not play. A baseline older than the retention window still gives you
honest *numbers*; it cannot give you *watchable evidence*. Keep the focus window inside retention so
the sessions you cite are sessions the merchant can actually open.

---

## Step 2: Wide — did anything actually move?

Three calls, both windows. Resist every urge to jump to a specific session yet.

1. `funnel_summary` for the focus window and the baseline window. Read the drop-off rates, not the
   raw counts. **The v1 funnel ends at checkout entry** — the recorder does not run on the checkout
   origin (see `references/what-wisp-cannot-know.md`), so whenever you quote the last step you say
   what it is: shoppers who reached the doorway, not shoppers who bought.
2. `signal_stats` for both windows. Every rate needs its denominator attached from here on.
3. `daily_rollups` across both windows together, as one series. The series answers a question the two
   aggregates cannot: **step change or drift?** A metric that jumps on one day and holds is an event —
   a deploy, a broken script, a traffic-source change. A metric that slopes is a trend. They have
   completely different explanations and completely different fixes.
4. `compare_periods` on the headline metrics to get the deltas stated once, consistently.

Now render a small delta table — metric, baseline, focus, change, denominator — and read it honestly:

- **Nothing moved** → that is a real, publishable answer. Say it, show the table, and stop the
  investigation rather than hunting until something looks like a pattern. Manufacturing a finding
  from noise is how an analytics product loses a merchant permanently.
- **Something moved** → carry *only* that metric into Step 3. One thread at a time.

---

## Step 3: Narrow — which page

`top_friction_paths` over the focus window.

Rank by **density**, never by count. A page with ten times the traffic has ten times the rage clicks
and not one bit more of a problem; sorting by raw signals just re-discovers your most popular page
every single time. Then:

- Pull `signal_stats` scoped to the top one or two paths, so you can name **which** signal is
  elevated there rather than "friction". A path heavy in `dead_click` is a broken control; a path
  heavy in `quickback` is a page that fails to match its own link's promise; a path heavy in
  `js_error` + `error_click` is an engineering bug. These route to different people.
- Check the signal's **confidence** in `references/signals-and-thresholds.md` before you build on it.
  `rage_click` and `js_error` are confidence 1. `thrashed_cursor` is 0.6 — some people simply move
  the mouse while they read, and a story resting on it needs the sessions to carry it.

---

## Step 4: Specific — which sessions

`list_sessions`, filtered to the path and the signal you isolated: `path`, `signals[]`,
`minFrustration`, `device`, `reachedCheckout`, the window, `limit` (≤ 50).

Two rules about what comes back:

1. **Read the total, not the page.** The result tells you how many sessions match and how many it
   returned. "Of 412 matching sessions" is the sentence that makes an answer credible; the 50 rows in
   front of you are a sample of it, and treating the sample size as the finding is a lie of arithmetic.
2. **Cite the representative, not the spectacular.** Three typical sessions beat one dramatic outlier.
   Take your citations from the middle of the frustration distribution; if you include the worst
   session, label it as the outlier it is. The extreme session is the one most likely to be a single
   shopper with a broken extension.

Segment before you conclude. Run the same filter split by `device` at least once — a mobile-only
failure averaged against healthy desktop traffic reads as "a mild sitewide problem", which is both
wrong and unactionable. Note that sessions recorded before the metadata backfill shipped store the
literal string `unknown` for device and will never resolve; exclude them from a device split rather
than counting them as a class.

---

## Step 5: Watch — turn the citation into a claim

`get_session` on **at least three** of the sessions you selected. This step is not optional and it is
not a formality: it is where a hypothesis either dies or becomes a finding.

Each call returns the session's metadata, its ordered pageviews, its signals with timestamps, an AI
summary, and a `playerUrl`. Read the signals **in time order against the pageviews** — the sequence is
the story. A `dead_click` at 00:42 followed by a `quickback` at 00:47 is a shopper who pressed
something, got nothing, and left. That is a sentence you can defend.

- **Use the `playerUrl` exactly as returned.** Never hand-assemble a player link; the returned URL
  carries the seek offset that lands the merchant on the moment you are describing.
- `get_session` never returns raw recording chunks, and you never need them. The summary, the signal
  timeline and the recording itself are the evidence.
- **If your three sessions disagree with each other, you have variance, not a cause.** Go back to
  Step 4, widen the filter, and read three more — or accept that the honest finding is "these
  sessions fail in different ways", which is itself worth telling a merchant.
- A session flagged `degraded` had mutations dropped by the recorder's circuit breaker. Its replay is
  incomplete and `dead_click` is deliberately never fired on it. Do not use one as the load-bearing
  example, and say "degraded" if you show one.

---

## Step 6: Grade the evidence before you write a word

The gate. Apply it to the **narrowest** claim you intend to make — the segment you actually observed,
not the sitewide total you started from.

| Sessions supporting the claim | What you are allowed to say |
| --- | --- |
| **Fewer than 10** | **Nothing generalising.** "I found 4 sessions where X happened" — the count, the recordings, and an explicit *"that is too few to call a pattern."* No rate, no trend, no cause, no recommendation resting on it. |
| **10–29** | A pattern, hedged, with the denominator in the same sentence and the baseline beside it. "Worth a look", not "this is what's happening." |
| **30+, and the baseline moved with it** | A finding. State it plainly. |

**Ten is the floor, and it is the product's own number** — Wisp's tool layer marks results below it
insufficient in-band rather than leaving it to judgement, precisely because "3 sessions did X" is the
exact shape a language model likes to narrate into a trend. If a tool result carries a `sufficient:
false` or a note about sample size, that verdict wins over your reading of the numbers. Never
average it away by widening the window until the count clears the bar and then reporting the narrow
claim.

Then separate what you have from what you'd like to have:

- **Correlation** — the two things moved together. This is what nearly every result in this skill is,
  and saying so costs you nothing: *"Rage clicks on the size selector rose in the same week the
  variant picker changed."*
- **Cause** — you watched the mechanism happen, repeatedly, in sessions you can cite: *"In 12 of 14
  sessions the shopper clicked the size swatch, the DOM did not change for two seconds, and they left
  the page."* Only Step 5 can produce this, and only from the recordings.

Say which one you have. A merchant who acts on a correlation you dressed as a cause will ship the
wrong fix and blame the tool that told them to.

Finally, check the question against the blind spots in
`references/what-wisp-cannot-know.md`. Three that come up constantly:

- **Checkout is not recorded in v1.** Anything after the exit to the checkout origin is invisible.
- **Input content is masked at capture** and is unknowable by design — there is no unmask, no
  privileged reveal. You may say a shopper filled the email field. You can never say what they typed,
  and you must not infer it.
- **Not every visit is recorded.** Sampling, GPC/DNT, iframes and headless browsers all decline to
  record. The corpus is storefront traffic that consented to be recorded, not all traffic.

If the question lands squarely in a blind spot, say the question cannot be answered from the
recordings and name the closest question that can be. That is a better answer than a confident one.

---

## Step 7: Answer

Structure it this way, every time:

1. **The headline** — one or two sentences. The finding, its denominator, and whether it is
   correlation or cause.
2. **How it moved** — the delta table from Step 2: metric, baseline, focus, change, denominator.
3. **Where** — the ranked paths from Step 3, by density, with the specific signal named.
4. **The evidence** — a table of the sessions you actually watched. One row each: session id, device,
   the moment that matters, one line of what happens, and the **`playerUrl`**. Prefer the
   representative sessions; mark any outlier as an outlier.
5. **What I can't see** — the blind spots that bear on *this* question, in one or two lines. Not a
   disclaimer dump; only the ones that would change how the merchant reads the answer.
6. **What to do about it** — at most three items, ordered by expected impact, and **each one tied to
   the specific evidence above it**. A recommendation with no session behind it does not go in the
   list. If the evidence only supports "watch this for another week", that is the recommendation, and
   it is a legitimate one.

Write it in the merchant's register: elevated, concise, no hype. No exclamation marks, no
"significant" without a denominator, no urgency the data did not earn.

---

## When the honest answer is "not yet"

Ending a run with *"there isn't enough here to tell you"* is a success condition of this skill, not a
failure of it. Say what you looked at, what you found, how far it fell short of the bar, and what
would close the gap — usually more time, sometimes a different window, occasionally a fix to the
install itself (`mist/wisp-install`). Then stop.

The credibility of every future answer is spent from the same account as this one.
