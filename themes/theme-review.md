---
name: themes-review
description: |
  Iterative reviewer and fixer for Fluid Liquid themes. Themes live in their own Git repos
  (e.g. base-theme) and sync to the Fluid API via the `fluid theme` CLI. Use when reviewing
  a theme PR, auditing a section/component, or working through a theme to fix bad code and
  schema. Companion to the `themes` skill — that one teaches how to *build*, this one
  teaches how to *review and fix*. Works **one section at a time**: review it, fix it,
  re-run `fluid theme lint --json`, and repeat until that section is clean before moving on,
  pausing once in a while to ask the user whether to continue, skip, or stop. Covers: the
  schema validator, every valid setting `type`, singular vs plural selector misuse (e.g.
  multiple `product` settings → one `product_list`), the blocks-first content model, Liquid
  correctness, performance, security, accessibility, and file-size/DRY thresholds. Never
  push to the live theme API without explicit approval.
---

# Theme Review & Fix

This skill is the reviewer counterpart to `themes`. It is opinionated and adversarial: every check has a fix, and every fix has a severity. The agent **edits theme files in place** to fix them (every change is reversible — the user can review or undo it), but it **never writes to the live theme API without explicit approval**.

## How to work — one section at a time

The goal is to get the theme healthy **one section at a time** — not to fix the whole theme in a single sweep. Pick the smallest unit (a single section, component, or block file) and stay on it until it's right before touching anything else.

For each unit:

1. **Read it** and run every relevant check below — structure, schema, blocks-first content model, selector singular→list, Liquid correctness, performance, security, accessibility.
2. **Fix** the findings, one focused change at a time, highest severity first (`blocker` → `should` → `nit`).
3. **Re-validate** with `fluid theme lint --json` after each change. Parse the JSON (don't eyeball the text), fix what it flags, and run it again. Keep looping until that file is clean.
4. **Confirm the unit is right** — lint is clean _and_ the relevant checklist boxes pass — then **move on** to the next unit.

### Check in with the user

Don't run end to end silently. **Once in a while — after finishing a section, or before starting a large or risky change — pause and ask the user how to proceed:** continue to the next section, skip this one, stop here, or look at what changed. Default to pausing at natural boundaries (a section just finished, you're about to touch many files, or you're about to make a change that isn't a clear-cut validator error) rather than interrupting mid-fix.

## Where themes actually live

Themes are **separate Git repos**, one repo per theme. The reference starter is `git@github.com:fluid-commerce/base-theme.git`. They are not part of the fluid Rails monorepo and not part of fluid-mono — fluid-mono only ships the _tooling_ (CLI + validator) that operates on them.

A typical theme repo looks like this (verified against the `base-theme` starter cloned by `fluid theme init`):

```
my-theme/
├── assets/                     ← CSS, JS, images, video — flat at root
├── components/{name}/          ← shared partials, at root (no templates/ wrapper)
│   ├── pagination/index.liquid
│   ├── cart_template/index.liquid
│   └── ...
├── config/
│   ├── settings_schema.json    ← theme-wide settings
│   └── settings_data.json      ← compiled preset values (managed; rarely hand-edited)
├── home_page/default/index.liquid     ← page templates: {type}/{variant}/index.liquid
├── product/default/index.liquid
├── cart_page/default/index.liquid
├── collection/default/index.liquid
├── collection_page/default/index.liquid
├── enrollment_pack/default/index.liquid
├── join_page/default/index.liquid
├── page/default/index.liquid
├── library/default/index.liquid
├── navbar/default/index.liquid
├── footer/default/index.liquid
├── medium/default/index.liquid
├── layouts/
│   └── theme.liquid            ← flat layout files, no wrapping dir
├── locales/
│   ├── en.json
│   ├── de.json
│   └── ...                     ← flat one-file-per-locale
├── sections/{name}/            ← reusable sections, at root
│   ├── hero_section/index.liquid
│   ├── cta_banner/index.liquid
│   └── ...
├── blocks/{name}/              ← standalone (reusable) block templates, at root
│   ├── review_card/index.liquid
│   └── ...
├── styleguide/index.liquid     ← optional dev-only preview
├── cover.png                   ← theme thumbnail for the editor picker
├── global_styles.css           ← optional theme-wide CSS at root
├── .fluid-theme.json           ← CLI metadata (themeId, company, checksums)
├── .fluidignore                ← like .gitignore
└── README.md
```

**There is no `templates/` wrapper.** Sections, components, standalone blocks, and page-type folders each sit in their own directory at the theme root — the directory name _is_ the artifact type (`sections/`, `components/`, `blocks/`, `layouts/`, plus page types like `home_page/`, `product/`, `cart_page/`). A hand-rolled `templates/sections/...` or `templates/blocks/...` path is wrong; flatten it to the root.

`.fluid-theme.json` is the one piece of CLI state worth reading. It is not human-edited, but it's helpful to look at: it records the remote theme ID, the company subdomain, and a SHA256 checksum per file (the CLI uses these to detect remote drift on push). When a review needs to know which remote theme a repo is wired to, this is the file to check.

