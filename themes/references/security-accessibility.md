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

**`blocker`.** Any string that originated from a user (product title, comment, custom heading) outside of a `richtext`/`html`/`html_textarea` field must be escaped. Default to `| escape` for any string field. The only exception is the HTML-shaped types — those are HTML by design.

```liquid
<h2>{{ product.title | escape }}</h2>
```

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

```liquid
{%- comment -%} Bad {%- endcomment -%}
<img src="{{ product.featured_image }}" />

{%- comment -%} Good {%- endcomment -%}
<img src="{{ product.featured_image }}" alt="{{ product.title | escape }}" />
```

Decorative images: `alt=""`.

### 2. Heading hierarchy

A section shouldn't skip from `h1` to `h4`. Make heading tag a setting and default sensibly (`h2` for section titles, `h3` for cards).

### 3. Button vs link semantics

A clickable `<div>` is `blocker`. Use `<button>` for actions, `<a href>` for navigation.

### 4. `decoding="async"` and `loading="lazy"`

```liquid
<img src="..." alt="..." loading="lazy" decoding="async" />
```

Don't set `loading="lazy"` on hero/above-the-fold images — it delays LCP.

---
