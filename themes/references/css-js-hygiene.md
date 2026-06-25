# CSS / JS asset hygiene

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- 1. Naming and scoping — everything lives under `assets/`
- 1a. Deprecated — co-located `styles.css` / `style.css`
- 2. Tailwind class duplication
- 3. Dead code
- 4. Inline `<style>` blocks — extract to assets
- 5. Inline `<script>` blocks — extract to assets
- 6. Hardcoded URLs — use `asset_url`
- 7. Hardcoded copy in markup


### 1. Naming and scoping — everything lives under `assets/`

**All stylesheets live under `assets/`.** Co-located `styles.css` / `style.css` files inside `sections/{name}/`, `components/{name}/`, etc. **are deprecated** and should be migrated.

- Section CSS: `assets/{section_name}.css`
- Component CSS: `assets/{component_name}.css`
- Global / theme-wide CSS: `assets/theme.css` (or named after intent — `assets/typography.css`, `assets/utilities.css`)
- Custom stylesheets: `assets/{name}.css`
- Scope class names by section: `.cart-page__line-item`, not `.line-item`

Referenced via `asset_url`:

```liquid
{{ 'featured_products.css' | asset_url | stylesheet_tag }}
````

### 1a. Deprecated — co-located `styles.css` / `style.css`

The earlier theme convention placed a `styles.css` next to each template, section, or component (e.g. `sections/featured/styles.css`). **This is being phased out** in favor of `assets/`-only. The reference `base-theme` still contains `styles.css` files inside section / page-variant directories — these are being migrated.

**`should`** when a PR adds or modifies a co-located stylesheet. **`blocker`** for any new file added under this pattern (new code must follow the assets-only convention).

| You see                                                                                                            | Severity  | Fix                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------ | --------- | ----------------------------------------------------------------------------------------------------------------- |
| New file `sections/{name}/styles.css`                                                                              | `blocker` | Place it under `assets/{name}.css` instead and reference via `{{ '{name}.css' \| asset_url \| stylesheet_tag }}`. |
| New file `components/{name}/style.css`                                                                             | `blocker` | Same — `assets/{name}.css` and `asset_url`.                                                                       |
| New file under a page-variant directory like `{type}/{variant}/styles.css`                                         | `blocker` | Move to `assets/{name}.css`.                                                                                      |
| Existing co-located stylesheet edited in the PR                                                                    | `should`  | Suggest migrating to `assets/` as part of the same PR if the diff is small, or a follow-up if not.                |
| Global / custom stylesheets anywhere outside `assets/` (other than the engine-recognized root `global_styles.css`) | `blocker` | Move to `assets/`.                                                                                                |
| Hardcoded path like `<link rel="stylesheet" href="/sections/{name}/styles.css">` (bypassing `asset_url`)           | `blocker` | Move the file and switch to `asset_url`.                                                                          |

Migration recipe (suggest in the comment when applicable):

```bash
# 1. Move the file
git mv sections/featured/styles.css assets/featured.css

# 2. Update the reference in the section template
# Find:   {{ 'sections/featured/styles.css' | asset_url | stylesheet_tag }}
# Replace:{{ 'featured.css' | asset_url | stylesheet_tag }}

# 3. Validate
fluid theme lint --json
```

### 2. Tailwind class duplication

Long, identical `class="…"` strings repeated across cards → extract via `{% capture %}` or a component. **`should`** when 4+ identical class strings appear.

### 3. Dead code

See [Dead code — unused blocks, components, sections, assets](#dead-code--unused-blocks-components-sections-assets) for the unified audit. Assets are one category among four.

### 4. Inline `<style>` blocks — extract to assets

**`should`** when any inline `<style>` block exceeds **10 lines**, or when the same inline rules repeat across multiple sections. The engine deduplicates external stylesheets across the page, so external is almost always better.

```liquid
{%- comment -%} Bad: 40 lines of CSS shipped per section render {%- endcomment -%}
<style>
  .featured-products { padding: 64px 0; }
  .featured-products__heading { font-size: 48px; }
  .featured-products__grid { display: grid; gap: 24px; ... }
  /* ... 30 more lines ... */
</style>

