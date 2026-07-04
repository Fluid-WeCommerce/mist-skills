---
name: Germany country settings
description: Legal and commercial defaults for selling into Germany — VAT, currency, language, address, disclosures, cookie/privacy law, and price-display rules.
icon: flag
category: countries
---

# Germany (DE) — country settings

Everything below is the compliance baseline the `open-country` workflow and the German `compliance-manager` skill read for this market. Values are load-bearing; do not paraphrase them at call sites.

## VAT profile

- Name: `Mehrwertsteuer (USt)`
- Standard rate: `19%`
- Reduced rate: `7%` — most groceries, books, newspapers, cultural events.
- Notes: EU OSS registration applies to distance sales into DE from other EU states once the €10,000 pan-EU threshold is crossed. Non-EU sellers register directly with the Bundeszentralamt für Steuern.

## Currency

- Code: `EUR`
- Symbol: `€` — placed AFTER the amount with a non-breaking space: `19,99 €`.
- Decimal separator: `,` (comma). Thousands separator: `.` (period). Example: `1.234,56 €`.

## Language

- Primary: `de` (German).
- Widely spoken: `en` (English) — acceptable as a secondary storefront language but never as the only one.

## Address format

Example (realistic):

```
Anna Müller
Musterstraße 12
10115 Berlin
Deutschland
```

Rules:

- House number FOLLOWS the street name — `Musterstraße 12`, never `12 Musterstraße`.
- Postal code is 5 digits, precedes the city on the same line — `10115 Berlin`.
- Country line only for international shipping. Domestic addresses omit it.

## Mandatory disclosure pages

Every commercial storefront serving DE must link the following pages from the site footer (Telemediengesetz §5 and BGB-InfoV):

1. **Impressum** — legal notice: full company name, address, phone/email, register number, VAT ID, managing directors, responsible person for content.
2. **Datenschutzerklärung** — GDPR/DSGVO-compliant privacy policy.
3. **AGB (Allgemeine Geschäftsbedingungen)** — general terms and conditions.
4. **Widerrufsbelehrung** — right-of-withdrawal notice with the 14-day model form.
5. **Versand- und Zahlungsbedingungen** — shipping and payment terms.

All five must be reachable from every page in the storefront in the primary language (German). Missing an Impressum has been repeatedly ruled abmahnfähig (grounds for cease-and-desist).

## Consumer protection basics

- Cooling-off period: **14 days** from receipt, unconditional. The clock only starts once the Widerrufsbelehrung was correctly provided; failing to provide it extends the window to 12 months + 14 days.
- Refund window: refund must be issued within **14 days** of the withdrawal notice; the merchant may withhold until either the goods are returned or the customer proves they were shipped back.
- Cross-border obligations: NFR shipments — customer is the importer of record; the storefront must be explicit about that and about the potential for customs duties/VAT on delivery.
- Warranty: statutory 2-year seller warranty (Gewährleistung) applies — cannot be contracted away for B2C.

## Cookie / privacy law

- Framework: **DSGVO** (GDPR as transposed) + **TTDSG** (Telekommunikation-Telemedien-Datenschutz-Gesetz, in force since December 2021).
- Cookie banner: opt-in, granular, equal-prominence for accept/reject. "Accept all" without a same-level "Reject all" button is non-compliant per BGH ruling (Cookie II, 2020).
- Analytics loading: no analytics/marketing scripts before explicit consent.
- Data-processing addendum: any US-based processor (Stripe, Klarna, TikTok, Meta) must be covered by an SCC or DPF certification referenced in the Datenschutzerklärung.

## Price display rule

- **VAT-inclusive**: all consumer prices on the storefront MUST be shown inclusive of VAT (Preisangabenverordnung §1). "€19,99 inkl. MwSt." is the acceptable phrasing; "plus tax" is not.
- Shipping costs must be indicated either as a specific amount or a clear reference to where the amount is computed, on the same page as the price.

## Unit-price rule

**Yes — Grundpreisverordnung (PAngV §4).** Any product sold by weight, volume, length, or area must show the unit price alongside the total price: `19,99 € (39,98 €/kg)`. Applies to almost all food, drink, cosmetics, and consumables. Missing unit prices is one of the most-abmahnt violations in DE e-commerce.
