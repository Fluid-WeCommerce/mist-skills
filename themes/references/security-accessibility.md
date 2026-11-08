# Security & accessibility

> Part of the `themes-review` skill. See [`../SKILL.md`](../SKILL.md) for the review workflow, severity ladder, and validator rules.

## Contents

- 1. Unescaped user content
- 2. Raw output of URLs in `href` / `src`
- 3. Comments with secrets
- 1. Missing `alt` on images
- 2. Heading hierarchy
- 3. Button vs link semantics
- 4. `decoding="async"` and `loading="lazy"`


### 1. Unescaped user content

**`blocker`.** Escape plain strings: resource fields such as `product.title`, comments, `plaintext` settings, and global `settings.<id>` values of type `text` (the Theme panel renders `text` as a plain input).

```liquid
<h2>{{ product.title | escape }}</h2>
<input placeholder="{{ section.settings.email_placeholder | escape }}">  {%- comment -%} plaintext setting {%- endcomment -%}
```

Do **not** escape the HTML-shaped **section and block** setting types: `text`, `textarea`, `richtext` / `rich_text`, and `html` / `html_textarea`. In section and block schemas, `text` and `textarea` are rich-text editors — they save HTML such as `Free delivery on <strong>every</strong> order` — so `| escape` shows merchants `&lt;strong&gt;`. Render them raw, in element content only. A section or block value that must go into an attribute, a CSS value, a URL, or a script needs a `plaintext` setting instead; flag `text`/`textarea` in those positions as a `blocker`.

Global settings from `config/settings_schema.json` are different: the Theme panel renders `text` as a plain input and `textarea` as rich text, and offers no `plaintext`. Escape a global `text` value (`{{ settings.announcement | escape }}`); render a global `textarea` raw.

### 2. Raw output of URLs in `href` / `src`

**`should`.** Escape:

```liquid
<a href="{{ section.settings.link_url | escape }}">Link</a>
```

### 3. Comments with secrets

**`should`.** `{% comment %}` blocks are not rendered, but they _are_ shipped to clients if the theme source is exposed (CDN, git). Don't paste tokens or internal URLs in comments.

---

## Accessibility

`should` by default. Bump to `blocker` if the section is the storefront homepage or checkout flow.

### 1. Missing `alt` on images

Render the image with `| media_tag` (see [Media rendering](https://docs.fluid.app/themes/media-tag)) and pass `alt`:

```liquid
{%- comment -%} Bad: the picker value is a bare URL, so this ships alt-less {%- endcomment -%}
{{ section.settings.image | media_tag }}

{%- comment -%} Good: the editor stores alt text in the `<id>_alt` companion setting {%- endcomment -%}
{{ section.settings.image | media_tag: alt: section.settings.image_alt }}
```

Every `image_picker`, `video_picker`, and `media_picker` gets an editor-managed `<id>_alt` setting that merchants fill in next to the picker; don't declare it, read it. Don't reuse a heading as alt text — a `text` heading is HTML. `media_tag` takes `alt` from an image value that carries one (an entry in `product.images`, for example); picker values carry none. Decorative images: `alt: ''`.

### 2. Heading hierarchy

A section shouldn't skip from `h1` to `h4`. Make heading tag a setting and default sensibly (`h2` for section titles, `h3` for cards).

### 3. Button vs link semantics

A clickable `<div>` is `blocker`. Use `<button>` for actions, `<a href>` for navigation.

### 4. `decoding="async"` and `loading="lazy"`

`| media_tag` applies `decoding="async"` and `loading="lazy"` for you — don't hand-roll them. For hero/above-the-fold images pass `loading: 'eager'`, since lazy loading there delays LCP:

```liquid
{{ section.settings.hero | media_tag: loading: 'eager', alt: section.settings.hero_alt }}
```

---
