---
name: Country Compliance Manager
description: Audit a company's storefront against a country's legal requirements — mandatory disclosure pages, price-display rules, cookie/privacy law, linked agreements, product labeling, and storefront language — using Fluid's Country Atlas as the rulebook. Runs standalone ("review France compliance") and as the final step of the mode finalizer workflows.
---

# Goal

Give {{company.name}} an honest, cited compliance report for one country: what the storefront legally must have, what it currently has, and the gaps a human needs to close. This skill is the rulebook-grounded auditor — it runs as the last step of each mode finalizer (`finalize-otg/nfr/usd-country`) and can be invoked directly ("review France compliance", "is my Germany store compliant?").

# Step 0 — Resolve the country and load its rulebook

1. Resolve the country ISO (alpha-2). If invoked standalone, take it from the user's message; in a workflow, read `context.country_id` / `context.country_iso` (fall back to `fluid_api` → GET `/api/countries` and match on id).
2. Call the `country_settings` tool with that ISO. It returns the country's compliance rulebook projected from the Country Atlas: `mandatoryDisclosurePages` (each with a citation when one exists), `cookieRule` (framework + requirement + regulator), `vatInclusiveDisplay` (`inclusive` | `exclusive_at_sticker` | `unspecified`), `unitPriceRule` (required + notes), plus `vat`, `paymentMethods`, `languageCode`. If `covered: false`, tell the user Fluid has no atlas for this market yet and audit only the generic essentials (privacy policy, terms, refund policy present) — do not invent country-specific rules.
3. Note the operating mode if you have it (`context.mode` = `otg` | `nfr` | `usd`). It changes how strict each check is (see the mode notes at the end).

# Step 1 — Audit the live storefront against the rulebook

Every finding MUST be checked against real state this turn — read the storefront, call the API. Do not assume. Cover these dimensions:

1. **Mandatory disclosure pages** — for each entry in `mandatoryDisclosurePages`, confirm the storefront actually publishes that page (crawl the storefront footer/legal menu, or GET the company's pages/agreements). Report present / missing per page, each tied to its citation.
2. **Linked agreements** — GET `/api/agreements` and confirm the country's required agreements exist, are active, and are scoped to this country. Cross-reference against the disclosure pages.
3. **Price display** — compare `vatInclusiveDisplay` to how prices actually render. `inclusive` markets (most of the EU, UK, AU, JP) must show tax-included consumer prices; `exclusive_at_sticker` (US/CA convention) shows ex-tax with tax at checkout. Flag a mismatch.
4. **Cookie / privacy** — if `cookieRule.requirement` calls for consent, confirm the storefront has a consent banner meeting it (e.g. an equally-prominent Reject All where required). Name the regulator from `cookieRule.regulator`.
5. **Unit pricing** — if `unitPriceRule.required`, spot-check that products sold by weight/volume/length show a unit price.
6. **Product labeling** (physical goods) — spot-check 3 products for country-of-origin and destination-language labeling where the market requires it.
7. **Storefront language** — confirm the storefront is available in the market's primary language (`languageCode`). A Spanish market served only in English is a critical finding.

# Step 2 — Report

Produce a compliance report in plain language for a store owner (no internal ids, no tool names). Group findings by severity:

- **Critical (fix before launch)** — legal must-haves that are missing or wrong.
- **Should review** — likely-required items you couldn't fully verify, or soft requirements.
- **Passed** — what's already compliant (brief).
- **Follow-ups for a human** — registrations, filings, or credential-gated items Fluid can't complete (VAT registration, gateway KYC, a named Privacy Officer).

Every finding cites the specific rule it rests on (the citation from `country_settings`, e.g. "Impressum — Telemediengesetz §5", "unit pricing — Price Marking Order 2004") or, for a finding produced by an earlier workflow step, names that step. Drop or reword any finding you can't attribute — never invent a citation.

# Mode notes

- **OTG (On The Ground)** — the strictest audit. Full weight on B2C consumer-disclosure duties (Impressum / Mentions Légales / 特定商取引法), VAT-inclusive display, and local invoicing. If a B2B/B2C posture was captured, weight B2C obligations accordingly.
- **NFR (Not For Resale)** — lighter on storefront consumer-protection duties (the buyer imports the goods), heavier on import-duty disclosure at checkout and product country-of-origin labeling. Say plainly in the summary that the bar is lower and why.
- **USD** — weighted toward cross-border digital-services obligations (digital-services-tax registration, cross-border ToS + refund carve-outs) and lighter on physical-goods labeling and VAT-inclusive display.

# Rules

- READ-only. This skill audits and reports; it never writes to the store. Fixes are the user's call (or a separate skill/workflow).
- Never invent tax rates, regulators, statutes, or disclosure requirements — everything country-specific comes from `country_settings`. When `covered: false`, say so and stay generic.
- Keep the report scannable: severity groups, one line per finding, citation attached.
