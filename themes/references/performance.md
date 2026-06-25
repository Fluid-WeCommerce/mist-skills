# Performance

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- 1. `asset_url` inside a loop
- 2. Unbounded `for` over a large collection
- 3. `sort` on large arrays
- 4. Repeated `section.settings.X` access
- 5. JS without `defer`
- 6. CSS scoping


### 1. `asset_url` inside a loop

**`blocker`** if it generates a unique URL per iteration, **`should`** if the URL is the same every time. Either way, hoist:

```liquid
{%- comment -%} Bad: same URL resolved N times {%- endcomment -%}
{%- for product in products -%}
  <img src="{{ 'placeholder.png' | asset_url }}" />
{%- endfor -%}

{%- comment -%} Good {%- endcomment -%}
{%- assign placeholder_src = 'placeholder.png' | asset_url -%}
{%- for product in products -%}
  <img src="{{ placeholder_src }}" />
{%- endfor -%}
```

### 2. Unbounded `for` over a large collection

**`should`** when iterating `collection.products` or any collection that can grow unbounded without `limit:`:

```liquid
{%- comment -%} Bad {%- endcomment -%}
{%- for product in collection.products -%} ... {%- endfor -%}

{%- comment -%} Good {%- endcomment -%}
{%- for product in collection.products limit: 12 -%} ... {%- endfor -%}
```

For paginated views, use `{% paginate %}`.

### 3. `sort` on large arrays

**`should`.** Liquid `sort` is in-memory and O(n log n) every render. Pre-sort at the data layer when possible, or cache via `{% capture %}` after the first sort.

### 4. Repeated `section.settings.X` access

**`nit`/`should`.** If the same setting is read 5+ times in markup, alias it once at the top:

```liquid
{%- assign show_title = section.settings.show_title -%}
{%- assign title_tag  = section.settings.title_tag  | default: 'h2' -%}
```

Improves perf and makes the section's "inputs" readable in one block.

### 5. JS without `defer`

**`should`.** Render-blocking script tags hurt LCP:

```liquid
{%- comment -%} Bad {%- endcomment -%}
<script src="{{ 'cart_page.js' | asset_url }}"></script>

{%- comment -%} Good {%- endcomment -%}
<script src="{{ 'cart_page.js' | asset_url }}" defer></script>
```

Exception: scripts that must run before DOM (rare in themes).

### 6. CSS scoping

**`should`.** Per-section CSS belongs in the section file:

```liquid
{{ 'cart_page.css' | asset_url | stylesheet_tag }}
```

Loading it in `layouts/theme.liquid` ships it on every page. The engine deduplicates stylesheets across the page, so it's safe to declare per-section.

---
