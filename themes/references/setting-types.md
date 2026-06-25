# Setting types — the engine contract

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- Input
- Number & selection
- Visual & media
- Layout
- Organization
- Resource — single
- Resource — list (multiple)
- Common type mistakes — find and fix


These are the canonical setting types. **Any `type:` value not in this list is rejected by the validator** (`fluid theme lint --json`).

### Input

| `type`          | Stores      | Notes                                                     |
| --------------- | ----------- | --------------------------------------------------------- |
| `text`          | string      | Single-line.                                              |
| `plaintext`     | string      | Single-line, no formatting allowed.                       |
| `textarea`      | string      | Multi-line, no formatting.                                |
| `richtext`      | HTML string | WYSIWYG. **Render with `{{ value }}` — do not `escape`.** |
| `rich_text`     | HTML string | Alias for `richtext`. Prefer `richtext`.                  |
| `html`          | HTML string | Raw HTML editor. Same render rule as `richtext`.          |
| `html_textarea` | HTML string | Multi-line raw HTML. Same render rule.                    |
| `url`           | string      | Validated URL input.                                      |

### Number & selection

| `type`     | Required extras                       | Notes                                                           |
| ---------- | ------------------------------------- | --------------------------------------------------------------- |
| `range`    | `min`, `max`, `step`                  | Slider. Optional `unit`.                                        |
| `number`   | —                                     | Free numeric input (no slider). Prefer `range` when bounded.    |
| `select`   | `options` array of `{ value, label }` | Dropdown.                                                       |
| `radio`    | `options` array of `{ value, label }` | Radio group.                                                    |
| `checkbox` | —                                     | Boolean. **Always set `default:`** so the value is never `nil`. |

### Visual & media

| `type`             | Notes                                                             |
| ------------------ | ----------------------------------------------------------------- |
| `color`            | Single color picker.                                              |
| `color_background` | Same as `color`, semantic name for fills.                         |
| `font`             | Font family.                                                      |
| `font_picker`      | Font family with Google Fonts + system fonts.                     |
| `image`            | Single image.                                                     |
| `image_picker`     | Single image. Prefer `image_picker` in new code (clearer intent). |
| `video_picker`     | Single video.                                                     |
| `media_picker`     | Image **or** video — use when both are acceptable.                |
| `text_alignment`   | left / center / right control.                                    |

### Layout

| `type`             | Notes                           |
| ------------------ | ------------------------------- |
| `media_fit`        | cover / contain / fill control. |
| `corner_radius`    | Border-radius preset.           |
| `padding`          | Padding scale picker.           |
| `border`           | Border preset.                  |
| `gradient_overlay` | Gradient editor for overlays.   |

### Organization

| `type`   | Notes                                                 |
| -------- | ----------------------------------------------------- |
| `header` | Settings-panel divider. No `id`. Requires `content:`. |

### Resource — single

These pick **one** resource. Settings hold the resource object/ID.

`product`, `collection`, `category`, `blog`, `post`, `enrollment`, `enrollment_pack`, `variant`, `forms`, `media`, `link_list`

> **Naming oddity:** `products`, `collections`, `categories`, `posts`, `enrollments` also exist in the _single_ bucket of the canonical list. Read this as **legacy aliases**. Always pair "I want multiple resources" with the `_list` types below — that is the unambiguous, list-shaped contract.

### Resource — list (multiple)

These pick **many** resources, stored as arrays. Always require `limit:`.

`product_list`, `products_list`, `collection_list`, `collections_list`, `category_list`, `categories_list`, `posts_list`, `enrollment_list`, `enrollments_list`, `blog_list`, `blogs_list`, `post_list`, `enrollment_packs_list`

**Canonical names to prefer in new code:**

| Resource                | Use                     |
| ----------------------- | ----------------------- |
| Products (many)         | `product_list`          |
| Collections (many)      | `collection_list`       |
| Categories (many)       | `category_list`         |
| Posts (many)            | `posts_list`            |
| Enrollments (many)      | `enrollment_list`       |
| Enrollment packs (many) | `enrollment_packs_list` |
| Blogs (many)            | `blog_list`             |

The `*s_list` variants (`products_list`, `collections_list`, etc.) exist but are duplicative — flag them as a `nit` and suggest the canonical `*_list` form.

### Common type mistakes — find and fix

| You see                                                   | What you do                                                                                               |
| --------------------------------------------------------- | --------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| `type: "text_area"`                                       | **`blocker`.** Use `textarea` (one word).                                                                 |
| `type: "checkBox"` / `"image_pick"`                       | **`blocker`.** Mistyped — replace with the exact value from the lists above.                              |
| `type: "product_list"` without `"limit":`                 | **`should`** — the field saves but has no defined cap. Always set `limit:`.                               |
| `type: "range"` without `min`/`max`/`step`                | **`blocker`.** Slider UI breaks.                                                                          |
| `type: "select"` or `"radio"` without `options:`          | **`blocker`.** Empty dropdown / radio group.                                                              |
| `type: "checkbox"` without `default:`                     | **`should`.** Truthiness is ambiguous on first render. Set `default: false` (or `true`).                  |
| `type: "richtext"` rendered as `{{ value                  | escape }}`                                                                                                | **`blocker`.** Double-escapes HTML — users see `&lt;p&gt;`. Render raw: `{{ value }}`. |
| Setting missing `id` / duplicate `id`                     | **`blocker`.** The validator will reject.                                                                 |
| Block missing `type` or `name`                            | **`blocker`.** Validator rejects. (`name` may be omitted only for `@app`, `@theme`, or named-block refs.) |
| `"settings": { ... }` inside a block (object, not array)  | **`blocker`.** Validator rejects — must be an array.                                                      |
| `{% section 'foo' %}` with no `sections/foo/index.liquid` | **`blocker`.** Validator rejects.                                                                         |
| 2+ singular `product` settings playing the same role      | **`should`.** Collapse to one `product_list`. See [next section](#selector-heuristic--singular--list).    |
| `products_list` instead of `product_list`                 | **`nit`.** Both valid; prefer `product_list`.                                                             |

---
