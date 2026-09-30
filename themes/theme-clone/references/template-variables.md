# Template Variables & Scopes

Which Liquid variables each template type exposes is documented in [Theme variables](https://docs.fluid.app/themes/theme-variables). Look a variable up there with `search_docs` or `query_docs` before you use it. Never rely on a remembered variable name. This file keeps only the scope rules and defensive patterns.

---

## Scope Rules (STRICT)

1. Each template type exposes a specific set of data (its "template scope").
2. Sections can use only the data their page's scope provides.
3. Global variables (`company`, `request`, `affiliate`, `localization`, `settings`) are available on every page.
4. Data outside the scope renders empty, with no error.
5. Don't assume cross-page access. For example, a top-level `product` isn't available on the home page.
6. `request` carries only `path`, `host`, `page_type`, `query_parameters`, and `full_url`. Read the visitor's language and country from `localization`, never from `request.locale`.
7. Only some resource setting types resolve into objects. A `post` or `collection_list` setting gives you the saved ID or slug. See [Common theme pitfalls](https://docs.fluid.app/themes/common-pitfalls#know-which-settings-fluid-resolves).

---

## Defensive Usage Patterns

### Always provide fallbacks
```liquid
{{ company.name | default: 'Company' }}
{{ product.title | default: 'Product Title' }}
```

### Guard optional structures
```liquid
{% if product and product.images %}
  <img src="{{ product.images[0].src }}" alt="{{ product.title | default: 'Product' }}">
{% endif %}
```

### Check the scope before you write the section

Before building a section for a template, look up that template's variables in the docs and confirm every variable the section reads is listed there. Typical mistakes:

- Reading `media.*` fields in a section meant for the home page.
- Reading `collection.filters` in a product-page section.
- Reading a top-level `product` on a collection page, where products come from `collection.products`.

---

## Global Theme Settings

Defined in `config/settings_schema.json`. Accessed via `settings.*` (NOT `section.settings.*`):

```liquid
{{ settings.primary_color }}
```
