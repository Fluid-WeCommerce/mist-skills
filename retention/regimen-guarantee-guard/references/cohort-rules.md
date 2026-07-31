# Cohort rules

## Evidence states

Every condition has exactly one state:

- `Met` — a cited source proves the condition
- `Missed` — a cited source proves the condition failed
- `Unknown — data unavailable` — the source or field is unavailable
- `Not applicable` — a cited policy proves the condition does not apply

Never coerce `Unknown` to a boolean. Unknown evidence may trigger a data-closing
action, but it may not prove eligibility, disqualification, or cohort entry
unless the rule below explicitly uses a known deadline plus an unknown state.

## Calculations

Use calendar days and `{{today}}` as the fixed run date.

- `regimen_age_days` = `{{today}}` minus first successful subscription order
- `months_on_regimen` = `regimen_age_days / 30.4375`
- `bottles_180d` = successful, non-refunded bottle units delivered during the
  inclusive 180-day window ending `{{today}}`
- `elapsed_guarantee_days` = minimum of 180 and days since first successful
  subscription order
- `bottles_required_by_today` = ceiling(`6 × elapsed_guarantee_days / 180`)
- `days_since_successful_charge` = `{{today}}` minus latest successful charge
- `monthly_value` = current subscription unit price × active quantity
- `dollar_at_risk` = `Assumption: monthly_value × 3`

If the guarantee policy uses a delivery count or window other than six bottles
in 180 days, use the supplied company policy and cite it. If no company policy
is supplied, the guarantee cohort is `Unknown — policy not supplied`.

## Mutually exclusive precedence

Evaluate customers in this order. Stop at the first qualifying cohort and keep
later matches as secondary flags.

### 1. Silent Lapse

Qualifies when all are true:

- latest subscription status is failed, past-due, or paused, or the latest
  charge is proven failed
- no later successful charge exists
- no recovery attempt after that failure is proven

If recovery-attempt data is unavailable, do not claim “no recovery attempt.”
Set a secondary flag `Recovery status unknown` and use the next known qualifying
cohort. If there is no other qualifying cohort, the next action is to verify the
recovery queue; do not label the customer Silent Lapse.

### 2. Guarantee Breakage

Qualifies when either is proven:

- `bottles_180d < bottles_required_by_today`, meaning the customer is behind the
  six-bottles-in-180-days pace; or
- more than the policy's app-download window has elapsed since the first
  successful order and the app-download condition is `Missed`

An app-download state of `Unknown — data unavailable` does not qualify the
customer as breakage. It creates a secondary `Guarantee evidence gap` flag and
an action to retrieve the missing evidence.

Dosage, check-ins, and progress photos remain visible as `Met`, `Missed`, or
`Unknown`. A `Missed` state is a guarantee-breakage reason only when the supplied
company policy makes it a hard condition.

### 3. Cliff Risk

Qualifies when all are true:

- `months_on_regimen >= 2` and `< 4`
- subscription is active or pending
- no failed or missed successful billing cycle is proven
- customer did not already qualify for Silent Lapse or Guarantee Breakage

The action should bridge the customer to the company's cited results window.
Never promise results.

### 4. Regimen Gap

Qualifies when all are true:

- an active core formula is proven
- the customer's stated root cause is proven
- the supplied policy maps that root cause to a booster
- no active matching booster is proven

If root cause or mapping is missing, set `Unknown — data unavailable` or
`Unknown — policy not supplied`; do not recommend a guessed product.

## Priority within a cohort

Sort first by urgency, then by verified monthly value descending, then customer
ID for deterministic ties:

1. failed charge age / guarantee deadline proximity
2. verified monthly value
3. stable customer ID

Keep verified monetary values unprefixed. Prefix the projected three-month
`dollar_at_risk` and any recovery estimate with `Assumption:`.
