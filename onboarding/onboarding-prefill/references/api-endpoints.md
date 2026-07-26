# Onboarding API Reference

> **All calls go through the `fluid_api` tool** — `fluid_api(path, method, body)` with a
> RELATIVE path (e.g. `/api/settings/brand_guidelines`). The token and active company are
> injected automatically; never use raw fetch/curl or collect an API key.

All endpoints are paths on the active company's Fluid API.

Authentication is injected automatically by the Mist runtime — call these endpoints via the `fluid_api(path, method, body)` tool, which targets the active company and adds the token for you. You never pass a token or store URL. For example: `fluid_api("/api/companies/{id}/onboarding_info", "GET")`.

## Onboarding Info

| Method | Endpoint                              |
| ------ | ------------------------------------- |
| GET    | `/api/companies/{id}/onboarding_info` |
| PUT    | `/api/companies/{id}/onboarding_info` |

**Critical:** `PUT` overwrites the ENTIRE `onboarding_info` blob. Always `GET` first, deep-merge new data into the existing blob, then `PUT` back.

The GET response can contain empty optional nested objects such as
`terms_and_conditions_info: {}`. Do **not** echo an empty optional object into the PUT:
the write contract validates any object that is present and will reject it when its required
human-consent fields are absent. Omit an empty optional object. Preserve a non-empty
human-entered object verbatim; never invent or alter consent fields.

## Legal Entities

| Method | Endpoint                             |
| ------ | ------------------------------------ |
| GET    | `/api/companies/{id}/entities`       |
| POST   | `/api/companies/{id}/entities`       |
| PUT    | `/api/companies/{id}/entities/{eid}` |
| DELETE | `/api/companies/{id}/entities/{eid}` |

## Bank Accounts

| Method | Endpoint                                  |
| ------ | ----------------------------------------- |
| GET    | `/api/companies/{id}/bank_accounts`       |
| POST   | `/api/companies/{id}/bank_accounts`       |
| PUT    | `/api/companies/{id}/bank_accounts/{bid}` |
| DELETE | `/api/companies/{id}/bank_accounts/{bid}` |

## Owners

| Method | Endpoint                           |
| ------ | ---------------------------------- |
| GET    | `/api/companies/{id}/owners`       |
| POST   | `/api/companies/{id}/owners`       |
| PUT    | `/api/companies/{id}/owners/{oid}` |
| DELETE | `/api/companies/{id}/owners/{oid}` |

## Document Upload

| Method | Endpoint                                                                    |
| ------ | --------------------------------------------------------------------------- |
| POST   | `/api/companies/{id}/onboarding_info/upload_document` (multipart, 10MB max) |

## Lookups

| Method | Endpoint                                 |
| ------ | ---------------------------------------- |
| GET    | `/api/mcc_codes`                         |
| GET    | `/api/business_types?country_code={iso}` |

## Payments Status

| Method | Endpoint                              |
| ------ | ------------------------------------- |
| GET    | `/api/companies/{id}/payments_status` |

## Settings

| Method | Endpoint                          | Used for                                               |
| ------ | --------------------------------- | ------------------------------------------------------ |
| GET    | `/api/settings/company`           | Company identity (id, name) for preflight confirmation |
| GET    | `/api/settings/company_countries` | Token validation + country data                        |
| GET    | `/api/settings/brand_guidelines`  | Read identity, colors, fonts, and `brand_md`            |
| PATCH  | `/api/settings/brand_guidelines`  | Set identity, colors, fonts, images, and `brand_md`     |

## Brand Guidelines (identity + fonts + brand.md) — exact contract

`PATCH /api/settings/brand_guidelines` accepts EXACTLY these fields (verified against the
Rails `UpdateAction` params schema — anything else is dropped):

