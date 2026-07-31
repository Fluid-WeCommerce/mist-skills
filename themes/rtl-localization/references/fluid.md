# Fluid API Appendix (public-facing)

This skill runs against the **exposed Fluid company API** — everything below is callable by an
external client with a company token. Work against the active company: base URL
`{{company.api_base}}`, `Authorization: Bearer <token>`, `Content-Type: application/json`.
Do NOT rely on editing repo files or the Rails console — use these endpoints. Verify against
the OpenAPI specs (`docs/openapi/themes-v0.yaml`, `docs/openapi/admin-v2025-06.yaml`) if a
field is unclear.

## Scopes required

- Templates + region rules: `application_themes:view` (read), `application_themes:update` (write).
- Sitemap: `sitemap:view` (read), `sitemap:update` (write).

## Key facts

- The theme layout ships with no `dir` attribute today — Phase 2 adds it. Both the Liquid
  `content` and the `stylesheet` (CSS) of a template are editable through the template API, so
  the direction-aware markup and logical-property CSS go through the same endpoint.
- A template's `content` is locale-translatable, but template selection is **not** locale-aware.
  Serving a different template per **country** is done with a region rule.
- Region is resolved from `?region=`, the `fluid_locale` cookie, or geo headers — not a URL path.

## Phase 2 & 4 — edit / clone the template

List, read, and write templates via `/api/application_theme_templates`.

- **Find the target template:** `GET {{company.api_base}}/api/application_theme_templates`
  (filter by `themeable_type`, e.g. `home_page`, `product`, `page`).
- **Clone into an RTL variant** (preferred over editing the shared template):
  `POST {{company.api_base}}/api/application_theme_templates/:id/clone`
- **Edit the variant's markup/CSS** (add `dir`, convert to logical properties):
  `PATCH {{company.api_base}}/api/application_theme_templates/:id`

```json
{
  "application_theme_template": {
    "name": "Home — RTL (ar)",
    "content": "…Liquid with dir-aware layout…",
    "stylesheet": "…CSS using logical properties…",
    "status": "draft"
  }
}
```

- **Publish when approved:** `POST {{company.api_base}}/api/application_theme_templates/:id/publish`
- Create-from-scratch (if not cloning): `POST {{company.api_base}}/api/application_theme_templates?application_theme_id=:id`
  with `application_theme_template: { name, themeable_type, content, stylesheet, variables, translations }`.
- Other useful ops: `POST …/:id/set_default`, `POST …/:id/render_page` (preview),
  `GET …/:id/available_variables`.

## Phase 5 — assign the template to a country (the "router")

Bind country → template with a region rule. This is the mechanism behind "assign it per country".

`POST {{company.api_base}}/api/theme_region_rules`

```json
{
  "theme_region_rule": {
    "route_path": "/",
    "region_code": "SA",
    "application_theme_template_id": 12345,
    "route_kind": "page",
    "redirect_type": "template",
    "priority": 0,
    "active": true
  }
}
```

- `region_code` is the country ISO (e.g. `SA`) or `default`.
- `application_theme_id` is optional (defaults to the company's current theme).
- Manage with `GET /api/theme_region_rules`, `PUT /api/theme_region_rules/:id`,
  `DELETE /api/theme_region_rules/:id`.

## Phase 6 — SEO / sitemap (what the API actually allows)

`/api/v2025-06/sitemap` exposes **visibility only**:

- `GET {{company.api_base}}/api/v2025-06/sitemap` — list URLs + visibility state.
- `PATCH {{company.api_base}}/api/v2025-06/sitemap` — `{ "url": "...", "active": true|false }`,
  or `{ "url": "hide-all"|"show-all", "active": ... }`.

**Known limitation (do not overpromise):** there is **no exposed API** to emit per-country
`hreflang` alternates or path-based localized URLs. hreflang is emitted per-language via a
`?lang=<iso>` param in the storefront head, and the sitemap only hides/shows URLs. Ship RTL
with the template + region rule, set language `hreflang` where available, and flag deeper
per-country SEO indexing as a backend follow-up rather than implementing it here.

## Verify

Preview with `POST …/:id/render_page`, then load the storefront with the target region
(`?region=SA`) and run the Phase 7 checks.
