# Model and guardrails

## Calculation model

For each market:

```text
conversion rate = orders / visitors
refund rate = refunds / orders
normalized price = local price * usd_per_local
price before included tax = normalized price / (1 + tax rate)
contribution per retained order =
  price before tax * (1 - percentage fee)
  - fixed fee
  - variable cost
retained orders = orders * (1 - refund rate)
contribution revenue = retained orders * contribution per retained order
projected orders = orders * (1 + assumed conversion lift)
projected contribution revenue =
  projected orders * (1 - refund rate) * proposed contribution per retained order
price-only contribution =
  current retained orders * proposed contribution per retained order
price effect = price-only contribution - current contribution revenue
volume recovery =
  projected contribution revenue - price-only contribution
break-even lift =
  current contribution per retained order
  / proposed contribution per retained order
  - 1
cumulative test contribution change =
  scenario contribution change per analysis period
  * periods per quarter
  * selected quarters
  * eligible traffic reach
cumulative additional first orders =
  scenario additional orders per analysis period
  * periods per quarter
  * selected quarters
  * eligible traffic reach
```

Round only displayed values. Calculate with unrounded values.

## Interpretation

- `break-even lift` answers how much more conversion is required to preserve contribution revenue at unchanged traffic.
- `price effect` isolates what the candidate price costs at unchanged order volume.
- `volume recovery` isolates what the selected conversion response earns back.
- `margin of safety` is the assumed lift minus break-even lift. A positive value is modeled headroom, not statistical confidence.
- A positive base scenario is a modeled hypothesis, not causal proof.
- A negative scenario is useful evidence; do not hide it from totals.
- Use contribution revenue rather than checkout gross whenever fees and costs are known.
- Do not project lifetime value from one-period conversion data.
- Label one-period acquisition output as `first-order contribution`; do not call it MRR, ARR, or LTV.
- Label multi-quarter output a `constant-run-rate scenario`, not a forecast.
- A traffic-reach slider sizes exposure; it does not estimate sampling error or statistical power.

## Evidence grades

- `observed`: derived from the company’s own historical cohort.
- `experiment`: derived from a controlled test on a comparable cohort.
- `benchmark`: derived from a current cited external source.
- `hypothesis`: supplied planning assumption without direct evidence.
- `synthetic`: demonstration data only.

Never silently promote an evidence grade.

## Recommendation labels

- `Keep current price`: the candidate price is unchanged.
- `Needs more evidence`: the base response does not clear break-even.
- `Small test only`: the base response clears break-even but the conservative response loses contribution.
- `Strong test candidate`: even the conservative response clears break-even and inputs pass validation.

These labels never mean `publish` or `roll out`.

## Required caveats

- Traffic, mix, retention, and refund behavior may change after a price change.
- Cross-border purchasing and VPN use can weaken country segmentation.
- Existing subscribers, taxes, app-store tiers, and platform policies need separate review.
- Forecast ranges depend on user-supplied conversion assumptions.
