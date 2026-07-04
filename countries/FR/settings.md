---
name: France country settings
description: Legal and commercial defaults for selling into France — VAT, currency, language, address, disclosures, cookie/privacy law, and price-display rules.
icon: flag
category: countries
---

# France (FR) — country settings

Baseline the `open-country` workflow and the French `compliance-manager` skill load for FR. Values below are load-bearing.

## VAT profile

- Name: `TVA`
- Standard rate: `20%`
- Reduced rates: `10%` (restaurants, transport), `5.5%` (most food, books, feminine hygiene), `2.1%` (medicines reimbursed by social security).
- Notes: Distance selling into FR from another EU state falls under the EU OSS €10,000 threshold. Non-EU sellers register directly with the DGFiP.

## Currency

- Code: `EUR`
- Symbol: `€` — placed AFTER the amount with a non-breaking space: `19,99 €`.
- Decimal separator: `,` (comma). Thousands separator: space (thin space) — `1 234,56 €`.

## Language

- Primary: `fr` (French). Under the **Loi Toubon**, consumer-facing commercial information MUST be in French.
- Widely spoken: `en` (English) — acceptable as a secondary language only. English-only storefronts violate Loi Toubon.

## Address format

Example (realistic):

```
Marie Dupont
12 rue de la République
75001 PARIS
France
```

Rules:

- House number PRECEDES the street name — `12 rue de la République`.
- Postal code is 5 digits, precedes the city on the same line — `75001 PARIS`. City is written in CAPITALS by convention.
- `CEDEX` suffix appears on business addresses served by a dedicated post office bin (e.g. `75008 PARIS CEDEX 08`).

## Mandatory disclosure pages

Every commercial storefront serving FR must link these pages from the footer (LCEN 2004-575 and Code de la consommation):

1. **Mentions Légales** — legal notice: publisher name/address, RCS/SIRET number, VAT number, host provider name/address, publication director.
2. **Politique de Confidentialité** — RGPD-compliant privacy policy.
3. **CGV (Conditions Générales de Vente)** — general sales terms.
4. **CGU (Conditions Générales d'Utilisation)** — site usage terms (often merged with CGV).
5. **Politique de Cookies** — separate cookie policy or dedicated section within Politique de Confidentialité.
6. **Droit de Rétractation** — 14-day withdrawal notice and model form (Article L221-18 Code de la consommation).

All must be reachable in French from every page. Mentions Légales missing carries fines up to €75,000 for individuals, €375,000 for legal entities.

## Consumer protection basics

- Cooling-off period: **14 days** from receipt (Article L221-18). Extending to 12 months + 14 days if the merchant failed to inform the consumer of the right.
- Refund window: refund within **14 days** of the withdrawal notice; same-method-of-payment rule applies.
- Guarantee: **legal conformity guarantee** — 2 years for goods, 1 year for used goods, extends to digital services (Ordonnance 2021-1247).
- Cross-border obligations: NFR — the storefront must warn the customer that they are the importer and that customs duties/TVA on import may apply.

## Cookie / privacy law

- Framework: **RGPD** (GDPR as transposed) + **Loi Informatique et Libertés** enforced by the **CNIL**.
- Cookie banner: opt-in, granular, Refuser must be as easy as Accepter (CNIL guidelines 2020, tightened 2021). A "Continue browsing" or "×" dismissal treated as consent is non-compliant.
- Analytics loading: no non-essential trackers before consent. Google Analytics (GA4) requires additional safeguards after the EDPB Schrems II ruling — most operators use a proxy or a CNIL-approved audience-measurement tool with a documented DPIA.
- Fines: CNIL has issued €50M+ orders against Google and Amazon for cookie violations; expect enforcement.

## Price display rule

- **VAT-inclusive (TTC — Toutes Taxes Comprises)**: all consumer prices MUST be shown inclusive of TVA (Article L112-1 Code de la consommation). "Prix TTC" is the standard label.
- Shipping costs must be indicated no later than the beginning of the ordering process; a specific amount or a clear reference to the calculation.

## Unit-price rule

**Yes — Article L112-1 Code de la consommation.** Products sold by weight, volume, length, or count must show a unit price (per kg, per litre, per metre, per unit) alongside the sale price. Applies to most food, drink, cosmetics, and prepackaged goods. The DGCCRF actively enforces this in online retail.
