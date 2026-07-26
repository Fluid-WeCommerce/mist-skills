# Canonical Fluid section template

Use a section already shipped by the current base theme whenever it fits. This template is
only for a source section that has no canonical equivalent.

The non-negotiable contract is:

- Section settings describe layout, never visible copy.
- The Section Shell has 6 controls and the Container has 9 controls.
- Visible copy and content images are blocks.
- Text blocks use `richtext`; content images use the canonical `image` block shape.
- Every color and font choice resolves through the theme option groups.
- Breakpoints are `max-width: 991px` and `max-width: 767px`.
- The root emits `section.fluid_attributes`; block wrappers emit `block.fluid_attributes`.
- Template schemas carry section types, order, and optional section settings only. They
  never carry block instances.

## Minimal implementation

```liquid
{%- style -%}
  .source-feature.section-{{ section.id }} {
    {%- assign p = section.settings.section_padding -%}
    {%- if p -%}
      padding: {{ p.top | default: 80 }}px {{ p.right | default: 0 }}px {{ p.bottom | default: 80 }}px {{ p.left | default: 0 }}px;
    {%- else -%}
      padding: 80px 0;
    {%- endif -%}
    {%- assign r = section.settings.section_border_radius -%}
    {%- if r -%}
      border-radius: {{ r.tl }}px {{ r.tr }}px {{ r.br }}px {{ r.bl }}px;
    {%- endif -%}
    background-color: {{ section.settings.background_color | default: 'transparent' }};
    {%- if section.settings.background_image != blank -%}
      background-image: url({{ section.settings.background_image | img_url: 'w-2400,f-auto,q-80' }});
      background-position: center;
      background-repeat: no-repeat;
      background-size: cover;
    {%- endif -%}
    {% if section.settings.section_border_width > 0 %}
      border: {{ section.settings.section_border_width }}px solid {{ section.settings.section_border_color }};
    {% endif %}
  }

  .source-feature.section-{{ section.id }} .source-feature__container {
    position: relative;
    max-width: {{ section.settings.container_max_width | default: '1280px' }};
    margin: 0 auto;
    {%- assign cp = section.settings.container_padding -%}
    {%- if cp -%}
      padding: {{ cp.top | default: 0 }}px {{ cp.right | default: 64 }}px {{ cp.bottom | default: 0 }}px {{ cp.left | default: 64 }}px;
    {%- else -%}
      padding: 0 64px;
    {%- endif -%}
    {%- assign cr = section.settings.container_border_radius -%}
    {%- if cr -%}
      border-radius: {{ cr.tl }}px {{ cr.tr }}px {{ cr.br }}px {{ cr.bl }}px;
    {%- endif -%}
    background-color: {{ section.settings.container_background_color | default: 'transparent' }};
    {%- if section.settings.container_background_image != blank -%}
      background-image: url({{ section.settings.container_background_image | img_url: 'w-2400,f-auto,q-80' }});
      background-position: center;
      background-repeat: no-repeat;
      background-size: cover;
    {%- endif -%}
    {% if section.settings.container_border_width > 0 %}
      border: {{ section.settings.container_border_width }}px solid {{ section.settings.container_border_color }};
    {% endif %}
  }

  {%- if section.settings.container_overlay_color != blank and section.settings.container_overlay_opacity > 0 -%}
    {%- assign overlay_opacity = section.settings.container_overlay_opacity | divided_by: 100.0 -%}
    .source-feature.section-{{ section.id }} .source-feature__container::before {
      content: "";
      position: absolute;
      inset: 0;
      background: {{ section.settings.container_overlay_color }};
      opacity: {{ overlay_opacity }};
      pointer-events: none;
    }
  {%- endif -%}

  .source-feature.section-{{ section.id }} .source-feature__container > * {
    position: relative;
  }

  .source-feature.section-{{ section.id }} .source-feature__content {
    display: grid;
    grid-template-columns: minmax(0, 1fr) minmax(0, 1fr);
    gap: 48px;
    align-items: center;
  }

  .source-feature.section-{{ section.id }} .rte h1,
  .source-feature.section-{{ section.id }} .rte h2,
  .source-feature.section-{{ section.id }} .rte h3 {
    font-family: var(--ff-heading);
  }

  @media (max-width: 991px) {
    .source-feature.section-{{ section.id }} .source-feature__container {
      padding-right: 24px;
      padding-left: 24px;
    }
  }

  @media (max-width: 767px) {
    .source-feature.section-{{ section.id }} .source-feature__container {
      padding-right: 16px;
      padding-left: 16px;
    }

    .source-feature.section-{{ section.id }} .source-feature__content {
      grid-template-columns: 1fr;
      gap: 24px;
    }
  }
{%- endstyle -%}

<section
  class="source-feature section-{{ section.id }}"
  data-section-id="{{ section.id }}"
  {{ section.fluid_attributes }}
>
  <div class="source-feature__container">
    <div class="source-feature__content">
      {% for block in section.blocks %}
        {% case block.type %}
          {% when 'copy' %}
            <div class="source-feature__copy rte" {{ block.fluid_attributes }}>
              {{ block.settings.heading }}
              {{ block.settings.text }}
            </div>
          {% when 'image' %}
            <div class="source-feature__image" {{ block.fluid_attributes }}>
              {% if block.settings.image %}
                <img
                  src="{{ block.settings.image | img_url: 'w-1600,f-auto,q-80' }}"
                  alt="{{ block.settings.alt_text | escape }}"
                  loading="lazy"
                  width="1600"
                  height="1200"
                >
              {% else %}
                <div class="source-feature__image-placeholder" aria-hidden="true"></div>
              {% endif %}
            </div>
        {% endcase %}
      {% endfor %}
    </div>
  </div>
</section>

{% schema %}
{
  "name": "Source feature",
  "settings": [
    { "type": "header", "content": "Section Shell" },
    { "type": "padding", "id": "section_padding", "label": "Section Padding" },
    { "type": "corner_radius", "id": "section_border_radius", "label": "Section Border Radius" },
    {
      "type": "select",
      "id": "background_color",
      "label": "Background Color",
      "options": "background_colors",
      "default": "transparent"
    },
    {
      "type": "image_picker",
      "id": "background_image",
      "label": "Background Image",
      "info": "Decorative section background only."
    },
    {
      "type": "range",
      "id": "section_border_width",
      "label": "Section Border Width",
      "min": 0,
      "max": 10,
      "step": 1,
      "default": 0,
      "unit": "px"
    },
    {
      "type": "select",
      "id": "section_border_color",
      "label": "Section Border Color",
      "options": "background_colors",
      "default": "var(--clr-primary)"
    },
    { "type": "header", "content": "Container" },
    {
      "type": "select",
      "id": "container_max_width",
      "label": "Max Width",
      "default": "1280px",
      "options": [
        { "value": "720px", "label": "Extra narrow (720px)" },
        { "value": "960px", "label": "Narrow (960px)" },
        { "value": "1080px", "label": "Comfy (1080px)" },
        { "value": "1280px", "label": "Default (1280px)" },
        { "value": "1440px", "label": "Wide (1440px)" },
        { "value": "100%", "label": "Full (100%)" }
      ]
    },
    { "type": "padding", "id": "container_padding", "label": "Container Padding" },
    { "type": "corner_radius", "id": "container_border_radius", "label": "Container Border Radius" },
    {
      "type": "select",
      "id": "container_background_color",
      "label": "Container Background Color",
      "options": "background_colors",
      "default": "transparent"
    },
    { "type": "image_picker", "id": "container_background_image", "label": "Container Background Image" },
    {
      "type": "select",
      "id": "container_overlay_color",
      "label": "Container Overlay Color",
      "options": "background_colors",
      "default": "transparent"
    },
    {
      "type": "range",
      "id": "container_overlay_opacity",
      "label": "Container Overlay Opacity",
      "min": 0,
      "max": 100,
      "step": 5,
      "default": 0,
      "unit": "%"
    },
    {
      "type": "range",
      "id": "container_border_width",
      "label": "Container Border Width",
      "min": 0,
      "max": 10,
      "step": 1,
      "default": 0,
      "unit": "px"
    },
    {
      "type": "select",
      "id": "container_border_color",
      "label": "Container Border Color",
      "options": "background_colors",
      "default": "var(--clr-primary)"
    }
  ],
  "blocks": [
    {
      "type": "copy",
      "name": "Copy",
      "settings": [
        {
          "type": "richtext",
          "id": "heading",
          "label": "Heading",
          "default": "<h2>Source heading</h2>"
        },
        {
          "type": "richtext",
          "id": "text",
          "label": "Text",
          "default": "<p>Source body copy.</p>"
        }
      ]
    },
    {
      "type": "image",
      "name": "Image",
      "limit": 1,
      "settings": [
        { "type": "image_picker", "id": "image", "label": "Image" },
        { "type": "text", "id": "alt_text", "label": "Alt Text" }
      ]
    }
  ],
  "presets": [
    {
      "name": "Source feature",
      "blocks": [
        { "type": "copy" },
        { "type": "image" }
      ]
    }
  ]
}
{% endschema %}
```

The shortened image schema above demonstrates placement only. In a real section, copy the
complete canonical image block settings from `blocks/image/index.liquid` in the scaffold so
aspect ratio, fit, position, overlay, border, and radius controls remain available.

## Before using the section

Run:

```bash
python3 <THEME_AUDIT_PATH> sections/source_feature/index.liquid
```

Do not push until it exits zero. If the source pattern can be expressed by an existing base
theme section, use that canonical section and delete this custom one.
