# Fluid-Specific Rules

## DO NOT Replace

| Section                                                                                                                  | Why                                                                                                                                               |
| ------------------------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------- |
| Scaffold's product-data section (`sections/product_hero` in current starters, `sections/main_product` in older starters) | Wired to Fluid's product object (name, price, images, variants, add-to-cart). Inspect the scaffold and build around its canonical implementation. |
| Cart functionality                                                                                                       | Fluid-controlled. Don't touch `cart_page` templates.                                                                                              |
| Checkout                                                                                                                 | Fluid-controlled. Don't clone.                                                                                                                    |

---

## Theme Directory Structure

```
your-theme/
├── layouts/
│   └── theme.liquid              ← Global wrapper (nav + footer + content)
├── home_page/
│   └── default/index.liquid      ← Homepage template
├── page/
│   ├── about/index.liquid        ← Static page templates
│   └── [slug]/index.liquid
├── product/
│   └── [slug]/index.liquid       ← Product page templates
├── collection/
│   └── default/index.liquid      ← Collection page templates
├── sections/
│   ├── main_navbar/index.liquid  ← Global nav (in theme.liquid)
│   ├── main_footer/index.liquid  ← Global footer (in theme.liquid)
│   ├── product_hero/index.liquid ← Canonical product data; name varies by starter
│   └── <descriptive_name>/index.liquid ← Custom section only when the library has no fit
├── config/
│   ├── settings_schema.json      ← Theme setting definitions
│   └── settings_data.json        ← Current theme setting values
└── assets/
    └── product.js, etc.
```

---

## Navigation & Footer

The global nav and footer live in:

- `sections/main_navbar/index.liquid`
- `sections/main_footer/index.liquid`

These are rendered by `layouts/theme.liquid` and appear on every page. Only modify if you are cloning the source site's nav/footer.

---

## Video Handling

| Type                          | Handling                                                                                                                    |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| Self-hosted (`.mp4`, `.webm`) | Upload the public source directly with `dam_upload(url=..., create_media=true)`. If rejected for size, fetch to the sandbox, run `compress_media`, and retry with `dam_upload(path=...)`. Use `asset.default_variant_url`. |
| YouTube/Vimeo embeds          | Keep original embed URLs. Use a supported `url` setting or the canonical Fluid Media block.                                 |
| Background videos             | Use `autoplay`, `loop`, `muted`, `playsinline` attributes. Include poster image fallback.                                   |

Rendered HTML can expose different desktop and mobile `<source>` URLs. Record
and upload both when present. Replacing a required source video with a still
image, poster, gradient, or flat color is a launch-blocking fidelity defect.

---

## Fluid Liquid Objects

Use these instead of hardcoded values where applicable:

```liquid
{{ product.name }}
{{ product.price | money }}
{{ product.description }}
{{ product.images }}
{{ cart.total | money }}
{{ cart.items }}
{{ company.name }}
{{ company.logo_url }}
{{ company.shop_page_url }}
{{ company.checkout_url }}
{{ 'key' | t }}                          {%- comment -%} Translations {%- endcomment -%}
{{ image.url | img_url: 'w-600,h-400,f-auto,q-80' }}   {%- comment -%} Product images (ImageKit transform, not a size string) {%- endcomment -%}
```

---

## Global Sections vs Template Sections

### Global Sections (in `theme.liquid`)

- Appear on EVERY page
- Defined once, shared data
- Examples: `main_navbar`, `main_footer`

### Template Sections (in templates)

- Page-specific
- Each template stores section instances, order, and optional layout settings.
- Visible content blocks come from each section's preset when Fluid expands the template.
- Same section type can have different expanded block data per template after editor saves.

---

## Defensive Liquid Patterns

Always provide fallbacks:

```liquid
{{ company.name | default: 'Company' }}
```

Guard optional structures:

```liquid
{% if product and product.images %}
  <img src="{{ product.images[0].src }}" alt="{{ product.title | default: 'Product' }}">
{% endif %}
```

Use `section.blocks.size` to check if blocks exist:

```liquid
{% if section.blocks.size > 0 %}
  {% for block in section.blocks %}
    ...
  {% endfor %}
{% endif %}
```
