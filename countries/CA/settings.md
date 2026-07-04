---
name: Canada country settings
description: Legal and commercial defaults for selling into Canada — GST/HST/QST, currency, bilingual language rule, address, disclosures, privacy law, and price-display rules.
icon: flag
category: countries
---

# Canada (CA) — country settings

Baseline the `open-country` workflow and the Canadian `compliance-manager` skill load for CA. Canada is a federal + provincial patchwork; the rules below distinguish where it matters.

## VAT profile

- Name: `GST/HST` (federal Goods and Services Tax / Harmonized Sales Tax)
- Standard federal GST rate: `5%`
- HST provinces (combined federal + provincial): `13%` (ON), `15%` (NB, NL, NS, PE).
- Non-HST provinces charge provincial sales tax separately (BC PST `7%`, SK PST `6%`, MB RST `7%`).
- Quebec: `QST` `9.975%` on top of federal GST `5%` — total effective ~`14.975%`.
- Notes: sellers with worldwide revenue > CAD $30,000 must register for GST/HST. Digital-services sellers into Canada have registered under the simplified GST/HST framework since July 2021.

## Currency

- Code: `CAD`
- Symbol: `$` (or `C$` / `CAD$` to disambiguate). Placed BEFORE the amount, no space: `$19.99`.
- Decimal separator: `.` (period). Thousands separator: `,` (comma). Example: `$1,234.56`.
- Quebec (French): decimal separator is `,` and symbol placed AFTER — `19,99 $ CA`.

## Language

- Primary: `en-CA` (English) with `fr-CA` (French) as a co-equal requirement in **Quebec**.
- Widely spoken: `fr` (French) — required for consumer-facing content in Quebec under the **Charter of the French Language (Loi 101)**, tightened by **Loi 96** in 2022.
- Bilingual labeling is federally required for prepackaged goods under the **Consumer Packaging and Labelling Act**.

## Address format

Example (realistic):

```
John Tremblay
123 Main Street West
Suite 400
Toronto ON  M5V 2H1
Canada
```

Rules:

- House number PRECEDES the street name.
- Province is written as a 2-letter code — `ON`, `BC`, `QC`, `AB`. Two spaces separate province and postal code.
- Postal code is `A1A 1A1` alternating letter-digit, in CAPITALS.
- Quebec: address elements may appear in French (`rue`, `avenue`, `boulevard`).

## Mandatory disclosure pages

Every consumer-facing Canadian storefront must link the following from the footer:

1. **Terms of Service** — sales terms.
2. **Privacy Policy** — PIPEDA + Quebec Law 25 compliant.
3. **Cookie Policy** — separate or embedded in Privacy Policy.
4. **Returns & Refunds Policy** — provincial consumer-protection acts govern this; each has its own rules (Ontario CPA 2002 § 25, Quebec CPA §54.7, etc.).
5. **Shipping & Delivery**.
6. **Contact Information** — geographical business address; for a Quebec-registered enterprise, the NEQ (Numéro d'entreprise du Québec) if applicable.
7. **French-language versions of all of the above** if the site serves Quebec.

## Consumer protection basics

- Cooling-off period: federal + provincial mix. Distance-sales consumer-protection law across provinces gives buyers **at least 7 days** to cancel goods not received on time, and **10-30 days** on various types of contracts. There is no unconditional pan-Canadian 14-day right of withdrawal — provinces vary.
- Refund window: same-method-of-payment refund within `15 days` in most provinces once cancellation is valid.
- Warranty: implied warranty of merchantable quality under provincial Sale of Goods Acts; Quebec adds a robust legal-warranty regime (CPA §37-40) that cannot be waived.
- Cross-border obligations: NFR into Canada — CBSA collects duty and GST/HST at the border for shipments over CAD $150 (de minimis is CAD $20 for most, or CAD $150 for USMCA-origin goods).

## Cookie / privacy law

- Framework: **PIPEDA** federally, **Quebec Law 25** (formerly Bill 64) — the strictest privacy regime in Canada.
- Cookie banner: PIPEDA is consent-based rather than opt-in-per-cookie, but Law 25 (Quebec) requires opt-in for non-essential trackers with a same-prominence Refuse button.
- Cross-border data transfers: Law 25 §17 requires a Privacy Impact Assessment and explicit disclosure whenever personal information is transferred outside Quebec, including to the US.
- Regulator: **OPC** (Office of the Privacy Commissioner) federally; **CAI** (Commission d'accès à l'information) in Quebec. Law 25 fines up to CAD $25M or 4% of global turnover.

## Price display rule

- **VAT-exclusive at sticker; tax added at checkout**: Canadian convention. Consumer prices displayed on-shelf/in the storefront are typically exclusive of GST/HST/PST; the tax is calculated and shown at checkout.
- Quebec: additional rules under CPA §223-236 for accurate advertised pricing; the "Correction Policy" (10% discount when the scanned price is higher than the advertised price) applies to physical retail but has online-store analogues around price-match commitments.
- Shipping costs must be disclosed before order confirmation.

## Unit-price rule

**Provincial only.** No federal unit-pricing law. Quebec CPA requires unit prices on shelf tags for pre-packaged goods in retail; online-store equivalents are recommended but not legally mandatory. Score online-store unit-price displays as `ok` when present, `review` (not `fail`) when absent for CA.
