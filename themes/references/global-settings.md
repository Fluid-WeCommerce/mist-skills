# Global settings — typography, color, spacing, dark mode

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- The pattern
- What `config/settings_schema.json` looks like
- What `layouts/theme.liquid` does with them
- What belongs at the global level
- What does NOT belong at the global level
- Findings to surface
- Dark-mode patterns — two acceptable shapes
- Quick audit — globals health


The most-overlooked layer of a theme is **`config/settings_schema.json` + `layouts/theme.liquid`**. Globals are how a theme stays coherent: change one font in one place and every section follows. Reviewers should check both ends of this pipeline.

### The pattern

1. **`config/settings_schema.json`** declares theme-wide settings, grouped by `name` (typography, spacing, color_schema, shadows, border_radius, cards, etc.).
2. **`layouts/theme.liquid`** reads `{{ settings.* }}` and emits **CSS custom properties on `:root`** inside a `<style>` block.
3. **Sections and components** consume those custom properties via `var(--font-body)`, `var(--color-primary)`, etc. — never re-reading the underlying `settings.*` value.

### What `config/settings_schema.json` looks like

```json
[
  {
    "name": "theme_info",
    "theme_name": "My Theme",
    "theme_version": "1.0.0",
    "theme_author": "..."
  },
  {
    "name": "typography",
    "settings": [
      { "type": "header", "content": "Body" },
      {
        "type": "font_picker",
        "id": "font_family_body",
        "label": "Font family",
        "default": "Inter"
      },
      {
        "type": "range",
        "id": "font_weight_body",
        "label": "Weight",
        "min": 100,
        "max": 900,
        "step": 100,
        "default": 400
      },
      { "type": "header", "content": "Headings" },
      {
        "type": "font_picker",
        "id": "font_family_heading",
        "label": "Font family",
        "default": "Inter"
      },
      {
        "type": "range",
        "id": "font_size_h1",
        "label": "H1 size",
        "min": 24,
        "max": 96,
        "step": 1,
        "default": 48,
        "unit": "px"
      }
    ]
  },
  {
    "name": "color_schema",
    "settings": [
      {
        "type": "color",
        "id": "color_primary",
        "label": "Primary",
        "default": "#0a0a0a"
      },
      {
        "type": "color",
        "id": "color_secondary",
        "label": "Secondary",
        "default": "#ffffff"
      },
      {
        "type": "color",
        "id": "color_text",
        "label": "Body text",
        "default": "#111111"
      }
    ]
  },
  {
    "name": "appearance",
    "settings": [
      {
        "type": "checkbox",
        "id": "enable_dark_mode",
        "label": "Enable dark mode toggle",
        "default": false
      }
    ]
  }
]
```

Note: the **outer array is grouped**, not flat. Each object with a `name:` becomes a settings group in the editor UI. The `theme_info` group is metadata and contains no `settings:` array.

### What `layouts/theme.liquid` does with them

```liquid
<head>
  ...
  {{ settings.font_family_body    | font_face: font_display: 'swap' }}
  {{ settings.font_family_heading | font_face: font_display: 'swap' }}

  <style>
    :root {
      /* Typography */
      --font-body:        {{ settings.font_family_body    | font_family | default: "Inter, system-ui, sans-serif" }};
      --font-heading:     {{ settings.font_family_heading | font_family | default: "Inter, system-ui, sans-serif" }};
      --font-weight-body: {{ settings.font_weight_body | default: 400 }};
      --font-size-h1:     {{ settings.font_size_h1     | default: 48 | append: 'px' }};

      /* Color */
      --color-primary:    {{ settings.color_primary   | default: '#0a0a0a' }};
      --color-secondary:  {{ settings.color_secondary | default: '#ffffff' }};
      --color-text:       {{ settings.color_text      | default: '#111111' }};
    }

    {%- if settings.enable_dark_mode -%}
      @media (prefers-color-scheme: dark) {
        :root {
          --color-primary:   {{ settings.color_primary_dark   | default: '#ffffff' }};
          --color-secondary: {{ settings.color_secondary_dark | default: '#0a0a0a' }};
          --color-text:      {{ settings.color_text_dark      | default: '#fafafa' }};
        }
      }
    {%- endif -%}
  </style>
</head>
```

And sections then look like:

```css
.featured-products h2 {
  font-family: var(--font-heading);
  font-size: var(--font-size-h1);
  color: var(--color-text);
}
```

### What belongs at the global level

Anything that should stay consistent across the whole theme:

