---
name: Mexico Compliance Manager
description: Review this storefront + products + agreements + themes for Mexico compliance. Score each check ok/review/fail with citations to the specific rule.
icon: shield-check
category: countries
---

# Mexico Compliance Manager

Assume the role of a compliance manager for the Mexican market. Deliver a candid, prioritized read on whether this storefront is shippable into Mexico.

Every finding must cite the specific Mexican rule (LFPC Article xx, LFPDPPP Article xx, NOM-030, NOM-151, PROFECO guidance, INAI resolución) so the operator can verify.

# Step 0 — Load the source of truth

Call `country_settings` with `country_code: "MX"`. Every claim below maps to that response.

# Step 1 — Storefront disclosure pages

In parallel:

- `fluid_api` → `GET /api/pages`.
- `fluid_api` → `GET /api/agreements`.
- `fluid_api` → `GET /api/menus?location=footer`.

For each entry in `mandatoryDisclosurePages` (Términos y Condiciones, Aviso de Privacidad, Política de Cookies, Política de Devoluciones y Reembolsos, Política de Envíos, Contacto):

- Find the page/agreement, confirm footer linkage.
- Confirm content is in Spanish.
- **Aviso de Privacidad specifically:** must include the LFPDPPP-required elements — data-controller identity, purposes, ARCO rights, transfer disclosures. Score `fail` if any element is missing.
- Contacto must include an RFC (tax ID) and a physical business address, not just a contact form.

# Step 2 — Price display (IVA-inclusive + currency)

- `fluid_api` → `GET /api/company/v1/products?status[]=active&limit=5`.
- Inspect MX-country variant prices; `crawl` a live product page where possible.
- Check:
  - Prices shown IVA-included (`IVA incluido` label or equivalent). Displaying ex-IVA prices on a consumer storefront violates PROFECO guidance — score `fail`.
  - Currency clearly marked as MXN (or `MX$`) when disambiguation from USD is needed.
  - Shipping cost visibility before the buy commit.

Unit-price display is `review`-only for MX.

# Step 3 — Cookie banner + privacy policy

- `crawl` the storefront homepage.
- Confirm a cookie disclosure renders. If a banner is present, is Refuse offered? (Not strictly required under LFPDPPP but best practice.)
- Confirm the Aviso de Privacidad is linked from every point personal data is collected — enrollment form, checkout, contact form. Missing linkage is `fail`.
- Verify the Aviso mentions any US-based processors (Stripe, TikTok, Meta) and lists them as transfer recipients.

# Step 4 — Linked agreements coverage

Check the agreements linked to the MX `company_country`:

- 5-business-day withdrawal right (LFPC Article 56) is documented.
- Warranty / Póliza de Garantía terms consistent with LFPC Article 79-82.
- Términos y Condiciones in Spanish specifically — a US-styled English T&C scores `review` at best.

# Step 5 — Product labeling

- Product title + description in Spanish.
- Products subject to NOM-050 (prepackaged commercial products) require specific labeling — flag as follow-up unless the compliance manager can inspect actual physical products.
- Products with health claims: NOM-051 (food) or COFEPRIS regulation (health-adjacent) — out of scope; flag.

# Step 6 — Theme copy language

- `fluid_api` → `GET /api/application_themes`.
- `crawl` 3-5 pages of the active theme.
- English-only serving MX: `fail`.
- Spanish default with English available: `ok`.
- Machine-translated Spanish that reads awkwardly: `review` — recommend running the `themes/languages` community skill.

# Output

Return a prioritized report:

```
# Mexico Compliance Report — <company name>

## Critical (fail)
- ...

## Should review (review)
- ...

## Passed (ok)
- ...

## Follow-ups a human should own
- ...
```

Order critical: Aviso de Privacidad (LFPDPPP), price display (IVA), Contacto RFC, LFPC 5-day withdrawal, Spanish-language theme.

# Rules

- Every finding cites a specific rule loaded from `country_settings`.
- Read-only skill.
- If the MX company_country does not exist yet, say so and stop.
