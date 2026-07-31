---
name: Theme Section Report
description: Audit the active company's database-backed theme for manual template code, broken section references, and classified orphan sections without making changes.
icon: scan-search
---

# Goal

Audit one theme—the active theme for the current company—and report the health
of its section usage. Produce a read-only list of findings for a human to act
on. Never edit data, call HTTP endpoints, run a write path, fail the run because
one record cannot be read, or turn this report into a gate.

# Execution boundary

Run this audit in a Rails runner or console with Active Record access. Use the
read-only production replica (`bin/rails c -e prod_read_only`) for a real store,
or the development database for seed-theme testing. When running Rails from the
`fluid` repository, invoke Rails through its Docker devcontainer.

In a request, resolve the company from the ambient context: prefer
`Current.company_id`, which `current_attributes` sets on every request, and use
the controller's `current_company` only when that is the available context.

A console has no request context. Seed it before the audit:

```ruby
Current.company_id = Company.find_by!(subdomain: "<store>").id
```

This skill is pure Active Record reads. Do not use `fluid_api`, make HTTP
requests, modify a model, invoke a bang mutation, or call `save`, `update`,
`destroy`, `publish`, or any service that can write.

Handle lookup, content-read, and parsing errors per record: add an execution
note, use the conservative classification where one exists, and continue with
the remaining records. The report itself never raises or blocks.

# Resolve the target

1. Read the current company and its one active theme:

   ```ruby
   company = Company.find(Current.company_id)
   theme = company.application_themes.find_by(status: :active)
   ```

2. If the company context is missing or cannot be read, report that as an
   execution note and stop cleanly.
3. If `theme` is `nil`, report that the company has no active theme and stop.
   There is nothing to audit. Do not substitute a draft, development, importing,
   or error theme.
4. Record the company subdomain and theme id. Audit no other company or theme.

# Read the database-backed Liquid

Templates and sections are `Themes::Template` rows in
`application_theme_templates`, not files. Read each row's published Liquid
with `template.published&.content`; fall back to `template.content` only when a
published revision is unavailable. Keep line breaks so every finding can cite
the relevant line or line range.

Treat these as page-template types:

```text
home_page, cart_page, product, category, category_page, collection,
collection_page, shop_page, post, post_page, join_page, enrollment_pack,
navbar, footer, library, library_navbar, medium, page
```

Sections are rows with `themeable_type: "sections"`, resolved by `name`.

Whenever a section name must resolve, follow the engine's precedence exactly:

```ruby
theme.application_theme_templates_with_global_templates
     .prefer_theme_specific
     .where(themeable_type: "sections", name: section_name)
     .first
```

This chooses a theme-specific section before the global-library fallback. Do
not approximate resolution with two unrelated searches, and never treat a
global/shared section as owned by the audited theme.

# Checks

## 1. MANUAL_CODE—inline code that should be a section

Inspect each page template's full Liquid. Exempt `library`, `medium`,
`library_navbar`, and `page` templates from this check because they are
legitimately section-less or custom-heavy.

Allow only this template shell:

- A CSS load using either
  `{{ '…css' | inline_asset_content }}` or
  `{{ '…css' | asset_url | stylesheet_tag }}`.
- A `<script src=…>` element with no inline script body.
- Structural wrappers such as `<main>` or nested `<div class="flex…">`
  elements when their only children are section tags, comments, or other
  qualifying structural wrappers.
- A section tag, including `{% section 'x', id: … %}` and whitespace-control
  variants.
- A `{% schema %} … {% endschema %}` block.
- HTML comments and Liquid `{% comment %} … {% endcomment %}` blocks, including
  whitespace-control variants.

Flag anything else as `MANUAL_CODE`, including:

- elements containing real content such as headings, paragraphs, images,
  links, or forms;
- control flow that emits markup, including `{% for %}` and `{% if %}`;
- variable output such as `{{ product.x }}`;
- a bare `{% render %}` in a page template;
- inline JavaScript or other executable/template logic outside the allowed
  shell.

This is the only judgment-based check. Be conservative, cite the exact line or
line range, quote only the shortest useful snippet, and explain which inline
content or logic caused the finding. A structural wrapper is allowed only when
all of its descendants satisfy the shell rules.

