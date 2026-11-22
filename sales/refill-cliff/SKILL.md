---
name: Refill Cliff
description: Find the billing cycle where subscribers actually churn, explain what happens at that cycle, size the recoverable revenue in each at-risk segment, and hand back a ranked save list with a dollar figure per play.
icon: trending-down
---

# Goal

For a subscription business, almost all of the churn is concentrated at one
billing cycle — and it is almost never the one people assume. Find that cycle for
{{company.name}}, prove what changes there, and turn the finding into a ranked
list of save plays with real money attached to each one.

Today is {{today}}.

This is a **measure → explain → size → hand over** run. The deliverable is not a
retention chart. It is: _"the cliff is at cycle N, here is what happens at cycle
N, here are the M subscriptions standing at the edge of it right now, worth
$X — and here is the one play to run first."_

Every number must come from a tool call you made this turn. Anything you infer
beyond the returned data — a save rate, a lifetime assumption, an attribution —
must be **labeled an assumption in the output**. Never present an assumption as
a measurement.

## 0. Find the data before you analyze it

Two sources, in this order.

**Reporting database (preferred).** Cohort retention needs per-subscription
history, which the REST API does not aggregate. Run `db_schema` with
`mode: "search"` and keyword `subscription` to find the real table and column
names — do not guess them. Then run `db_schema` with `mode: "tables"` on the
matched tables to get columns and foreign keys. Confirm the status vocabulary
with a `SELECT DISTINCT status, COUNT(*)` before you filter on any status value;
every Fluid company spells its lifecycle slightly differently.

`references/cohort-sql.md` has the survival-curve, price-step and at-risk queries
in both Postgres and T-SQL. Adapt the column names to what `db_schema` actually
returned; do not paste them blind.

**REST API (fallback, or cross-check).** If `db_query` errors because no
reporting database is connected, work from:

- `fluid_api("/api/subscriptions?status=active&limit=100", "GET")` — cursor
  paginated (follow `meta.pagination.next_cursor`), also accepts
  `status=inactive` and `search_query`. `active` covers live, pending and
  past-due; `inactive` covers cancelled and paused.
- `fluid_api("/api/subscription_plans", "GET")` — the billing interval per plan.
  You need the interval to convert elapsed time into cycles.
- `fluid_api("/api/v202506/orders?within_days=90&page[limit]=100", "GET")` — the
  billing events themselves. Read `meta.pagination.total_count`, never the array
  length. Sample a handful of orders and inspect their `type` values before
  filtering on one; do not assume a `subscription` type string exists.

If `/api/subscriptions` 404s or comes back scoped to a single member rather than
the company, say so plainly and stop that branch — **do not probe path variants.**
Report what you could measure and what you could not.

Useful fields on a subscription, all real: `status`, `created_at`,
`cancelled_at`, `last_bill_date`, `next_bill_date`, `last_failed_at`,
`next_retry_at`, `price`, `original_price`, `quantity`, `decline_count`,
`attempts`, `skipped_count`, `max_skips`, `subscription_plan`, `variant`,
`customer`.

## 1. Build the survival curve — and censor it honestly

Assign every subscription a **cycle count**: how many times it has actually been
billed. Prefer counting real billing events (orders joined to the subscription).
Fall back to date arithmetic only if no join exists:
`cycles = floor(months_between(created_at, coalesce(cancelled_at, last_bill_date, {{today}})) / plan_interval_months)`.

Then compute retention at each cycle: `S(n) = subscriptions that reached cycle n ÷ subscriptions that reached cycle 1`.

**The censoring rule — get this wrong and the whole report is wrong.** A
subscription that started three weeks ago on a monthly plan has not *failed* to
reach cycle 2; it has not had the chance. Including it in the cycle-2
denominator manufactures a cliff that does not exist.

> For each cycle `n`, the denominator is only subscriptions whose start date is
> at least `n × interval` in the past. Every cycle has its own eligible
> population, and the populations shrink as `n` grows.

State the eligible count next to every cycle in the output. When the eligible
population for a cycle drops below ~30 subscriptions, mark that cycle **thin**
and stop drawing conclusions past it.

## 2. Locate the cliff

The cliff is not the lowest point on the curve — retention always trends down.
It is the steepest **conditional** drop: the cycle `n` that minimizes
`S(n+1) ÷ S(n)`, the share of subscribers who survive one more cycle _given that
they got to n_.

Report the conditional retention for every transition, and name the single worst
one as the cliff. If two transitions are within a couple of points of each other,
say the cliff is shallow and the churn is distributed — that is a real, useful,
different finding, and it changes the recommendation.

## 3. Explain the cliff — start with the price step

A cliff is an event, not a mood. Check these against the data, in order, and
report only the ones you can actually evidence:

