---
name: United Kingdom country settings
description: Legal and commercial defaults for selling into the United Kingdom — VAT, currency, language, address, disclosures, cookie/privacy law, and price-display rules.
icon: flag
category: countries
---

# United Kingdom (GB) — country settings

Baseline the `open-country` workflow and the UK `compliance-manager` skill load for GB. Values are load-bearing.

## VAT profile

- Name: `VAT`
- Standard rate: `20%`
- Reduced rate: `5%` (children's car seats, home energy).
- Zero rate: `0%` (most food, children's clothing, books).
- Notes: post-Brexit, UK VAT is separate from EU VAT. Sales to consumers under £135 require the seller to charge and remit UK VAT via an HMRC registration; over £135 the customer pays import VAT.

## Currency

- Code: `GBP`
- Symbol: `£` — placed BEFORE the amount, no space: `£19.99`.
- Decimal separator: `.` (period). Thousands separator: `,` (comma). Example: `£1,234.56`.

## Language

- Primary: `en-GB` (British English).
- Widely spoken: none required. Welsh is co-official in Wales; storefronts targeting Wales specifically may add `cy`.

## Address format

Example (realistic):

```
Emma Thompson
221B Baker Street
London
SW1A 1AA
United Kingdom
```

Rules:

- House number PRECEDES the street name — `221B Baker Street`.
- Postcode is alphanumeric (outward + inward code), goes on its own final line above the country — `SW1A 1AA`.
- County is optional in modern UK addressing (Royal Mail dropped the requirement decades ago); include only when locality is ambiguous.

## Mandatory disclosure pages

Every consumer-facing UK storefront must link the following from the footer (Consumer Contracts Regulations 2013 + Consumer Rights Act 2015):

1. **Terms & Conditions** — sales terms.
2. **Privacy Policy** — UK GDPR / Data Protection Act 2018 compliant.
3. **Cookie Policy** — separate or a dedicated section within Privacy Policy.
4. **Returns & Refunds Policy** — 14-day right to cancel under CCRs 2013.
5. **Delivery Information** — shipping terms and expected timelines.
6. **Contact Information** — geographical address of the business (a PO box is not sufficient).

The trader's name, geographical address, and contact details (Regulation 27 CCRs) must appear before the customer places the order.

## Consumer protection basics

- Cooling-off period: **14 days** from receipt (CCRs 2013 Regulation 29). Extends to 12 months + 14 days if the trader failed to provide the withdrawal information.
- Refund window: refund within **14 days** of receiving the returned goods (or evidence of return).
- Statutory rights: goods must be of satisfactory quality, fit for purpose, and as described (Consumer Rights Act 2015). Short-term right to reject: 30 days. These cannot be excluded for B2C.
- Cross-border obligations: NFR into GB — HMRC now expects sellers to charge UK VAT at point of sale for consignments under £135; above that, the customer is importer of record.

## Cookie / privacy law

- Framework: **UK GDPR** + **Data Protection Act 2018** + **PECR** (Privacy and Electronic Communications Regulations).
- Cookie banner: opt-in for non-essential cookies (PECR Regulation 6). ICO 2023 guidance: Reject All must be as easy to click as Accept All.
- International transfers: post-Brexit, transfers to the US require the UK Extension to the EU-US DPF, or SCCs with the ICO's UK IDTA addendum. Reference in the privacy policy.
- Regulator: **ICO** (Information Commissioner's Office). Fines up to £17.5M or 4% of turnover.

## Price display rule

- **VAT-inclusive**: consumer prices on the storefront MUST be shown inclusive of VAT (Price Marking Order 2004). Business-only channels (B2B) may show ex-VAT with a clear indicator, but consumer sites cannot.
- Delivery charges must be shown before the customer commits to buying.

## Unit-price rule

**Yes — Price Marking Order 2004 (Schedule 1).** Products sold by weight, volume, or unit-count in specified categories (most food and drink, cosmetics, cleaning products) must show a unit price. Enforced by Trading Standards.
