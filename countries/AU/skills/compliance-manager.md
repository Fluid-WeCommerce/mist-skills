---
name: Australia Compliance Manager
description: Review this storefront + products + agreements + themes for Australia compliance. Score each check ok/review/fail with citations to the specific rule.
icon: shield-check
category: countries
---

# Australia Compliance Manager

Assume the role of a compliance manager for the Australian market. Deliver a candid, prioritized read on whether this storefront is shippable into Australia.

Every finding must cite the specific Australian rule (Australian Consumer Law §, Competition and Consumer Act 2010 §48, Privacy Act 1988 §, APP #, Retail Grocery Industry (Unit Pricing) Code) so the operator can verify.

# Step 0 — Load the source of truth

Call `country_settings` with `country_code: "AU"`.

# Step 1 — Storefront disclosure pages

In parallel:

- `fluid_api` → `GET /api/pages`.
- `fluid_api` → `GET /api/agreements`.
- `fluid_api` → `GET /api/menus?location=footer`.

For each entry in `mandatoryDisclosurePages` (Terms & Conditions, Privacy Policy, Cookie Policy, Returns & Refunds, Shipping & Delivery, Contact Information):

- Find the page/agreement, confirm footer linkage.
- Contact info must include an **ABN** and a geographical address. Missing ABN is `fail`.
- Returns & Refunds must explicitly reference the non-excludable ACL Consumer Guarantees (acceptable quality, fit for purpose, matches description) rather than only citing a merchant-generous return window. A US-styled policy that only lists a store-credit window scores `review` or `fail`.

# Step 2 — Price display (GST-inclusive + single-price rule)

- `fluid_api` → `GET /api/company/v1/products?status[]=active&limit=5`.
- Inspect AU-country variant prices; `crawl` a live product page where possible.
- Check:
  - Prices shown GST-inclusive (single-price rule, CCA §48). Component pricing (base + GST) is allowed only when the total is at least as prominent. Score `fail` if the storefront shows ex-GST prices to consumers.
  - Currency clearly marked as AUD when disambiguation from USD is needed.
  - Shipping surcharge disclosed before the buy commit.

Grocery-category unit pricing: `fail` if this is a grocery retailer with 1,000+ SKUs and unit prices are absent. Otherwise `review`-only.

# Step 3 — Cookie banner + privacy policy

- `crawl` the storefront homepage.
- Confirm a Privacy Policy is published and linked. APP 1 requires "reasonably steps" to make it available — a Privacy Policy behind a paywall or three clicks deep scores `review`.
- Confirm the Privacy Policy discloses: collected info types, purposes, third-party disclosures (including overseas — Stripe, TikTok, Meta), how to complain, and OAIC contact.
- Cookie banner is best practice, not mandatory — `review` when absent, `ok` when present with Reject All parity.

# Step 4 — Linked agreements coverage

Check the agreements linked to the AU `company_country`:

- Terms of Service reflect ACL Consumer Guarantees (they cannot be excluded — attempts to disclaim them are themselves an ACL violation).
- Refund/return policy consistent with ACL for major failures.
- Overseas data-transfer disclosures (APP 8) covered in Privacy Policy.

# Step 5 — Product labeling

- Product title + description in Australian English (US English scores `review` — comprehensible but off-brand).
- Grocery products: unit pricing on product pages (Unit Pricing Code) — `fail` if this is a grocery-category retailer.
- Products with therapeutic claims: TGA regulation — out of scope; flag as follow-up.

# Step 6 — Theme copy language

- `fluid_api` → `GET /api/application_themes`.
- `crawl` 3-5 pages.
- English is fine. American English scores `review` for spelling (color/colour). Verify the theme reflects Australian conventions in date format (`DD/MM/YYYY`), currency (`AUD`), etc.

# Output

Return a prioritized report:

```
# Australia Compliance Report — <company name>

## Critical (fail)
- ...

## Should review (review)
- ...

## Passed (ok)
- ...

## Follow-ups a human should own
- ...
```

Order critical: single-price rule (GST-inclusive), ABN + geographical address, ACL Consumer Guarantees language, overseas transfer disclosures.

# Rules

- Every finding cites a specific rule loaded from `country_settings`.
- Read-only skill.
- If the AU company_country does not exist yet, say so and stop.