## Directory & file structure — validate first

Before reading any Liquid, walk the repo root. `fluid theme lint --json` only checks schema JSON — it doesn't enforce layout. The reviewer enforces layout.

A valid theme is recognized by the presence of an `assets/` or `config/` directory. In practice every published theme has `assets/`, `config/`, `layouts/`, and the page-type and section folders below.

### Required at the repo root

| Path                          | Severity if missing                     | Notes                                                                  |
| ----------------------------- | --------------------------------------- | ---------------------------------------------------------------------- | --------------------------------------------- |
| `config/settings_schema.json` | `blocker` for any new theme             | Theme-wide settings. Even an empty `[]` is acceptable; absence is not. |
| `layouts/theme.liquid`        | `blocker` if the theme renders any page | At least one layout must exist for pages to render.                    |
| `assets/`                     | `should`                                | Almost every theme needs at least images.                              |
| `locales/en.json`             | `should`                                | If the theme uses `{{ 'foo'                                            | t }}`translations anywhere, this is`blocker`. |
| `cover.png`                   | `nit`                                   | Used by the editor as the theme thumbnail.                             |
| `README.md`                   | `nit`                                   | Document install / deploy.                                             |
| `.fluidignore`                | `nit`                                   | Exclude `node_modules`, `.DS_Store`, etc.                              |

### Canonical paths per artifact

Every artifact has a fixed depth and shape. **No deeper nesting is allowed under any of these.**

| Artifact          | Canonical path                                                    | Example                                                          | Multiple variants?                                                                                 |
| ----------------- | ----------------------------------------------------------------- | ---------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Page templates    | `{page_type}/{variant}/index.liquid`                              | `home_page/default/index.liquid`, `library/revised/index.liquid` | **Yes** — `default` is conventional, but a page type can have any number of variant directories.   |
| Sections          | `sections/{name}/index.liquid`                                    | `sections/hero_section/index.liquid`                             | No variants. One directory per section type.                                                       |
| Components        | `components/{name}/index.liquid`                                  | `components/button/index.liquid`                                 | No variants.                                                                                       |
| Standalone blocks | `blocks/{name}/index.liquid`                                      | `blocks/review_card/index.liquid`                                | No variants. Reusable block templates a section opts into via `@theme` or a named-block reference. |
| Layouts           | `layouts/{name}.liquid` (flat file, no wrapping dir)              | `layouts/theme.liquid`                                           | Multiple layouts possible; each is a flat `.liquid` file.                                          |
| Global config     | `config/settings_schema.json`, `config/settings_data.json` (flat) | —                                                                | —                                                                                                  |
| Locales           | `locales/{lang}.json` (flat)                                      | `locales/en.json`, `locales/de.json`                             | —                                                                                                  |
| Assets            | `assets/{file}` (flat)                                            | `assets/featured.css`, `assets/logo.svg`                         | No sub-folders.                                                                                    |
| Root-level CSS    | `global_styles.css` at the theme root                             | —                                                                | Optional theme-wide stylesheet.                                                                    |
| Theme thumbnail   | `cover.png` at the theme root                                     | —                                                                | —                                                                                                  |
| Styleguide        | `styleguide/index.liquid`                                         | —                                                                | Optional dev-only preview.                                                                         |

**Page-type folder names recognized** (from the base-theme + reference theme):
`home_page`, `product`, `cart_page`, `collection`, `collection_page`, `category`, `category_page`, `enrollment_pack`, `join_page`, `page`, `post`, `post_page`, `library`, `medium`, `navbar`, `footer`, `shop_page`, plus any others the engine adds. Each one holds **one or more variant directories** (`default/`, `revised/`, `holiday/`, etc.), each containing an `index.liquid`.

**Blocks come in two shapes — prefer standalone.** Fluid themes are **blocks-first** (see [Blocks vs. sections](references/blocks-vs-sections.md)), and standalone blocks are the default shape.

1. **Standalone (theme) blocks** — their own template at `blocks/{name}/index.liquid`, reusable across sections. A section opts in by declaring `@theme` (accept any theme block) or a named-block reference (a `{ "type": "<name>" }` entry with no `name`/`settings`) in its schema's `"blocks"` array; the engine resolves that to the matching `blocks/<name>/index.liquid` template. **This is the preferred shape for almost everything** — reusable, testable on its own, and it keeps the section to a few whole-section settings while each element's settings live on its block.
2. **Inline blocks** — defined inside a section's `{% schema %}` `"blocks": [...]` array, local to that one section. **Use only when the block is very small and genuinely one-off.** Extracting an inline block into `blocks/` is always a valid, encouraged recommendation.

Blocks can also nest (a block declaring its own `"blocks"`), up to the engine's depth limit. What is **not** allowed is nesting block files _under_ a section or page-variant directory (`sections/x/blocks/...`) — standalone blocks live in the top-level `blocks/` directory, parallel to `sections/` and `components/`.

