---
name: optimizing-theme-images
description: Use when building or editing Fluid Liquid themes and adding or optimizing images or videos — writing responsive markup, srcset/sizes, lazy loading, preventing layout shift, or applying ImageKit transforms. Fluid's `media_tag` filter emits a complete responsive `<img>`/`<video>`; `image_url`/`img_url` return a transformed URL for when you only need the string.
---

# Optimizing Theme Images (Fluid + ImageKit)

## Overview

Fluid themes are **Liquid**, and Fluid serves images and videos through **ImageKit**. Fluid gives you two filters for this — reach for them in this order:

- **`media_tag`** — pipe a media object (or URL) through it and get a complete, responsive `<img>` or `<video>`: `srcset`, `sizes`, `width`/`height`, `loading`, `decoding`, and `alt`, all with sensible defaults. **This is the default — use it for essentially every image and video.**
- **`image_url` / `img_url`** — return just the transformed ImageKit **URL** (with a `tr:` segment inserted). Use it only when you need a bare URL: a CSS `background-image`, a `<source>`, or hand-rolled markup `media_tag` can't produce.

You almost never hand-build an ImageKit URL or hand-write an `<img>` anymore. Let `media_tag` do it.

**Core principle:** Never ship a raw, full-size image into a fixed-size container. `media_tag` requests the display size from ImageKit, generates a `srcset` so the browser picks the right one, and sets `width`/`height` so the page doesn't jump.

## What Fluid gives you (quick reference)

| You want | Use | Result |
|---|---|---|
| A full responsive image | `{{ image \| media_tag }}` | `<img>` with `srcset`/`sizes`/`width`/`height`/`loading`/`decoding`/`alt` |
| A full responsive video | `{{ video \| media_tag: autoplay: true, muted: true, loop: true }}` | `<video>` with transcoded MP4 source + auto poster + `playsinline` |
| Just a transformed URL | `{{ image \| image_url: 'w-600,f-auto,q-80' }}` | `…/tr:w-600,f-auto,q-80/image.jpg` |
| Width / height / alt (px) | `{{ image.width }}` / `{{ image.height }}` / `{{ image.alt }}` | For manual markup; `media_tag` reads these itself when the input carries them |

> `image_tag` still exists but emits a bare `<img>` with **no** `srcset`/`width`/`height`/`loading` — prefer `media_tag`.

## A. `media_tag` — the primary tool

```liquid
{{ section.settings.image | media_tag }}
```
```text
<img src="…/tr:w-1600,f-auto,q-80/banner.jpg"
     srcset="…/tr:w-400,f-auto,q-80/banner.jpg 400w,
             …/tr:w-800,f-auto,q-80/banner.jpg 800w,
             …/tr:w-1200,f-auto,q-80/banner.jpg 1200w,
             …/tr:w-1600,f-auto,q-80/banner.jpg 1600w"
     sizes="100vw" alt="" loading="lazy" decoding="async">
```

### Image options

Every option is optional. Anything **not** in this list is emitted verbatim as an HTML attribute (`class`, `id`, `style`, `data-*`, `fetchpriority`, …), so attach whatever the markup needs.

| Option | Default | Effect |
|---|---|---|
| `sizes` | `100vw` (or `{width}px` if `width` set) | The `sizes` attribute — tell the browser the rendered size. Set it to match your layout. |
| `widths` | `400,800,1200,1600` | Comma-separated widths for the `srcset` ladder. |
| `width` | — | A **fixed** display width: builds a `[width, width×2]` retina `srcset`, sets the `width` attribute, defaults `sizes` to `{width}px`. |
| `height` | — | The `height` attribute (layout stability). |
| `quality` | `80` | Quality 1–100 (`q-`). |
| `format` | `auto` | Output format (`f-`); `auto` lets ImageKit negotiate WebP/AVIF. |
| `crop` | — | Focus point: `top`/`bottom`/`left`/`right`/`center` (`fo-`). |
| `transform` | — | Raw ImageKit transform applied to every variant. Don't put a `w-` token here — width is owned by the filter. |
| `loading` | `lazy` | `loading` attribute — set `eager` for above-the-fold. |
| `alt` | image's alt, else `""` | The `alt` attribute. |

`decoding="async"` is always emitted.

**Fluid width (default)** — width-based `srcset` from the ladder; `sizes` tells the browser which to pick:
```liquid
{{ product.image | media_tag: sizes: '(max-width: 768px) 100vw, 600px', alt: product.title }}
```

**Fixed width** — the image renders at a known size; ladder collapses to `width` + its 2× retina, `sizes` defaults to `{width}px`:
```liquid
{{ section.settings.logo | media_tag: width: 240, alt: 'Logo' }}
```