1. **The price step-up.** Acquisition-discounted subscriptions bill the first
   cycle at a promotional `price` and later cycles closer to `original_price`.
   Compute the average `price` billed at each cycle. If the cliff cycle is where
   the amount charged jumps, that is your headline: the churn is priced in, not
   accidental. Give the step in dollars **and** as a percentage of cycle-1 price.
2. **Dunning.** Average `decline_count` and `attempts` by cycle. A spike at the
   cliff means the subscriber did not choose to leave — the card failed and the
   retries ran out. That is a recoverable cliff, and it is the cheapest one to fix.
3. **Skips as a leading indicator.** Compare `skipped_count` for subscriptions
   that survived past the cliff versus those that did not. If skippers churn at a
   materially higher rate, skips are an early-warning signal you can act on
   before the cancel.
4. **Plan and variant mix.** Split the cliff by `subscription_plan` and by
   `variant`. A cliff that only exists on one plan or one pack size is a
   packaging problem, not a retention problem.

If none of the four explains it, say so. "The cliff is real but the cause is not
in this data; here is what to instrument" is an honest and useful answer.

## 4. Size the money still on the table

Bucket the **currently live** subscriptions by how they are at risk. Each bucket
gets a count and a dollar figure:

| Bucket | Signal | Why it is recoverable |
| ------ | ------ | --------------------- |
| **Retry window open** | `last_failed_at` set and `next_retry_at` in the future | The retry has not run yet — a card update today still saves it |
| **Dunning exhausted** | `decline_count > 0`, no future `next_retry_at`, still billable | Silent involuntary churn nobody has contacted |
| **Skip-to-churn** | `skipped_count >= 2`, or at `max_skips` | Disengaging, has not cancelled yet |
| **Standing at the cliff** | Cycle count == cliff cycle − 1 and `next_bill_date` within 14 days | The pre-emptive save window, and the only bucket that is time-boxed |
| **Price-step exposed** | Next bill is the first at the stepped-up price | Overlaps the cliff bucket; report the overlap, do not double-count |

Dollar-size each bucket as `subscriptions × price × expected remaining cycles`.
Then apply a save rate to get recoverable revenue.

**You do not have a measured save rate.** Use a stated placeholder — 20% for
voluntary-churn buckets, 50% for the payment-failure buckets, since a card update
recovers a subscriber who never intended to leave — and write in the output, in
plain words, that these are assumptions and what the number would be at half and
double the rate. Show the arithmetic. A CEO who cannot see the multiplier will
not trust the total.

Deduplicate before totaling: one subscription can land in three buckets. Report
the union as the headline number and the overlap explicitly.

## 5. Show it

Call `show_dashboard` with a title like "Refill Cliff" and these sections:

- `stat_tiles` — active subscriptions, MRR, conditional retention at the cliff,
  total recoverable revenue (the deduplicated union).
- `hero_chart` (`variant: "bar"`, `xKey` the cycle number) — the survival curve,
  with the cliff cycle as the `highlight: true` series. One dark hero card, not four.
- `stat_rows` or `mini_table` — the at-risk buckets: count, monthly value,
  recoverable at the stated save rate.
- `leaderboard` — the top save targets, ranked by recoverable dollars.
- `insight_banner` — one line: the cliff cycle, the conditional retention there,
  and what changes at it.

Put raw numbers in `metric` with a `format` hint (`currency`, `percent`,
`number`), never pre-formatted strings. If validation fails, fix the named fields
and call it again — do not re-gather the data.

If you answered from SQL, the headline query must also go through
`sql_answer_card` so the user gets a saveable card and an editor tab. State the
metric definition you used in the text after the card: which statuses counted as
churned, whether the figures are gross or net of refunds, and which timestamp you
bucketed on.

## 6. Hand over the save list

Below the dashboard, write the ranked plays. Each play is one line and names:
the bucket, the number of subscriptions, the recoverable dollars, and the single
concrete action. Order them by dollars-per-effort, not by dollars.

```
1. Retry window open — 74 subs, $5.9k recoverable — card-update SMS before the retry fires (this week or never)
2. Dunning exhausted — 412 subs, $32.9k recoverable — hand to support as a call list, oldest failure first
3. Standing at the cliff — 188 subs, $15.0k recoverable — hold cycle-2 at the cycle-1 price for this group and measure against a holdout
```

Then render `resource_card` (or `product_card` where the subscription maps to a
product) for the top few targets so the user can click straight through.

Close with **one** recommendation, not five. Name the play, the reason it is
first, and what it would take to know it worked.

## 7. Ask, then remember

Finish by asking the user, in one short message, which play they want to run and
what save rate they actually see in practice. Then **END YOUR TURN and wait.**
Do not keep calling tools.

When they answer, record it with `update_memory` under a "Retention" note: their
real save rates, which buckets they care about, the cliff cycle and the date you
measured it. The next run of this skill starts from their numbers instead of
placeholders — that is what makes the second run better than the first.