### The depth rule

**No artifact nests deeper than the canonical path above.** Specifically:

- ✗ `sections/main_product/blocks/breadcrumb/index.liquid` (block file nested under a section — extract it to top-level `blocks/breadcrumb/index.liquid` instead)
- ✗ `components/buttons/primary/index.liquid` (sub-grouped components)
- ✗ `assets/icons/social/twitter.svg` (assets in sub-folders)
- ✗ `home_page/default/blocks/hero/index.liquid` (block file under a page variant — move to top-level `blocks/hero/index.liquid`)
- ✓ `sections/main_product/index.liquid`
- ✓ `blocks/breadcrumb/index.liquid` (standalone block at the top level)
- ✓ `components/button_primary/index.liquid` (rename to flatten)
- ✓ `assets/icon-social-twitter.svg` (rename to flatten)

If you feel the urge to nest, rename: `assets/icon-social-twitter.svg`, `components/card_product/index.liquid`, etc.

### Layout requirements

Every layout file under `layouts/` **must emit both magic drops** for the engine to inject head content and page content:

- `{{ content_for_header }}` — placed inside `<head>`. The engine injects meta tags, analytics, editor-mode scripts, asset preloads, and the FairShare runtime initialization here.
- `{{ content_for_layout }}` — placed where the page content goes (inside `<body>`, typically inside the main container). The selected page template renders into this slot.

A layout missing either one is broken. Missing `content_for_header` breaks editor mode, analytics, and head-injected assets. Missing `content_for_layout` renders an empty page.

```liquid
<!doctype html>
<html lang="{{ request.locale.iso_code }}">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ page_title }}</title>

    {{ 'theme.css' | asset_url | stylesheet_tag }}

    {{ content_for_header }}   {# ← required #}
  </head>
  <body>
    {% section 'main_navbar' %}

    <main>
      {{ content_for_layout }}  {# ← required #}
    </main>

    {% section 'main_footer' %}
  </body>
</html>
```

### Findings to surface

| You see                                                                                      | Severity                                       | Fix                                                                                                                                               |
| -------------------------------------------------------------------------------------------- | ---------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Section file outside `sections/{name}/index.liquid`                                          | `blocker`                                      | Move it. The `{% section 'x' %}` resolver only looks in `sections/`.                                                                              |
| Component file with a `{% schema %}` block                                                   | `blocker`                                      | Components don't have schemas. Move to `sections/`, or strip the schema.                                                                          |
| Section file without `{% schema %}`                                                          | `blocker`                                      | A section without a schema is just markup — make it a component (move to `components/{name}/index.liquid`).                                       |
| Page template at `{type}/index.liquid` (missing variant dir)                                 | `blocker`                                      | Wrap in a variant directory: `{type}/default/index.liquid`.                                                                                       |
| Asset (`.css`, `.js`, image) outside `assets/` or `global_styles.css` / `cover.png` at root  | `blocker`                                      | Move to `assets/` and reference via `\| asset_url`.                                                                                               |
| Sub-folder inside `assets/` (e.g. `assets/icons/`)                                           | `should`                                       | Flatten: rename file to `assets/icon-{whatever}.svg`.                                                                                             |
| Sub-folder inside `sections/{name}/` or `components/{name}/` (e.g. `sections/hero/blocks/`)  | `blocker`                                      | Sections and components don't nest. A reusable block belongs in the top-level `blocks/{name}/` directory, not under a section.                    |
| Co-located `styles.css` / `style.css` next to a section, component, or page template variant | `blocker` for new files, `should` for existing | **Co-located stylesheets are deprecated** — all CSS lives under `assets/`. See [CSS hygiene §1a](references/css-js-hygiene.md). |
| Hand-rolled `templates/sections/...` or `templates/components/...` paths                     | `blocker`                                      | The base-theme convention has no `templates/` wrapper. Move to root-level `sections/` / `components/`.                                            |
| `config/settings_schema.json` missing                                                        | `blocker` for new themes                       | Create it. Start with `[]` if no global settings.                                                                                                 |
| Filename casing mismatch (e.g. `ProductCard/index.liquid`)                                   | `should`                                       | Directory and filenames should be `snake_case`. The engine is case-sensitive on most filesystems.                                                 |
| Two sections with the same directory name in different paths                                 | `blocker`                                      | Section types must be globally unique.                                                                                                            |
| `{% section 'foo' %}` referencing a missing `sections/foo/index.liquid`                      | `blocker`                                      | Validator catches this — but flag it explicitly with the fix.                                                                                     |
| Files committed under `assets/` but never referenced                                         | `nit` → `should`                               | Dead assets bloat downloads. Run the dead-asset grep in [Dead code](references/dead-code.md).                        |

### Quick structural audit

From the theme repo root, this gives a one-shot health view:

