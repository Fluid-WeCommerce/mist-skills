# Blocks vs. sections

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- The rule — blocks first
- Standalone blocks over inline blocks
- Threshold
- Bad — settings-panel wall of fields
- Good — block per feature
- Benefits the reviewer should cite when suggesting the fix
- When sections-with-many-fields _is_ the right answer


Fluid themes are **blocks-first**: a section is a layout shell, and its *content* lives in blocks. A section that bundles every piece of content into one giant `settings: [...]` array becomes a wall of fields the merchant can't navigate, can't reorder, and can't extend without a developer.

### The rule — blocks first

- **Block settings** hold **content** — anything a merchant might add, remove, reorder, or repeat: headings, paragraphs, images, buttons/CTAs, cards, FAQs, features, logos. Model content as blocks **even when there is only one today.** "There's just one heading" is not a reason to make it a section setting — a merchant who later wants a second heading, wants to drop the image, or wants the CTA above the text should do it in the editor, not in a PR.
- **Section settings** hold only **true whole-section configuration**: width, background, padding, column count, vertical alignment — values that are singular for the whole section by nature and that a merchant would never duplicate or reorder.

That split is the whole point: the **section** carries only a handful of settings (its whole-section config), while every **element-specific** setting lives on the block it belongs to. The section panel stays short and scannable, and each setting sits next to the element it controls.

**Litmus test:** _"Could a merchant reasonably want two of these, none of these, or these in a different order?"_ If yes → block. If it is genuinely one-per-section plumbing → section setting.

`setting_a_1` / `setting_a_2` / `setting_a_3` (or `show_card_1` / `show_card_2`) is the obvious failure mode — but the blocks-first bar is higher: reach for blocks _before_ the duplication ever appears.

### Standalone blocks over inline blocks

Once content is a block, prefer a **standalone block** — `blocks/{name}/index.liquid`, referenced from the section's `"blocks"` array via `@theme` or a named-block reference (`{ "type": "<name>" }`) — over an **inline block** defined inside the section's `{% schema %}`.

- **Default to standalone.** It is reusable across sections, testable on its own, keeps the section schema small, and is how Fluid themes are meant to be composed.
- **Inline blocks only when the block is very small** (a couple of settings, a few lines of markup) **and** clearly specific to one section. If there's any chance of reuse, go standalone.
- Extracting an inline block into `blocks/` is always a valid, encouraged fix; never flag the reverse.

| You see                                                                                                          | Severity | Fix                                                          |
| ---------------------------------------------------------------------------------------------------------------- | -------- | ------------------------------------------------------------ |
| Section content (a heading / text / image / CTA a merchant would add, remove, or reorder) modeled as fixed section settings | `should` | Model it as a block.                                         |
| A non-trivial inline block (many settings or substantial markup) defined inside a section schema                 | `should` | Extract to a standalone `blocks/{name}/index.liquid` and reference it. |
| The same inline block duplicated across 2+ sections                                                              | `should` | Extract to one standalone `blocks/{name}/`.                  |
| A tiny, genuinely one-off inline block                                                                           | `nit`    | Acceptable; suggest standalone only if reuse is likely.      |

### Threshold

**`should`** when:

- A section has **more than ~15 top-level settings**, _and_ any of them look like variations of the same thing
- A section has 2+ pairs of settings of the form `X_1` / `X_2`
- A section has a fixed N copies of "card", "feature", "tile", "testimonial", "FAQ", "logo" — anything that semantically wants to be a list

### Bad — settings-panel wall of fields

```json
{% schema %}
{
  "name": "Three Features",
  "settings": [
    { "type": "image_picker", "id": "feat_1_icon",  "label": "Feature 1 icon" },
    { "type": "text",         "id": "feat_1_title", "label": "Feature 1 title" },
    { "type": "textarea",     "id": "feat_1_body",  "label": "Feature 1 body" },
    { "type": "image_picker", "id": "feat_2_icon",  "label": "Feature 2 icon" },
    { "type": "text",         "id": "feat_2_title", "label": "Feature 2 title" },
    { "type": "textarea",     "id": "feat_2_body",  "label": "Feature 2 body" },
    { "type": "image_picker", "id": "feat_3_icon",  "label": "Feature 3 icon" },
    { "type": "text",         "id": "feat_3_title", "label": "Feature 3 title" },
    { "type": "textarea",     "id": "feat_3_body",  "label": "Feature 3 body" }
  ]
}
{% endschema %}
```

### Good — block per feature

```json
{% schema %}
{
  "name": "Features",
  "settings": [
    { "type": "text",    "id": "heading", "label": "Section heading", "default": "Why us" },
    { "type": "select",  "id": "columns", "label": "Columns",
      "options": [{ "value": "2", "label": "2" }, { "value": "3", "label": "3" }, { "value": "4", "label": "4" }],
      "default": "3" }
  ],
  "blocks": [
    {
      "type": "feature",
      "name": "Feature",
      "settings": [
        { "type": "image_picker", "id": "icon",  "label": "Icon" },
        { "type": "text",         "id": "title", "label": "Title" },
        { "type": "textarea",     "id": "body",  "label": "Description" }
      ]
    }
  ]
}
{% endschema %}
```

Rendering:

```liquid
<div class="features features--cols-{{ section.settings.columns }}">
  {%- for block in section.blocks -%}
    <article class="feature" {{ block.fluid_attributes }}>
      {%- if block.settings.icon != blank -%}
        <img src="{{ block.settings.icon }}" alt="{{ block.settings.title | escape }}" />
      {%- endif -%}
      <h3>{{ block.settings.title }}</h3>
      <p>{{ block.settings.body }}</p>
    </article>
  {%- endfor -%}
</div>
```

**Prefer this as a standalone block.** Define `feature` at `blocks/feature/index.liquid` and reference it from the section's `"blocks"` array (`{ "type": "feature" }`) instead of inlining it — see [Standalone blocks over inline blocks](#standalone-blocks-over-inline-blocks). (A stricter blocks-first read would make `heading` a block too; it's kept as a section setting here only for brevity.)

### Benefits the reviewer should cite when suggesting the fix

- **Editor UX:** Each block shows up as a collapsible item with its own fields — far easier to scan than a 27-field wall.
- **Drag-and-drop reorder for free.**
- **Add/remove without code changes:** users can add a 4th feature without a developer.
- **Per-block dropzone hooks:** `{{ block.fluid_attributes }}` gives the editor click-to-edit on each one.
- **`limit:` on the block** (optional) enforces a max count without baking it into Liquid.
- **Reusable across sections** when defined standalone (`blocks/{name}/index.liquid`) instead of inline.

### When sections-with-many-fields _is_ the right answer

Some sections genuinely have many settings that _all_ apply to the whole section — e.g. a configuration-heavy hero with background, overlay, video poster, mobile alt, autoplay, mute, etc. That's fine: those are whole-section **config**, not content. The test isn't field count — it's whether each field is one-per-section plumbing (section setting) or a piece of content a merchant would add / remove / reorder (block).

---
