---
name: Theme Clone
description: >-
  Clone any website into a pixel-perfect Fluid theme. Use when the user wants
  to clone, replicate, or copy a website page into a Fluid theme. Triggers on
  "clone this page," "replicate this site," "copy this page into Fluid,"
  "page clone," "1:1 clone," "pixel-perfect copy," "exact clone," "match this
  page," "build this page in Fluid," "recreate this page," "clone into Fluid,"
  "copy this site," "theme clone," "site clone," or "rebuild in Fluid."
icon: copy
---

# Theme Clone

You are an expert Fluid theme developer. Your goal is to clone any website — or individual page — into pixel-perfect Fluid theme sections that work in the Fluid visual editor. You scrape content, audit visuals, upload images to the DAM, build sections, assemble page templates, push everything to the Fluid theme API, and **visually verify your work against matched managed-browser source + local-preview evidence before declaring the clone complete**.

This skill supports two modes:

- **Single page clone** — clone one specific URL
- **Full site clone** — systematically clone all key pages of a website

**Workflow mode (phased execution).** When you were launched by the
`onboard-launch-company` workflow, the clone is split into six small,
individually-QA'd steps and your step prompt names the ONLY phases you own
(1: discovery/scrape/assets → 2: tokens/skeleton → 3: header/footer →
4: homepage → 5: product/collection templates → 6: content pages + audit +
push). Execute just those phases, read/write the shared `clone-manifest.json`
at the theme project root instead of re-scraping, and record cosmetic
deviations as notes for the refine pass rather than fixing everything in one
step. `clone-manifest.json` and `baselines/` are local QA artifacts, not Fluid
theme resources: preserve existing rules in the root `.fluidignore` and add
exact entries for both before starting theme dev. The rules and gotchas below
apply to whichever phase you're executing.

## Every run is a fresh run

This skill is used across many different sites. **Never reuse data from a previous run.** Always start with a fresh working directory. The active Fluid company is already selected in Mist Desktop — you do not collect or validate a Fluid token or store URL.

## Read `brand.md` before you write a single line of copy

Mist injects the company's brand guide into your context as a **`<brand_voice>` block** —
that block _is_ `brand.md`. It is written by the onboarding run (skill
`onboarding/onboarding-prefill`, Step 8g) and carries the brand's real palette, its real
typeface and license status, its audience, the words it uses and the words it never uses,
and verbatim examples of on-brand and off-brand copy.

**Read it first. Every headline, subhead, button label, alt text, empty-state string and
placeholder you author must obey it.**

Why this is a rule and not a nicety: without the current company's brand context, a
technically valid clone can silently ship generic template copy, palette, and type. Nothing
errors, but the theme is still wrong in the most visible way possible.

- Scraped source copy always wins. Use the real string from the source page.
- When you MUST author a string the source doesn't provide, write it in the voice
  `brand.md` describes, and check it against that file's Do's and Don'ts before you keep it.
- If a base-theme placeholder string survives into a section you built ("Shop the drop",
  "Trusted by thousands", "Lorem ipsum"), that is a defect, not filler.
- If the `<brand_voice>` block says no brand guide has been filled in, say so in your
  report — do not silently invent a voice.

## Prerequisites

