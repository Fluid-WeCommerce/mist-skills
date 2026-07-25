# Fluid page templates

A page template composes sections. It does not contain page copy and it does not recreate
blocks that belong to section presets.

## Template contract

1. Use canonical section names from the scaffold whenever possible.
2. Give every section instance a unique `id`.
3. The template schema has top-level `sections` and `order`.
4. Each schema section entry contains `type` and, only when necessary, layout `settings`.
5. Never put `blocks` in a template schema. Blocks come from the referenced section preset.
6. Use the scaffold's canonical product-data section first on PDPs. Inspect the scaffold:
   current starters use `product_hero`; older starters use `main_product`. Do not replace,
   fork, or hand-roll it.
7. Build one faithful `product/default` template for the normal PDP structure and one
   faithful `collection/default` template for normal collections. Only create a
   slug-specific template when the source truly uses a different structure.

## Homepage

```liquid
{% section 'hero_centered', id: 'home_hero' %}
{% section 'image_text_split', id: 'home_story' %}
{% section 'featured_products', id: 'home_products' %}
{% section 'testimonial_grid', id: 'home_reviews' %}
{% section 'cta_banner_v2', id: 'home_cta' %}

{% schema %}
{
  "sections": {
    "home_hero": { "type": "hero_centered" },
    "home_story": { "type": "image_text_split" },
    "home_products": { "type": "featured_products" },
    "home_reviews": { "type": "testimonial_grid" },
    "home_cta": { "type": "cta_banner_v2" }
  },
  "order": [
    "home_hero",
    "home_story",
    "home_products",
    "home_reviews",
    "home_cta"
  ]
}
{% endschema %}
```

The source manifest decides which canonical sections appear and in what order. The list
above is a shape example, not a default homepage recipe.

## Product default

Inspect the current scaffold before choosing the first line.

```liquid
{% section 'product_hero', id: 'product_main' %}
{% section 'product_benefits', id: 'product_benefits' %}
{% section 'product_details', id: 'product_details' %}
{% section 'product_reviews', id: 'product_reviews' %}
{% section 'product_related', id: 'product_related' %}

{% schema %}
{
  "sections": {
    "product_main": { "type": "product_hero" },
    "product_benefits": { "type": "product_benefits" },
    "product_details": { "type": "product_details" },
    "product_reviews": { "type": "product_reviews" },
    "product_related": { "type": "product_related" }
  },
  "order": [
    "product_main",
    "product_benefits",
    "product_details",
    "product_reviews",
    "product_related"
  ]
}
{% endschema %}
```

If the scaffold ships `main_product` instead, use it in both the Liquid tag and schema.
The sections after it must follow the source PDP's actual order; do not cargo-cult the
example list.

## Collection and shop

```liquid
{% section 'collection_banner', id: 'collection_banner' %}
{% section 'collection_products', id: 'collection_products' %}
{% section 'cta_banner_v2', id: 'collection_cta' %}

{% schema %}
{
  "sections": {
    "collection_banner": { "type": "collection_banner" },
    "collection_products": { "type": "collection_products" },
    "collection_cta": { "type": "cta_banner_v2" }
  },
  "order": [
    "collection_banner",
    "collection_products",
    "collection_cta"
  ]
}
{% endschema %}
```

For a source with a dedicated all-products or collections index, also compose the
scaffold's `shop_page` / collection-index surface rather than forcing the source shop
into one collection detail template.

## Content page

```liquid
{% section 'page_header', id: 'page_header' %}
{% section 'rich_text', id: 'page_body' %}
{% section 'cta_banner_v2', id: 'page_cta' %}

{% schema %}
{
  "sections": {
    "page_header": { "type": "page_header" },
    "page_body": { "type": "rich_text" },
    "page_cta": { "type": "cta_banner_v2" }
  },
  "order": [
    "page_header",
    "page_body",
    "page_cta"
  ]
}
{% endschema %}
```

Remember that a template does not create a routeable page record. Create or reconcile the
corresponding Fluid page resource separately.

## Anti-pattern: blocks in template schemas

```json
{
  "sections": {
    "hero": {
      "type": "hero_centered",
      "blocks": {
        "heading": { "type": "heading" }
      }
    }
  }
}
```

This is invalid for Fluid theme templates. Put the default blocks in
`sections/hero_centered/index.liquid`'s preset and let Fluid expand them when the template
record is created.

After changing a preset for an existing template, delete the stale
`application_theme_template` record and re-PUT the template resource so the preset expands
again. Editing a preset does not retroactively mutate already-expanded template data.
