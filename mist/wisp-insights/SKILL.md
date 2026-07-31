---
name: Wisp insights across sessions
description: Turn a vague question about the storefront into a grounded answer across the whole Wisp session corpus — every claim carrying a session the merchant can watch.
icon: telescope
category: mist
---

# Answer a question about {{company.name}}'s storefront, from the sessions

Wisp records every storefront page as a replayable session and detects frustration signals in cron.
This skill is the analyst's half of that: it takes a
question a merchant would actually ask — *"why are people bouncing on the product page?"*, *"did last
week's redesign help?"*, *"where is the worst friction?"* — and walks it down to an answer that is
**grounded in many sessions and carries the recordings that prove it.**

The thesis of the whole product, and the standard this skill holds itself to:

> **An insight without a session you can watch is a guess with good grammar.**

Every behavioural claim in your answer carries at least one `playerUrl`. A sentence you cannot attach
a recording to is not a finding — it is a hypothesis, and it gets labelled as one or deleted.

Today is {{today}}. To *install* Wisp on a company that doesn't have it, use the sibling skill
**[`mist/wisp-install`](../wisp-install/SKILL.md)** — this one assumes recording is already live.

**Who this is for.** This is an *operator's* tool — someone working a Fluid company from Mist
Desktop. **Merchants do not need it and should never be sent here.** A merchant asks Wisp questions
from the **Ask panel inside the Wisp droplet** (Fluid admin → Droplets → Wisp → Ask), which is
authenticated by the panel session they already have: no token, no MCP server, no settings dialog.
Wisp's MCP server exists so the corpus can also be reached from outside Fluid — Claude Desktop,
Cursor, Claude Code — a deliberate power-user opt-in, not something an end user is asked to set up.
**This skill does not use it**: inside Mist Desktop the database is right there.

**This skill is read-only.** It queries. It never changes a setting, never rotates the write key or
the MCP token, never touches the Global Embed. Rotating a token invalidates a merchant's working
configuration; there is no read-only question worth that.

> ### Run this from the Wisp Mist app project, and query the database directly
>
> **Which project you are in decides whether this works at all.** `db_query` targets the ACTIVE
> project's database, and only the Wisp Mist app (`prose-8de108` for Prose) has the `wisp_*` tables.
> From a company chat or any other project you will hit a different connection — often
> `role "postgres" does not exist` — and there is nothing to answer from. Step 0 checks this first.
>
> On a Mist app project — which is what Wisp is — `db_query` targets that project's own database,
> and Wisp's tables are in it. That is the whole connection story: **nothing to configure.**
>
> It also keeps working under **Safe Mode**, because `db_query` is read-only enforced by its own SQL
> gate. (Safe Mode refuses every `mcp__*` tool outright, which is one reason this skill does not use
> them.) The MCP route still exists for reaching Wisp from OUTSIDE Mist Desktop — Claude Desktop,
> Cursor, Claude Code — and lives in an appendix at the bottom. You will not need it here.

## Before you start

| Reference | Read it when |
| --- | --- |
| [references/sql-path.md](references/sql-path.md) | **The path you are taking.** Canonical SQL for every question below — read it before Step 0 |
| [references/connect-and-troubleshoot.md](references/connect-and-troubleshoot.md) | The corpus comes back empty, or you are on the MCP route from another host |
| [references/signals-and-thresholds.md](references/signals-and-thresholds.md) | Step 3 onward — you need what a signal actually means before you explain it |
| [references/what-wisp-cannot-know.md](references/what-wisp-cannot-know.md) | Step 6 — the question is drifting into a blind spot, or you're about to write a causal sentence |

Do not improvise a definition of "rage click". The detectors are deterministic functions with fixed
thresholds, and a merchant who hears two different definitions in two answers stops trusting both.

---

## Step 0: Confirm you are in the right project, then resolve the company

**Run this skill from the Wisp Mist app project itself** — the project whose database holds the
`wisp_*` tables (for Prose that is `prose-8de108` / `mist-8de108`). `db_query` only ever targets the
**active project's** connection. Run this from a company chat, a theme project, or any other Mist
app and it will reach a different database — or Prose's saved reporting connection, which commonly
errors with `role "postgres" does not exist`.

Check first, before anything else:

