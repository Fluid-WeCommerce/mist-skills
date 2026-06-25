# Editor selector attributes — fluid_attributes

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- What `fluid_attributes` emits
- The two drops
- Correct usage
- Findings to surface
- Examples from the reference theme
- Quick audit


Sections and blocks have a Liquid drop called `fluid_attributes` that emits the `data-fluid-section-*` attributes the visual editor uses to find, select, click-to-edit, and drag-to-reorder the element. **Without these attributes on the right element, the editor cannot interact with the content** — click handlers don't bind, inspector panels don't open, drag-and-drop is dead.

> **Note:** Despite the `data-fluid-*` prefix, these are _editor_ attributes — not the same as the runtime [FairShare behavioral attributes](#fairshare-behavioral-attributes--data-fluid-) below (which wire up cart, checkout, enrollment behavior). Keep them straight: `section.fluid_attributes` / `block.fluid_attributes` are Liquid drops the _theme engine_ emits in editor mode; FairShare attributes are _hand-written_ HTML attributes that the FairShare runtime SDK reads.

These attributes are only populated in editor preview mode; in production rendering, the drops emit an empty string. So a missing call has zero visible effect at runtime — the bug only surfaces in the editor. That's why reviewers must catch it.

### What `fluid_attributes` emits

In editor mode, `{{ block.fluid_attributes }}` expands to the full set of `data-fluid-*` attributes the editor needs to find and edit the block — block id, parent section type, section id, block type, and a serialized settings payload — rendered as one attribute string on the element:

```html
<div
  data-fluid-section-block-id="abc123"
  data-fluid-parent-section-type="hero"
  data-fluid-section-id="45678"
  data-fluid-section-block-type="heading"
  data-fluid-block-attribute='{"color":"#000000",...}'
></div>
```

### The two drops

| Drop                             | Where it's available                                                                             | Where to emit it                                |
| -------------------------------- | ------------------------------------------------------------------------------------------------ | ----------------------------------------------- |
| `{{ section.fluid_attributes }}` | Inside a section file (`sections/{name}/index.liquid`)                                           | On the **root** wrapper element of the section  |
| `{{ block.fluid_attributes }}`   | Inside a `{% for block in section.blocks %}` loop, or when a block context is passed to a render | On the **root** wrapper element of _each_ block |

**These are the only two.** There is no `component.fluid_attributes`, no dropzone drop, no slot drop, no inline-editing helper. Components are pure partials — they don't have editor presence on their own; the section/block that _renders_ them carries the attributes.

### Correct usage

```liquid
{%- comment -%} Section root: section's attributes on the outer wrapper {%- endcomment -%}
<section class="featured-products" {{ section.fluid_attributes }}>
  {%- for block in section.blocks -%}
    {%- case block.type -%}
      {%- when 'heading' -%}
        <h2 class="featured-products__heading" {{ block.fluid_attributes }}>
          {{ block.settings.text | escape }}
        </h2>

      {%- when 'product_card' -%}
        <article class="featured-products__card" {{ block.fluid_attributes }}>
          {% render 'product_card', product: block.settings.product %}
        </article>

      {%- when 'cta' -%}
        {%- comment -%} Passing into a component? Forward the attrs through a named arg. {%- endcomment -%}
        {% render 'button',
          text:    block.settings.label,
          href:    block.settings.link,
          variant: block.settings.variant,
          attr:    block.fluid_attributes %}
    {%- endcase -%}
  {%- endfor -%}
</section>
```

When a block's content is fully delegated to a component, the standard pattern is to forward the attributes as a named argument (`attr: block.fluid_attributes`) and have the component apply them on its root element. See `sections/hero_section/index.liquid` in the reference theme and the `button` component for examples.

### Findings to surface

| You see                                                                                                                      | Severity                    | Fix                                                                                                                                                                                                                   |
| ---------------------------------------------------------------------------------------------------------------------------- | --------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Section file has no `{{ section.fluid_attributes }}` anywhere                                                                | `blocker`                   | Add it to the outer wrapper element of the section. Editor cannot select the section without it.                                                                                                                      |
| Section uses `{% for block in section.blocks %}` and the block's root element has no `{{ block.fluid_attributes }}`          | `blocker`                   | Each block's outer element must carry its own `block.fluid_attributes`. Without it the editor can't click-to-edit individual blocks.                                                                                  |
| Typo: `{{ section.fluid_attribute }}` (singular)                                                                             | `blocker`                   | The drop name is `fluid_attributes` (plural). The singular form renders empty.                                                                                                                                        |
| Typo: `{{ block.fluid_attr }}` / `{{ section.fluidAttributes }}` / `{{ section.fluid_attribute_set }}`                       | `blocker`                   | Only `fluid_attributes` exists.                                                                                                                                                                                       |
| Attributes applied on a child element instead of the root                                                                    | `blocker`                   | Move to the outermost element of the section/block. The editor walks ancestors looking for the closest match; placing it on a child means the editor picks up _that_ element as the section bounds, not the real one. |
| Same `{{ section.fluid_attributes }}` applied to multiple elements                                                           | `should`                    | Apply it once — to the root. Duplicates render the same `data-*` attributes twice in the DOM.                                                                                                                         |
| Hardcoded `data-fluid-*` attributes (`data-section-id="{{ section.id }}"`) instead of the helper                             | `blocker`                   | Replace with `{{ section.fluid_attributes }}` / `{{ block.fluid_attributes }}`. The helper emits a full attribute set; hand-rolling drops most of them.                                                               |
| Block-aware component (renders inside `{% for block %}`) has no `attr` parameter to receive `block.fluid_attributes`         | `should`                    | Add an `attr` argument to the component's signature and apply it on the component's root element.                                                                                                                     |
| Conditional render without protecting against `nil`: `<div {{ section.fluid_attributes }}>` where `section` may be undefined | `should` (rarely `blocker`) | Wrap: `{% if section %}{{ section.fluid_attributes }}{% endif %}`. Same for `block`. Only relevant where the value can legitimately be nil.                                                                           |

### Examples from the reference theme

Section root with attributes — `sections/main_product/index.liquid:49-51` in the reference fluid theme:

```liquid
<div
  class="MainProductBlock MainProductBlock--breadcrumb MainProductBlock--{{ block.id }}"
  {{ block.fluid_attributes }}
>
```

Block forwarding through to a component as `attr:` — `sections/hero_section/index.liquid:140-149` in the reference fluid theme:

```liquid
{%- if block.type == 'button' -%}
  {%- render 'button',
    text:    block.settings.text,
    href:    block.settings.link,
    variant: block.settings.variant | default: 'primary',
    size:    block.settings.size    | default: 'md',
    attr:    block.fluid_attributes
  -%}
```

Multiple blocks each carrying their own attrs — `sections/main_category/index.liquid:109,123,158` in the reference fluid theme:

```liquid
<div class="categories-page-header-copy" {% if header_block %}{{ header_block.fluid_attributes }}{% endif %}>
  <h2>{{ page_title }}</h2>
</div>

<div class="categories-page-view-all" {% if view_all_block %}{{ view_all_block.fluid_attributes }}{% endif %}>
  {% render 'button', ... %}
</div>

<div
  class="splide carousel"
  data-fluid-resource-slider
  {% if grid_block %}{{ grid_block.fluid_attributes }}{% endif %}
>
```

### Quick audit

From the theme repo root:

```bash
# Sections missing section.fluid_attributes entirely
for f in sections/*/index.liquid; do
  grep -q 'section\.fluid_attributes' "$f" || echo "MISSING section.fluid_attributes  $f"
done

# Sections that iterate blocks but never emit block.fluid_attributes
for f in sections/*/index.liquid; do
  iterates=$(grep -q 'for\s\+block\s\+in\s\+section\.blocks' "$f" && echo yes)
  emits=$(grep -q 'block\.fluid_attributes' "$f" && echo yes)
  if [ "$iterates" = "yes" ] && [ "$emits" != "yes" ]; then
    echo "MISSING block.fluid_attributes  $f"
  fi
done

# Common typos
grep -rE 'fluid_attribute[^s]|fluidAttributes|fluid_attribute_set' sections/ components/

# Hardcoded data-fluid-* attributes (likely should use the helper)
grep -rE 'data-fluid-section-id|data-fluid-section-block-id|data-fluid-parent-section-type' sections/ components/ \
  | grep -v 'fluid_attributes'
```

The last grep is the one to actually open a PR comment on — any hit is a hand-rolled subset of what the helper would emit.

---
