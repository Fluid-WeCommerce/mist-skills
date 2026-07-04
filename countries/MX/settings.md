---
name: Mexico country settings
description: Legal and commercial defaults for selling into Mexico — IVA, currency, language, address, disclosures, privacy law, and price-display rules.
icon: flag
category: countries
---

# Mexico (MX) — country settings

Baseline the `open-country` workflow and the Mexican `compliance-manager` skill load for MX.

## VAT profile

- Name: `IVA` (Impuesto al Valor Agregado)
- Standard rate: `16%`
- Reduced rate: `0%` — most food and medicine.
- Border regions rate: `8%` — narrow northern and southern border zones (Región Fronteriza Norte / Sur decrees, renewed by executive order).
- Notes: since June 2020, non-resident digital-services providers into Mexico register with the SAT and remit IVA. E-invoicing (CFDI) is mandatory — any B2B customer will demand a CFDI-compliant invoice.

## Currency

- Code: `MXN`
- Symbol: `$` (or `MX$` / `MXN$` to disambiguate from USD). Placed BEFORE the amount: `$19.99` (with `MXN` suffix when disambiguation is helpful).
- Decimal separator: `.` (period). Thousands separator: `,` (comma). Example: `$1,234.56 MXN`.

## Language

- Primary: `es-MX` (Mexican Spanish).
- Widely spoken: `en` (English) — acceptable as a secondary storefront language, especially in border/tourism zones, but never as the only one.

## Address format

Example (realistic):

```
María González
Av. Reforma 12, Piso 5
Col. Juárez
Cuauhtémoc, 06600
Ciudad de México, CDMX
México
```

Rules:

- Street name PRECEDES the house number: `Av. Reforma 12`.
- `Colonia` (neighborhood) is a REQUIRED address line for delivery — `Col. Juárez`.
- Municipio / delegación (`Cuauhtémoc`) precedes the postal code and state.
- Postal code is 5 digits.
- State written as full name or 3-letter abbreviation (`CDMX`, `JAL`, `NLE`).

## Mandatory disclosure pages

Every consumer-facing Mexican storefront must link the following (Ley Federal de Protección al Consumidor + LFPDPPP + NOM-151):

1. **Términos y Condiciones** — sales terms.
2. **Aviso de Privacidad** — this is the LFPDPPP-required disclosure and MUST include specific elements: data-controller identity, purposes of processing, ARCO rights (Access, Rectification, Cancellation, Opposition), transfer disclosures.
3. **Política de Cookies** — separate policy or a dedicated section within the Aviso de Privacidad.
4. **Política de Devoluciones y Reembolsos**.
5. **Política de Envíos**.
6. **Contacto** — RFC (tax ID), physical address, and customer-service contact.

The full Aviso de Privacidad (aviso integral) must be linked from the point where personal data is collected — checkout, enrollment, contact form.

## Consumer protection basics

- Cooling-off period: **5 business days** for distance sales (LFPC Article 56) — narrower than EU regimes but unconditional within that window.
- Refund window: refund via the same payment method promptly upon valid cancellation.
- Warranty: mandatory manufacturer / seller warranty for reasonable time under LFPC Article 79-82; specific products (electronics, appliances) require formal Póliza de Garantía.
- Cross-border obligations: NFR into MX — customs (SAT / Aduanas) collect IVA + IEPS + duties for shipments over the personal-use de minimis. NOM-050 labelling requirements apply to products sold via Mexican channels; NFR imports for personal use are generally exempt.

## Cookie / privacy law

- Framework: **LFPDPPP** (Ley Federal de Protección de Datos Personales en Posesión de los Particulares) — enforced by **INAI**.
- Aviso de Privacidad: three layers (short / simplified / integral) — checkout must expose at least the short notice with a link to the integral version.
- Cookie banner: not a specific LFPDPPP requirement per se, but consent-based tracker use is best practice; the Aviso de Privacidad must disclose cookies used.
- Cross-border transfers: allowed with the individual's consent OR under one of LFPDPPP's Article 37 exceptions; specify transfers in the Aviso.
- Regulator: **INAI** (Instituto Nacional de Transparencia). Fines up to ~MXN $32M.

## Price display rule

- **VAT-inclusive**: consumer prices in Mexico are displayed IVA-included (`IVA incluido`) — PROFECO enforces this under LFPC. Prices without the `IVA incluido` label are treated as inclusive by default; showing prices ex-IVA on a consumer storefront is misleading advertising.
- Shipping costs must be disclosed before order confirmation.
- Currency must be identified when the storefront could ambiguously be USD or MXN.

## Unit-price rule

**Limited.** No general online unit-price mandate. NOM-030 requires unit pricing on physical retail shelves for prepackaged goods, but online-store equivalents are not universally enforced. Score online unit-price displays as `ok` when present, `review` when absent for MX.
