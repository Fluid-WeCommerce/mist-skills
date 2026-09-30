# Global settings — typography, color, spacing, dark mode

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Where global settings are documented

How `config/settings_schema.json` is shaped, which setting types the theme panel renders, how typography presets work, and how `layouts/theme.liquid` turns settings into CSS custom properties are documented on docs.fluid.app. Look them up with `search_docs` or `query_docs`:

- [Root theme configuration](https://docs.fluid.app/themes/root-theme-configuration): the settings → `layouts/theme.liquid` → CSS variable flow.
- [Settings schema](https://docs.fluid.app/themes/settings-schema): the types the theme panel renders, the `typography` group, font IDs, and preset CSS variables.
- [Linked CSS variable presets](https://docs.fluid.app/themes/linked-css-variable-presets).

This file keeps only the review checks.

### The pattern to check for

1. `config/settings_schema.json` declares theme-wide settings in named groups.
2. `layouts/theme.liquid` reads `{{ settings.* }}` and emits CSS custom properties on `:root`.
3. Sections consume those properties with `var(--...)` rather than re-reading `settings.*`.

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

| You see | Severity | Fix |
| --- | --- | --- |
| A section adds its own `font_family` / `font_size` / `color_*` setting when a global already exists | `should` | Use the global's CSS variable. Keep per-section overrides as the exception, defaulting to the global. |
| No global typography settings, and every section hardcodes fonts | `blocker` | Add a `typography` group to `config/settings_schema.json` and a `:root` block in `layouts/theme.liquid`. |
| No global color settings, and hex values are hardcoded everywhere | `blocker` | Add a color group. |
| `layouts/theme.liquid` reads `settings.*` but emits no CSS variables | `should` | Wire the settings into `:root` custom properties so sections can consume them. |
| A font setting in `config/settings_schema.json` whose type isn't `font_picker` | `should` | Use `font_picker`. Other font types render no control in the theme panel. |
| Typography settings in a group not named exactly `typography` | `should` | Rename the group. Only `typography` becomes preset cards. |
| `header` entries in `config/settings_schema.json` | `nit` | The theme panel drops them. Use groups instead. |
| Neither `font_family_heading` nor `font_family_body` declared | `should` | Declare at least one; presets fall back to them. |
| Headings read only `var(--font_family_heading)` where a typography preset exists | `should` | Read the preset's variable first, as the settings-schema docs show, or preset changes won't show. |
| A filter the engine doesn't define, such as `\| font_family` | `blocker` | Check the docs for the filter. `font_face` exists; `font_family` doesn't. |
| Font settings exist, but every section hardcodes `font-family: 'Inter'` | `blocker` | Rewire sections to the font variables. Globals nothing reads are dead weight. |
| A dark-mode setting in the schema but no `@media (prefers-color-scheme: dark)` or `[data-theme="dark"]` block in `theme.liquid` | `blocker` | The setting does nothing. Wire it. |

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
