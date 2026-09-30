# Schema Settings Reference

The rules this clone workflow enforces on section and block schemas. The setting types themselves, their fields, examples, `visible_if`, and which types Fluid resolves into Liquid objects are documented on docs.fluid.app. Look them up with `search_docs` or `query_docs` instead of relying on memory:

- [Schema components](https://docs.fluid.app/themes/schema-components): every supported `type`, setting fields, `visible_if`, resource selectors, presets, and option groups.
- [Settings schema](https://docs.fluid.app/themes/settings-schema): theme-wide settings and the types the theme panel renders.
- [Blocks and components](https://docs.fluid.app/themes/blocks-and-components): inline blocks, standalone blocks, and `content_for`.
- [Common theme pitfalls](https://docs.fluid.app/themes/common-pitfalls).

Labels should use **Title Case**.

---

## 🚫 NON-NEGOTIABLE RULES — Read first, every time

These rules are violated most often. Before you write any schema, internalize them.

### 1. Content images MUST be `blocks/image` — never `image_picker`

Any image the merchant can swap — a hero image, a card photo, an avatar, a logo, a step illustration, an ingredient shot, a "before"/"after" photo — **must be added as a canonical `image` block**. Not as a section-level `image_picker`. Not as an inline `image_picker` inside some other block's settings.

**ALLOWED uses of `image_picker`:**

| Location                                         | Id (convention)              | Purpose                                                   |
| ------------------------------------------------ | ---------------------------- | --------------------------------------------------------- |
| Section Shell                                    | `background_image`           | Decorative full-section background                        |
| Container                                        | `container_background_image` | Decorative container background                           |
| Canonical `blocks/image` only                    | `image`                      | The single image control inside the canonical image block |
| Data-driven wrappers (`blocks/post_image`, etc.) | varies                       | Fallback when the resource's own image is blank           |

**FORBIDDEN uses of `image_picker`:**

- As a section-level content image (e.g. `before_image`, `after_image`, `hero_image`, `logo_image`)
- As an image field inside a non-image block (e.g. `avatar` on a review card, `photo` on a testimonial, `logo_image` on a press card)
- As an "image override" on a product-picker block that isn't the canonical image block

**Why:** the canonical `image` block ships 7+ controls (aspect ratio, fit, object position, corner radius, border width/color, overlay) that every card/tile/hero needs. When you inline an `image_picker` directly, merchants lose all of those controls, can't duplicate the image independently, and the layout breaks the moment the design needs variation.

**When a section needs images per card** (review grid, testimonial grid, logo bar, step list, before/after, ingredient list), use the **divider block pattern**: one divider block type (e.g. `review`, `step`, `logo_item`) with no image field, plus canonical `image` block instances that render inside the current divider's scope via the stateful walk.

**Pre-push checklist:** grep your section for `"type": "image_picker"`. Every match must fall into one of the three ALLOWED rows above. If any match is a content image, convert it to a canonical `image` block.

### 2. Content fonts MUST come from `font_families` option group — never `font_picker`

`font_picker` only lives in `config/settings_schema.json`. Section-level font choices are `select` pointed at `font_families`, whose values are CSS variables (`var(--ff-heading)`, `var(--ff-italic)`, etc.).

### 3. Content colors MUST come from `background_colors` option group — never raw hex

Same reason as fonts. Section-level color choices are `select` pointed at `background_colors`, whose values are CSS variables (`var(--clr-primary)`, `transparent`, etc.).

### 4. Every section uses Section Shell + Container — no exceptions

Canonical structure (6 + 9 = 15 settings that every section ships):

**Section Shell (6 settings — always at the bottom of the settings array under a `{ "type": "header", "content": "Section Shell" }` header):**

- `padding` — id `section_padding`
- `corner_radius` — id `section_border_radius`
- `select` (background_colors) — id `background_color`
- `image_picker` — id `background_image`
- `range 0–10` — id `section_border_width`
- `select` (background_colors) — id `section_border_color`

**Container (9 settings — under a `{ "type": "header", "content": "Container" }` header, placed just before Section Shell):**

- `select` — id `container_max_width` (options: 1080px / 1280px / 1440px / 100%)
- `padding` — id `container_padding`
- `corner_radius` — id `container_border_radius`
- `select` (background_colors) — id `container_background_color`
- `image_picker` — id `container_background_image`
- `select` (background_colors) — id `container_overlay_color`
- `range 0–100%` — id `container_overlay_opacity`
- `range 0–10` — id `container_border_width`
- `select` (background_colors) — id `container_border_color`

**Implementation in Liquid:**

```liquid
.sec.section-{{ section.id }} {
  {%- assign p = section.settings.section_padding -%}
  {%- if p -%}padding: {{ p.top | default: 80 }}px 0 {{ p.bottom | default: 80 }}px 0;{%- else -%}padding: 80px 0;{%- endif -%}
  background-color: {{ section.settings.background_color | default: 'transparent' }};
}
.sec.section-{{ section.id }} .sec__container {
  max-width: {{ section.settings.container_max_width | default: '1280px' }};
  margin: 0 auto;
  padding: 0 64px;
}
```

Vertical padding on the shell keeps the background edge-to-edge. The container holds content at max-width. **Don't** put horizontal padding on the shell or you'll kill full-bleed backgrounds.

### 5. Hero intros use richtext BLOCKS — not section-level text fields

Every section with an intro (heading, eyebrow, subhead) exposes them as canonical `eyebrow`, `heading`, `subhead` blocks — each a single `richtext` setting with a styled default. Merchant can edit, add, remove, and reorder them independently. Never a single `{ "type": "text", "id": "heading" }` section setting for a visible title.

**Default richtext** ships with inline `style=""` so first-paint looks intentional:

```json
{
  "type": "richtext",
  "id": "text",
  "label": "Text",
  "default": "<h2 style=\"color: var(--clr-primary); font-size: clamp(32px, 4.5vw, 56px); font-weight: 700; letter-spacing: -0.02em; line-height: 1.05;\">Default heading</h2>"
}
```

### 6. `{% render %}` resolves ONLY from `components/` — never `blocks/`

`{% render 'name' %}` looks up `components/` only, so `{% render 'cart_button' %}` finds nothing in `blocks/`. Files in `blocks/` are standalone blocks, which Fluid renders through `{% content_for 'blocks' %}` or `{% content_for 'block', type: '...', id: '...' %}`. This workflow treats the canonical `blocks/*` files as reference schemas: when a section needs one of them as fixed markup (like `blocks/cart_button`), **inline** the markup in the section. Put any other shared markup chunk in `components/` and render it from there.

---

## Not supported — use alternatives

Using these types will error or silently fail in the editor:

| Unsupported                           | Use instead                                  |
| ------------------------------------- | -------------------------------------------- |
| `paragraph`                           | `header` (with `content`)                    |
| `inline_richtext`                     | `text` or `richtext`                         |
| `article` / `article_list`            | `post` / `posts_list`                        |
| `video` / `video_url`                 | `video_picker` or `url`                      |
| `page`                                | — (not available)                            |
| `liquid`                              | — (cannot inject raw Liquid)                 |
| `color_scheme` / `color_scheme_group` | `select` with `options: "background_colors"` |
| `metaobject` / `metaobject_list`      | — (not available)                            |

---

## Common schema conventions

- Labels use **Title Case** ("Section Padding", not "section padding")
- Every section schema has `name`, `settings`, `blocks`, `presets`
- Every block schema has `name`, `settings`
- Use `header` to visually group related settings
- Use `visible_if` for dependent settings
- Use `"limit": 1` on blocks that should appear at most once
- Use `"info"` to hint recommended sizes, formats, or examples
- Private blocks start with `_` (e.g., `_product-card`) and are excluded from the `@theme` wildcard

## Live reference

A live, browsable version of every control with rendered examples lives at `page/schema-reference/index.liquid` in the base theme. Push the theme and visit `/pages/schema-reference` on your Fluid store.
