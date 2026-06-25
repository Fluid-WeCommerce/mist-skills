# Dynamism — settings over hardcoded values

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- What "hardcoded" looks like
- What dynamic looks like
- Findings to surface
- When _not_ to make something a setting


The point of a theme is that the _company_ can edit it without touching code. Anything user-visible that's hardcoded into Liquid is a missed setting. The reviewer should be relentless here: every literal string, color, image URL, link, count, or toggle in markup is a candidate.

**The principle:** if a company employee, designer, or marketer might ever want to change it, it belongs in `{% schema %}`.

### What "hardcoded" looks like

```liquid
{%- comment -%} Bad: every value here is locked in code {%- endcomment -%}
<section style="background:#0a0a0a;padding:64px 0;">
  <h2 style="font-size:48px;color:white;">Our Bestsellers</h2>
  <p>Browse this season's most popular picks.</p>
  <img src="https://cdn.example.com/static/banner.jpg" alt="Banner" />
  <a href="/shop?sort=popular" class="btn">Shop now</a>
</section>
```

Every one of those values — background, padding, heading text, body text, image, button text, button link — is a hardcoded decision the company can never override without a code change.

### What dynamic looks like

```json
{% schema %}
{
  "name": "Bestsellers Banner",
  "settings": [
    { "type": "text",             "id": "heading",       "label": "Heading",         "default": "Our Bestsellers" },
    { "type": "textarea",         "id": "body",          "label": "Body text",       "default": "Browse this season's most popular picks." },
    { "type": "image_picker",     "id": "banner_image",  "label": "Banner image" },
    { "type": "color_background", "id": "bg_color",      "label": "Background",      "default": "#0a0a0a" },
    { "type": "color",            "id": "text_color",    "label": "Text color",      "default": "#ffffff" },
    { "type": "padding",          "id": "section_pad",   "label": "Section padding" },
    { "type": "text",             "id": "cta_label",     "label": "Button label",    "default": "Shop now" },
    { "type": "url",              "id": "cta_url",       "label": "Button link",     "default": "/shop?sort=popular" },
    { "type": "checkbox",         "id": "show_cta",      "label": "Show button",     "default": true }
  ]
}
{% endschema %}
```

```liquid
{%- assign s = section.settings -%}
<section style="background:{{ s.bg_color }};padding:{{ s.section_pad }};">
  <h2 style="color:{{ s.text_color }};">{{ s.heading | default: 'Our Bestsellers' }}</h2>
  <p>{{ s.body }}</p>
  {%- if s.banner_image != blank -%}
    <img src="{{ s.banner_image }}" alt="{{ s.heading | escape }}" />
  {%- endif -%}
  {%- if s.show_cta -%}
    <a href="{{ s.cta_url }}" class="btn">{{ s.cta_label }}</a>
  {%- endif -%}
</section>
```

### Findings to surface

| You see                                                                | Severity                                        | Why                                                                                               |
| ---------------------------------------------------------------------- | ----------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| User-visible literal text in markup (heading, paragraph, button label) | `should`                                        | Should be a `text` / `textarea` / `richtext` setting.                                             |
| Hardcoded colors (`#0a0a0a`, `rgb(...)`, `red`) in style/attribute     | `should`                                        | Should be a `color` or `color_background` setting.                                                |
| Hardcoded image URL (external CDN, hardcoded path)                     | `blocker` if external CDN, `should` if internal | External CDNs can break, get blocked, or change. Upload to `assets/` or expose as `image_picker`. |
| Hardcoded `href` to a fixed page or `?sort=popular`-style URL          | `should`                                        | Use a `url` setting.                                                                              |
| Hardcoded counts (`limit: 6`, `limit: 12`) in `for` loops              | `nit` → `should`                                | Expose as a `range` setting if the company might want to change density.                          |
| Boolean branches with no user toggle (`{% if true %}`)                 | `should`                                        | Either delete or expose as a `checkbox`.                                                          |
| Tailwind class strings that bake in color (`bg-black text-white`)      | `should`                                        | Use CSS variables driven by `color` settings.                                                     |

### When _not_ to make something a setting

Adding settings has a real cost — they clutter the editor and shift the burden to non-technical users. Skip settings for:

- Internal layout primitives (grid gaps, micro-margins) the design system already controls
- Engineering plumbing (data attributes, schema markup hooks)
- Values that _must_ stay in lockstep with code (icon class names, route slugs the theme relies on)

The test: _would I expect a non-developer to want to change this?_ No → leave it hardcoded. Yes → make it a setting.

---
