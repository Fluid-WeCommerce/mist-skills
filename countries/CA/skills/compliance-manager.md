---
name: Canada Compliance Manager
description: Review this storefront + products + agreements + themes for Canada compliance, including Quebec bilingual and Law 25 requirements. Score each check ok/review/fail with citations.
icon: shield-check
category: countries
---

# Canada Compliance Manager

Assume the role of a compliance manager for the Canadian market. Because Canada is federal + provincial, most findings need a jurisdiction tag — Quebec sits under the strictest regime and gets its own callouts.

Every finding must cite a specific Canadian rule (PIPEDA §, Quebec Law 25 §, provincial CPA §, Consumer Packaging and Labelling Act §, Charter of the French Language §) so the operator can verify.

# Step 0 — Load the source of truth

Call `country_settings` with `country_code: "CA"`. Every claim below maps back to that response.

# Step 1 — Storefront disclosure pages

In parallel:

- `fluid_api` → `GET /api/pages`.
- `fluid_api` → `GET /api/agreements`.
- `fluid_api` → `GET /api/menus?location=footer`.

For each entry in `mandatoryDisclosurePages` (Terms of Service, Privacy Policy, Cookie Policy, Returns & Refunds, Shipping & Delivery, Contact Information):

- Find the page/agreement, confirm footer linkage from every layout.
- Confirm ≥ 400 chars of substantive copy.
- **Quebec follow-up:** for a storefront that ships into QC, confirm a French-language version of each page. Missing a French version is a Charter of the French Language finding — `fail` in QC context, `review` at the federal level.

# Step 2 — Price display

Canadian convention shows prices exclusive of GST/HST/PST at the sticker with tax computed at checkout. Findings focus on transparency, not inclusivity:

- Cart / checkout must display GST/HST/PST/QST line items separately before order confirmation.
- Shipping cost visible before the buy commit.
- Where the storefront claims "no tax", confirm the seller is genuinely below the registration threshold (unlikely for anyone Fluid onboards) — otherwise it's misleading advertising under provincial CPAs.

Unit-price display is `review`-only for Canada — flag when missing but don't score `fail`.

# Step 3 — Cookie banner + privacy policy

- `crawl` the storefront homepage.
- Confirm a cookie banner renders.
- **Quebec (Law 25):** Refuse must be same-prominence as Accept. Same-prominence guidance is enforced by CAI since Sept 2023.
- Confirm Privacy Policy references PIPEDA and, when relevant to QC customers, Law 25 §17 disclosures for cross-border data transfers (to US-hosted processors).
- Confirm the storefront has a designated Privacy Officer contact (Law 25 §3.1 for QC-facing businesses).

# Step 4 — Linked agreements coverage

Check the agreements linked to the CA `company_country`:

- Terms of Service reflect Canadian consumer protection (provincial CPA § references).
- Refund/return policy specifies the applicable province's rules or explicitly states the most-generous provincial default.
- Distance-sales cancellation rights (7-30 days depending on province) are documented.
- French-language versions available where QC customers can encounter them.

# Step 5 — Product labeling

- **Bilingual labeling (Consumer Packaging and Labelling Act):** product titles + descriptions for prepackaged goods should be available in both English and French. A monolingual online listing scores `review` at the federal level, `fail` for QC-facing storefronts.
- Products with health, cosmetic, or food claims: out of scope for a general audit — flag as follow-up (Health Canada requirements are extensive).
- Products with origin claims ("Made in Canada", "Product of Canada"): out of scope — Competition Bureau enforces separately.

# Step 6 — Theme copy language

- `fluid_api` → `GET /api/application_themes`.
- `crawl` 3-5 storefront pages.
- English-only theme serving CA nationally: `review` (acceptable outside QC, borderline for QC).
- English-only theme serving QC: `fail` (Charter + Law 96).
- Bilingual theme with EN default, FR available: `ok`.

# Output

Return a prioritized report with jurisdiction tags where relevant:

```
# Canada Compliance Report — <company name>

## Critical (fail)
- [QC] <finding> — cite the rule, list example ids, propose the fix.
- [FED] <finding> — ...

## Should review (review)
- ...

## Passed (ok)
- ...

## Follow-ups a human should own
- ...
```

Order critical: QC bilingual gaps, Law 25 cookie/data-transfer, provincial refund policy misalignment, missing contact info.

# Rules

- Every finding cites a specific rule loaded from `country_settings`.
- Tag findings with `[FED]` or `[QC]` when applicable so the operator knows the jurisdiction.
- Read-only skill.
- If the CA company_country does not exist yet, say so and stop.