## 2. BROKEN_REF—a referenced section does not exist

1. Extract every literal section name from `{% section 'x' %}` tags in every
   page template, including tags with an `id:` argument and whitespace-control
   variants.
2. Do not resolve `navbar`, `footer`, or `library_navbar`; those names are
   template-type references, not section rows.
3. Do not resolve a name beginning with `fluid://`; it is an app-extension URI.
4. Resolve every other name with
   `application_theme_templates_with_global_templates.prefer_theme_specific`
   as shown above.
5. If no row resolves, emit `BROKEN_REF` with the page-template type/name, the
   referenced name, and the fact that neither a theme-specific nor global
   section exists.

A template that has no section references is not itself a broken reference.

## 3. ORPHAN—a theme-owned section no page template uses

1. Build the set of literal section names referenced by all page templates.
2. Enumerate only the audited theme's own rows:

   ```ruby
   theme.application_theme_templates.where(themeable_type: "sections")
   ```

3. A theme-owned section whose name is absent from the reference set is an
   orphan candidate. Global/shared and extension sections are never candidates.
4. Open and read the candidate's full published Liquid before classifying it.
   Also read any wired section proposed as its replacement. A name resemblance
   is evidence, not proof.
5. Classify every candidate into exactly one of these findings:

### ORPHAN (review—insertable)

Use this when the section declares a `{% schema %}` with `presets` or `preset`,
or when its body otherwise demonstrates that it is a generic,
merchant-insertable building block such as a hero, feature grid, CTA, or
testimonial. Absence from a template does not prove it is dead: a merchant can
add it from the editor. It is never a deletion candidate.

### ORPHAN (delete candidate—superseded)

Use this only when both conditions are confirmed from the bodies:

1. The orphan declares no preset/schema that would let the editor insert it.
2. A currently wired section demonstrably supersedes it: both serve the same
   purpose, and the orphan's name and body map to the wired section's body.

Name the superseding section and state the evidence for both conditions. For
example: `product_hero_2` is superseded by wired `product_hero`, and the orphan
declares no preset. Never infer this verdict from a suffix, version number, or
name similarity alone.

### ORPHAN (unclear)

Use this whenever the two delete-candidate conditions are not both confirmed,
including when a body could not be read, no demonstrably equivalent wired
section exists, or the evidence is ambiguous. Report the uncertainty instead
of guessing.

# Output

Group findings by check in this order: `MANUAL_CODE`, `BROKEN_REF`, then the
three `ORPHAN` classifications. Each finding must contain:

- `check`;
- the template type/name or section name;
- a concise detail with evidence and line references where applicable.

Use wording like:

```text
MANUAL_CODE — enrollment_pack/default: <div class="hero"> contains inline markup (lines 4–22)
BROKEN_REF — home_page/default wires 'promo' — no theme-specific or global section named 'promo'
ORPHAN (delete candidate—superseded) — product_hero_2 → wired product_hero; same purpose confirmed from both bodies; declares no preset
ORPHAN (review—insertable) — cta_banner_v2 — declares presets; merchant can insert it from the editor
ORPHAN (unclear) — rich_content — body could not be read
```

If there are no findings, output exactly one result line:

```text
theme #{theme.id} — #{company.subdomain} (active): ✓ no findings
```

Otherwise, finish with a one-line roll-up for the theme. Count
`MANUAL_CODE` and `BROKEN_REF`, and break the orphan total into delete
candidate, review, and unclear so nobody can read the total as a deletion list.

Finish with `Execution notes` that state:

- the environment and company/theme audited;
- that only Active Record reads were performed;
- whether published content or the current-content fallback was read;
- every template or section body that could not be opened;
- that an unopened orphan body was classified as unclear, never as a delete
  candidate.

# Non-goals

- No CI gate, failure status, blocking verdict, or automatic fix.
- No canonical-template presence check.
- No canonical-section-name check.
- No schema-coherence audit beyond the orphan classification evidence.
- No filesystem lint of `app/themes/templates/` or a local theme checkout.
- No writes of any kind.
