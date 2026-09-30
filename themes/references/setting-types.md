# Setting types — review checks

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Where the setting types are documented

The list of setting types, their fields, and how each one reaches Liquid lives on docs.fluid.app. Look it up there with `search_docs` or `query_docs` instead of relying on memory:

- [Schema components](https://docs.fluid.app/themes/schema-components): every supported `type`, the common setting fields, range and select examples, and resource selectors.
- [Settings schema](https://docs.fluid.app/themes/settings-schema): theme-wide settings in `config/settings_schema.json`.
- [Common theme pitfalls](https://docs.fluid.app/themes/common-pitfalls): which setting types Fluid resolves into Liquid objects.

`fluid theme lint --json` rejects any `type:` the validator doesn't know. This file keeps only the review checks.

## Resolved and unresolved resource types

Fluid resolves only these setting types into Liquid objects: `product`, `variant`, `collection`, `category`, `enrollment_pack`, `media`, `link_list`, and `product_list`. Every other resource type (`post`, `blog`, `forms`, `collection_list`, `posts_list`, and the rest) reaches Liquid as the saved value, usually an ID or slug.

Check every template that reads a resource setting:

- `section.settings.<id>.title` (or any other property) on an unresolved type renders empty. **`blocker`** if the section depends on it. Switch to a resolved type, or look the record up another way.
- For several products, use `product_list`. The `products_list` spelling passes lint but isn't resolved.

## Common type mistakes — find and fix

| You see | What you do |
| --- | --- |
| `type: "text_area"` | **`blocker`.** Use `textarea` (one word). |
| `type: "checkBox"` / `"image_pick"` | **`blocker`.** Mistyped. Replace with a type from the docs. |
| A property read on an unresolved resource type | **`blocker`.** See the section above. |
| `type: "products_list"` where the template loops over products | **`blocker`.** Use `product_list`, which Fluid resolves. |
| `type: "range"` without `min`/`max`/`step` | **`blocker`.** The slider has no bounds. |
| `type: "select"` or `"radio"` without `options:` | **`blocker`.** Empty dropdown or radio group. |
| `type: "checkbox"` without `default:` | **`should`.** The value is empty until an editor saves one. Set `default: false` (or `true`). |
| `type: "product_list"` without `"limit":` | **`nit`.** The stock theme caps list pickers with `limit:`; match it. |
| `richtext` output passed through `escape` | **`blocker`.** Double-escapes HTML, so shoppers see `&lt;p&gt;`. Output it raw: `{{ value }}`. |
| Setting missing `id` / duplicate `id` | **`blocker`.** The validator rejects it. |
| Block missing `type` or `name` | **`blocker`.** The validator rejects it. (`name` may be omitted only for `@app`, `@theme`, or standalone block refs.) |
| `"settings": { ... }` inside a block (object, not array) | **`blocker`.** The validator rejects it; it must be an array. |
| `{% section 'foo' %}` with no `sections/foo/index.liquid` | **`blocker`.** The validator rejects it. |
| A setting value interpolated into CSS with no `default` | **`should`.** An empty value makes the browser drop the declaration. Add `\| default:`. |
| 2+ singular `product` settings playing the same role | **`should`.** Collapse them into one `product_list`. |
