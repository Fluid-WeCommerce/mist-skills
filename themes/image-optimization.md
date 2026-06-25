---
name: optimizing-theme-images
description: Use when building or editing Fluid Liquid themes and adding or optimizing images served from ImageKit — writing <img> markup, responsive srcset/sizes, lazy loading, preventing layout shift, or appending ImageKit ?tr= transformation params (w-, q-, f-auto, dpr-) to image URLs.
---

# Optimizing Theme Images (Fluid + ImageKit)

## Overview

Fluid themes are **Liquid**, and Fluid serves images through **ImageKit**. Unlike Shopify, Fluid has **no built-in image-transformation filter** — the theme filters (`asset_url`, `img_url`, `image_tag`) return a plain URL and do **not** resize, reformat, or generate `srcset`. (`img_url`/`image_url` even accept a `size`/options argument, but it is **ignored** — do not rely on it.)

So optimization in a Fluid theme is two manual jobs, and this skill covers both:

- **A. Build the ImageKit URL** — append `?tr=` transformation params to request the right size, format, and quality.
- **B. Write the `<img>` yourself** — add `width`/`height`, `loading`, `decoding`, and a responsive `srcset`/`sizes`.

**Core principle:** Never ship a raw, full-size image URL into a fixed-size container. Request the display size from ImageKit, let the browser pick the right one, and reserve the space so the page doesn't jump.

## What Fluid gives you (quick reference)

| You have | How | Notes |
|---|---|---|
| Theme asset URL | `{{ 'banner.jpg' \| asset_url }}` | May be a Fluid-hosted URL that redirects to ImageKit — see Caveats |
| Image URL from a product/media object | `{{ image.src }}` (or `{{ image.url }}`) | Served by ImageKit for DAM/product images |
| Width / height (px) | `{{ image.width }}` / `{{ image.height }}` | Use to set attributes + prevent layout shift |
| Aspect ratio | `{{ image.aspect_ratio }}` | Use for CSS `aspect-ratio` |
| Alt text | `{{ image.alt }}` | Always output it |
| Basic `<img>` | `{{ image.src \| image_tag: alt: image.alt }}` | ⚠️ emits no `width`/`height`/`srcset`/`loading` — hand-write for anything important |
| Transform / resize / srcset | ❌ none | Build the `?tr=` URL and `<img>` manually (this skill) |

## A. ImageKit URL parameters

Append a transformation as a query string: `?tr=key-value,key-value`. Chain params with commas.

| Param | Use | Recommended |
|---|---|---|
| `f-auto` | Auto-pick WebP/AVIF/JPEG per browser | Always include |
| `q-80` | Quality (1–100) | `q-80` for photos; `q-100` only for archival |
| `w-` / `h-` | Resize to display size | Match the rendered container, not the source |
| `c-` / `fo-auto` | Crop mode / smart focus | `fo-auto` (or `fo-face`) for cropped thumbnails |
| `dpr-2` | Retina density | Cap at `2` — `dpr-3` is imperceptible and heavier |
| `pr-true` | Progressive render | Large hero JPEGs |
| `bl-` | Blur (low-quality placeholder) | Tiny `w-` + `bl-` for LQIP |

Canonical full URL:
```
https://ik.imagekit.io/<id>/path/image.jpg?tr=w-800,f-auto,q-80
```
ImageKit already auto-optimizes format and quality by default, but stating `f-auto,q-80` explicitly is clearer and safe. **Resize is the biggest win** — serving a 2000px image into a 400px slot wastes most of the bytes.

## B. The Liquid — one good responsive image

Fluid has no `srcset` helper, so build it with a reusable snippet. Drop this in `snippets/responsive_image.liquid` and `{% render %}` it:

```liquid
{%- comment -%}
  responsive_image.liquid
  params: image (object), sizes (string), loading ('lazy'|'eager'), class
{%- endcomment -%}
{%- assign base = image.src -%}
<img
  src="{{ base }}?tr=w-800,f-auto,q-80"
  srcset="{{ base }}?tr=w-400,f-auto,q-80 400w,
          {{ base }}?tr=w-800,f-auto,q-80 800w,
          {{ base }}?tr=w-1200,f-auto,q-80 1200w"
  sizes="{{ sizes | default: '(max-width: 768px) 100vw, 800px' }}"
  width="{{ image.width }}"
  height="{{ image.height }}"
  alt="{{ image.alt | escape }}"
  loading="{{ loading | default: 'lazy' }}"
  decoding="async"
  class="{{ class }}" />
```

Use it:
```liquid
{% render 'responsive_image', image: product.featured_media,
   sizes: '(max-width: 768px) 100vw, 600px', class: 'product-hero' %}
```

**Hero / LCP image** (above the fold) — load it eagerly and prioritize it; never lazy-load your Largest Contentful Paint image:
```liquid
{% render 'responsive_image', image: section.banner, loading: 'eager' %}
{%- comment -%} also add fetchpriority="high" to the <img> for the single LCP image {%- endcomment -%}
```

**Theme asset image** (decorative/static):
```liquid
<img src="{{ 'badge.png' | asset_url }}?tr=w-120,f-auto,q-80"
     width="120" height="120" alt="" loading="lazy" decoding="async">
```

## Best-practice checklist

- [ ] `f-auto` and `q-80` on every ImageKit URL.
- [ ] `w-` sized to the **rendered** width (×2 for the retina entry in `srcset`).
- [ ] `srcset` with ~3 widths (e.g. 400/800/1200) + a real `sizes` value. Don't over-fragment — too many widths hurt CDN cache hits.
- [ ] `width` + `height` (from `image.width`/`image.height`) or CSS `aspect-ratio` on every `<img>` to prevent layout shift.
- [ ] `loading="lazy"` + `decoding="async"` for below-the-fold; `loading="eager"` + `fetchpriority="high"` for the hero/LCP image only.
- [ ] `alt` from `image.alt` (empty `alt=""` for purely decorative).

## Common mistakes

| Mistake | Fix |
|---|---|
| Outputting `{{ image.src }}` raw into a small container | Append `?tr=w-<displaywidth>,f-auto,q-80` |
| Relying on `img_url: '400x400'` to resize | That size arg is **ignored** in Fluid — use `?tr=` |
| Expecting `image_tag` to add `srcset`/`loading` | It doesn't — hand-write the `<img>` or use the snippet |
| No `width`/`height` → page jumps as images load | Always set them (or `aspect-ratio`) |
| Lazy-loading the hero image | Hero/LCP = `eager` + `fetchpriority="high"` |
| `dpr-3` or 6 srcset widths "to be safe" | Cap DPR at 2; keep ~3 widths for cache efficiency |

## Fluid caveats (verify before relying on them)

- **`?tr=` only works when the URL is actually served by ImageKit.** Product/media/DAM image URLs are ImageKit-served. `asset_url` may return a **Fluid-hosted URL that redirects to ImageKit** — confirm the `?tr=` params survive the redirect for theme assets before depending on it; if not, transform on the image object's `src` instead.
- Fluid does not expose ImageKit named/chained transformations to themes today — build params inline.
- There is no theme helper that emits `srcset`; the snippet above is the supported pattern.