{%- comment -%} Good {%- endcomment -%}
{{ 'featured_products.css' | asset_url | stylesheet_tag }}
```

**Exception:** A small block of _dynamic_ CSS that depends on schema settings is fine inline — the dynamism is the whole point. Even then, extract the static base to a stylesheet and leave only the per-section overrides inline:

```liquid
{{ 'featured_products.css' | asset_url | stylesheet_tag }}
<style>
  .featured-products[data-section-id="{{ section.id }}"] {
    --section-bg: {{ section.settings.bg_color }};
    --section-pad: {{ section.settings.section_pad }};
  }
</style>
```

### 5. Inline `<script>` blocks — extract to assets

Same rule, lower threshold. **`should`** when any inline `<script>` block exceeds **5 lines**. Inline JS bypasses caching, defeats `defer`, and runs render-blocking unless explicitly deferred via `setTimeout`.

```liquid
{%- comment -%} Bad {%- endcomment -%}
<script>
  document.addEventListener('DOMContentLoaded', function() {
    const slider = document.querySelector('.featured-slider');
    new Splide(slider, { type: 'loop', perPage: 3 }).mount();
    // ...
  });
</script>

{%- comment -%} Good {%- endcomment -%}
<script src="{{ 'featured_slider.js' | asset_url }}" defer></script>
```

**Exception:** Tiny dynamic config bridges — passing schema settings into a global config object — are acceptable inline if under 5 lines. Keep the runtime in an asset:

```liquid
<script>
  window.fluidFeaturedConfig = {{ section.settings | json }};
</script>
<script src="{{ 'featured_slider.js' | asset_url }}" defer></script>
```

### 6. Hardcoded URLs — use `asset_url`

Any reference to an external CDN URL, hardcoded path, or `https://cdn.example.com/...` for assets the theme owns is a finding. The asset belongs in `assets/` and the URL should resolve through `| asset_url`.

| You see                                                                          | Severity  | Fix                                                                                                                                          |
| -------------------------------------------------------------------------------- | --------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| `src="https://cdn.example.com/img/banner.jpg"` (external CDN, theme-owned asset) | `blocker` | Download the file into `assets/banner.jpg` and use `{{ 'banner.jpg' \| asset_url }}`. External CDNs can disappear or change CORS.            |
| `src="/assets/banner.jpg"` (hardcoded path)                                      | `blocker` | Use `{{ 'banner.jpg' \| asset_url }}`. The engine versions/CDN-fronts the URL.                                                               |
| `href="https://fonts.googleapis.com/css?family=..."`                             | `should`  | Either upload the font files to `assets/` and `@font-face` them via stylesheet, or use `font_picker`.                                        |
| `<link rel="stylesheet" href="/some-static.css">`                                | `blocker` | `{{ 'some-static.css' \| asset_url \| stylesheet_tag }}`.                                                                                    |
| `<script src="https://unpkg.com/some-lib"></script>` (third-party library)       | `should`  | Vendor it into `assets/` and reference via `asset_url`. unpkg/jsDelivr can go down and you have no control over what loads.                  |
| Image URL hardcoded in CSS (`background-image: url(/assets/x.png)`)              | `should`  | Move the rule into Liquid where `asset_url` is available, or pre-process the CSS, or use a CSS variable injected via inline `<style>` block. |
| Hardcoded route paths (`href="/products"`, `href="/cart"`)                       | `nit`     | Acceptable when they're well-known engine routes. Surface only if the route ever changes per company.                                        |

**Why these matter:**

- `asset_url` returns a fingerprinted CDN URL — cache-busted on deploy, CDN-fronted globally.
- External CDNs introduce a dependency on a server you don't control.
- Hardcoded paths break when the theme is renamed or moved.

### 7. Hardcoded copy in markup

Already covered as **`should`** under [Dynamism](#dynamism--settings-over-hardcoded-values), but it's worth restating here because reviewers often miss it during a CSS/JS pass: literal English (or any language) hardcoded in markup is the same shape of problem as a hardcoded URL — it locks the theme to one company / one locale / one campaign.

- User-visible string → `text` / `textarea` / `richtext` setting
- Repeated brand-agnostic UI string (Add to cart, Read more) → `locales/en.json` and `{{ 'add_to_cart' | t }}`

---