```bash
# Required files
[ -f config/settings_schema.json ] && echo "OK  config/settings_schema.json" || echo "MISSING  config/settings_schema.json"
[ -f layouts/theme.liquid ]        && echo "OK  layouts/theme.liquid"        || echo "MISSING  layouts/theme.liquid"

# Sections without schemas
for f in sections/*/index.liquid; do
  grep -q '{% schema %}' "$f" || echo "NO SCHEMA  $f"
done

# Components with schemas (anti-pattern)
for f in components/*/index.liquid; do
  grep -q '{% schema %}' "$f" && echo "HAS SCHEMA  $f"
done

# Anything nested deeper than 2 dirs from theme root (excluding hidden dirs)
find . -mindepth 4 -type f -not -path '*/.*' \
  -not -path './layouts/*' -not -path './assets/*' -not -path './locales/*' -not -path './config/*'

# Deprecated co-located stylesheets
find . -type f \( -name 'styles.css' -o -name 'style.css' \) \
  -not -path './assets/*' -not -path './.git/*'

# Hand-rolled `templates/` wrapper (wrong convention)
[ -d templates ] && echo "WRONG  templates/ wrapper found — flatten to root"
```

If any line of output is unexpected, raise it as a finding before reading the diff line-by-line.

---

## The tooling — `fluid theme` CLI

The `fluid theme` command group is how a theme repo syncs with the Fluid API. The reviewer references these commands so the author can reproduce checks locally — it never runs the mutating ones (`push`, `pull`) itself.

| Command                | What it does                                                                                          | When the reviewer references it                                                        |
| ---------------------- | ----------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `fluid theme init`     | Clone the base theme as a new repo                                                                    | Suggest in comments when a PR is creating a new section from scratch with no structure |
| `fluid theme dev`      | Local dev server on `:9292` with hot-reload, proxied to `{company}.fluid.app`                         | Suggest when debugging visual issues                                                   |
| `fluid theme push`     | Validates the schema, then uploads changed files. **Validation runs automatically unless `--force`.** | Suggest before merge                                                                   |
| `fluid theme pull`     | Download remote theme to disk                                                                         | Mention when local is stale                                                            |
| `fluid theme lint --json`     | Read-only schema validator. **The agent should run/reference this in every review.**                  | Always reference: "this is what `fluid theme lint --json` would flag"                         |
| `fluid theme navigate` | Opens browser to the dev theme editor                                                                 | Mention for visual verification                                                        |

**`fluid theme lint --json` is the official self-check.** Any finding the validator surfaces (see next section) maps directly to a `blocker` severity in your review — it would fail validation.

---

## Operating Rules

