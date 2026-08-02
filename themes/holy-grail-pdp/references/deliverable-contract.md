# Holy Grail PDP deliverable contract

## Table of contents

1. Status header
2. Audit and redesign report
3. Competitor report
4. Build report
5. Experiment contract

## 1. Status header

Start every final deliverable with:

```text
Status: PASS | NEEDS REVIEW
Mode: Audit | Redesign | Build | Compare
Primary constraint: <one sentence>
Visual thesis: <one sentence>
Primary metric: <one metric or "unavailable">
```

`PASS` means every mode-specific required check ran successfully. `NEEDS REVIEW` means the output remains useful, but one or more evidence, rendering, interaction, or approval gates remain open.

## 2. Audit and redesign report

Use this order:

1. **Diagnosis** — one primary constraint and why it is the earliest high-impact decision problem.
2. **Known context** — product, buyer, awareness, traffic promise, goal, economics, and observed funnel behavior. Label inferences.
3. **Evidence ledger** — claim/decision, status, source, risk, allowed use, missing proof.
4. **Buyer-question spine** — five to eight questions in order.
5. **Module map** — one row per included module:

| Order | Chapter | Buyer question | Message | Psychology | Evidence | Visual direction | Mobile behavior | CTA/transition | Failure mode |
| ----- | ------- | -------------- | ------- | ---------- | -------- | ---------------- | --------------- | -------------- | ------------ |

6. **High-leverage creative moments** — complete briefs for hero, mechanism, and strongest proof story.
7. **Offer architecture** — total, per-unit basis, choices, bundle/subscription, renewal, cancellation, delivery, guarantee, returns, and payments. Mark missing facts.
8. **Mobile recomposition** — dominant media, control order, sticky state machine, thumb-zone risks, compressed content, and preserved state.
9. **Prioritized backlog** — P0 broken decisions, P1 major persuasion gaps, P2 optimization, P3 polish.
10. **Experiment backlog** — one hypothesis and primary metric per test.
11. **Evidence/content gates** — exact facts, assets, substantiation, policies, or analytics still required.

For a redesign brief, include draft copy only where the evidence ledger permits it. Use bracketed content requirements such as `[verified delivery window]` rather than plausible filler.

## 3. Competitor report

Use:

1. pages and exact URLs inspected;
2. desktop/mobile capture paths;
3. comparable module matrix;
4. page-by-page strongest decision, weakest decision, evidence quality, and mobile behavior;
5. recurring category conventions;
6. distinctive brand devices;
7. patterns rejected for weak evidence, manipulation, friction, or copying risk;
8. one original recommended sequence and visual thesis for the target brand.

Never rank pages by assumed conversion. Say `more complete`, `clearer`, or `better evidenced` only when the inspected facts support it.

## 4. Build report

Include:

1. `Status` and the exact product route tested.
2. Files created/changed and each file's job.
3. What remains bound to dynamic Fluid product state.
4. Claims/proof used, omitted, or default-hidden.
5. Desktop and mobile screenshot paths for the final round.
6. Interactions exercised and observed state transitions.
7. `fluid theme lint --json` result.
8. DOM, console, and server-log result.
9. Accessibility and overflow checks.
10. Remaining `NEEDS REVIEW` items.
11. Publication status: always `not published` until the approved push completes.

Do not describe a change as visually verified without a final screenshot path. Do not describe an interaction as verified without a tool result from the same final implementation.

## 5. Experiment contract

For every proposed test provide:

```text
Observation:
Buyer problem:
Hypothesis: If <specific change>, then <one primary metric> should improve because <decision principle>.
Variant:
Primary metric:
Guardrails:
Segment:
Decision rule:
```

Pre-register a meaningful change. Do not bundle hero, offer, proof, and navigation into one test when causal learning is the goal. Watch revenue per visitor, returns, churn, support contacts, and performance when they can expose a hollow conversion win.
