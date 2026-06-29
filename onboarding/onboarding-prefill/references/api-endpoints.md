# Onboarding API Reference

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