**Hero / LCP image** (above the fold) — load eagerly and prioritize; never lazy-load your Largest Contentful Paint image:
```liquid
{{ section.settings.hero | media_tag: loading: 'eager', fetchpriority: 'high', sizes: '100vw', class: 'hero__img' }}
```

### Videos

A video object or a URL ending in `.mp4`/`.mov`/`.webm`/`.m4v` renders a `<video>`. The source is transcoded to MP4 and a poster is auto-generated from the first frame.

```liquid
{{ section.settings.bg_video | media_tag: autoplay: true, loop: true, muted: true, class: 'section__bg' }}
```
```text
<video src="…/clip.mp4?tr=f-mp4" poster="…/clip.mp4/ik-thumbnail.jpg"
       autoplay loop muted playsinline></video>
```

| Option | Default | Effect |
|---|---|---|
| `autoplay` / `loop` / `muted` / `controls` | off | Bare boolean flags. |
| `poster` | auto (ImageKit thumbnail) | Override the generated poster. |
| `format` | `mp4` | ImageKit video format. |
| `quality` / `transform` | — | Video quality / raw video transform. |

`playsinline` is added automatically whenever `muted` or `autoplay` is set, so autoplaying background videos work on mobile.

## B. `image_url` / `img_url` — when you only need the URL

For CSS backgrounds or markup `media_tag` can't emit. Pass a raw ImageKit string, named parameters, or both:

```liquid
{{ image | image_url: 'w-600,c-at_max,f-auto,q-80' }}          {%- comment -%} raw string {%- endcomment -%}
{{ image | image_url: width: 600, quality: 80, format: 'auto' }} {%- comment -%} named params {%- endcomment -%}
```
```liquid
<div style="background-image:url('{{ section.settings.bg | image_url: 'w-2000,f-auto,q-80' }}')"></div>
```

Named parameters: `width`→`w`, `height`→`h`, `quality`→`q`, `format`→`f`, `crop`→`fo` (focus; only applies alongside a resize). Everything else (blur, effects, named presets) goes through the raw string.

Common ImageKit transform codes: `w-` width · `h-` height · `q-` quality (1–100) · `f-auto` format · `c-at_max`/`c-maintain_ratio` crop mode · `fo-center` focus · `dpr-2` retina · `bl-10` blur · `ar-4-3` aspect ratio · `n-<name>` named preset.

## Best-practice checklist

- [ ] Reach for `media_tag` first — it sets `srcset`/`sizes`/`width`/`height`/`loading`/`decoding`/`alt` for you.
- [ ] Set `sizes` to the real rendered layout (or pass `width` for a fixed-size image so `sizes` and the retina `srcset` are derived).
- [ ] `loading: 'eager'` + `fetchpriority: 'high'` for the hero/LCP image; leave the default `lazy` for everything below the fold.
- [ ] For picker settings (plain strings with no intrinsic size), pass `width`/`height`/`alt` yourself.
- [ ] Use `image_url`/`img_url` only for CSS backgrounds or markup `media_tag` can't produce — never to rebuild an `<img>` by hand.

## Common mistakes

| Mistake | Fix |
|---|---|
| Hand-writing an `<img>` with `?tr=` query URLs | Pipe through `media_tag` — it builds the `tr:` URLs and full markup |
| `img_url: '300x200'` / `'master'` (Shopify size strings) | **Not supported** — they return the original image unchanged. Use `image_url: 'w-300,h-200'` or `media_tag` |
| Expecting `image_tag` to add `srcset`/`loading` | It doesn't — use `media_tag` |
| No `width`/`height` → page jumps | `media_tag` sets them when the input carries them; for pickers pass `width`/`height` (or CSS `aspect-ratio`) |
| Lazy-loading the hero image | `loading: 'eager'` + `fetchpriority: 'high'` on the LCP image only |
| Putting `w-` inside `media_tag`'s `transform:` | Width owns the `srcset` — use `width`/`widths` instead |

## Fluid behavior (good to know)

- **Only ImageKit media is transformed.** A third-party/custom host URL is emitted as a plain `<img>`/`<video>` with the original `src`, no `srcset`/transform/poster.
- **Image objects fill in width/height/alt**, and the `srcset` ladder is capped to the source's intrinsic width — `media_tag` never requests an upscaled rendition. **Picker settings are plain strings** with none of that, so pass `width`/`height`/`alt` yourself.
- **Output is escaped** and event-handler attributes (`onerror`, `onload`, …) are dropped — a `media_tag` can't inject script.
- **Blank input renders nothing** (empty string), so `{% if %}` guards around it are usually unnecessary.
