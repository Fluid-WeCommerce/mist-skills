# Worked examples — full section reviews

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- Summary review output
- Inline comment (line 9)
- Inline comment (lines 5-8)


**File:** `sections/featured_products/index.liquid`

```liquid
{% schema %}
{
  "name": "Featured Products",
  "settings": [
    { "type": "text",        "id": "heading", "label": "Heading" },
    { "type": "product",     "id": "p1",      "label": "Product 1" },
    { "type": "product",     "id": "p2",      "label": "Product 2" },
    { "type": "product",     "id": "p3",      "label": "Product 3" },
    { "type": "product",     "id": "p4",      "label": "Product 4" },
    { "type": "text_area",   "id": "desc",    "label": "Description" },
    { "type": "image",       "id": "bg",      "label": "Background" }
  ]
}
{% endschema %}

<section>
  <h2>{{ section.settings.heading }}</h2>

  {% for product in products %}
    <img src="{{ 'placeholder.png' | asset_url }}" />
    <a href="{{ product.url }}">{{ product.title }}</a>
  {% endfor %}

  {% if section.settings.p1 != blank %}{% render 'product_card', product: section.settings.p1 %}{% endif %}
  {% if section.settings.p2 != blank %}{% render 'product_card', product: section.settings.p2 %}{% endif %}
  {% if section.settings.p3 != blank %}{% render 'product_card', product: section.settings.p3 %}{% endif %}
  {% if section.settings.p4 != blank %}{% render 'product_card', product: section.settings.p4 %}{% endif %}
</section>
````

### Summary review output

```
## Theme review — featured_products.liquid

**8 findings** — 3 blocker, 4 should, 1 nit

Reproduce locally with `fluid theme lint --json`.

| Severity | Line | Finding |
|---|---|---|
| blocker | 9  | Invalid type `text_area` — use `textarea`. Validator rejects. |
| blocker | 16 | Missing `{{ section.fluid_attributes }}` on the section root — editor cannot select or click-to-edit this section. Replace `<section>` with `<section {{ section.fluid_attributes }}>`. |
| blocker | 18 | `{% for product in products %}` — `products` is undefined in this scope. It is not a global drop, and the schema declares no `products` setting. Loop silently iterates `nil`. Collapse to the `product_list` fix below (`section.settings.products`) or remove. |
| should  | 10 | Type `image` is valid but `image_picker` is clearer for new code |
| should  | 5-8 | Four `product` settings, same role — collapse to one `product_list` with `limit: 4` |
| should  | 19 | `asset_url` resolved inside loop — hoist above |
| should  | 16-21 | Missing whitespace control on `{% for %}` / `{% endfor %}` |
| nit     | 17 | `<h2>{{ section.settings.heading }}</h2>` — add `| default: 'Featured'` |
```

### Inline comment (line 9)

````
[blocker] Invalid setting type `text_area`

The schema validator only accepts the canonical type list. `fluid theme lint --json`
fails on this. The correct type is `textarea`:

```json
{ "type": "textarea", "id": "desc", "label": "Description" }
```
````

### Inline comment (lines 5-8)

````

[should] Four `product` settings — collapse to `product_list`

Four singular product pickers playing the same role. Replace with one list:

```json
{
  "type": "product_list",
  "id": "products",
  "label": "Products",
  "limit": 4
}
```

Render block becomes a single loop:

```liquid
{%- for product in section.settings.products -%}
  {% render 'product_card', product: product %}
{%- endfor -%}
```

This drops 4 conditionals + 4 settings into 1 + 1 and removes the per-slot upper
bound the manual setup encoded by accident. A `product_list` does **not** give
drag-and-drop reorder — that's a blocks feature; model items as blocks if the
merchant needs to reorder them.

````

---