```jsonc
{
  "brand_guidelines": {
    "name": "Brand Name", // optional, string
    "logo_url": "https://…", // optional, string URL — see logo flow below
    "icon_url": "https://…", // optional, string URL
    "favicon_url": "https://…", // optional, string URL
    "color": "#1A2B3C", // optional — PRIMARY brand color
    "secondary_color": "#DDEEFF", // optional
    "default_og_image": "https://…", // optional, string URL
    "default_og_description": "…", // optional, string
    "default_fallback_image": "https://…", // optional, string URL
    "brand_md": "# Brand Guide\n…", // optional, string; normally write via update_brand_voice
    "fonts": [
      {
        "name": "Licensed Font Family", // required
        "file_url": "https://ik.imagekit.io/fluid/…/font.woff2", // required
        "file_id": 123, // optional integer DAM asset id
        "format": "woff2", // optional
        "weight": "400", // optional string
        "style": "normal", // optional string
        "role": "body", // optional string, e.g. body or heading
      },
    ],
  },
}
```

**Logo/image flow — two steps, in order.** The endpoint takes a **URL**, not a file:

1. In Mist, use `dam_upload` for files already in the project sandbox. It returns
   `asset.default_variant_url`.
2. For a remote source URL, the upload service also accepts multipart
   `external_asset_url` and fetches the bytes server-side; `fileName` is auto-detected
   unless supplied. The exact field name is `external_asset_url`, not `external_url`.
   The Fluid CLI exposes this as `fluid dam upload --url <SOURCE_URL>`.
3. `PATCH /api/settings/brand_guidelines` with `logo_url` (and/or `icon_url`,
   `favicon_url`) set to that DAM URL. Never point these at the source site's CDN — those
   links rot and leak the source domain.
4. Re-GET the settings and re-fetch each saved asset URL. Require a successful response,
   non-empty bytes, and the expected media type. Confirm `logo_url` is the canonical
   standalone brand mark from the rendered global header/source metadata—not a collaboration
   lockup, campaign graphic, or generic Fluid default. Use a verified same-brand fallback for
   icon/favicon only when the source exposes no distinct icon, and record that decision.

**Font flow.** Only ingest a font when the company owns a webfont license that
allows re-hosting:

1. Record the exact family, weights, styles, file URLs, license source, and
   verdict from the source stylesheet and supporting evidence.
2. Ingest each licensed font through the DAM using a local file or multipart
   `external_asset_url`, just like an image.
3. Add one `fonts[]` entry per real font file. `name` and `file_url` are
   required; populate `file_id`, `format`, `weight`, `style`, and `role` when
   known.
4. For a proprietary or unverified font, do not copy its bytes. Record the
   original family and a legally usable substitute in `brand.md`, and only
   persist the licensed substitute in `fonts`.
5. Re-fetch every persisted `file_url`. Reject 404/empty responses and reject several
   declared weights that all resolve to one duplicated regular-font file.

Notes:

- Wrap the payload in the `brand_guidelines` key — a flat body is ignored.
- A successful update auto-re-evaluates the Getting Started "brand guidelines" step
  (`onboarding.check_brand_guidelines`) — no separate check_step call needed for it.
- `brand_md` is part of this endpoint, but in Mist use `update_brand_voice`
  rather than a direct PATCH so the local `<company>/brand.md` and API value
  stay synchronized.
- Verify after push: `GET /api/settings/brand_guidelines` and confirm the fields landed.

## Company profile (rename, support email, country) — exact contracts

**`PATCH /api/settings/companies/{id}`** — rename + support email live HERE (verified
against the Rails UpdateAction schema). The `{id}` in the path is REQUIRED (integer — the
company id from `GET /api/settings/company`); PATCHing `/api/settings/company` (no id) or
sending a flat body 400s. Body wrapped in the `company` key:

```jsonc
{
  "company": {
    "name": "Bucked Up", // rename
    "support_email": "cs@brand.com", // support/customer-service email
    "country_code": "US", // company-level country code
  },
}
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

**`PATCH /api/settings/company_countries/{company_country_id}`** — attach the matched
legal entity to an existing selling country and record settlement details. The id in this
path is the company-country record id returned by `GET /api/settings/company_countries`,
not the country id and not the entity id:

```jsonc
{
  "company_country": {
    "entity_id": 126,
    "entity_legally_registered": true,
    "settlement_currency": "USD",
  },
}
```

After the PATCH, GET the company countries again and require the intended country row to
return that entity, `entity_legally_registered: true`, and the expected settlement
currency. Writing the same values only to `onboarding_info.countries_info` does not attach
the entity to the live market.
