---
name: Set FairShare preferences
description: Configure a company's FairShare attribution preferences — how orders and enrollments are credited to reps, and what happens to customers with no sponsor. Explains what each option does and what it's worth to the business and the field. Use when asked to set up FairShare, change attribution, set order or enrollment volume credit, fix orphan sponsor handling, or review current FairShare settings.
icon: network
category: FairShare
---

# Set FairShare preferences

Set {{company.name}}'s four FairShare preferences through a guided picker,
explain what each one is worth, then write them back safely.

FairShare decides **which rep gets credit** for an order or an enrollment. The
four preferences live on the company as a single JSON object, read and written
through one endpoint:

- `GET /api/v2025-06/fairshare/settings`
- `PATCH /api/v2025-06/fairshare/settings`

## The one rule that matters

**Always GET, merge your changes onto the full object, then PATCH all five
fields.** Never PATCH a partial object.

Every field in the PATCH schema is marked optional, so a partial body is
accepted — but the server assigns the whole object at once, and any field you
omit is reset to its **default**, not left alone. PATCHing only
`orphan_sponsor_config` will silently flip `attribution_config` back to
`last_touch` and re-credit orders.

Defaults, for reference — these are what omitted fields become:

| Preference                 | Default        |
| -------------------------- | -------------- |
| `attribution_config`       | `last_touch`   |
| `order_volume_config`      | `sponsor_rep`  |
| `enrollment_volume_config` | `customer_rep` |
| `orphan_sponsor_config`    | `empty_rep`    |

## How volume actually gets assigned

Explain this before the picker — the preferences only make sense against it.
Volume credit resolves in a fixed order, and the first match wins:

1. **The buyer's own rep account** — a rep buying for themselves keeps their own
   volume. On *enrollment* orders this step is gated by
   `enrollment_volume_config`.
2. **The attributed rep** — only if `order_volume_config` allows it.
3. **The nearest rep-eligible sponsor** — the direct sponsor if they're a rep,
   otherwise Fluid walks up the genealogy to the closest rep-eligible ancestor.
   Volume passes *through* customer interior nodes; customers never earn.
4. **The attributed rep again** — as a fallback when no eligible sponsor exists
   anywhere in the upline. This happens even on `sponsor_rep`, so "sponsor only"
   never means "the attributed rep is ignored."
5. **The orphan policy** — last resort, when steps 1–4 all came up empty.

**Warning worth stating up front:** every step above is gated on
`rep_eligible?`. If a company's member-type permissions are empty, no member is
rep-eligible, the whole chain collapses to step 5, and every one of these
preferences appears to do nothing. If the user reports "I changed it and nothing
happened," check rep eligibility before touching FairShare again.

## Step 1 — Read the current settings

```
fluid_api("/api/v2025-06/fairshare/settings", "GET")
```

The settings are under `fairshare_settings`. Keep the whole object — you need
every field for the PATCH in step 4.

Show what's set today before asking them to change anything, and mark any value
that is still the default. "Still on defaults" usually means nobody has made a
decision here yet, which is worth saying out loud.

If the GET fails with 401/403 the user lacks the company-settings permission.
Say so and stop — do not attempt the PATCH.

## Step 2 — Explain the four preferences

Walk through these before opening the picker. Each option gets the same three
lines: what it does, who it pays, and what it's worth. Use the "worth" column to
frame the trade — do **not** invent numbers, and do not claim to have measured
this company's orders. This skill explains mechanisms; it does not quantify them.

### `attribution_config` — when several reps touched a sale, who earns the credit?

| Option        | What it does                                                                              | Who it pays                              | What it's worth                                                                                                                                                                          |
| ------------- | ----------------------------------------------------------------------------------------- | ---------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `last_touch`  | The most recent tracked touch before the order wins. Fluid's default.                     | The closer                               | **Helps reps who convert.** Rewards the rep who actually asked for the sale, so closing effort pays. Costs you the nurturer: a rep who warmed the customer for months loses to whoever sent the last link, which is the most common source of commission disputes. |
| `first_touch` | The earliest tracked touch wins, however long ago.                                        | The introducer                           | **Helps recruiters and content creators.** Protects the rep who did the expensive part — acquiring a stranger. Reduces churn among top-of-funnel reps, who are the hardest to replace. Costs you closers, who can feel unpaid on long cycles. |
| `most_touch`  | The rep with the most tracked touches wins; ties go to the most recent.                    | The rep who did the most work            | **Cheapest in disputes.** Hardest option to game with one lucky link, so it produces the fewest "that was my customer" escalations. Best fit for consultative or high-touch selling. Weakest signal when most journeys have only one touch. |

Money framing to state plainly: attribution disputes cost real money in support
time, manual commission adjustments, and goodwill credits — and a rep who feels
robbed is a rep who leaves. Replacing a producing rep costs far more than the
commission that was in dispute. The cheapest configuration is the one the field
believes is fair.

### `order_volume_config` — who receives the sales volume?

| Option                                     | What it does                                                                     | Who it pays                          | What it's worth                                                                                                                                                                                    |
| ------------------------------------------ | -------------------------------------------------------------------------------- | ------------------------------------ | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `sponsor_rep`                              | Volume goes up the genealogy to the nearest rep-eligible sponsor. Fluid's default. | The upline                           | **Most predictable liability.** Volume follows the org chart, so payouts are stable and easy to forecast. The cost is commission leakage: an inactive sponsor keeps earning on customers they no longer service, while the rep who drove the sale gets nothing. |
| `attribution_rep`                          | Volume goes to the rep who earned the attribution credit.                        | The rep who drove the sale           | **The setting that makes social selling pay.** A rep who shares a link and produces a sale gets the volume even on someone else's customer, which is the direct incentive to keep sharing. Genealogy is left untouched, so nothing is destroyed. |
| `attribution_rep_and_reassign_sponsor_rep` | Volume goes to the attributed rep **and** they become the customer's sponsor.     | The rep who drove the sale, forever  | **Stops paying dormant sponsors.** This is the one option that structurally ends commission leakage to inactive reps — the customer moves to whoever is actually servicing them. It also permanently rewrites genealogy, and there is no API to undo it. |