1. **One section at a time; fix, re-lint, repeat.** Stay on a single section / component / block until it's clean before moving on. See [How to work](#how-to-work--one-section-at-a-time).
2. **No writes to the live API without approval.** When fixing locally you edit theme files in place (changes are reversible — the user can review or undo any of them), but you **never** run `fluid theme push` or otherwise write to the live theme without explicit approval. When reviewing a PR instead of fixing locally, don't push to the author's branch — leave comments or open a follow-up PR.
3. **Quote the original line.** Every finding must reference `file:line` and show the offending snippet. No vague "the loop is inefficient".
4. **Severity is required.** Every finding is tagged `blocker` / `should` / `nit`. See [Severity ladder](#severity-ladder).
5. **Cite the validator.** If `fluid theme lint --json` would flag it, say so — the dev should be able to reproduce the failure locally.
6. **Don't restyle.** Pure formatting churn is forbidden — if a file needs both a fix and a tidy, keep them as separate, focused changes.

---

## Severity ladder

| Tag       | Meaning                                                                                                                                   | Examples                                                                                                                                                                                      |
| --------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `blocker` | The validator would reject it on `fluid theme push`, OR it renders wrong / breaks a page / exposes user data. Must be fixed before merge. | Invalid `type:` value, missing `id`, duplicate `id`, missing `type:` on a block, settings shape is object not array, referenced section not on disk, unescaped user HTML, unclosed `{% if %}` |
| `should`  | Works today but will hurt later: perf cliff, DRY violation, missing default, missing whitespace control in a hot loop.                    | `asset_url` inside a `for` loop, 3+ identical `{% render %}` snippets, multiple `product` settings playing the same role, missing `default:` on a user-facing setting                         |
| `nit`     | Cosmetic, style, or low-impact. Leave one comment, do not block.                                                                          | Comment style, optional `default` on internal-only setting, naming nits                                                                                                                       |

Decision rule: if `fluid theme lint --json` would error on it, it's `blocker`. If it would render wrong but the validator lets it through, it's `blocker`. If it changes nothing visible today, it's `should` or `nit`.

---

## The schema validator (`fluid theme lint --json`)

`fluid theme lint --json` is the read-only schema validator. It's the same check the editor runs and the same one `fluid theme push` runs before upload, so anything it rejects is a `blocker`. It runs on every `{% schema %}` block and enforces the rules below.

### Schema-level rules

- JSON must be parseable. Syntax errors point to the line number.
- No duplicate `"blocks"` keys in the same object.

### Settings rules

For each entry in `"settings": [...]`:

- `id` is required, non-empty, non-whitespace — **except** for `type: "header"` settings, which carry no `id` and use `content:` instead (the validator accepts them without one).
- `id` must be unique across all settings in the same file (excluding `header` entries, which have no `id`).
- `type` is required.
- `type` must be one of the canonical types — see the [full list below](references/setting-types.md).

### Blocks rules

For each entry in `"blocks": [...]`:

- `type` is required.
- `name` is required _unless_ the block is `@app`, `@theme`, or a named-block reference (type only, no `name`/`settings` — these point at a standalone `blocks/{name}/index.liquid` template).
- `settings` (when present) must be an array `[]`, not an object `{}`.
- Each setting inside is recursively validated (same rules as above).
- Nested `blocks` are recursively validated.
- Duplicate `type` values within a blocks array produce a warning.

### Section references

- Every `{% section 'name' %}` in a Liquid template must have a matching section file on disk. Missing sections produce errors.

### Template vs section block shape

- **Section files** (`sections/{name}/index.liquid`): `blocks` is an **array** `[]`.
- **Page templates** (`{page_type}/{variant}/index.liquid` — e.g. `home_page/default/index.liquid`, `product/default/index.liquid`): `blocks` is an **object** `{}`.

If you see the wrong shape, that's a `blocker`.

---


## Reference catalogs

The deep check catalogs live in `references/` and load only when a review or fix
touches them. Read the matching file when you hit its topic:

- **[Setting types](references/setting-types.md)** — the canonical `type:` list the validator enforces. Read when checking any `{% schema %}` setting `type:`.
- **[Navigation](references/navigation.md)** — `link_list` menu selector vs. hardcoded `<a>` rows.
- **[Dynamism](references/dynamism.md)** — settings/locales over hardcoded values.
- **[Global settings](references/global-settings.md)** — typography/color/spacing tokens, dark mode, `config/settings_schema.json` + `theme.liquid` wiring.
- **[Blocks vs. sections](references/blocks-vs-sections.md)** — when a setting belongs in a block; settings-panel ergonomics.
- **[Liquid correctness](references/liquid-correctness.md)** — variable scope, balanced tags, whitespace control, typoed ids.
- **[Editor attributes](references/editor-attributes.md)** — `section.fluid_attributes` / `block.fluid_attributes`.
- **[FairShare attributes](references/fairshare-attributes.md)** — `data-fluid-*` cart / add-to-cart behavioral attributes + the CDN script.
- **[Performance](references/performance.md)** — `asset_url` in loops, render hygiene.
- **[Security & accessibility](references/security-accessibility.md)** — escaping user content, alt text, semantic clickables.
- **[Dead code](references/dead-code.md)** — unused sections/components/assets, unhandled block types.
- **[CSS / JS hygiene](references/css-js-hygiene.md)** — co-located stylesheet deprecation, inline `<style>`/`<script>` thresholds, `defer`.
- **[Worked examples](references/examples.md)** — full section reviews, end to end.

Every reference links directly from here (one level deep). "The validator" always means
`fluid theme lint --json` — run it after each change and parse the JSON output rather than
eyeballing the text.

---
## Selector heuristic — singular → list

This is one of the most common smells.

**If a section or block has two or more singular resource pickers playing the _same role_, collapse them to one `*_list` setting.**

The test: would a user reasonably want N+1 items in the same role? If yes, it's a list. If the section needs _exactly one_ hero product _and separately_ one upsell product, those are two different roles — keep them singular.

### Bad — six product settings playing the same role

```json
{
  "settings": [
    { "type": "product", "id": "product_1", "label": "Product 1" },
    { "type": "product", "id": "product_2", "label": "Product 2" },
    { "type": "product", "id": "product_3", "label": "Product 3" },
    { "type": "product", "id": "product_4", "label": "Product 4" },
    { "type": "product", "id": "product_5", "label": "Product 5" },
    { "type": "product", "id": "product_6", "label": "Product 6" }
  ]
}
```

### Good — one list

```json
{
  "settings": [
    {
      "type": "product_list",
      "id": "products",
      "label": "Products",
      "limit": 6
    }
  ]
}
```

### Rendering changes too

```liquid
{%- comment -%} Bad: six lookups, six render calls {%- endcomment -%}
{%- if section.settings.product_1 != blank -%}{% render 'product_card', product: section.settings.product_1 %}{%- endif -%}
{%- if section.settings.product_2 != blank -%}{% render 'product_card', product: section.settings.product_2 %}{%- endif -%}
{%- comment -%} ...four more times... {%- endcomment -%}

{%- comment -%} Good: one list, one loop {%- endcomment -%}
{%- for product in section.settings.products -%}
  {% render 'product_card', product: product %}
{%- endfor -%}
```

### Same rule for every resource

| Singular smell                                          | List fix                                    |
| ------------------------------------------------------- | ------------------------------------------- |
| 2+ `product` (or `products`) settings, same role        | `product_list`                              |
| 2+ `collection` settings, same role                     | `collection_list`                           |
| 2+ `category` settings, same role                       | `category_list`                             |
| 2+ `post` settings, same role                           | `posts_list`                                |
| 2+ `enrollment` / `enrollment_pack` settings, same role | `enrollment_list` / `enrollment_packs_list` |
| 2+ `blog` settings, same role                           | `blog_list`                                 |

The benefit isn't just lines of code — a `*_list` setting lets the merchant **add or remove** items without a code change and drops the fixed per-slot count. It does **not** give per-item drag-and-drop reorder, though — that's a *blocks* feature. If the merchant needs to reorder items, model them as blocks instead.

---

## File-size and DRY thresholds — when to extract

Sections grow. Past certain thresholds, they stop being readable. Severity for "this section is too big" is `should` (rarely `blocker`), but the fix is mechanical.

### Section line counts

| Lines   | Action                                                                                                                                                |
| ------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| < 200   | Fine.                                                                                                                                                 |
| 200–400 | Watch for repetition. 3+ near-identical render snippets → extract a component.                                                                        |
| 400–700 | **`should`.** Split section into named blocks via `{% schema %}` `"blocks": [...]` and dispatch in a single `{% for block in section.blocks %}` loop. |
| > 700   | **`should`** (or `blocker` if it also has bugs). Decompose. Prefer multiple smaller sections or component extraction over one giant section.          |

### Component line counts

Components are simpler than sections (no schema), so the threshold is lower.

| Lines   | Action                                                                                 |
| ------- | -------------------------------------------------------------------------------------- |
| < 100   | Fine.                                                                                  |
| 100–250 | Look for sub-component extraction.                                                     |
| > 250   | **`should`.** A pure presentation partial that's 250+ lines is doing too much — split. |

### Duplication — the rule of three for Liquid

Liquid `{% render %}` snippets often carry 8+ arguments. The parameter list itself is maintenance burden the moment you copy it.

**`should`** when:

- The same `{% render 'card', ... %}` with the same arg list appears 3+ times in one file → extract to a smaller wrapper component or a `{% capture %}` block.
- The same chunk of markup (5+ lines) appears 3+ times across two or more sections → move to a new `components/{name}/index.liquid` and `{% render %}` it.
- The same Liquid logic block (`{% assign … %}` followed by computation) appears in 3+ sections → move to a component and `{% render %}` it.

### Block extraction — when an inline branch becomes a block

If a section has three or more `{% if section.settings.show_X %}` branches at the top level, that's a sign each `X` wants to be a `{% schema %}` block. Block-driven sections look like this:

```liquid
{% for block in section.blocks %}
  {% case block.type %}
    {% when 'page_header' %}   {%- render 'resource_listing_header' -%}
    {% when 'product_grid' %}  {%- render 'product_grid', block: block -%}
    {% when 'cta_banner' %}    {%- render 'cta_banner',   block: block -%}
  {% endcase %}
{% endfor %}
```

Schema side:

```json
"blocks": [
  { "type": "page_header",  "name": "Page Header",  "limit": 1, "settings": [...] },
  { "type": "product_grid", "name": "Product Grid",                "settings": [...] },
  { "type": "cta_banner",   "name": "CTA Banner",                   "settings": [...] }
]
```

This gives users drag-and-drop reorderability and lets each block's logic and settings live together.

---

## Review workflow — how to actually output findings

### A. Reviewing a GitHub PR (default)

Themes live in their own repos. PRs typically arrive via `gh pr view <number>` against `base-theme` or a fork of it.

1. Read the PR diff. For each changed `.liquid` or `.json` file, walk through these check sections in order:
   - Validator-level rules (would `fluid theme lint --json` reject it?)
   - Setting types (every `type:` in the canonical list)
   - Selector singular→list
   - File-size / DRY thresholds
   - Liquid correctness
   - Performance
   - Security
   - Accessibility
   - CSS/JS hygiene
2. Group findings by file. Within each file, sort by line number.
3. For each finding, prepare a **single inline comment** at the offending line. Format:

````
[blocker] Invalid setting type `text_area`

The schema validator only accepts the canonical type list. Running `fluid theme lint --json`
locally would fail on this. Use `textarea` (one word):

```json
{ "type": "textarea", "id": "description", "label": "Description" }
````

```

4. After all inline comments, post **one summary review** (e.g. `gh pr review --comment --body ...`) with the rollup:

```

## Theme review

**4 findings** — 1 blocker, 2 should, 1 nit

Reproduce locally with `fluid theme lint --json`.

| Severity | File                               | Finding                                             |
| -------- | ---------------------------------- | --------------------------------------------------- |
| blocker  | sections/featured/index.liquid:42  | Invalid setting type `text_area`                    |
| should   | sections/featured/index.liquid:118 | Six `product` settings — collapse to `product_list` |
| should   | sections/products/index.liquid:155 | Same `{% render 'product_card', ... %}` repeated 4× |
| nit      | components/button/index.liquid:8   | Missing whitespace control in tight loop            |

**Suggested fix path:** I can open a follow-up PR with the blocker + the two `should` items. Reply with `open the fix PR` to proceed.

```

### B. Auditing without a PR (local)

Same checks, but output goes to the user as a single ranked markdown report. End with the same offer: "I can open a PR with these fixes — say the word."

If the user has the CLI installed, also suggest:

```

For a fast first pass: `fluid theme lint --json` from the theme repo root.

```

### C. Applying fixes — opening a follow-up PR

**Only after explicit approval** (`open the fix PR`, `yes do it`, `apply the fixes`):

1. Branch from the PR's head (not main): `git checkout -b fix/<short-slug>`
2. Apply ONE fix at a time, one commit per finding. Commit messages must follow Conventional Commits (this is the fluid-mono style and matches what most theme repos use):

```

fix(theme): collapse six product settings into product_list

Six identical `type: "product"` settings on the featured-products block —
replaced with one `type: "product_list"` with `limit: 6` and a single
`{% for product in section.settings.products %}` loop.

Severity: should

```

3. Run `fluid theme lint --json` locally as the final check.
4. Push the branch.
5. Open the PR with this body (using `gh pr create`):

```

## Theme review fixes

Follow-up to #<original-pr>. Each commit addresses one finding from the review.
Validated locally with `fluid theme lint --json`.

| Commit | Severity | Finding                                    |
| ------ | -------- | ------------------------------------------ |
| abc123 | blocker  | Invalid setting type `text_area`           |
| def456 | should   | Collapse `product` × 6 into `product_list` |
| ...    | ...      | ...                                        |

````

6. **Never amend or force-push.** Each fix is a reversible commit.

### D. What never to do

- **Never** push directly to the PR's branch without approval.
- **Never** run `fluid theme push` against a production theme. The agent's job is to comment, lint, and propose. The CLI's `push` writes to the live API.
- **Never** bundle unrelated style/cosmetic changes with a behavioral fix.
- **Never** mark a `nit` as `blocker` to force engagement.
- **Never** rewrite a section the user didn't ask you to rewrite. Propose first.

---

## Quick reference — the checklist

When reviewing any theme file, run through this in order. Anything unchecked is a finding.

**Structure**

- [ ] Repo has `assets/`, `config/`, and at least one page-type directory (e.g. `home_page/`, `product/`) — at minimum the ones it needs
- [ ] `config/settings_schema.json` exists
- [ ] `layouts/theme.liquid` exists
- [ ] Sections live under `sections/{name}/index.liquid`; components under `components/{name}/index.liquid`; page templates under `{page_type}/{variant}/index.liquid` (where `variant` is `default` or any user-defined name)
- [ ] No `templates/` wrapper directory at the theme root (sections/components/page-types sit at root)
- [ ] No files nest deeper than two directories from theme root (no `sections/{name}/blocks/{...}`, no `assets/icons/social/{...}`)
- [ ] No sections without `{% schema %}`; no components *with* `{% schema %}`
- [ ] No `.css`/`.js`/image assets outside `assets/`
- [ ] No co-located `styles.css` / `style.css` next to a template, section, or component (deprecated — all CSS lives in `assets/`)
- [ ] Section/component directory names are `snake_case` and globally unique

**Layout**

- [ ] Every file in `layouts/` emits `{{ content_for_header }}` inside `<head>`
- [ ] Every file in `layouts/` emits `{{ content_for_layout }}` inside `<body>`

**Schema correctness**

- [ ] Every `{% schema %}` `type:` value is one of the canonical setting types (`fluid theme lint --json` rejects unknown types)
- [ ] Every setting has a non-empty, unique `id` — *except* `type: "header"` settings, which carry `content:` instead of `id`
- [ ] Every block has a `type` and (where required) a `name`
- [ ] `range` has `min`/`max`/`step`; `select`/`radio` has `options`; `*_list` has `limit`
- [ ] User-facing settings have a `default:`
- [ ] Every `{% section 'name' %}` has a matching `sections/name/index.liquid` on disk
- [ ] `fluid theme lint --json` runs clean

**Settings dynamism**

- [ ] No user-visible literal text in markup (use `text`/`textarea`/`richtext`)
- [ ] No hardcoded colors in styles (use `color` / `color_background` or a global token)
- [ ] No hardcoded image URLs (use `image_picker` or upload to `assets/`)
- [ ] No external CDN URLs for theme-owned assets
- [ ] No hardcoded `href` to fixed paths the company might want to change (use `url`)

**Global settings (config + layout)**

- [ ] `config/settings_schema.json` defines `typography`, `color_schema`, and `spacing` groups (at minimum)
- [ ] `layouts/theme.liquid` reads those settings and emits CSS variables on `:root`
- [ ] Sections consume `var(--font-*)`, `var(--color-*)`, `var(--space-*)` rather than re-reading `settings.*` directly
- [ ] No section-level setting duplicates a global token (per-section overrides are the exception, default `unset`)
- [ ] Schema is grouped by `name:` (not a flat array)
- [ ] If dark mode is in schema, it's wired in `theme.liquid` (`@media (prefers-color-scheme: dark)` or `[data-theme="dark"]`)

**Blocks-first content model**

- [ ] Section *content* (headings, text, images, CTAs, cards, etc.) is modeled as **blocks**, not fixed section settings — even when there's only one today
- [ ] Section settings hold only true whole-section config (width, background, padding, columns, alignment)
- [ ] Blocks are **standalone** (`blocks/{name}/index.liquid`); inline blocks only for very small, one-off cases
- [ ] No content element a merchant would add / remove / reorder is locked into a section setting

**Settings ergonomics**

- [ ] Section settings panel under ~15 fields, OR repeated variations moved to blocks
- [ ] No 2+ singular resource pickers playing the same role (collapse to `*_list`)
- [ ] No `X_1` / `X_2` / `X_3` parallel-named settings (use blocks)
- [ ] No `*s_list` where the canonical `*_list` exists (e.g. `product_list`, not `products_list`)

**Dead code**

- [ ] No section files with zero `{% section 'name' %}` references (after confirming editor metadata)
- [ ] No component files with zero `{% render 'name' %}` references
- [ ] No `{% schema %}` `blocks:` declaring a `type:` the template never handles
- [ ] No `assets/` files with zero references in any `.liquid` or `.css` (greppable from the theme root)

**Liquid + size**

- [ ] Section under 400 lines; component under 250 lines
- [ ] No identical `{% render %}` snippet appearing 3+ times
- [ ] No `asset_url` inside a `for` loop
- [ ] All `for`/`if` in markup context use `{%-` / `-%}` whitespace control
- [ ] `{% if %}` / `{% endif %}` (and `for`/`case`/`capture`) tags balance

**Variable scope**

- [ ] Every `{{ section.settings.* }}` / `{{ block.settings.* }}` read has a matching `id` declared in the same file's `{% schema %}`
- [ ] No resource drops (`product`, `collection`, etc.) read outside the templates where they're in scope, unless explicitly passed
- [ ] `block` and `forloop.*` references only appear inside their respective loops
- [ ] Components only read variables passed via `{% render %}` arguments
- [ ] No typos in setting `id`s (silently render empty)

**Navigation**

- [ ] No hardcoded `<a href="/...">` rows that visually form a navigation — use `link_list`
- [ ] No `text` + `url` setting pairs used to fake a menu

**Assets**

- [ ] No inline `<style>` block over 10 lines (extract to `assets/*.css`)
- [ ] No inline `<script>` block over 5 lines (extract to `assets/*.js`)
- [ ] JS tags have `defer` (or a justification for not)
- [ ] No dead assets under `assets/`

**Editor attributes (`section.fluid_attributes` / `block.fluid_attributes`)**

- [ ] Every section file emits `{{ section.fluid_attributes }}` on its root wrapper element
- [ ] Every block iterated via `{% for block in section.blocks %}` carries `{{ block.fluid_attributes }}` on its own root element
- [ ] No typos (`fluid_attribute`, `fluid_attr`, `fluidAttributes`)
- [ ] No hand-rolled `data-fluid-section-*` attributes — always go through the helper
- [ ] When passing through a component, attributes are forwarded as `attr: block.fluid_attributes`

**FairShare behavioral attributes (`data-fluid-*`)**

- [ ] Every attribute uses kebab-case `data-fluid-*` (no camelCase, no underscores, `data-` prefix required)
- [ ] `data-fluid-cart` is one of `"open"` / `"close"` / `"toggle"` (lowercase)
- [ ] Modifier attributes (`quantity`, `subscribe`, `subscription-plan-id`, `bundled-items`, `bundle-selections`, `open-cart-after-add`) are always paired with an add-action attribute
- [ ] `data-fluid-subscription-plan-id` carries a single integer (never comma-separated)
- [ ] JSON-valued attributes (`bundled-items`, `bundle-selections`) are valid JSON with numeric IDs and quantities
- [ ] Attributes live on `<button>` or `<a>` (not `<div>` without semantics)
- [ ] Exactly one `<script id="fluid-cdn-script">` with `data-fluid-shop` set is loaded by the layout

**Security & a11y**

- [ ] User content escaped (`| escape`) unless it's a HTML-shaped type (`richtext`/`html`/`html_textarea`)
- [ ] Images have `alt`; below-the-fold images have `loading="lazy"`
- [ ] Clickable elements use `<button>` (action) or `<a href>` (nav) — never `<div>`

If every box checks, the file is healthy. Each unchecked box is a finding — tag it and report it per [Review workflow](#review-workflow--how-to-actually-output-findings).
