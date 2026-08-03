# Fluid File-Based Theme Appendix

This skill operates on a **file-based** Fluid theme (the `product/default/index.liquid` +
`sections/*` layout), not the API-managed template API. If the company's theme is API-managed,
STOP — creating a file-based artifact against an API theme leaves an orphan.

## Theme layout

```
layouts/theme.liquid          ← the <html> shell; where `dir` goes
sections/<name>/index.liquid  ← shared, reusable sections (with {% schema %})
product/default/index.liquid  ← a page template: composes sections via {% section %}
product/<variant>/index.liquid← a slug/variant template (only for different structure)
```

A page template composes shared sections and carries a `{% schema %}` with `sections` + `order`.
It holds no page copy and does not recreate section blocks. Every RTL-locale visitor renders the
same templates — so mirroring belongs in the shared layout/CSS, applied once.

## Phase 2 — where direction localization goes

- **`dir` attribute:** in `layouts/theme.liquid`, on the `<html>` tag, driven by the locale:
  ```liquid
  <html lang="{{ localization.language.iso_code }}" dir="{% if localization.language.rtl %}rtl{% else %}ltr{% endif %}">
  ```
  If the theme exposes no `rtl` flag, resolve it by testing `localization.language.iso` against
  the RTL set in `references/direction-map.md` (a small `{% case %}`/`{% if contains %}` check).
  `localization.language`, `localization.country`, and `localization.available_countries` are
  available in every template.
- **Logical CSS:** convert physical properties to logical ones in the theme's shared CSS so the
  whole layout mirrors under `dir="rtl"`. Do this in the shared stylesheets/section CSS — not in
  per-market copies.

## Phase 3 — special sections

Fix directional components in the **existing shared** `sections/*` with `[dir=rtl]` overrides
(see `references/special-sections.md`). Never fork a section into an RTL twin.

## Phase 4 — variant template (only for different content)

Repo rule: *"Only create a slug/variant template when the source truly uses a different
structure."* Mirroring is never a reason to create one. When the user has asked for different
content:
- Create `product/<variant>/index.liquid` (or the relevant resource) that **reuses the shared
  sections** with a different `order`/settings, plus at most one new market section.
- Give every section instance a unique `id`; keep blocks in the section presets, not the template.

## Phase 5 — push + verify

Push the theme with the project's normal mechanism (e.g. `fluid theme push`, or the Mist theme
tooling). Then load the storefront in the target locale/region and run the Phase 5 checks. Take
before/after screenshots.

## Country routing & SEO — what to know

- Pure mirroring needs **no** per-country routing: `dir` is locale-driven, so any RTL-locale
  visitor gets the mirrored layout automatically once the shared theme is pushed.
- A *different-content* variant that must be served to a specific country relies on region
  routing (a region rule keyed on country ISO). That is an API/config concern outside the theme
  files — confirm the mechanism with the user before wiring it, to avoid an orphan mapping.
- **SEO limitation (don't overpromise):** there is no exposed way to emit per-country `hreflang`
  alternates or path-based localized URLs; `hreflang` is per-language via a `?lang=<iso>` param.
  Flag deeper per-country indexing as a backend follow-up.
