---
name: theme-section-report
description: Report the section-usage health of a company's active theme — inline (unsectioned) template code, broken section references, and unused sections. Operates on the current company's active theme, read from the database. Report-only, never blocks. Use when asked to audit or check a store's theme sections, find dead sections, or find template markup that should be extracted into a section.
---

# Theme Section Report

Audit **one** theme — the **active theme of the current company** — and report
the health of its section usage. This is a read-only report: it never fails,
never blocks, never edits anything. It hands a human a list of findings to act
on.

## Resolve the target (current company → active theme)

1. **Current company** comes from the ambient request context — `Current.company_id`
   (set on every request via the `current_attributes` concern), or the
   controller's `current_company`.
   - When running in a **console** (e.g. the read-only prod replica), there is
     no request, so seed it first:
     `Current.company_id = Company.find_by!(subdomain: "<store>").id`.
2. **Active theme** — a company has exactly one (`application_themes` carries a
   unique partial index on `company_id where status = 1`):

   ```ruby
   company = Company.find(Current.company_id)
   theme   = company.application_themes.find_by!(status: :active)   # Themes::Theme
   ```

If no active theme exists, report that and stop — there is nothing to audit.

## What you read

Templates and sections are **database rows**, not files: `Themes::Template`
(`has_many` on the theme) carries `themeable_type` (enum), `name`, and the Liquid
in `published` / `content`.

- **Page templates:** `themeable_type IN (home_page, cart_page, product, category, category_page, collection, collection_page, shop_page, post, post_page, join_page, enrollment_pack, navbar, footer, library, library_navbar, medium)`.
- **Sections:** `themeable_type: "sections"`, resolved by `name`.
- **Resolve references the way the engine does** — theme-specific section first,
  then the global-library fallback (`application_theme_templates_with_global_templates` /
  `prefer_theme_specific`). This keeps the checks correct instead of approximate.

## The three checks

### 1. MANUAL_CODE — inline code that should be a section

In each page template's Liquid, allow only the legitimate **shell**:

- CSS load: `{{ '…css' | inline_asset_content }}` or `{{ '…css' | asset_url | stylesheet_tag }}`
- `<script src=…>`
- Structural wrappers (`<main>`, `<div class="flex…">`, nested) whose only children are `{% section %}` + comments
- `{% section 'x', id: … %}`
- `{% schema %} … {% endschema %}`
- Comments (`<!-- … -->`, `{%- comment -%}`)

Flag anything else: elements with real content (`<h1>`, `<p>`, `<img>`, `<a>`,
forms…), control flow with markup (`{% for %}`, `{% if %}`…), variable output
(`{{ product.x }}`), or a bare `{% render %}` in a template.

- **Exempt:** `library`, `medium`, `library_navbar` (legitimately section-less), and `page` (custom-heavy by nature).
- This is the only judgment-based check — which is exactly why the skill is report-only.

### 2. BROKEN_REF — a referenced section does not exist

For each `{% section 'x' %}` in a page template, resolve `x` (theme-specific,
then global). If nothing resolves → `BROKEN_REF`.

- **Exempt** (not section records): `navbar`, `footer`, `library_navbar` (template-type resolved), and any `fluid://…` extension URI (app extension).

### 3. ORPHAN — a section no one uses

For each of the theme's **own** section rows (`themeable_type: "sections"`,
this `application_theme_id`), check whether any page template references it by
name. If none, it is an ORPHAN candidate — then **classify it, do not just list
it**. Never emit a bare "delete" verdict from naming alone.

Open the section's own Liquid and decide:

- **`ORPHAN (review — insertable)`** — the section declares a `{% schema %}`
  with a `presets`/`preset` (or is otherwise a generic, merchant-insertable
  building block: hero, feature grid, CTA, testimonial…). Absence from a
  template does NOT prove it's dead — a merchant can add it from the editor.
  **Never a deletion candidate.**
- **`ORPHAN (delete candidate — superseded)`** — only when BOTH hold, and say
  which:
  1. it declares **no** preset/schema that would let the editor insert it, and
  2. a **wired** section demonstrably supersedes it — same purpose, and the
     orphan's name/body maps to the wired one (e.g. `product_hero_2` →
     wired `product_hero`). State the superseding section by name.
- **`ORPHAN (unclear)`** — neither condition is confirmed (e.g. you couldn't
  read the body). Report it as unresolved rather than guessing a verdict.

Rules:

- Only theme-owned sections are candidates — never global/shared ones.
- The delete verdict requires reading the section body. If you did not open it,
  it is `unclear`, not `delete`. Say so in the Execution notes.
- A name resemblance is evidence, not proof — it only supports `delete` when the
  body confirms supersession.

## Execution

Runs in a Rails runner / console — pure AR reads, no HTTP, no writes. Target the
**read-only prod replica** (`bin/rails c -e prod_read_only`) to audit a real
store; the dev DB works for testing against seed themes. Never call a write path
or a bang mutation.

## Output

For the audited theme, grouped by check:

- `theme #{theme.id} — #{company.subdomain} (active): ✓ no findings`
- otherwise a list of `{ check, template/section, detail }`:
  - `MANUAL_CODE — enrollment_pack: <div class="hero"> with inline markup (lines 4-22)`
  - `BROKEN_REF — home_page wires 'promo' — no theme-specific or global section named 'promo'`
  - `ORPHAN (delete candidate — superseded) — product_hero_2 → superseded by wired product_hero; declares no preset`
  - `ORPHAN (review — insertable) — cta_banner_v2 — declares presets; merchant can insert from editor`
  - `ORPHAN (unclear) — rich_content — body not read`
- A one-line roll-up for the theme — break the ORPHAN count into
  `delete-candidate / review / unclear` so no one reads the total as a delete list.

## Non-goals

Report only — no CI gate, no fixes. No canonical-template presence check, no
canonical-section-name check, no schema coherence. Not a filesystem linter of
`app/themes/templates/` — it audits the DB-stored active theme.
