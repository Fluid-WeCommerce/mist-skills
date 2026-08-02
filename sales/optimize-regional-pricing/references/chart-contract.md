# Chart contract

Build an explanation, not a dashboard of decorative metrics.

## Required questions

Each visual must answer one question:

1. **What could we change?** List the strongest product-country price changes across the requested product or portfolio scope.
2. **What is the risk and likely reward?** Pair weak-response downside with the base-case outcome for every recommendation.
3. **What happens over time at a controlled test size?** Show cumulative quarterly contribution versus keeping current prices, plus additional first orders.
4. **What must be true?** Compare break-even conversion lift with the low, base, and high assumptions on one shared axis.
5. **Where does the money move?** Decompose the change into the negative price effect, positive volume recovery, and final net change.
6. **What is known versus assumed?** Keep source notes and evidence grades visible.

## Decision hierarchy

Lead with the pricing opportunities, not the model:

1. State how many product-country prices are strong candidates, small tests, or not ready.
2. Rank only strong candidates and small tests by base-case contribution result.
3. For each included test, lead with a large sourced product image, followed by the product name, market, exact local price change, weak-response downside, base-case outcome, recommendation label, and one-quarter conservative exposure at the default test reach.
4. Show a cumulative quarterly projection and the selected outcome, conservative exposure, and additional first orders after the product cards.
5. Put the scenario control, charts, assumptions, and sources behind one supporting-analysis disclosure.
6. Preserve rejected candidates in the machine-readable analysis, but do not place `hold` rows in the primary recommendation view.

Do not let a decorative hero, generic slogan, or oversized section title delay the decision output.
Use one primary decision heading. When that heading already states the number
of prices needing controlled tests, place the recommendation cards directly beneath its
short explanatory sentence; do not insert another `Recommended tests` heading
or repeat the eligibility explanation.

## Visual language

Use a restrained light analytical report:

- show a sourced, uncropped product image in a large top image area on every product recommendation card;
- do not add standalone illustrations, hero diagrams, visual metaphors, or social-post compositions;
- use literal chart titles and labels such as `Conversion lift`, `Break-even lift`, `Price effect`, and `Volume recovery`;
- keep typography moderate and reuse one five-role scale for caption, body, card title, section heading, and display value;
- use a warm white canvas, white surfaces, soft borders, and restrained rounded corners;
- use normal sentence-case labels; do not add uppercase monospace eyebrows, numbered kickers, or decorative microcopy above headings;
- use thin structural rules, direct annotations, and no shadows or gradients;
- use solid marks for the selected assumption, outlined marks for thresholds, and dashed lines for uncertainty or below-break-even states;
- use one clear green root for modeled opportunity and positive outcomes and one clear red root for downside and negative outcomes; keep other numbers neutral and retain signed labels plus structural marks;
- keep controls familiar and avoid ornamental icons, oversized slogans, or inverted poster-like blocks.

Prioritize comprehension over a signature visual style.

Choose the chart form that best answers the question. A range plot suits conversion lift versus break-even, a signed horizontal bar chart suits price effect versus volume recovery versus net change, and a slope or paired-value plot suits current versus candidate prices. Replace a chart when another familiar form communicates the same data more clearly.

## Opportunity list

Use one card per recommended product-market pair. Keep unchanged controls and
base-case failures out of the primary recommendation count. Show:

- sourced product image and product name;
- market name and code;
- current and proposed local price;
- price change percentage;
- low-assumption contribution delta labeled `Weak response`;
- base-assumption contribution delta labeled `Modeled base`;
- one-quarter conservative exposure at the default test reach;
- `Strong test candidate` only when the conservative scenario clears break-even;
- `Small test only` when the base scenario clears but the conservative scenario does not.

Use signed labels for the two contribution deltas and consistent colors across
cards. Rank by base-case contribution result. Explain that `Modeled base` is an
assumption, not a measured probability. Rejected candidates remain available in
the saved JSON/CSV for audit without appearing as recommendations.

Keep the card hierarchy flat: the recommendation grid itself is not another
card, the paired contribution figures use plain columns separated by a thin
rule, and status labels are direct text rather than nested pills. Omit utility
topbars and decorative eyebrow text. Use an accessible country flag above each
product name in the primary cards instead of a colored market name/code label;
retain the written market name and code in the supporting table.

For the aggregate slider-driven figures, show selected contribution,
conservative exposure, and additional first orders, with short captions
underneath. Keep all figures in sync with the selected response, reach, and
horizon. Do not add colored dots or eyebrow labels
that make the summary resemble a chart key. End the report with at most one short
safety sentence; keep the complete caveat in the saved analysis data.

## Controlled-test projection

When every recommendation has low, base, and high order estimates, place a
single aggregate quarterly line graph between the product cards and financial
summary. Keep the current-price baseline at zero. Plot cumulative conservative,
selected, and strong contribution change against Q1 through Q4. Add three
keyboard-operable controls: customer response, test reach, and time horizon.
Default to the base response, 10% reach, and four quarters unless the project
config supplies valid alternatives. Interpolate response only between the
supplied low, base, and high endpoints. Scale selected contribution,
conservative exposure, and additional orders by the same reach and period
multiplier. Update every related mark, number, and caption together.

State that the result is a constant-run-rate scenario rather than a demand
forecast. Use green for nonnegative selected contribution and red for negative
selected contribution and conservative exposure. Do not extrapolate beyond the
response endpoints, and do not call orders unique buyers without
unique-customer evidence.

## What must be true

For each recommended market, place:

- the low-to-high assumption range as a thin line;
- break-even lift as an outlined diamond;
- the selected scenario as a filled circle;
- the margin of safety as a signed direct label.

Exclude unchanged controls and base-case failures from the recommendation count.

## Where the money moves

Build a conventional signed horizontal bar chart:

```text
PRICE EFFECT       negative bar
VOLUME RECOVERY   positive bar
NET CHANGE        signed bar
```

Keep a visible zero axis. Use bar direction, `+`/`−`, and direct labels as the
primary encodings; green and red may reinforce positive and negative outcomes
but must not carry the distinction alone. Do not draw a stepped path,
connected-node diagram, or other illustration-like bridge.

## Market comparison

Show current and proposed prices in local currency and normalized base currency. Label the percentage change directly. Show current and selected contribution on a shared scale or slope; do not imply that lower prices are inherently better.

## Assumptions table

Show visitors, conversion, refunds, break-even lift, selected lift, incremental
orders needed, evidence grade, source note, and next action. The table may sit
behind the same single supporting-analysis disclosure as the charts, but it must
remain keyboard-accessible and require no additional interaction to read once
that disclosure is open.

## Interaction

- Default the visible projection to base response, 10% reach, and four quarters.
- Keep low, base, and high supporting analysis one click away.
- Update the point, margin of safety, signed driver chart, and totals together.
- Keep selected scenario state local to the report.
- Provide keyboard-operable controls and accessible chart descriptions.
- Respect reduced motion.

## Language

Use `scenario`, `candidate`, `assumption`, `break-even`, `first-order contribution`, and `experiment`.

Do not use `guaranteed`, `will earn`, `optimal`, `winner`, `forecast`, or `rollout-ready` for modeled output.
