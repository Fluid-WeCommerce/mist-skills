# Onboarding API Reference

> **All calls go through the `fluid_api` tool** — `fluid_api(path, method, body)` with a
> RELATIVE path (e.g. `/api/settings/brand_guidelines`). The token and active company are
> injected automatically; never use raw fetch/curl or collect an API key.

All endpoints are paths on the active company's Fluid API.

Authentication is injected automatically by the Mist runtime — call these endpoints via the `fluid_api(path, method, body)` tool, which targets the active company and adds the token for you. You never pass a token or store URL. For example: `fluid_api("/api/companies/{id}/onboarding_info", "GET")`.

## Onboarding Info

| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/onboarding_info` |
| PUT | `/api/companies/{id}/onboarding_info` |

**Critical:** `PUT` overwrites the ENTIRE `onboarding_info` blob. Always `GET` first, deep-merge new data into the existing blob, then `PUT` back.

## Legal Entities

| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/entities` |
| POST | `/api/companies/{id}/entities` |
| PUT | `/api/companies/{id}/entities/{eid}` |
| DELETE | `/api/companies/{id}/entities/{eid}` |

## Bank Accounts

| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/bank_accounts` |
| POST | `/api/companies/{id}/bank_accounts` |
| PUT | `/api/companies/{id}/bank_accounts/{bid}` |
| DELETE | `/api/companies/{id}/bank_accounts/{bid}` |

## Owners

| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/owners` |
| POST | `/api/companies/{id}/owners` |
| PUT | `/api/companies/{id}/owners/{oid}` |
| DELETE | `/api/companies/{id}/owners/{oid}` |

## Document Upload

| Method | Endpoint |
|--------|----------|
| POST | `/api/companies/{id}/onboarding_info/upload_document` (multipart, 10MB max) |

## Lookups

| Method | Endpoint |
|--------|----------|
| GET | `/api/mcc_codes` |
| GET | `/api/business_types?country_code={iso}` |

## Payments Status

| Method | Endpoint |
|--------|----------|
| GET | `/api/companies/{id}/payments_status` |

## Settings

| Method | Endpoint | Used for |
|--------|----------|----------|
| GET | `/api/settings/company` | Company identity (id, name) for preflight confirmation |
| GET | `/api/settings/company_countries` | Token validation + country data |
| GET | `/api/settings/brand_guidelines` | Read current brand (logo, colors) before pushing |
| PATCH | `/api/settings/brand_guidelines` | Set brand colors + logo/icon/favicon/OG images |

## Brand Guidelines (logo + colors) — exact contract

`PATCH /api/settings/brand_guidelines` accepts EXACTLY these fields (verified against the
Rails `UpdateAction` params schema — anything else is dropped):

```jsonc
{ "brand_guidelines": {
  "name": "Brand Name",                 // optional, string
  "logo_url": "https://…",              // optional, string URL — see logo flow below
  "icon_url": "https://…",              // optional, string URL
  "favicon_url": "https://…",           // optional, string URL
  "color": "#1A2B3C",                   // optional — PRIMARY brand color
  "secondary_color": "#DDEEFF",         // optional
  "default_og_image": "https://…",      // optional, string URL
  "default_og_description": "…",        // optional, string
  "default_fallback_image": "https://…" // optional, string URL
}}
```

**Logo/image flow — two steps, in order.** The endpoint takes a **URL**, not a file:
1. Upload the image to the Fluid DAM first. In Mist, use the `dam_upload` tool (or the
   upload service with `external_asset_url: <source image URL>` so it fetches the remote
   file server-side). It returns `asset.default_variant_url`.
2. `PATCH /api/settings/brand_guidelines` with `logo_url` (and/or `icon_url`,
   `favicon_url`) set to that DAM URL. Never point these at the source site's CDN — those
   links rot and leak the source domain.

Notes:
- Wrap the payload in the `brand_guidelines` key — a flat body is ignored.
- A successful update auto-re-evaluates the Getting Started "brand guidelines" step
  (`onboarding.check_brand_guidelines`) — no separate check_step call needed for it.
- **Fonts are NOT part of brand_guidelines** — there is no font field in this schema.
  Brand fonts live in the theme (theme tokens / settings_data), so set them via the
  theme, and don't fail a brand-QA check for a "missing font" on this endpoint.
- Verify after push: `GET /api/settings/brand_guidelines` and confirm the fields landed.

## Company profile (rename, support email, country) — exact contracts

**`PATCH /api/settings/companies/{id}`** — rename + support email live HERE (verified
against the Rails UpdateAction schema). The `{id}` in the path is REQUIRED (integer — the
company id from `GET /api/settings/company`); PATCHing `/api/settings/company` (no id) or
sending a flat body 400s. Body wrapped in the `company` key:

```jsonc
{ "company": {
  "name": "Bucked Up",              // rename
  "support_email": "cs@brand.com",  // support/customer-service email
  "country_code": "US"              // company-level country code
}}
```
(Other permitted fields: appstore_url, playstore_url, active, allow_signup, sandbox,
mobile_app_identifier, … — anything not in the schema is dropped.)

**`POST /api/settings/company_countries`** — add a selling country/market. Body wrapped in
`company_country`:

```jsonc
{ "company_country": { "country_id": 214, "currency": "USD", "default": true } }
```
(`country_id` integer required — 214 = US. `GET /api/settings/company_countries` first to
check what exists; note `company_country_id` ≠ `country_id`.)