```
db_schema   →  look for wisp_sessions, wisp_signals, wisp_daily_rollups
```

- **Tables present** → you are in the right place. Continue.
- **`role "postgres" does not exist`, or no `wisp_*` tables** → you are in the wrong project. **Stop
  and say so.** Ask the user to open the Wisp Mist app project and re-run this skill there. That is
  a five-second switch and it is the whole fix.

Three things NOT to do when you land in the wrong project, because each one produces a confident
answer that Wisp did not earn:

- Do not answer from the product docs, from the storefront, or from general ecommerce knowledge.
- Do not mint a `wmcp_…` MCP token to reach across the boundary. This skill is read-only, and
  minting credentials to work around a project boundary is not a read.
- Do not hand the question to another project's agent unless the user asks you to. If you offer it,
  offer it as a choice and name the cost: the answer lands in that project's chat, not this one.

The MCP appendix at the bottom is the *supported* cross-host route, and it exists for Claude Desktop
and Cursor — not as a way around being in the wrong Mist project.

### Then resolve the company

**Get the company id, and never query without it.** One Wisp database holds every company that
installed the droplet. The MCP derives the tenant from a token so it *cannot* read the wrong one;
**raw SQL has no such protection**, and an unfiltered `SELECT` reads another merchant's customers'
recordings. That is the worst thing this product can do.

```sql
SELECT id, name, fluid_company_id FROM companies WHERE active = true ORDER BY created_at;
```

Run it with `db_query`. One row → that is your `companyId`, and it goes into **every** statement
from here on. More than one row → **ask which company before you query anything else.** Never
assume, and never answer across all of them.

Everything below is `db_query` with `params: [companyId, from, to]` against the `$1/$2/$3` SQL in
**[references/sql-path.md](references/sql-path.md)**. On a Mist app `db_query` defaults to
`side: "production"` — the real corpus, which is what you want. Use `db_schema` if a column
surprises you rather than guessing.

> **Do not reach for `sql_answer_card`.** It refuses on Mist app projects — it is gated on
> `projectInfo.kind === "database"` and a Mist app's kind is `"mist"`. Here `db_query` does both the
> exploring and the final answer, and you write that answer as prose plus small tables in Step 7.
> That is the intended shape on a Mist app, not a downgrade.

**Then probe the corpus before you plan anything.** Run the signal-rate query over the last 7 days
and read the denominator first:

- **Zero sessions** → the pixel is not recording, recording is disabled, or your window is wrong.
  **Say that plainly and stop.** Do not answer the merchant's question from the product docs, from
  general ecommerce knowledge, or from anything other than their sessions. An answer Wisp did not
  earn is worse than no answer. Triage table in
  [references/connect-and-troubleshoot.md](references/connect-and-troubleshoot.md).
- **Single digits** → say so now, before doing the work. The honest outcome of this run may be "the
  corpus is too small to support a conclusion", and the merchant should get to decide whether to
  spend the time.
- **Enough to work with** → carry the denominator into every rate you quote from here on.
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

---

## Appendix: reaching Wisp from another host

You do not need this inside Mist Desktop — Step 0's `db_query` is the path. It is here for when the
same questions get asked from **Claude Desktop, Cursor, or Claude Code**, where there is no
`db_query` and no Mist database connection.

Wisp exposes the same aggregations over MCP at `https://<mist-host>.wecommerce.dev/api/mcp`,
authenticated with a per-company `wmcp_…` bearer token minted in the Wisp droplet panel (shown
once). Tools: `list_sessions`, `get_session`, `signal_stats`, `top_friction_paths`,
`funnel_summary`, `compare_periods`, `daily_rollups` — every session-naming result carries a
`playerUrl`, and the token *is* the tenant, so no tool can read another merchant.

Two ways to attach it, both covered in
**[references/connect-and-troubleshoot.md](references/connect-and-troubleshoot.md)**: register the
server in the host's MCP settings, or POST JSON-RPC at it directly (`Accept` must list **both**
`application/json` and `text/event-stream`, or every call is refused).

**One thing that path buys you that SQL does not:** the computed extras — the real frustration
score, `sufficient` guards, `playerUrl`s built for you, and the checkout `blindSpot` annotation on
the funnel. On the SQL path those are yours to remember.
