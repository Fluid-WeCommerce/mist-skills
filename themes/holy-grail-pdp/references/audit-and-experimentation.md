# PDP audit and experimentation

## Table of contents

1. Funnel diagnosis
2. Audit scoring
3. Priority system
4. Experiment format
5. Measurement cautions

## 1. Funnel diagnosis

Use the narrowest metric that reflects the observed problem:

- **Low product-view-to-add-to-cart:** Check message match, product comprehension, offer clarity, button visibility, configuration effort, missing evidence, fit/sizing, ingredients/materials, or price-value framing.
- **Healthy add-to-cart but low reach-checkout:** Check cart page loads, drawer behavior, upsell friction, shipping surprises, discount errors, overlays, payment visibility, and extra clicks.
- **Healthy reach-checkout but low completion:** Check shipping cost/time, taxes and fees, payment methods, trust, account requirements, delivery uncertainty, and checkout errors.
- **Low AOV:** Check bundles, quantity logic, threshold value, relevant add-ons, and whether savings are transparent.
- **Low repeat purchase or high churn:** Check product efficacy, onboarding, ritual, replenishment timing, subscription transparency, support, and post-purchase education.

## 2. Audit scoring

Score each issue from 1 to 5 on:

- **Customer impact:** How strongly could this block understanding, belief, desire, or completion?
- **Evidence strength:** How directly do analytics, research, user feedback, session recordings, reviews, or page observation support the diagnosis?
- **Reach:** How many relevant visitors encounter the issue?
- **Effort:** How difficult and risky is implementation? A higher score means more effort.

Use `priority = (impact x evidence x reach) / effort` only as an ordering aid. Do not present the result as scientific certainty.

## 3. Priority system

- **P0 - broken decision:** Errors, inaccessible controls, false or missing price, blocked CTA, covered checkout, lost state, or misleading terms.
- **P1 - major persuasion gap:** Ad mismatch, unclear outcome, weak offer comprehension, missing essential proof, high-risk objection unanswered, or unusable mobile flow.
- **P2 - optimization:** Rhythm, hierarchy, proof placement, comparison clarity, bundle framing, or content compression.
- **P3 - polish:** Decorative refinements that do not solve an observed decision problem.

## 4. Experiment format

For every proposed test, write:

- **Observation:** What is happening and where?
- **Buyer problem:** Which internal question remains unanswered?
- **Hypothesis:** If we change X, then Y metric should improve because Z psychological or usability principle is better served.
- **Variant:** Exact content, layout, or behavior change.
- **Primary metric:** One decision metric.
- **Guardrails:** Revenue per visitor, AOV, returns, subscription churn, support contacts, or performance.
- **Segment:** Traffic source, device, new/returning, product, region, or buyer intent.
- **Decision rule:** Minimum duration/sample plan and how contradictory metrics will be handled.

## 5. Measurement cautions

- Do not claim a page is "highest converting" without comparable data and attribution.
- Do not use industry benchmarks as guarantees.
- Watch revenue per visitor and returns, not conversion rate alone.
- Separate mobile and desktop behavior.
- Avoid testing multiple persuasion changes at once when the goal is causal learning.
- Treat qualitative research as diagnostic evidence, not a lift estimate.