| Group           | Settings typically here                                                                                      |
| --------------- | ------------------------------------------------------------------------------------------------------------ |
| `typography`    | Body + heading font families, font weights, font size scale (`xs`–`9xl`), heading sizes (h1–h6), line height |
| `color_schema`  | Brand palette (primary, secondary, accent, text, surface, border), plus dark-mode variants                   |
| `spacing`       | Spacing scale, section padding scale                                                                         |
| `layout`        | Max container width, gutter, grid breakpoints                                                                |
| `border_radius` | Radius scale (sm, md, lg, full)                                                                              |
| `shadows`       | Shadow scale (sm, md, lg)                                                                                    |
| `cards`         | Card-wide defaults (radius, shadow, padding) that per-card-type groups inherit                               |
| `appearance`    | Dark mode toggle, motion-reduce, animation preferences                                                       |
| `theme_info`    | Theme name, version, author, docs URL — **metadata only, no `settings:`**                                    |

### What does NOT belong at the global level

- Per-section labels and copy (those are section-level)
- Per-page hero images, banners, CTAs (section/block-level)
- One-off colors used by exactly one section (section-level)
- Anything that varies per page or per resource

The test: _would changing this break the visual coherence of the rest of the theme?_ If yes, it's a global. If no, it's a section setting.

### Findings to surface

| You see                                                                                                                        | Severity  | Fix                                                                                                                                                                             |
| ------------------------------------------------------------------------------------------------------------------------------ | --------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Section adds its own `font_family` / `font_size` / `color_*` setting when the global already exists                            | `should`  | Use `var(--font-body)`, `var(--color-primary)`, etc. Per-section overrides should be the _exception_, configured via section setting `color_override` that defaults to `unset`. |
| Theme has 0 global typography settings but every section hardcodes fonts in inline styles                                      | `blocker` | Add a `typography` group to `config/settings_schema.json` and a `:root` `<style>` block in `layouts/theme.liquid`.                                                              |
| Theme has 0 global color settings but uses hardcoded hex everywhere                                                            | `blocker` | Add a `color_schema` group.                                                                                                                                                     |
| `layouts/theme.liquid` reads `settings.*` but emits no `<style>` / CSS variables                                               | `should`  | Wire the settings into `--var` declarations on `:root`. Without this layer, sections have no way to consume globals.                                                            |
| `config/settings_schema.json` is a **flat array of settings** (no `name:` groups)                                              | `should`  | The engine accepts it, but the editor UI flattens to one giant panel. Group by `name:` (typography, color, spacing, …) for usability.                                           |
| `theme_info` group missing                                                                                                     | `nit`     | Adds version + author metadata visible to admins.                                                                                                                               |
| Two `font_family_body` and `font_family_heading` settings exist but every section uses a hardcoded `font-family: 'Inter'`      | `blocker` | Rewire sections to `var(--font-heading)` / `var(--font-body)`. Globals that nothing consumes are dead weight.                                                                   |
| Dark-mode toggle exists in schema but no `@media (prefers-color-scheme: dark)` / `[data-theme="dark"]` block in `theme.liquid` | `blocker` | Setting is a lie — wire it.                                                                                                                                                     |

### Dark-mode patterns — two acceptable shapes

1. **System-driven** (`@media (prefers-color-scheme: dark)`): respects OS setting, no user toggle. Lighter touch, no JS.
2. **Toggle-driven** (`[data-theme="dark"]` on `<html>`): explicit toggle, persisted in `localStorage`, falls back to system. Heavier but lets users override.

Reviewer's rule: if the theme has a _toggle button_ anywhere, it MUST use the toggle-driven pattern. If it has none and only the schema checkbox, system-driven is fine.

### Quick audit — globals health

```bash
# 1. Are global groups defined?
jq -r '.[].name' config/settings_schema.json

# 2. Does the layout consume them?
grep -E 'settings\.' layouts/theme.liquid | head

# 3. Does the layout emit CSS variables?
grep -E '^\s*--[a-z-]+:' layouts/theme.liquid | head

# 4. Do sections actually USE the variables (vs. hardcoded)?
grep -rE 'font-family:\s*[A-Za-z]' --include='*.liquid' --include='*.css' . 2>/dev/null  # hardcoded fonts
grep -rE 'color:\s*#[0-9a-fA-F]'   --include='*.liquid' --include='*.css' . 2>/dev/null  # hardcoded colors
```

If steps 1–3 are populated and step 4 finds lots of hardcoded fonts/colors, the globals exist but nothing uses them — file a `should` to rewire.

---
