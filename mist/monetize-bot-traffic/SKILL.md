---
name: monetize-bot-traffic
description: Audit a storefront or digital business for safe, high-value bot-facing routes that can become metered, pay-per-request products. Use when a merchant wants to monetize AI agents, scrapers, partner automation, catalog feeds, availability checks, or other machine traffic with Tollbooth and x402.
---

# Monetize Bot Traffic

Turn an existing storefront into a machine-revenue plan. Identify valuable bot demand, select the best routes, and produce an evidence-backed Tollbooth/x402 pilot that preserves the human shopping experience.

## Operating rules

- Inspect before recommending. Use the connected company, storefront, catalog, analytics, route inventory, and existing documentation when available.
- Keep human-facing pages open. Target machine-oriented endpoints or explicit `/machine/*` routes.
- Never invent traffic, conversion, margin, pricing, or revenue numbers. Label estimates and show assumptions.
- Do not expose customer, health, payment, authentication, or other sensitive data.
- Do not move money, change production routes, enable a signer, or deploy a payment policy without explicit approval.
- Prefer public catalog, availability, content, and approved partner metadata.
- Start with simulation, advance to testnet, and require a separate production gate.

## Workflow

### 1. Build the machine-demand inventory

Inspect the business and list assets that software agents may repeatedly request, including:

- product catalog and structured specifications
- inventory or availability checks
- comparison, compatibility, or recommendation data
- approved editorial or research content
- partner, affiliate, and reseller feeds
- high-cost computation or frequently refreshed data

For each asset, record the current source, likely machine consumer, freshness requirement, sensitivity, and evidence that it exists. Do not treat ordinary human page views as bot demand without evidence.

### 2. Score candidates

Score each candidate from 0 to 5 on:

| Dimension | 0 | 5 |
| --- | --- | --- |
| Machine demand | No credible recurring use | Clear repeat demand from agents or partners |
| Marginal cost | Near-zero and static | Material compute, licensing, or refresh cost |
| Freshness or scarcity | Commodity and stale-tolerant | Timely, scarce, or differentiated |
| Safety | Sensitive or legally risky | Public, approved, and low-risk |
| Integration ease | Requires core-system redesign | Can wrap an existing read-only route |

Rank primarily by machine demand, safety, and integration ease. Select at most three pilot routes. Explain why lower-ranked candidates were deferred.

### 3. Design the paid route map

For every selected route, provide an exact request flow:

```text
/machine/<resource>
  -> Tollbooth policy check
  -> HTTP 402 payment requirement
  -> payment or approved access token
  -> existing read-only source
  -> response plus verifiable receipt
```

Specify the response payload, freshness target, rate limit, cache behavior, intended buyer, and the existing source being wrapped. Keep the original human route unchanged.

### 4. Propose pricing as a test

Offer a simple starting hypothesis such as per-request, prepaid credits, or partner allowance. Show the logic and assumptions rather than presenting unverified economics as fact. Include one free or low-friction discovery path so agents can understand what is purchasable before paying.

### 5. Create the seven-day pilot

Use three explicit gates:

1. **Simulation:** deterministic development identity, fake facilitator, synthetic requests, no real funds.
2. **Testnet:** Base Sepolia wallet, real signing flow, test funds only, receipts verified end to end.
3. **Production review:** verified Fluid admin session, real facilitator and signer, approved treasury, monitoring, rollback, and owner sign-off.

Production must never use a fake facilitator, test signer, or development identity. Call out missing prerequisites instead of silently weakening this rule.

### 6. Deliver the executive brief

Return these sections in order:

1. **Why now** — a concise, high-energy explanation of the shift from human clicks to autonomous buying agents.
2. **Opportunity inventory** — evidence-backed table of candidates and scores.
3. **Top three paid routes** — exact route maps and intended buyers.
4. **Pilot plan** — simulation, testnet, and production gates with owners and success criteria.
5. **Business case** — value drivers, assumptions, risks, and measurements; do not fabricate ROI.
6. **Next actions** — the smallest concrete steps needed to launch the simulation.

End with a one-sentence pitch suitable for a CEO presentation.

## Quality bar

A complete result names real assets from the inspected business, distinguishes facts from assumptions, protects sensitive data, keeps human commerce unaffected, and leaves the team with a testable route-level plan rather than generic advice.