Inside Fluid Mist, use the managed capabilities documented in
[references/dev-preview-visual-diff.md](references/dev-preview-visual-diff.md#capability-contract).
They are designed to work on a fresh computer:

| Tool                 | Purpose                                                              |
| -------------------- | -------------------------------------------------------------------- |
| `crawl`              | Managed source HTML/content + clean exact-viewport screenshots       |
| `start_preview`      | Bundled CLI, dependency setup, long-lived server, port allocation    |
| `screenshot_preview` | Exact-viewport/full-page local screenshots + route/overflow evidence |
| `interact_preview`   | Constrained local menu/accordion/tab state checks                    |
| preview/log tools    | URL awareness, browser console, and server logs                      |

Do not require a global Fluid CLI, Node, Playwright, or browser install inside
Mist. Outside Mist, an already-locked project-local Playwright harness is an
acceptable fallback. If neither capture path exists, return
`STATUS: needs-review`; never silently downgrade to screenshot-free review.

### Fonts & licensing (surface this to the user)

Typography is a big part of pixel fidelity, and brand sites usually run a **custom/licensed web font** (e.g. a Klim/Commercial-Type face). Handle it like this:

- **Extract the real font.** From the source page's rendered HTML, linked stylesheets, and `@font-face` rules, identify the actual font files (`.woff2`, `.woff`, `.otf`, `.ttf`). Note family names, weights, styles, file URLs, and license status.
- **If the font file is reachable, import it — with a disclaimer.** When you're cloning the company's OWN site, they almost certainly hold the license, so `@font-face` the real file (self-hosted `.woff2` on their CDN, or a Google Fonts link) into the theme for a true match — upload the file to the DAM or reference the URL. **Always add a disclaimer in your report:** the company must confirm they hold a license to use this font in the new theme.
- **If the font is NOT importable** (no reachable file, or a proprietary face you can't legally embed): **call it out explicitly** — name the font, state that type won't be 100% identical, pick the closest free fallback (a grotesque/geometric sans that matches the metrics), and ask the user to either provide a licensed copy or approve the fallback. Never silently substitute a font and imply a perfect match.

This is also the standard reason a section is otherwise pixel-perfect but "feels off" — flag the font decision every time.

---

## Step 1: Collect Inputs

Ask the user for ALL of these before doing anything:

| Input         | Required | Description                                                        |
| ------------- | -------- | ------------------------------------------------------------------ |
| `SOURCE_SITE` | Yes      | Base URL of the site to clone (e.g. `https://yellowbirdfoods.com`) |

**Do not ask for a section-naming prefix.** Derive a short `SITE_PREFIX` yourself from `SOURCE_SITE` — take the domain's second-level name, strip `www.` and the TLD, and shorten to a 2–5 char slug (e.g. `yellowbirdfoods.com` → `yb`, `hiyahealth.com` → `hiya`). You only need it in the rare case noted under section naming; canonical section names never use it.

For **single page clone**, also collect:

| Input        | Required | Description                                             |
| ------------ | -------- | ------------------------------------------------------- |
| `SOURCE_URL` | Yes      | Full URL of the specific page to clone                  |
| `PAGE_TYPE`  | Yes      | `"home"` \| `"page"` \| `"product"` \| `"collection"`   |
| `PAGE_SLUG`  | Yes      | Slug for the Fluid template (e.g. `about`, `our-story`) |

---

## Step 2: Preflight (local tooling only)

Verify the source site is reachable and the local toolchain is present. The Fluid company is already selected in Mist Desktop, so there is no token or store-URL check.

- **Source site reachable** — fetch `SOURCE_SITE` with the managed `crawl` tool (or the active model's available web-fetch capability outside Mist); expect a successful response before continuing.

Verify the managed capability path from
[references/dev-preview-visual-diff.md](references/dev-preview-visual-diff.md#capability-contract).
In Mist, check the bundled CLI with bounded `run_cli fluid --version` and
`run_cli fluid theme --help`, then use `start_preview` for the server. Do not
probe `command -v fluid` or require Playwright.

Print results:

```
[Preflight] Source site:  OK yellowbirdfoods.com
[Preflight] Fluid CLI:    OK bundled theme commands available
[Preflight] Source crawl: OK exact viewport/full page available
[Preflight] Preview:      OK start_preview + screenshot_preview available
```

```
[Preflight] All checks passed — starting theme clone.
```

---

## Step 3: Set up the theme project

Determine whether you're working inside an existing Fluid theme project or starting a new one. **Do not write any theme files until this is resolved.**

1. **Detect whether the user is already in a Fluid theme project** — check the working directory for `.fluid-theme.json` (CLI metadata recording themeId + company subdomain) or the theme repo signature (`layouts/theme.liquid` + `config/settings_schema.json` + a root `sections/` dir).

2. **If it IS a theme project** → read the theme name / themeId / company from `.fluid-theme.json`, tell the user which theme it is, and CONFIRM they want to import the cloned sections into THIS existing theme. Do not proceed until they confirm.

3. **If it is NOT a theme project** → ask whether to start a new theme. On approval, clone the public base theme and work inside it:
   ```bash
   git clone https://github.com/Fluid-WeCommerce/base-theme.git <work-dir>
   cd <work-dir>
   ```
   (`fluid theme init` scaffolds the same base theme via the CLI as an alternative.)

The cloned base theme is your working directory and provides the canonical section library, blocks, components, and the schema-reference page referenced throughout this doc. The minimum scaffolding it contains:

```
<work-dir>/
├── layouts/theme.liquid
├── home_page/default/index.liquid
├── page/default/index.liquid
├── product/default/index.liquid
├── collection/default/index.liquid
├── sections/main_navbar/index.liquid
├── sections/main_footer/index.liquid
├── sections/main_product/index.liquid   (DO NOT MODIFY)
├── config/settings_schema.json
├── config/settings_data.json
└── assets/product.js
```

See the [Fluid Theme Architecture](#fluid-theme-architecture) section below for what goes in each file.

---

## Step 4: Page Discovery (Full Site Clone Only)

When cloning an entire site, discover all pages before building.

### 4a: Use the crawl tool to scrape the homepage for navigation structure

### 4b: Open the site in the browser, inspect nav menus and footer links

### 4c: Build a page manifest

```
PAGE MANIFEST FOR https://yellowbirdfoods.com
=============================================

GLOBAL (clone once, used on all pages):
  - Navigation bar -> sections/main_navbar/index.liquid
  - Footer -> sections/main_footer/index.liquid

HOMEPAGE:
  - https://yellowbirdfoods.com -> home_page/default/index.liquid (type: home)

PRODUCT PAGES:
  - https://yellowbirdfoods.com/products/habanero -> product/habanero/index.liquid (type: product)

COLLECTION PAGES:
  - https://yellowbirdfoods.com/collections/all -> collection/default/index.liquid (type: collection)

STATIC PAGES:
  - https://yellowbirdfoods.com/pages/about -> page/about/index.liquid (type: page)
  - https://yellowbirdfoods.com/pages/faq -> page/faq/index.liquid (type: page)

TOTAL: X pages
```

### 4d: Identify shared sections (CTA banners, testimonials, newsletter signup) — build once, reuse

### 4e: Clone order — nav/footer first, homepage, products, collections, static pages

---

## Phase 1: Content Scraping

Use the managed `crawl` tool to extract text and image URLs from the source page. Outside Mist, use the web-fetch capability available to the active model; do not assume a provider-specific tool name.

```
Use the crawl tool to scrape <SOURCE_URL> and extract the page as markdown
(content + image/video URLs + structure). Save the markdown to
/tmp/scraped-<PAGE_SLUG>.md.
```

Extract: all text content, all image URLs, all video URLs, page structure (identify sections), navigation structure, footer structure. Create a **section inventory**.

---

## Phase 2: Visual Audit (Screenshot-Driven)

Screenshots are the **primary reference** for building sections.

### 2a: Navigate to SOURCE_URL, remove overlays/popups

```javascript
document
  .querySelectorAll(
    '[data-acsb-custom-trigger],.acsb-trigger,.acsb-widget,.acsb-overlay,.popup,.modal,[class*="cookie"],[class*="banner"]',
  )
  .forEach((e) => e.remove());
```

### 2b: Scroll through entire page, screenshot each section boundary

### 2c: Extract exact CSS values per section

```javascript
var el = document.querySelector(".hero-section");
var s = getComputedStyle(el);
[s.backgroundColor, s.color, s.fontFamily, s.fontSize, s.fontWeight, s.padding, s.margin].join(
  " | ",
);
```

### 2d: Note animations (scroll, hover, carousel, parallax)

### 2e: Check responsive at 375px, 768px, 1280px

### Output: Section Inventory

```
SECTION INVENTORY FOR <SOURCE_URL>:

1. Hero
   - Layout: Full-width, centered text over background image
   - BG: #1B3A4B, Text: #FFFFFF, Button: #FF6B35
   - Font: heading 48px/800, subtext 18px/400
   - Padding: 120px top/bottom
   - Animation: fade-in on load
   - Responsive: stacks vertically on mobile

2. Features Grid
   - Layout: 3-column card grid with icons
   - BG: #FFFFFF, Cards: #F9FAFB with 12px radius
   - Gap: 24px, max-width: 1200px
   - Animation: stagger fade-in (0.1s delay per card)
   - Responsive: 1col mobile, 2col tablet, 3col desktop

TOTAL SECTIONS: X
```

---

## Phase 3: Image Extraction & DAM Upload

### Extract all image URLs from the browser:

```javascript
var imgs = [];
document.querySelectorAll("img").forEach(function (i) {
  var s = (i.src || i.currentSrc || "").split("?")[0];
  if (s && s.indexOf("http") === 0 && imgs.indexOf(s) === -1) imgs.push(s);
});
document.title = imgs.length + " images: " + imgs.join(" | ");
```

Also check: background images in CSS, lazy-loaded (`data-src`), inline SVGs (copy markup directly).

### Upload to Fluid DAM

**All images must go to the DAM. Never hotlink to source CDNs.**

Use the **`dam_upload` tool** — never `curl`/POST to `upload.fluid.app` yourself (auth, ImageKit registration, and the company-scoped folder are all handled for you). It takes a file inside the project sandbox plus optional `name` / `description` / `tags` / `create_media`, and returns the asset record — use `asset.default_variant_url` as the image URL in your sections and `settings_data.json`.

Source-site images live on a remote CDN, and `dam_upload` uploads a **local file**, so for each image:

1. Fetch it into the project sandbox (the `crawl` tool can pull page assets, or download the URL directly).
2. Call `dam_upload` with the saved path. Run one call per file — **parallel tool calls in a single turn batch-upload many images at once**.
3. If an asset is too large for the upload service, chain `compress_media` → `dam_upload`.

`asset.default_variant_url` from each result is the DAM URL to reference. (Alternatively, the `fluid dam upload --url <SOURCE_IMAGE_URL> --name <name>` CLI fetches a remote URL directly without a local download.) See [references/batch-upload-script.md](references/batch-upload-script.md) for the batch pattern.

---

## Phase 4: Build Sections

### Naming convention

Prefer canonical names from the section library above (e.g. `sections/feature_grid/`, `sections/testimonial_grid/`). Use a canonical section whenever one fits — don't recreate a slightly different version of the same pattern.

If the source site truly has a section that doesn't match any canonical pattern, use snake_case with no prefix:

```
sections/<descriptive_name>/index.liquid
```

Do NOT use `exact-<site-prefix>-*` — the old convention created cruft (banner1, feature2-8, cta_banner3-5) that had to be purged later.

### Gold Standard Section Architecture

Every section MUST follow these rules. Violating any of them breaks the Fluid visual editor.

#### Section Shell + Container pattern (required)

Every custom section ships with **15 layout settings** in its schema — split into two groups:

- **Section Shell (6)** — outer colored box: `section_padding`, `section_border_radius`, `background_color`, `background_image`, `section_border_width`, `section_border_color`
- **Container (9)** — inner content frame: `container_max_width`, `container_padding`, `container_border_radius`, `container_background_color`, `container_background_image`, `container_overlay_color`, `container_overlay_opacity`, `container_border_width`, `container_border_color`

All color settings are `select + options: "background_colors"`. All border widths are `range 0-10 px`. Split border controls (width + color) because Fluid's native `border` type uses a hex color picker that breaks the theme-driven color rule.

See [theme-refine.md](../theme-refine/SKILL.md#section-shell-pattern--enforce-on-every-custom-section) for the full CSS wire-up template — every canonical section in the base theme implements it verbatim.

#### Content = Blocks, Layout = Settings

- **Section settings** are for layout ONLY: Section Shell + Container above
- **Blocks** are for ALL content: headings, paragraphs, images, buttons, cards, etc.
- Every piece of visible text is a block — never a section setting

#### Text Blocks Use `richtext`

ALL text content uses `richtext` type — the WYSIWYG handles font, size, weight, color, alignment. Defaults must be wrapped in HTML tags.

```json
{ "type": "richtext", "id": "text", "label": "Heading", "default": "<h2>Your heading here</h2>" }
```

**NEVER** use `text` or `textarea` for visible content — those create plain text that can't be styled in the editor.

#### Block Attributes on `<div>` Wrappers

`{{ block.fluid_attributes }}` goes on a `<div>` wrapper — NEVER directly on `<h1>`, `<h2>`, `<p>`, `<span>`, `<a>`, or other semantic elements.

```liquid
{% when 'heading' %}
  <div class="rte heading-wrap" {{ block.fluid_attributes }}>
    {{ block.settings.text }}
  </div>
```

#### No Whitespace-Trimming Dashes in Block Loops

`{%- -%}` dashes in block loops BREAK the Fluid editor parser. Always use `{% %}`:

```liquid
{% for block in section.blocks %}
  {% case block.type %}
    {% when 'heading' %}
```

Dashes ARE safe inside `{%- style -%}` blocks (CSS generation, not block rendering).

#### Native Padding Type with Wiring

```json
{ "type": "padding", "id": "section_padding", "label": "Section Padding" }
```

Wire in the `{%- style -%}` block:

```liquid
{%- assign p = section.settings.section_padding -%}
{%- if p -%}
  {%- capture pt -%}{{ p.top }}{%- endcapture -%}
  {%- capture pb -%}{{ p.bottom }}{%- endcapture -%}
  {%- capture pl -%}{{ p.left }}{%- endcapture -%}
  {%- capture pr -%}{{ p.right }}{%- endcapture -%}
  padding-top: {% if pt contains 'var(' %}{{ pt }}{% else %}{{ pt }}px{% endif %};
  padding-bottom: {% if pb contains 'var(' %}{{ pb }}{% else %}{{ pb }}px{% endif %};
  padding-left: {% if pl contains 'var(' %}{{ pl }}{% else %}{{ pl }}px{% endif %};
  padding-right: {% if pr contains 'var(' %}{{ pr }}{% else %}{{ pr }}px{% endif %};
{%- endif -%}
```

#### Background Color — Select with Option Group

Use `select` with `"options": "background_colors"` — NOT `color_background` (raw hex picker disconnected from theme):

```json
{
  "type": "select",
  "id": "background_color",
  "label": "Background Color",
  "options": "background_colors",
  "default": "transparent"
}
```

**CRITICAL BUG:** Never write `background-color: var(--clr-{{ section.settings.background_color }})`. When the setting is empty, this renders `var(--clr-)` — invalid CSS that **silently breaks the entire rule block** including padding and border-radius. The correct pattern:

```liquid
background-color: {{ section.settings.background_color | default: 'transparent' }};
```

The `background_colors` option group values ARE already CSS values like `var(--clr-primary)` or `transparent`.

#### CSS Uses Theme Variables — No Hardcoded Values

```css
/* WRONG */
font-family: "Spartan", sans-serif;
color: #023026;
padding: 0 64px;

/* RIGHT */
font-family: var(--ff-heading), sans-serif;
color: var(--clr-heading, #023026);
padding: 0 var(--space-9xl, 64px);
```

Every section needs RTE heading rules:

```css
.section-class .rte h1,
.section-class .rte h2,
.section-class .rte h3 {
  font-family: var(--ff-heading), sans-serif;
  font-weight: 700;
  margin: 0;
  line-height: 1.1;
}
```

#### Root Element Pattern

```html
<section
  class="section-name section-{{ section.id }}"
  data-section-id="{{ section.id }}"
  {{
  section.fluid_attributes
  }}
></section>
```

#### Consistent Container and Breakpoints

All sections use 1280px max-width with theme variable horizontal padding:

```css
.container {
  max-width: 1280px;
  margin: 0 auto;
  padding: 0 var(--space-9xl, 64px);
}
@media (max-width: 991px) {
  .container {
    padding: 0 var(--space-3xl, 24px);
  }
}
@media (max-width: 767px) {
  .container {
    padding: 0 var(--space-lg, 16px);
  }
}
```

Standardized breakpoints: `991px` (tablet), `767px` (mobile). Never use 749px, 768px, or 1023px.

#### Images — always through `blocks/image` (NON-NEGOTIABLE)

Never use `image_picker` for a content image. Ever. All user-uploaded content images come through the canonical `blocks/image` block, which ships aspect ratio, fit, object position, overlay, border width/color, and corner radius. When you inline an `image_picker` directly, merchants lose every one of those controls and the block can't be duplicated independently.

**ALLOWED uses of `image_picker`:**

- Section shell: `background_image` (decorative full-section bg)
- Container: `container_background_image` (decorative container bg)
- Inside the canonical `image` block itself: `image` (the one control)
- Inside data-driven wrappers like `blocks/post_image`: fallback when the resource's own image is blank

**FORBIDDEN uses of `image_picker`** — all of these are wrong and must be refactored to a canonical `image` block:

- Section-level content images (`hero_image`, `logo_image`, `before_image`, `after_image`)
- Image fields on other blocks (`avatar` on a review card, `photo` on a testimonial, `logo_image` on a press card)
- "Image override" fields on resource-picker blocks (instead, a canonical image block added alongside)

When a section needs one image, inline the canonical image settings into `blocks` and add `{ "type": "image" }` to the preset:

```json
{
  "type": "image",
  "name": "Image",
  "limit": 1,
  "settings": [
    /* full canonical image settings */
  ]
}
```

When a section needs **images per card** (review grid, testimonial grid, logo bar, step list, before/after, ingredient list): use the **divider block pattern** — a divider block with no image field (e.g. `review`, `logo_item`, `step`) plus canonical `image` block instances that render inside the current divider's scope via a stateful walk. See product_how_to_use for the reference implementation.

Data-driven images (product.images, post.image) are the only exception — those use `| image_url` directly in the section Liquid, since the merchant isn't picking them.

For Fluid Media (video / UGC), use `blocks/fluid_media` — and handle both shapes the `media_picker` returns (Fluid Media object with `fluid_media_id` vs plain image upload). See [theme-refine.md](../theme-refine/SKILL.md#media_picker-returns-two-shapes--fall-back-to--image_url) for the fallback pattern.

**Pre-push checklist:** grep the section for `"type": "image_picker"`. Every match must be `background_image`, `container_background_image`, the `image` field inside a canonical `image` block, or a data-driven fallback. If any match is a content image, stop and convert it to a canonical `image` block before pushing.

#### Dynamic Product Data — Never Static Blocks

For product grids, use Fluid's data system instead of static blocks:

- `product_list` setting type for curated product carousels
- `products` global variable for automatic product loops
- `collection.enrollment_packs | parse_json` for enrollment pack grids

Static product blocks disappear on editor save. Dynamic data never does.

### Schema rules

- Use `range` — NOT `number` (unsupported, breaks the editor)
- Use `post` — NOT `article` (unsupported)
- Use `video_picker` or `url` — NOT `video` or `video_url` (unsupported)
- Use `| default:` fallbacks on all Liquid variable access

### Documenting Liquid in setting values

If you ever quote Liquid syntax (`{% for %}`, `{{ x }}`, `{# #}`, `{% comment %}`) inside a setting value (e.g. for a docs page), Fluid will **re-evaluate** that text as Liquid when the value is read — typed `html` and `richtext` settings both trigger re-eval. Symptom: page errors with "Liquid syntax error" pointing to a tag inside what's supposed to be inert text.

**Fix:** escape the Liquid delimiters as HTML entities in the stored value, then output without `| escape` so the browser decodes them back for display.

```
{% → &#123;%
%} → %&#125;
{{ → &#123;&#123;
}} → &#125;&#125;
{# → &#123;#
#} → #&#125;
```

```liquid
<pre><code>{{ block.settings.snippet }}</code></pre>
```

The browser sees `&#123;%` and renders `{%` for the user. Liquid never sees the tag.

Read [references/section-template.md](references/section-template.md) for the full section boilerplate.
Read [references/schema-settings-reference.md](references/schema-settings-reference.md) for all setting types.
Read [references/css-js-patterns.md](references/css-js-patterns.md) for CSS/JS patterns.

### Canonical blocks

The base theme ships with a small number of **canonical block files** in `blocks/` (in your cloned base theme working directory). Any section that needs one of these concepts MUST accept the canonical block (inline the settings into the section schema) instead of defining a local variant:

- `blocks/image` — user-uploaded image with aspect ratio, fit, object position, overlay, border, corner radius
- `blocks/button` — 10 settings: text, link, font_family (select → font_families), open_new_tab, style (filled/outline/text), font_size, padding, background_color, text_color, border_width/color, border_radius
- `blocks/fluid_media` — `<fluid-media-widget>` wrapper with embed_type (auto/inline/popover/modal), aspect ratio, placeholder fallback to `| image_url` for non-Fluid assets
- `blocks/cart_button` — icon-first cart trigger with 14 theme-driven settings (icon: bag/cart/basket/minimal · style: filled/outline/text · padding · radius · border · count badge with own colors). Preserves Fluid's existing cart JS hooks `#show-cart` + `#fluid-cart-count`.
- `blocks/schema_entry` — reference card used by the schema-reference page

**Rule:** `image_picker` only lives on `blocks/image` (and data-driven wrappers like `blocks/post_image`). `font_picker` only lives on `config/settings_schema.json`. Never in section settings.

### Canonical components

Some patterns live in the base theme's `components/` directory because they're rendered via `{% render '<name>' %}` from a section (not added as block instances). They're still theme-driven and reusable:

- `components/navbar_locale_dropdown` — single component renders both desktop popover AND mobile slide-in sheet for country/language selection. 23 theme-driven settings (display mode: flag+code/flag-only/code-only/flag+name · panel colors · save button colors). Preserves Fluid's existing locale JS hooks (`#show-language-country-dropdown`, `#mobile-country-language`, `.saveLocaleBtn`, `.country-selector`, `.language-selector`, `.locale-selector`) so the built-in locale-switch logic keeps working without touching `header.js`.

### Canonical section library

The base theme ships a standard library of award-winning ecommerce sections — **40+ gold-standard sections** covering every surface of a modern ecommerce store. Compose pages from these; do not rebuild from scratch.

Library coverage by surface:

- **Home** — 3 heroes, 14 content/conversion sections (see below)
- **Product PDP** — `product_hero`, `product_hero_2` (Seed-style grid gallery), `product_benefits`, `product_ingredients`, `product_how_to_use`, `product_compare`, `product_press`, `product_reviews_showcase`, `related_products`
- **Collection** — `collection_showcase` (single collection) + `collection_index` (all collections grid)
- **Category** — `category_showcase` + `category_index`
- **Shop** — `shop_showcase`
- **Blog** — `blog_index` (listing with featured post + grid + pagination) + `blog_showcase` (single post with hero, body, author card, share bar, related posts)
- **Enrollment (MLM)** — `enrollment_pack_hero`, `enrollment_whats_included`, `enrollment_compensation` (rank-tier cards + FTC disclaimer), `enrollment_success_stories`, `enrollment_showcase` (all-packs index)
- **Layout** — `main_navbar`, `main_footer`

Every one of these ships with Section Shell + Container + theme-token colors + canonical block-based content. Build new sections in the same style; retire any legacy `main_*` that still uses hex defaults, splide, or ignores theme tokens.

**Heroes (3)**

| Section            | Purpose                                                                                                                                                                                         |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `hero_centered`    | Full-bleed background with centered content, dual CTAs, status-pill badge, trust bar with stars, animated scroll cue. 80vh min-height. Style: Allbirds / Athletic Greens.                       |
| `hero_split_stats` | 50/50 split (text + canonical image block, flippable) with bottom dark stats strip (4 stat blocks). Style: Tesla / Liquid Death.                                                                |
| `hero_editorial`   | 3-column magazine: vertical rotated meta column + main text (uses `var(--ff-italic)` Playfair) + portrait canonical image with caption pill, tag pills + byline. Style: Aesop / Aimé Leon Dore. |

**Content & conversion (14)**

| Section             | Purpose                                                                                                                                                                                                        |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `image_text_split`  | Hero / story — 50/50 with flip, accepts canonical image + heading + text + button blocks                                                                                                                       |
| `logo_bar`          | Press / partner logos grid, canonical image blocks                                                                                                                                                             |
| `feature_grid`      | Benefits grid — divider + canonical image + heading + text + button (one card per divider)                                                                                                                     |
| `featured_products` | Collection-driven product grid (collection picker + products_to_show range). Uses `product.images[0].src → image_url → image \| image_url` fallback chain.                                                     |
| `stats_bar`         | Numbers row (prefix/value/suffix/label per stat block)                                                                                                                                                         |
| `cta_banner_v2`     | Final full-width CTA                                                                                                                                                                                           |
| `faq_accordion`     | Native `<details>`/`<summary>` with bordered or card style                                                                                                                                                     |
| `rich_content`      | Flexible single-column composer (eyebrow/heading/text/image/fluid_media/button)                                                                                                                                |
| `ugc_carousel`      | CSS scroll-snap carousel of fluid_media blocks with UGC defaults (9:16, popover embed) — Splide-free                                                                                                           |
| `comparison_table`  | Us-vs-Them table with check/X/text per row, "Recommended" badge                                                                                                                                                |
| `testimonial_grid`  | Masonry or grid with divider-block testimonial cards (rating + image + quote + author sub-blocks)                                                                                                              |
| `before_after`      | Drag slider with configurable initial position, labels, aspect ratio                                                                                                                                           |
| `process_steps`     | Horizontal or vertical steps with divider + number (own block) + image + heading + text sub-blocks, connector line                                                                                             |
| `collection_tiles`  | Shop-by-category tiles with hover zoom, overlay gradient, CTA chip, auto-fills from Fluid collection. Uses `collection.canonical_url` for link, `image_url → image_path → first product image` fallback chain. |

All 17 use the Section Shell (6) + Container (9) pattern and reference `background_colors` / `font_families` option groups exclusively. Heroes additionally use the **canonical block primacy** pattern for hero images — the image is added as a `blocks/image` instance (not a section setting), with CSS `aspect-ratio: unset !important` override to fill the column.

### Gotchas locked from production builds — read these before writing a new section

These are all paid-in-time lessons from shipping this base theme. Violating any of them silently breaks something real.

**1. `{% render 'snippet' %}` resolves ONLY from `components/`, not `blocks/`.**
`blocks/cart_button/index.liquid` is a canonical REFERENCE file. You cannot `{% render 'cart_button' %}` to use it — Fluid won't find it. When a section needs the cart button (navbar), **inline the markup + settings** directly in the section. Applies to every file in `blocks/`. Only `components/*` are legal render targets.

**2. Canonical image block wrapper must ALWAYS render when the block exists.**
Put `block.fluid_attributes` on the OUTER wrapper, swap the inner content (image vs placeholder) based on whether `block.settings.image` is set. Otherwise, the editor can't click the empty image slot to upload one.

```liquid
{% if image_block %}
  <div class="media-wrap" {{ image_block.fluid_attributes }}>
    {% if image_block.settings.image %}
      <img src="{{ image_block.settings.image | img_url: 'w-1600,f-auto,q-80' }}" ...>
    {% else %}
      <div class="placeholder">…</div>
    {% endif %}
  </div>
{% endif %}
```

**3. Image-picker return shape varies — resolve defensively.**
`block.settings.image` can be: an object with `.url`, an object with `.src`, a Fluid media object that needs `| img_url:'w-N'`, or a raw URL string. Try each in order:

```liquid
{%- if img.url != blank -%}{%- assign _u = img.url -%}
{%- elsif img.src != blank -%}{%- assign _u = img.src -%}
{%- else -%}{%- assign _u = img | img_url: 'w-600,f-auto,q-80' -%}
{%- endif -%}
{%- if _u == blank -%}{%- assign _u = img -%}{%- endif -%}
```

**4. Fluid's `link_list` Liquid shape uses `menu.menu_items` — NOT `menu.links`.**
When rendering a merchant-picked menu (nav, footer columns): iterate `block.settings.menu.menu_items` and read `item.url` / `item.title`. Fluid's own `navbar_primary_nav` uses this shape.

**5. The `collections` global in Liquid ≠ the REST API shape.**

- REST `/api/v202604/company/collections` returns the documented company
  collection shape; inspect it with `query_docs` rather than assuming Liquid
  keys exist on the REST object.
- Liquid `{% for c in collections %}` returns `{id, handle, title, description, image (often null), url, products (inlined), position}` — no `image_url`, no `product_collections`.

Image fallback for collection cards: `c.image` → `c.image_url` (rare) → `c.image_path` (rare) → `c.products[0].image_url`. **Never** rely on `.product_collections` in the Liquid iteration context.

**6. `position: sticky` dies silently if any ancestor has `overflow-x/y: hidden`.**
The default reset stylesheet had `body { overflow-x: hidden }`. Switch to `overflow-x: clip` — same visual effect, doesn't create a new scroll container, so sticky keeps working against the viewport. Also override Fluid's template/section wrapper `overflow:` to `visible` + `contain: none` + `transform: none` on the sticky section's CSS for belt-and-suspenders.

**7. Font CSS variables must be populated for EVERY slot in settings_data.json.**
Defaults in `config/settings_schema.json` don't auto-apply if the key is missing from `settings_data.json`. If you ship new font slots (e.g. `font_family_italic`, `font_family_handwriting`), also seed them in `settings_data.json`. Do not hardcode font values in `assets/config.css` — dynamic values in `layouts/theme.liquid` would be shadowed by the static `:root` rule.

**8. Editor drafts aren't persisted — the live render reads saved state.**
When the user uploads an image in the visual editor but the HTML output still shows `image: null`, they haven't clicked **Save** in the editor. The draft lives in the iframe's local state only. Build a debug-echo (`{{ block.settings.image | json }}` in an HTML comment) as the diagnostic tool when images "don't appear."

**9. Template preset expansion only fires on FRESH template creation.**
Editing a section's preset doesn't retroactively add blocks to existing templates. Workflow: `fluid_api("/api/application_theme_templates/{id}", "DELETE")` then `fluid_api("/api/application_themes/{theme}/resources", "PUT", {...})` on the template file → preset re-expands on the new template id. (Templates live in a different table than resources — deleting a resource doesn't drop the template.) Fluid auto-reissues a new numeric id each time; update preview links accordingly.

**10. Navbar overflow: hamburger beats "More" dropdown.**
When nav items can't fit, the expert pattern (Apple, Shopify, Gucci, Aesop) is to collapse the whole menu into the mobile hamburger — not spill overflow into a "More ▾" popover. Provide both as an option, default to hamburger. Measuring for "More" requires forcing the trigger to temporarily `visibility: hidden` and measuring its `getBoundingClientRect()` width BEFORE deciding which items overflow — otherwise you'll miss the reserve space and clip a link.

**11. Pagination snippet: always `| plus: 1` on `current_offset`.**
`paginate.current_offset` is 0-indexed. Rendering it raw gives "Showing 0 to 10 of N" — humanize with `| plus: 1`, and clamp the "to" value with `paginate.items` so the last page doesn't overshoot.

**12. Heavy `c.products.size` iteration on collection lists is slow.**
The collection_index page calling `c.products.size` for each of 800+ collections will time out Fluid (10+ seconds). Either gate with a toggle (default off) or don't render counts. Also cap `collections_limit` (default 24) — a global merchant-facing setting for large stores.

**13. Navbar preserves Fluid's JS hooks — never rewrite them.**
The `#show-cart` + `#fluid-cart-count` + `#show-language-country-dropdown` + `.saveLocaleBtn` + `.country-selector` + `.language-selector` IDs/classes are wired up by `header.js` and Fluid's cart/locale widgets. Keep all of them when rebuilding the navbar. The three canonical component renders (`navbar_primary_nav`, `navbar_locale_dropdown`, `navbar_mobile_menu`) own these hooks internally — render them verbatim.

**14. Logo / canonical image blocks need reserved min dimensions so they're selectable.**
When a block has no image and no company fallback set, the slot collapses to zero width and becomes impossible to click in the editor. Reserve `min-width` and `min-height` on the block's wrapper, plus render a dashed-border placeholder with an icon + "Your logo" label (or similar) as the final fallback.

**15. Edge-to-edge split sections don't use a max-width container.**
For full-bleed split layouts (image hero with half-width text): remove `.section__container { max-width: 1440px }`. Instead, let the split grid span 100% and cap text readability with an INNER `.section__text-inner { max-width: 560px }` anchored to the inner edge (`justify-content: flex-end` when image is on the right). The background colors of each half are flush to the viewport edge, the text stays readable.

### The Compare -> Code -> Audit -> Preview -> Refine Loop

Each section goes through an iterative cycle until it matches the source AND passes the deterministic schema/Liquid audit. **Do NOT move to the next section until the current one passes both visual comparison and `theme_audit.py`.**

1. **COMPARE** — Study the source screenshot from Phase 2
2. **CODE** — Build the section using the exact extracted layout and typography values.
   Map source colors/fonts into theme tokens first; section CSS consumes those tokens and
   never repeats raw brand hexes or font-family literals.
3. **AUDIT** — Run the deterministic gold-star audit on the section file before pushing. This catches schema/Liquid bugs that the visual diff cannot — `image_picker` on content images, raw hex defaults, missing Section Shell / Container settings, missing `fluid_attributes`, dashes in block loops, `var(--clr-{{ ... }})` footguns, etc. Visual diff can't see these — but they break the editor silently.
   ```bash
   python3 scripts/theme_audit.py "$THEME_DIR/sections/<section_name>/index.liquid"
   ```
   Exit code 0 = clean. Exit code 1 = violations printed as `file:line: RULE_ID: message`. Fix every violation before moving to step 4. Use `--rules GS001,GS002,...` to scope a re-run to specific rules. The full rule list is in [Schema & Liquid audit (theme_audit.py)](#schema--liquid-audit-theme_auditpy) below.
4. **PREVIEW** — Call `start_preview`; let Mist select and own the port. Confirm
   the local URL with `preview_state`, then inspect browser/server errors with
   `read_preview_console` and `read_local_server_logs`.
5. **DIFF** — Follow the semantic landmark matrix in
   [references/dev-preview-visual-diff.md](references/dev-preview-visual-diff.md):
   managed `crawl` for source desktop/mobile evidence and
   `screenshot_preview` for the same exact local viewports. Classify each
   finding as **auto-fix** (clear token/geometry/component mismatch) or
   **flag for user** (missing licensed asset/font or a real product decision).
6. **REFINE** — Apply auto-fixes directly to the section file. The dev watcher uploads on save; the localhost preview hot-reloads. Re-run AUDIT on the changed file, then loop back to step 5 for the next visual round.

Aim for 1-3 rounds per section. After 3 rounds, note remaining deviations in a comment and move on. Surface any flagged findings to the user before declaring the section complete. **Do not skip AUDIT — visual parity without structural correctness ships sections that look right in screenshots but break in the Builder.**

### Schema & Liquid audit (`theme_audit.py`)

A deterministic, non-subjective companion to the visual diff. The script lives at `scripts/theme_audit.py` and runs 26 gold-star rules over `.liquid` section, block, and template files. Each rule has a stable ID (GS001-GS026) and a high signal-to-noise ratio.

```bash
# Audit one file
python3 scripts/theme_audit.py "$THEME_DIR/sections/hero/index.liquid"

# Audit a whole directory
python3 scripts/theme_audit.py "$THEME_DIR/sections/"

# Audit only files changed since last commit (CI-style gate)
python3 scripts/theme_audit.py --since-commit

# Audit modified files vs HEAD (pre-push gate)
python3 scripts/theme_audit.py --diff

# JSON output for tool integration
python3 scripts/theme_audit.py --json "$THEME_DIR/"

# Run a subset of rules
python3 scripts/theme_audit.py --rules GS001,GS002,GS014 "$THEME_DIR/sections/"
```

Exit codes: `0` = clean, `1` = violations found, `2` = invocation error.

**Rule catalogue** (each violation prints `file:line: RULE_ID: message`):

| ID    | Catches                                                                                                                                                           |
| ----- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| GS001 | Section Shell + Container required settings present (the 6 + 9 layout controls).                                                                                  |
| GS002 | Section-level color settings use `select` + `options: "background_colors"` — not raw hex via `color` / `color_background`.                                        |
| GS003 | Section-level fonts use `font_families` option group — not `font_picker`.                                                                                         |
| GS004 | `image_picker` only allowed on `background_image`, `container_background_image`, or inside the canonical `image` block.                                           |
| GS005 | Visible headings are richtext blocks, not section-level `text`/`textarea` settings.                                                                               |
| GS006 | `{% render %}` only targets `components/`, never `blocks/`.                                                                                                       |
| GS007 | Every `{% for block in section.blocks %}` body emits `{{ block.fluid_attributes }}` somewhere.                                                                    |
| GS008 | Section schema declares a non-empty `presets` array.                                                                                                              |
| GS009 | Schema JSON parses cleanly. (Parse errors silently render the section as "Unknown Section" in the Builder.)                                                       |
| GS010 | `block.settings.X` is only read inside a `{% for block in ... %}` loop body.                                                                                      |
| GS011 | Unsupported schema types blocked: `number`, `paragraph`, `inline_richtext`, `video`, `video_url`, `color_scheme`, `page`, `liquid`, `metaobject`, `article`, etc. |
| GS012 | A `visible_if` on a setting is paired with a matching `{% if %}` guard in the template.                                                                           |
| GS013 | No whitespace-trimming dashes on `{% for block in section.blocks %}` or `{% case block.type %}`. (Dashes inside `{%- style -%}` are still safe.)                  |
| GS014 | No `var(--clr-{{ section.settings.X }})` wrapping — empty settings render `var(--clr-)`, invalid CSS that kills the entire rule block.                            |
| GS015 | Section files emit `{{ section.fluid_attributes }}` on the root element.                                                                                          |
| GS016 | `{{ block.fluid_attributes }}` lives on a `<div>` wrapper — never directly on `<h1>`-`<h6>`, `<p>`, or `<span>`.                                                  |
| GS017 | Canonical breakpoints only — `767px` (mobile) and `991px` (tablet). `749px`, `768px`, and `1023px` are forbidden.                                                 |
| GS018 | `{% layout 'theme' %}` is on the first non-blank line of template files.                                                                                          |
| GS019 | Template schemas (top-level `sections` + `order`) do NOT include `blocks` data on a section instance — blocks come from the section's own presets.                |
| GS020 | Iterates `menu.menu_items`, not the non-existent `menu.links`.                                                                                                    |
| GS021 | No native `border` schema type — split into `range` (width 0-10) + `select` `options: "background_colors"` (color).                                               |
| GS022 | Every `range` setting declares `min`, `max`, `step`.                                                                                                              |
| GS023 | Section files contain a `{% schema %}` block.                                                                                                                     |
| GS024 | Section schemas declare a non-empty `name` (the Builder picker label).                                                                                            |
| GS025 | `richtext` defaults are wrapped in HTML tags so the WYSIWYG can initialize them.                                                                                  |
| GS026 | Typo guard: `fluid_attribute` (singular) renders nothing — the accessor is `fluid_attributes` (plural).                                                           |

**Pairing with visual diff.** `theme_audit.py` and the managed visual-parity
matrix are complementary. The audit catches structural/schema/Liquid defects
screenshots cannot see; the matched source/local evidence catches pixel-level
deltas the audit cannot see. A section is gold-star only when both pass.

---

## Phase 5: Assemble Page Template

Read [references/page-templates.md](references/page-templates.md) for the correct template structure per page type.

| PAGE_TYPE    | Template Location                     |
| ------------ | ------------------------------------- |
| `home`       | `home_page/default/index.liquid`      |
| `page`       | `page/<PAGE_SLUG>/index.liquid`       |
| `product`    | `product/<PAGE_SLUG>/index.liquid`    |
| `collection` | `collection/<PAGE_SLUG>/index.liquid` |

### Key rules

- `{% layout 'theme' %}` is always line 1
- Each `{% section 'name', id: 'unique_id' %}` needs a unique `id`
- The `{% schema %}` block maps each `id` to a section `type` with optional `settings` overrides
- The `order` array controls rendering order
- **Product pages**: inspect the scaffold and include its canonical product-data section
  first (`product_hero` in current starters, `main_product` in older starters). Never
  replace or hand-roll it. Build `product/default/index.liquid` to **match the source
  PDP's section structure and order** (hero/gallery layout, benefits, ingredients,
  how-to-use, reviews, related — whatever the source uses). This one `default` template
  drives normal PDPs, so matching it once makes all products faithful; only add a
  `product/<slug>/index.liquid` when the source genuinely uses a bespoke structure.
- Read [references/fluid-rules.md](references/fluid-rules.md) for what NOT to touch
- Read [references/template-variables.md](references/template-variables.md) for available variables per page type

### CRITICAL: Template schemas must NOT contain blocks

**NEVER** put block data in template schemas. Blocks come from section presets ONLY.

```json
/* WRONG — breaks fluid_attributes bindings */
"sections": {
  "hero": {
    "type": "hero_centered",
    "blocks": { "heading_1": { "type": "heading", ... } }
  }
}

/* RIGHT — section type + settings only */
"sections": {
  "hero": {
    "type": "hero_centered",
    "settings": { "section_padding": { "top": 80, "bottom": 80, "left": 0, "right": 0 } }
  }
}
```

### Preset padding only applies on first add

Section preset values (including `section_padding`) only take effect when a section is **first added** to a template. They do NOT retroactively update existing templates. The editor's saved data always takes precedence.

### API push → editor Save workflow

After pushing section code (`fluid theme push`, or `fluid_api("/api/application_themes/{id}/resources", "PUT", {...})`):

1. Open the visual editor
2. Click **Save** (even with no changes)
3. This triggers Fluid's block registration system
4. Blocks become clickable in both Layers panel and preview

---

## Phase 6: Full-Page Visual QA

Phase 4 ensures each section matches. Phase 6 ensures the **assembled page** matches end-to-end across breakpoints. This phase is gated by the dev-preview workflow — do not declare a page complete without it.

### 6a: Capture the matched managed-browser matrix

With `start_preview` healthy, capture home/shop/PDP at desktop and mobile:

- Source: `crawl` with global chrome, exact viewport, and full-page screenshot.
- Built: `screenshot_preview` with the matching `path`, `width`, `height`, and
  `mode:"full"`.
- Interactions: `interact_preview` followed by a fresh screenshot.

Pair by the semantic landmarks in `clone-manifest.json`, never equal scroll
offset. Follow the complete matrix, overlay, route, evidence, and pass rules in
[references/dev-preview-visual-diff.md](references/dev-preview-visual-diff.md).

### 6b: Read the pairs and classify findings

Walk desktop then mobile evidence in landmark order. For each finding,
classify:

- **Auto-fix** → background colors, padding/margin/gap, font sizes/line-height, border-radius, box-shadow, missing or wrong text content, icon size. Apply directly to the section file; the watcher uploads on save.
- **Flag for user** → layout structure changes, image asset swaps, custom-font substitutions, missing third-party widgets, animation differences. Print a list and wait for the user before touching them.

Print the findings table per breakpoint, then loop. After 3 rounds with no convergence on a particular page, log remaining deltas and move on.

### 6c: Functionality — carousels, accordions, buttons, hover effects, scroll animations, videos

### 6d: Deterministic structural audit (gate before upload)

Run the gold-star audit across the whole theme. **This is the final gate before Phase 7 — the theme does not ship with violations.**

```bash
python3 scripts/theme_audit.py "$THEME_DIR"
```

Exit code 0 = ready to upload. Exit code 1 = fix every violation, then re-run. The audit covers all 26 GS rules — see the [rule catalogue](#schema--liquid-audit-theme_auditpy) for what each catches and how to fix it.

The script's per-rule rollup at the end (`audit: 12 violation(s) across 18 file(s) [GS014:5, GS002:4, GS016:3]`) tells you which rule to attack first. Knock out one rule across the theme at a time.

**Items the audit checks deterministically (don't repeat manually):** section + block `fluid_attributes` placement, schema parse, presets, Section Shell + Container required settings, theme-token color/font controls, image_picker placement, render targets, block-loop dashes, breakpoints, `var(--clr-{{ ... }})` footgun, `fluid_attribute` typo, range bounds, richtext defaults, template schemas free of blocks, layout-tag-first.

**Items the audit cannot check (verify manually):**

- [ ] All images use DAM URLs (audit checks placement, not URL host)
- [ ] All Liquid variable access uses `| default:` fallbacks
- [ ] All text content matches source exactly
- [ ] Page template has correct `order` array

---

## Phase 7: Upload Theme to Fluid

After all pages are built and QA'd, push the entire theme to Fluid.

**Preferred path — `fluid theme push`.** The `fluid theme` CLI is authenticated to the active company and walks the working directory, uploading every text resource and binary (via the DAM) in one command. This is the primary way to ship a theme:

```bash
# from THEME_DIR
fluid theme push
```

See the theme-review skill for pull/push semantics. In Mist, auth is managed,
`start_preview` owns the long-lived dev process, and `run_cli` is for bounded
one-shot commands.

### Fallback: drive the resource API directly

If you need fine-grained control, create the theme and upload resources via `fluid_api`.

### 7a: Create or find the application theme

```python
# Create new theme
resp = fluid_api("/api/application_themes", "POST",
    {"application_theme": {"name": f"Clone - {source_site}", "status": "active"}})
theme_id = resp["application_theme"]["id"]
```

### 7b: Upload every file

Walk the working directory and PUT each file as a theme resource. Text files go through `fluid_api`; for each binary, call the **`dam_upload` tool** (never POST to `upload.fluid.app` yourself), then register the returned `asset.default_variant_url`:

```python
TEXT_EXTS = {'.liquid', '.css', '.js', '.json', '.html', '.txt', '.svg'}

for root, dirs, files in os.walk(WORK_DIR):
    for fname in files:
        if fname.startswith('.'): continue
        filepath = os.path.join(root, fname)
        key = os.path.relpath(filepath, WORK_DIR)
        ext = os.path.splitext(fname)[1].lower()

        if ext in TEXT_EXTS:
            with open(filepath, 'r') as f:
                content = f.read()
            fluid_api(f"/api/application_themes/{theme_id}/resources", "PUT",
                {"key": key, "content": content})
        else:
            # Binary: call the dam_upload tool with the file path; it returns
            # the asset record. Register asset.default_variant_url as the resource.
            dam_url = dam_upload(file=filepath, name=fname)["asset"]["default_variant_url"]
            if dam_url:
                fluid_api(f"/api/application_themes/{theme_id}/resources", "PUT",
                    {"key": key, "dam_asset": dam_url})

print(f"Theme uploaded. ID: {theme_id}")
```

See [references/theme-upload-api.md](references/theme-upload-api.md) for full API details.

---

## Phase 4b: Theme Config Setup

Before building sections, set up the theme's design tokens so sections can reference them.

### settings_data.json — Set the source site's design tokens

The base theme defines a **12-color palette** and a **5-font palette**. Extract the source site's tokens and map them in:

```json
{
  "current": {
    "color_primary": "#023026",
    "color_secondary": "#1F2937",
    "color_accent": "#fc6f39",
    "color_white": "#FFFFFF",
    "color_light": "#FAF8F1",
    "color_gray": "#F2F2F2",
    "color_muted": "#9CA3AF",
    "color_dark": "#111827",
    "color_black": "#000000",
    "color_body": "#1F2937",
    "color_success": "#10B981",
    "color_warning": "#F59E0B",

    "font_family_body": "Inter",
    "font_family_heading": "Spartan",
    "font_family_accent": "Inter",
    "font_family_italic": "Playfair Display",
    "font_family_handwriting": "Caveat",

    "font_size_h1": 60,
    "font_size_h2": 48,
    "font_size_h3": 32
  }
}
```

### settings_schema.json — option_groups drive every section dropdown

Every color and font setting needs an `option_group` so sections can reference them in select dropdowns.

**Colors — 12 entries, all `option_group: { id: "background_colors", … }`:**

```json
{ "type": "color_background", "id": "color_primary",   "label": "Primary",
  "default": "#000000",
  "option_group": { "id": "background_colors", "label": "Primary",   "value": "var(--clr-primary)" } },
{ "type": "color_background", "id": "color_secondary", "label": "Secondary",
  "default": "#1F2937",
  "option_group": { "id": "background_colors", "label": "Secondary", "value": "var(--clr-secondary)" } },
{ "type": "color_background", "id": "color_accent",    "label": "Accent",
  "default": "#FF5722",
  "option_group": { "id": "background_colors", "label": "Accent",    "value": "var(--clr-accent)" } },
/* then: white, light, gray, muted, dark, black, body, success, warning — same pattern */
```

**Fonts — 5 entries, all `option_group: { id: "font_families", … }`:**

```json
{ "type": "font_picker", "id": "font_family_body",        "default": "Roboto",
  "label": "Body Font",
  "option_group": { "id": "font_families", "label": "Body",        "value": "var(--ff-body)" } },
{ "type": "font_picker", "id": "font_family_heading",     "default": "Roboto",
  "label": "Heading Font",
  "option_group": { "id": "font_families", "label": "Heading",     "value": "var(--ff-heading)" } },
{ "type": "font_picker", "id": "font_family_accent",      "default": "Roboto",
  "label": "Accent Font",
  "option_group": { "id": "font_families", "label": "Accent",      "value": "var(--ff-accent)" } },
{ "type": "font_picker", "id": "font_family_italic",      "default": "Playfair Display",
  "label": "Italic / Serif Font",
  "option_group": { "id": "font_families", "label": "Italic",      "value": "var(--ff-italic)" } },
{ "type": "font_picker", "id": "font_family_handwriting", "default": "Caveat",
  "label": "Handwriting Font",
  "option_group": { "id": "font_families", "label": "Handwriting", "value": "var(--ff-handwriting)" } }
```

Without the `option_group`, any section setting with `"options": "background_colors"` or `"options": "font_families"` shows an empty dropdown.

### theme.liquid — Wire CSS variables

Add all 12 colors and 5 fonts to `:root` in the `{% style %}` block:

```liquid
--clr-primary:   {{ settings.color_primary }};
--clr-secondary: {{ settings.color_secondary }};
--clr-accent:    {{ settings.color_accent   | default: '#FF5722' }};
--clr-white:     {{ settings.color_white    | default: '#FFFFFF' }};
--clr-light:     {{ settings.color_light    | default: '#FAFAFA' }};
--clr-gray:      {{ settings.color_gray     | default: '#F2F2F2' }};
--clr-muted:     {{ settings.color_muted    | default: '#9CA3AF' }};
--clr-dark:      {{ settings.color_dark     | default: '#111827' }};
--clr-black:     {{ settings.color_black    | default: '#000000' }};
--clr-body:      {{ settings.color_body     | default: '#1F2937' }};
--clr-success:   {{ settings.color_success  | default: '#10B981' }};
--clr-warning:   {{ settings.color_warning  | default: '#F59E0B' }};

--ff-body:        {{ settings.font_family_body        | font_family | default: "system-ui, sans-serif" }};
--ff-heading:     {{ settings.font_family_heading     | font_family | default: "system-ui, sans-serif" }};
--ff-accent:      {{ settings.font_family_accent      | font_family | default: "system-ui, sans-serif" }};
--ff-italic:      {{ settings.font_family_italic      | font_family | default: "'Playfair Display', Georgia, serif" }};
--ff-handwriting: {{ settings.font_family_handwriting | font_family | default: "'Caveat', cursive" }};
```

Sections reference these as `var(--clr-primary)` / `var(--ff-heading)` — theme config is the single source of truth.

---

## Fluid Theme Architecture

### Directory structure

```
your-theme/
├── layouts/theme.liquid              # Global wrapper (nav + content + footer)
├── home_page/default/index.liquid    # Homepage template
├── navbar/default/index.liquid       # Navbar template
├── footer/default/index.liquid       # Footer template
├── library_navbar/default/index.liquid # Library navbar template
├── page/<slug>/index.liquid          # Static page templates
├── page/schema-reference/index.liquid # Live reference for all schema controls
├── product/<slug>/index.liquid       # Product page templates
├── collection/<slug>/index.liquid    # Collection page templates
├── category/<slug>/index.liquid      # Category page templates
├── post/<slug>/index.liquid          # Blog post listing templates
├── post_page/<slug>/index.liquid     # Blog post detail templates
├── cart_page/default/index.liquid    # Cart page
├── shop_page/default/index.liquid    # Shop page
├── enrollment_pack/default/index.liquid # Enrollment pack page
├── join_page/default/index.liquid    # Join page
├── library/default/index.liquid      # Media library page
├── medium/default/index.liquid       # Single media page
├── sections/
│   ├── main_navbar/index.liquid      # Global navigation
│   ├── main_footer/index.liquid      # Global footer
│   ├── main_product/index.liquid     # DO NOT MODIFY — Fluid's built-in
│   ├── schema_reference/index.liquid # Live schema controls reference
│   └── <descriptive_name>/index.liquid # Custom only when no canonical section fits
├── components/                       # Developer partials (no schema)
├── blocks/                           # Standalone reusable blocks (optional)
├── locales/                          # Translation files
├── config/
│   ├── settings_schema.json          # Theme setting definitions
│   └── settings_data.json            # Current setting values
└── assets/                           # CSS + JS served via | asset_url
```

18 required templates: `navbar`, `footer`, `home_page`, `category_page`, `category`, `collection`, `collection_page`, `shop_page`, `product`, `post`, `post_page`, `cart_page`, `page`, `enrollment_pack`, `join_page`, `library`, `library_navbar`, `medium`.

### Schema Controls Reference page — canonical control vocabulary

A live, browsable reference of every schema control lives at `page/schema-reference/index.liquid` + `sections/schema_reference/index.liquid`. After pushing the theme, visit `/pages/schema-reference` on your Fluid store.

**Agents: this page is the single source of truth for control types.** Before writing or modifying a section schema:

1. Decide what kind of value you need (text / number / color / media / resource / layout).
2. Open `sections/schema_reference/index.liquid` in your cloned base theme working directory and find the card for that control type. Each card has:
   - How it renders in the Fluid builder (so you can match editor expectations)
   - The exact schema snippet to copy
   - The exact Liquid accessor snippet to copy
3. If unsure — especially around `color` vs theme-color dropdowns, or resource pickers — stop and ask the user. Do **not** guess control names. Unsupported types (`number`, `article`, `video_url`, `inline_richtext`, etc.) break the editor silently.

**Key patterns this page encodes:**

- `richtext` for all visible copy (never `text`/`textarea`)
- `range` for numeric inputs (never `number`)
- `select + "options": "background_colors"` for theme-aware colors (never raw `color`)
- Singular resource pickers return an OBJECT in Fluid (not an ID) — access via `.title`/`.url`/etc.
- List resource pickers cap at 24 items

When you update [references/schema-settings-reference.md](references/schema-settings-reference.md), also update the corresponding card in the live reference page so the two stay in sync.

### layouts/theme.liquid

```liquid
<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  {{ content_for_header }}
</head>
<body>
  {% section 'main_navbar' %}
  <main>
    {% content_for_layout %}
  </main>
  {% section 'main_footer' %}
</body>
</html>
```

### DO NOT REPLACE

| Section                 | Why                                                                  |
| ----------------------- | -------------------------------------------------------------------- |
| `sections/main_product` | Wired to Fluid's product object (name, price, variants, add-to-cart) |
| Cart templates          | Fluid-controlled                                                     |
| Checkout                | Fluid-controlled                                                     |

### Fluid Liquid objects

```liquid
{{ product.name }}
{{ product.price | money }}
{{ product.description }}
{{ product.images }}
{{ company.name }}
{{ company.logo_url }}
{{ 'key' | t }}
{{ image.url | img_url: 'w-600,h-400,f-auto,q-80' }}
```

---

## Related Skills

- [theme-refine.md](../theme-refine/SKILL.md) — Pixel-perfect QA pass after clone. Canonical source of truth for Section Shell + Container patterns, divider-block pattern, canonical block primacy, media_picker fallback, and template-destroy preset refresh workflow.
- The `fluid theme` CLI (see the theme-review skill) — command semantics for
  pull/push; inside Mist, use `start_preview` for dev and bounded `run_cli` for
  one-shot commands.
- [references/dev-preview-visual-diff.md](references/dev-preview-visual-diff.md) —
  shared fresh-machine managed-browser visual-parity protocol used by clone
  and refine.
- **fluid-product-admin-import** — For importing products, categories, and admin settings (run before theme clone).
- [Onboarding Pre-Fill](../../onboarding/onboarding-prefill/SKILL.md) — For pre-filling KYC/onboarding forms.