### `enrollment_volume_config` — who receives the volume when someone enrolls?

Applies to enrollment orders only.

| Option         | What it does                                                     | Who it pays        | What it's worth                                                                                                                                                                          |
| -------------- | ---------------------------------------------------------------- | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `customer_rep` | The new enrollee's own rep account keeps the volume. Fluid's default. | The new rep        | **Helps new reps start strong.** Their own enrollment order counts toward their first rank, which is the moment most new reps decide whether this is real. Good for early retention.       |
| `sponsor_rep`  | The enrollee's sponsor gets the volume instead.                   | The recruiter      | **Makes recruiting pay immediately.** The sponsor sees volume the day they enroll someone rather than waiting for the downline to produce, which is the strongest lever on recruiting rate. Costs the new rep their fast start. |

### `orphan_sponsor_config` — what happens when nobody in the chain qualifies?

Reached only after steps 1–4 above all fail.

| Option       | What it does                                                                                                                | Who it pays                     | What it's worth                                                                                                                                                                                                       |
| ------------ | --------------------------------------------------------------------------------------------------------------------------- | ------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `empty_rep`  | Nobody is credited. Fluid's default.                                                                                        | Nobody                          | **Cheapest in raw payout** — no commission is generated on these orders at all. The hidden cost is service: nobody owns the customer, so nobody follows up, and orphan customers rarely reorder. You save the commission and lose the lifetime value. |
| `select_rep` | Every orphan goes to one rep you nominate.                                                                                  | The rep you choose              | **Turns orphans into an asset.** Point it at a house account and the company keeps the margin; point it at a field leader and someone actually services the customer, which is where repeat orders come from. Predictable and auditable. |
| `random_rep` | Assigned to a **random pick from the 10 reps with the most `url_visited` events in the last 30 days**, refreshed hourly.      | One of your 10 most active reps | **Rewards activity.** Not a blind lottery — it channels unclaimed customers to reps who are demonstrably working right now, which is a real incentive to keep sharing. Less predictable per-rep than `select_rep`, and the winner has no existing relationship with the customer. |

Correct a common misreading if it comes up: `random_rep` does **not** spray
orphans across the whole roster. The candidate pool is the current top 10 by
tracked link activity.

## Step 3 — Collect the choices

Call `steps` with title `FairShare settings — <company name>` and the five steps
below. Pre-select each step's current value so the panel opens on reality and
the user only changes what they mean to change. Put the "who it pays" line in
each option's description so the trade is visible at the moment of choosing.
Then **end your turn** and wait for the answers.

1. `attribution_config` — single_select, `skippable: false`
2. `order_volume_config` — single_select, `skippable: false`
3. `enrollment_volume_config` — single_select, `skippable: false`
4. `orphan_sponsor_config` — single_select, `skippable: false`
5. `orphan_sponsor_rep_id` — text_input, `skippable: false`,
   `show_if: { step_id: "orphan_sponsor_config", equals: "select_rep" }`

Option ids are exactly the values in the tables above.

For step 5, resolve and confirm the rep before writing it:

```
fluid_api("/api/v2025-06/reps/<id>", "GET")
```

If the id doesn't resolve, say so and re-ask. The API accepts a bad or deleted
rep id without complaint and stores it — nothing downstream will warn you.

## Step 4 — Confirm the two changes that are hard to undo

Before writing, if the user selected either of these, state the consequence in
one line and get an explicit yes. Do not fold this into the picker.

- **`attribution_config` changed at all** — this is **retroactive, not
  forward-only.** Each order carries its own snapshot of these settings, and
  that snapshot is overwritten with the company's current settings whenever the
  order's attribution is recomputed. Historical orders can re-credit to a
  different rep, which means commission that was already communicated to the
  field can move.
- **`order_volume_config: attribution_rep_and_reassign_sponsor_rep`** — this
  permanently moves customers between sponsors. There is no API to undo a
  reassignment.

If they decline either, keep the previous value for that field and carry on with
the rest.

## Step 5 — Write the full object

Merge the answers onto the object from step 1 and send **all five fields**:

```
fluid_api("/api/v2025-06/fairshare/settings", "PATCH", {
  "fairshare_settings": {
    "attribution_config": "...",
    "order_volume_config": "...",
    "enrollment_volume_config": "...",
    "orphan_sponsor_config": "...",
    "orphan_sponsor_rep_id": null
  }
})
```

`orphan_sponsor_rep_id` is `null` unless `orphan_sponsor_config` is
`select_rep`. Sending a rep id alongside `empty_rep` or `random_rep` stores a
value nothing reads — clear it to `null` instead.

A 422 means a value isn't in the allowed set. Re-read the option tables; don't
invent values.

## Step 6 — Verify and report

Re-GET the settings and confirm every field persisted as intended. Then report a
short before/after table covering only the fields that changed, the resolved rep
name if you set `orphan_sponsor_rep_id`, and one line per change restating who
now gets paid that didn't before.

If any field came back different from what you sent, say so plainly — that's the
partial-PATCH reset, and it means the merge in step 5 dropped a field.

## Scope

This skill explains and sets preferences. It does **not** measure what changing
them would do to this company's existing orders — the "what it's worth" column
describes mechanisms, not measurements. If the user asks "how many of my orders
would change?" or "why did this specific order credit the wrong rep?", tell them
this skill doesn't answer that rather than estimating.
