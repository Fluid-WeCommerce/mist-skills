---
name: Australia country settings
description: Legal and commercial defaults for selling into Australia — GST, currency, language, address, disclosures, Privacy Act, and price-display rules.
icon: flag
category: countries
---

# Australia (AU) — country settings

Baseline the `open-country` workflow and the Australian `compliance-manager` skill load for AU.

## VAT profile

- Name: `GST` (Goods and Services Tax)
- Standard rate: `10%`
- Zero-rated: fresh food, most health services, some educational courses.
- Notes: since July 2018, imported low-value goods (AUD $1,000 or less) sold to Australian consumers require the seller / marketplace to collect GST at point of sale (`LVIG` regime). Sellers with worldwide taxable Australian sales > AUD $75,000 must register with the ATO.

## Currency

- Code: `AUD`
- Symbol: `$` (or `A$` / `AUD$` to disambiguate). Placed BEFORE the amount, no space: `$19.99`.
- Decimal separator: `.` (period). Thousands separator: `,` (comma). Example: `$1,234.56`.

## Language

- Primary: `en-AU` (Australian English).
- Widely spoken: none required.

## Address format

Example (realistic):

```
Sarah Wilson
42 Collins Street
Melbourne VIC 3000
Australia
```

Rules:

- House number PRECEDES the street name.
- **Suburb** (not city) is the standard locality line — `Melbourne` in the example is a suburb of the metropolitan area.
- State written as abbreviation — `NSW`, `VIC`, `QLD`, `SA`, `WA`, `TAS`, `NT`, `ACT`.
- Postcode is 4 digits, on the same line as state.

## Mandatory disclosure pages

Every consumer-facing Australian storefront must link the following from the footer (Australian Consumer Law + Privacy Act 1988):

1. **Terms & Conditions**.
2. **Privacy Policy** — Privacy Act 1988 / Australian Privacy Principles (APPs) compliant.
3. **Cookie Policy** — separate or embedded in Privacy Policy.
4. **Returns & Refunds Policy** — must reflect Australian Consumer Law (ACL) consumer guarantees, which are non-excludable.
5. **Shipping & Delivery**.
6. **Contact Information** — Australian Business Number (ABN) and geographical address for the seller.

The seller's identity and ABN must be disclosed before the customer places the order.

## Consumer protection basics

- Cooling-off period: **no unconditional distance-selling cooling-off period at federal level** (unlike EU/UK). Some door-to-door / unsolicited-sales windows exist but don't apply to standard e-commerce.
- ACL Consumer Guarantees are stronger than a right of withdrawal — goods must be of acceptable quality, fit for purpose, matching description, safe, durable, and delivered on time. Cannot be waived. Refund/replacement/repair required for major failures.
- Refund window: no fixed statutory window; ACL requires refunds be issued "within a reasonable time" for eligible returns.
- Cross-border obligations: NFR into AU under AUD $1,000 — seller must collect GST at point of sale (LVIG). Over AUD $1,000, customs collects GST + duty at the border and the customer is importer of record.

## Cookie / privacy law

- Framework: **Privacy Act 1988** + **Australian Privacy Principles (APPs)**.
- Notification (APP 1): a Privacy Policy must be published, freely available, and disclose: types of personal information collected, purposes, disclosure to third parties (including overseas), and how to complain.
- Cookie banner: not federally required per se, but non-essential trackers benefit from consent under APP 3 (collection only when necessary). Best practice for retail e-commerce: opt-in with Reject All parity.
- Cross-border transfers: APP 8 requires the discloser to take reasonable steps to ensure overseas recipients handle personal info consistent with APPs, OR obtain express consent for the transfer.
- Regulator: **OAIC** (Office of the Australian Information Commissioner). 2022 amendments raised max fines to AUD $50M or 30% of adjusted turnover.

## Price display rule

- **GST-inclusive**: consumer prices on Australian storefronts MUST be shown inclusive of GST (Competition and Consumer Act 2010 §48). "Single-price rule" — the total price customers will pay, including all mandatory fees, must be prominent. Component-pricing (base + tax + surcharges) can be shown alongside but the total must be at least as prominent as any component.
- Shipping surcharges disclosed before order confirmation.

## Unit-price rule

**Retail Grocery Industry (Unit Pricing) Code — mandatory for grocery retailers with 1,000+ product lines including packaged food.** Applies to physical + online grocery retail. For non-grocery e-commerce, unit pricing is not mandatory but is best practice. Score `ok` when present, `review` when absent for non-grocery AU.
