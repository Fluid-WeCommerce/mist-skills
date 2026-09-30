# Fluid Builder — Block & Section Specification
**Version:** 3.0 (September 2026)
**Status:** Build reference for AI agents and theme developers. It standardizes *which controls a block or section gets, their IDs, labels, defaults and order*. For platform behavior (what the editor, renderer and schema engine actually do), the Fluid docs at [docs.fluid.app/themes](https://docs.fluid.app/themes/overview) are authoritative. If this document and the docs disagree about platform behavior, follow the docs and flag the conflict.
**Audience:** AI coding agents, theme developers, product/QA
**Built from:** a survey of every section and block schema in Yoli, Make Wellness, Puralta, TM3 United and Oliabo (1,148 section schemas, about 3,400 inline block definitions), plus the Fluid theme docs, `fluid-theme-presets-v2.md`, `themes_settings_updates_3-19-26.md` (Section Baseline) and `theme-metafields-skill.md`.

---

## 0. How to Read This Document

Each block is documented in two parts:

1. **Plain-English controls:** what the editor sees, in builder order. Use it for product decisions, QA and onboarding.
2. **Schema JSON:** the exact implementation. Copy it verbatim unless a delta says otherwise.

Blocks are organized into **families**. Every family has a **canonical block** with a full schema. Close variants are documented as **deltas**: "same as X, plus/minus these settings". Build a variant by copying the canonical schema and applying its delta. Don't redesign it from scratch. That is how agent-built blocks stay 90–95% consistent.

Shared control groups (prefix `CG-`) are defined once in §5 and referenced by name. When a block says "CG-BORDER", paste that group's JSON at that position.

### Precedence when rules collide

1. **Platform behavior:** docs.fluid.app wins.
2. **An existing theme's conventions:** when you edit an existing theme, match its token names, class prefixes and rendering style, and **never rename a shipped setting ID**. Renaming disconnects saved content.
3. **This document:** applies to every new section and block, and to any theme without a conflicting convention.

### Relevant Fluid docs (read these before building)

| Topic | Doc |
|---|---|
| Inline vs standalone blocks, components | [blocks-and-components](https://docs.fluid.app/themes/blocks-and-components) |
| Schema fields, setting types, option groups | [schema-components](https://docs.fluid.app/themes/schema-components) |
| `settings_schema.json` shape, typography presets | [settings-schema](https://docs.fluid.app/themes/settings-schema) |
| Linking editor presets to CSS variables | [linked-css-variable-presets](https://docs.fluid.app/themes/linked-css-variable-presets) |
| Settings → data → CSS variable flow | [root-theme-configuration](https://docs.fluid.app/themes/root-theme-configuration) |
| Liquid variables per template | [theme-variables](https://docs.fluid.app/themes/theme-variables) |
| Layout containers for whole sections | [section-slots](https://docs.fluid.app/themes/section-slots) |
| Affiliate names/images/links in cached pages | [affiliate-hydration](https://docs.fluid.app/themes/affiliate-hydration) |
| Responsive image/video output | [media-tag](https://docs.fluid.app/themes/media-tag) |
| Things that break silently | [common-pitfalls](https://docs.fluid.app/themes/common-pitfalls) |
| Product/variant metafields in sections | `/themes/theme-metafields-skill.md` (local) |

Tip: append `.md` to any docs.fluid.app URL to get raw markdown. `https://docs.fluid.app/llms.txt` is the full index.

---

## 1. Build Workflow for AI Agents

Follow these steps in order for every new section.

1. **Read the target theme first.** Open `config/settings_schema.json` and `layouts/theme.liquid`. Confirm the option groups exist (`background_colors`, `font_families`, `text_presets`; see §3) and note the CSS token names (`--clr-*`, `--ff-*`). Open one existing modern section to copy its class-prefix and `{% style %}` conventions.
2. **Classify the section** (§15):
   - **Content section:** editor-composed, uses blocks.
   - **Resource section:** product, enrollment pack, post or collection data. Zero blocks. See §16.
   - **Layout container:** arranges other sections. See §17.
3. **Pick block families** from the taxonomy (§6). Use canonical types and names. Never invent a synonym (`subhead`, `lede`, `kicker`…) for an existing type.
4. **Copy canonical schemas** from §7–§14 and apply deltas. Keep setting order exactly as written.
5. **Add the Section Base** (§15.1) *after* the section's content settings. The Section Shell group always comes last.
6. **Render** per §18: `{{ block.fluid_attributes }}` on every block, scoped `{% style %}`, palette values straight into CSS, `media_tag` for media, guards on every optional value.
7. **Make it responsive in CSS only** (§18.6). No schema setting may exist for mobile or tablet.
8. **Write a preset** with realistic blocks and defaults. New sections and blocks must never render blank.
9. **Validate:** `fluid theme lint --json`, then `fluid theme dev`. Check the browser console and test at 375 / 768 / 1280 px.

---

## 2. Platform Ground Rules

These are facts about how Fluid works, or firm decisions for this spec. They override older guidance.

### 2.1 Inline blocks are first-class. Standalone blocks are optional.

| | Inline block (**default**) | Standalone theme block (optional) |
|---|---|---|
| Where the schema lives | Inside the section's `{% schema %}` `"blocks"` array | `blocks/<name>/index.liquid` |
| How it renders | `{% for block in section.blocks %}{% case block.type %}…` | `{% content_for 'blocks' %}` |
| Reuse across sections | Copy the canonical schema into each section | Referenced by `{ "type": "name" }` or `@theme` |
| Child blocks | No | Yes, two levels |
| Used by the 5 surveyed themes | **100% of sections** | 0 sections. Makewellness/Puralta/TM3 ship a `blocks/` folder that nothing references. |

Build inline unless the theme already uses standalone blocks or the user asks for them. The schemas in this document are written for inline use. Appendix A shows how to package the same schema as a standalone block. Many people find standalone blocks confusing, so never mix the two render methods for the same block type in one section.

### 2.2 Resource sections have zero blocks

Sections that render a resource have **no blocks**. These are product headers/PDPs, enrollment-pack headers, blog-post headers, and collection/category mains. They render resource data (`product.*`, `enrollment_pack.*`, `post.*`) and fill gaps with **metafields** read by literal path (`product.metafields.<namespace>.<key>`). Blocks are stored per template, so a block-driven PDP needs one template per product. The surveyed themes have 36 (Yoli), 20 (Make Wellness) and 12 (Oliabo) product templates for exactly this reason. See §16.

*Replaces the old "Two-Zone Section Pattern."*

### 2.3 No mobile or tablet settings in any schema

Editing is desktop-only. Every tablet and mobile adaptation is automatic, in CSS:
- type scaling
- padding scaling
- column collapse
- stacking
- tap targets

Never add `*_mobile`, `*_tablet`, `*_desktop`, "hide on mobile", "mobile image" or "mobile alignment" settings. See §18.6 for the required responsive behavior.

### 2.4 Colors and fonts come from theme option groups. Palette only.

Every color control is a `select` with `"options": "background_colors"`. Every font control is a `select` with `"options": "font_families"`. The builder shows the theme's presets as swatch + label (Puralta is the reference implementation). There is **no free color picker on blocks**. If an editor needs a new color, they add a preset to the theme palette, and it appears in every dropdown. Raw `color` and `color_background` settings are **not** used in section or block schemas. The rich-text toolbar's own color and style menus are unaffected by this rule.

### 2.5 Things Fluid does for you, and things it doesn't

- Fluid adds editor attributes to each **section** wrapper. Don't output `section.fluid_attributes` yourself.
- You must output `{{ block.fluid_attributes }}` on each **block**'s outermost element, or the block can't be selected in the editor.
- These picker types resolve to Liquid objects: `product`, `variant`, `collection`, `category`, `enrollment_pack`, `media`, `link_list`, `product_list`. Every other type, including `post` and `collection_list`, gives you the saved identifier only.
- `padding` and `corner_radius` return structured values (`.top/.right/.bottom/.left`, `.tl/.tr/.br/.bl`). A side can be a number **or** a linked `var(--…)` string. Handle both (§18.3).
- An empty value interpolated into CSS drops the whole declaration silently. Always `| default:`.
- **Presets refill empty sections on every render.** A section whose blocks were all deleted shows its preset blocks again. Render an intentional empty state if "nothing" must be possible.
- `fluid theme lint` validates schemas. It doesn't render. A clean lint isn't a working page.

---

## 3. Theme Foundation Contract (`config/settings_schema.json`)

The block schemas in this document depend on these theme-level pieces. If a theme lacks one, add it to the theme **before** building sections. See [settings-schema](https://docs.fluid.app/themes/settings-schema), [linked-css-variable-presets](https://docs.fluid.app/themes/linked-css-variable-presets) and `fluid-theme-presets-v2.md` for the full design-token spec.

### 3.1 Required option groups

An option group is created by attaching `option_group` metadata to settings in `settings_schema.json`. Each setting contributes one choice. Sections reference the group by its **plain ID** (`"options": "background_colors"`). Never use a Liquid expression or an object.

| Option group | Declared on | Choice value format | Used by |
|---|---|---|---|
| `background_colors` | `color_background` settings in group `color_schema`, plus one utility entry, None (§3.2) | `var(--clr-primary)`, `transparent` | **Every** color select: text, background, border, overlay, icon, hover |
| `font_families` | `font_picker` settings (group `typography` or `fonts`) | `var(--ff-heading)`, `var(--ff-body)`, `var(--ff-accent)` | Font Family overrides, button font |
| `text_presets` | the size setting of each typography preset in group `typography` | class name, e.g. `text-h2` | Every **Text Style** select |

Reference declarations, from Puralta:

```json
{ "type": "color_background", "id": "color_primary", "label": "Umber", "default": "#47342A",
  "info": "Primary dark brand fill.",
  "option_group": { "id": "background_colors", "label": "Umber", "value": "var(--clr-primary)" } }

{ "type": "font_picker", "id": "font_family_heading", "label": "Heading Font", "default": "Instrument Sans",
  "option_group": { "id": "font_families", "label": "Heading", "value": "var(--ff-heading)" } }

{ "type": "range", "id": "font_size_h2", "label": "H2", "min": 26, "max": 56, "step": 1, "unit": "px", "default": 36,
  "role": "heading", "font_family_ref": "font_family_heading", "font_weight_ref": "font_weight_bold",
  "option_group": { "id": "text_presets", "label": "H2 · Section Heading", "value": "text-h2" } }
```

Rules:
- **Values must be valid CSS for how sections use them.** Sections print color values straight into CSS (`color: {{ block.settings.color }};`). Class-name values like `bg-primary` produce invalid CSS; Make Wellness's groups have this bug. Colors and fonts are always `var(--…)`. Text Style values are always class names.
- A select's `default` **must be one of the group's values**. A default outside the group renders, but once the editor changes it they can never select it again.
- An explicit `options` array overrides the group. Don't paste inline palette lists into sections: Oliabo has 835 of them, and they drift.
- Name the preset groups exactly `typography`, `color_schema`, `padding` and `corner_radius`. The editor's linked preset menus match these names exactly, and they're case-sensitive. Puralta/TM3's `border_radius` and `spacing` group names don't match.

### 3.2 Palette roles every theme provides

Canonical defaults in this document use these tokens. A theme may have more colors, but never fewer. If a theme uses different token names, substitute its names throughout.

| Token | Role | Notes |
|---|---|---|
| `var(--clr-primary)` | Main brand color | Default button fill |
| `var(--clr-secondary)` | Supporting brand color | Default hover fill |
| `var(--clr-accent)` | Highlight | |
| `var(--clr-body)` | Default text | |
| `var(--clr-muted)` | Secondary text, captions, fine print | |
| `var(--clr-white)` / `var(--clr-black)` | Pure neutrals | |
| `var(--clr-light)` / `var(--clr-dark)` | Light and dark surfaces | |
| `var(--clr-success)` / `var(--clr-error)` | Status | |
| `transparent` | **Utility:** "None" | Backgrounds, overlays, borders. See below |

**None** is the one non-palette choice. It's added to `background_colors` from a separate settings group so it doesn't clutter the palette:

```json
{ "name": "color_utilities", "settings": [
  { "type": "color_background", "id": "color_util_none", "label": "None", "default": "#00000000",
    "info": "Utility choice. Renders transparent.",
    "option_group": { "id": "background_colors", "label": "None", "value": "transparent" } }
] }
```

- **Where it appears:** every color dropdown, because every color select shares the one `background_colors` group. A setting can contribute to only one option group, so there's no way to show None in background dropdowns and hide it from text dropdowns.
- **What it means:** transparent. That's right for backgrounds, overlays and borders. It's never a sensible text or icon color, so text/icon color defaults are always a real preset (Primary, Body, Muted…).
- **Why it's needed:** a select can only return to a value that's in its option list. Without a None entry, a background changed from its `transparent` default could never be cleared again. Puralta has this problem: 432 selects default to `transparent`, which isn't in its group.

> ⚠️ **Verify in the editor** the first time you add it to a theme. The swatch should render and the choice should be selectable. Don't declare a CSS variable for it, so it stays out of the rich-text color menu.

### 3.3 Required text presets (`text_presets`)

Each preset is a size setting in the `typography` group. Give each one `role`, `unit: "px"`, `font_family_ref`, `font_weight_ref` and an `option_group` entry. Sizes, ranges and line heights follow `fluid-theme-presets-v2.md` §2a–2b. Responsive behavior is in §3.4.

| Setting ID | Class value (`text_presets`) | Label | Desktop default | Allowed range | Responsive | Line height |
|---|---|---|---|---|---|---|
| `font_size_h1` | `text-h1` | H1 · Page Title | 48px | 36–72 | scales | 1.15 |
| `font_size_h2` | `text-h2` | H2 · Section Heading | 36px | 26–56 | scales | 1.15 |
| `font_size_h3` | `text-h3` | H3 · Subsection | 30px | 20–40 | scales | 1.20 |
| `font_size_h4` | `text-h4` | H4 · Card Title | 24px | 16–36 | scales | 1.20 |
| `font_size_h5` | `text-h5` | H5 · Minor Heading | 20px | 16–36 | scales | 1.25 |
| `font_size_h6` | `text-h6` | H6 · Small Heading | 16px | 14–36 | flat at default | 1.30 |
| `font_size_body_lg` | `text-body-lg` | Body Large · Subheading | 20px | 16–36 | scales | 1.50 |
| `font_size_body` | `text-body` | Body | 16px | **16–20** | flat | 1.60 |
| `font_size_body_sm` | `text-body-sm` | Body Small | 14px | **12–15** | flat | 1.50 |
| `font_size_eyebrow` | `text-eyebrow` | Eyebrow (uppercase, tracked) | 12px | **11–15** | flat | 1.20 |
| `font_size_label` | `text-label` | Label · Badge | 12px | **11–14** | flat | 1.20 |
| `font_size_caption` | `text-caption` | Caption | 12px | **11–14** | flat | 1.40 |
| `font_size_quote` | `text-quote` | Quote | 20px | 16–32 | scales | 1.40 |
| `font_size_button` | `text-button` | Button | 16px | **14–24** | flat | 1.20 |
| `font_size_fine_print` | `text-fine-print` | Fine Print | 11px | **11–14** | flat | 1.40 |

"Scales" and "flat" describe the default size. The actual rule is size-based (§3.4): a preset scales whenever its desktop size is larger than Body. A merchant who sets H6 to 20px therefore gets scaling on H6.

**Bold ranges** are raised above `fluid-theme-presets-v2.md` to meet readability best practice:
- Body text is at least 16px: Google Material recommends 16sp minimum body text, and Apple's HIG recommends 17pt.
- No readable text goes below 11px, which is Apple's minimum legible size.
- Buttons are at least 14px.

Update the presets doc to match when it's next revised.

Each class is defined once in the theme's global CSS. It reads the editor's per-preset variables first, with the referenced setting's variable as the fallback. That way, repointing a preset in the editor moves every block using it:

```css
.text-h2 {
  font-family: var(--font_size_h2_font_family, var(--ff-heading));
  font-weight: var(--font_size_h2_font_weight, var(--fw-bold));
  font-size: var(--font_size_h2);     /* redefined per breakpoint in layouts/theme.liquid (§3.4) */
  line-height: 1.15;
}
```

`text-button` uses `"font_family_ref": "font_family_body"` and `"font_weight_ref": "font_weight_semibold"`. `text-eyebrow` adds `text-transform: uppercase; letter-spacing: .08em;` in CSS.

### 3.4 Responsive Typography (Automatic Scaling)

This consolidates `fluid-theme-presets-v2.md` §2b so agents have it in one place. It's fully automatic: **corporate sets the desktop size only, and nothing about tablet or mobile type exists in any schema.**

**What editors control:** Font Family, Font Weight, and the desktop Font Size within the preset's allowed range, in whole pixels.
**What's automatic:** tablet and mobile font sizes, and all line heights. Family and weight are identical at every breakpoint.

**Breakpoints and multipliers:**

| Breakpoint | Viewport width | Multiplier on the desktop size |
|---|---|---|
| Desktop | ≥ 1024px | 1.0 (the value corporate sets) |
| Tablet | 768–1023px | × 0.80 |
| Mobile | ≤ 767px | × 0.65 |

**The rule:** scale by the multiplier, but never below the preset's **floor** and never above its desktop size:

```
size(breakpoint) = min( desktop, max( round(desktop × multiplier), floor ) )
floor            = round( Body × step ratio )
```

| Preset | Step ratio | Floor at Body 16px |
|---|---|---|
| H1 | × 1.802 | 29px |
| H2 | × 1.602 | 26px |
| H3 | × 1.424 | 23px |
| H4 | × 1.266 | 20px |
| H5, Body Large, Quote, custom presets | × 1.125 | 18px |
| H6 | × 1.0 | 16px |
| Body, Body Small, Eyebrow, Label, Caption, Button, Fine Print | — | not scaled (flat) |

- The step ratios are a **Major Second (1.125) modular scale** anchored on Body: each heading level is one step above the next. On small screens, multiplication alone collapses the hierarchy: at the defaults, H5 would drop to 13px, below the 16px body text. The floors keep every heading visibly larger than body text and each level larger than the one below it.
- This matches standard practice for fluid and responsive type (Utopia's fluid scales, for example):
  - use a **tighter ratio on small screens** than on desktop
  - shrink large headings a lot and small headings very little
  - body text is never scaled down
- **Presets at or below Body size stay flat** automatically, because every floor is ≥ Body and the result is capped at the desktop size. Scaling compact text would make it unreadable.
- Line heights are unitless and fixed per preset (§3.3). They scale with the font size and need no breakpoint rules, and editors can't change them.
- **Form inputs, selects and textareas** are always at least 16px on mobile, whatever preset they use. iOS zooms the page when an input's text is smaller.

**Computed sizes at the defaults (Body 16px):**

| Preset | Desktop | Tablet (× 0.80) | Mobile (× 0.65) |
|---|---|---|---|
| H1 | 48 | 38 | 31 |
| H2 | 36 | 29 | 26 (floor) |
| H3 | 30 | 24 | 23 (floor) |
| H4 | 24 | 20 (floor) | 20 (floor) |
| H5 / Body Large / Quote | 20 | 18 (floor) | 18 (floor) |
| H6, Body, Body Small, Eyebrow, Label, Caption, Button, Fine Print | desktop value | same | same |

At the defaults, the mobile headings step 31 → 26 → 23 → 20 → 18 → 16. That's a clean hierarchy in the 28–40px mobile headline range common in web font-size guidance.

**Custom presets** follow the same formula with the 1.125 floor. Merchants can add presets such as "Hero Display" or "Price". Built-in presets cap at 72px. A custom preset can exceed that ("Exceed 72px limit" in theme settings) and still scales: 120px becomes 96px on tablet and 78px on mobile.

**CSS output (in `layouts/theme.liquid`).** Declare each preset's variable **under its setting ID**, then redefine the same variable per breakpoint:

```liquid
{%- style -%}
  {%- assign body = settings.font_size_body | default: 16 -%}

  {%- comment -%} One block like this per scaling preset. Floor = round(body × step ratio) {%- endcomment -%}
  {%- assign h1 = settings.font_size_h1 | default: 48 -%}
  {%- assign h1_floor = body | times: 1.802 | round -%}
  {%- assign h1_t = h1 | times: 0.8 | round | at_least: h1_floor | at_most: h1 -%}
  {%- assign h1_m = h1 | times: 0.65 | round | at_least: h1_floor | at_most: h1 -%}

  {%- assign h2 = settings.font_size_h2 | default: 36 -%}
  {%- assign h2_floor = body | times: 1.602 | round -%}
  {%- assign h2_t = h2 | times: 0.8 | round | at_least: h2_floor | at_most: h2 -%}
  {%- assign h2_m = h2 | times: 0.65 | round | at_least: h2_floor | at_most: h2 -%}

  :root {
    --font_size_body: {{ settings.font_size_body }}px;
    --font_size_h1: {{ settings.font_size_h1 }}px;
    --font_size_h2: {{ settings.font_size_h2 }}px;
    /* …one line per preset in §3.3, including the flat ones */
  }
  @media (max-width: 1023px) { :root { --font_size_h1: {{ h1_t }}px; --font_size_h2: {{ h2_t }}px; } }
  @media (max-width: 767px)  { :root { --font_size_h1: {{ h1_m }}px; --font_size_h2: {{ h2_m }}px; } }

  @media (max-width: 767px) { input, select, textarea { font-size: max(16px, 1em); } }
{%- endstyle -%}
```

Why redefine the variable instead of creating separate `-tablet`/`-mobile` variables:
1. The `:root` line `--font_size_h1: {{ settings.font_size_h1 }}px` is what makes the editor offer H1 as a linked preset. A setting with no variable is never offered.
2. Rich text styled from the toolbar saves `var(--font_size_h1)`. Because the variable itself changes per breakpoint, toolbar-styled text scales too, with no extra classes. This is the responsive-preset approach the [linked presets docs](https://docs.fluid.app/themes/linked-css-variable-presets) describe.

**Rules for agents building blocks and sections:**
- Size text **only** through a `text-*` class (from the block's Text Style) or `var(--font_size_*)`. Never hard-code a `font-size` in px, and never use `clamp()`/`vw` for preset text; both break the link to the theme.
- Never add a mobile or tablet font-size setting.
- **Manual Overrides** follow the same formula, using the 1.125 floor (Body × 1.125); the implementation is in §18.5.
- Section-specific display text (e.g. a giant hero number) should use a preset such as `text-h1` or a custom preset. Don't invent a one-off size.
- Heading size never depends on the heading level. An H3 tag can use the H1 Text Style.

### 3.5 Other theme-level tokens blocks rely on

| Token(s) | Group | Used by |
|---|---|---|
| `--padding-*` settings | `padding` | Linked presets inside `padding` controls |
| `--rounded-*` settings (None 0, SM 4, MD 8, LG 16, XL 24, Full 9999) | `corner_radius` | Linked presets inside `corner_radius` controls |
| `--shadow-sm / md / lg / xl` | CSS only (`fluid-theme-presets-v2.md` §7) | Card Shadow selects |
| `--fw-regular / medium / semibold / bold` | weight settings (group `font_weights`) | Preset weight references |
| `button_hover_style` select | theme group for buttons (Puralta/TM3: `button_hover`) | The "Theme Default" hover choice on every button (§8.1) |
| `--radius-media` (default media corner radius) | group `corner_radius` | Fallback when a media block's Corner Radius is blank |

Every setting whose value should be linkable **must** have a CSS custom property declared in `layouts/theme.liquid` inside `{% style %}` (`--x: {{ settings.id }}`). A setting without one never appears as a preset.

---

## 4. Schema Conventions

### 4.1 Choosing a setting type

| Need | Type | Notes |
|---|---|---|
| Short single-line text: heading, eyebrow, label, button text, name | `text` | Headings are `text` + a Heading Level select, not `richtext` (§7.1) |
| Multi-line plain text: quote without formatting, one-item-per-line lists | `textarea` | Say "one per line" in `info` |
| Formatted copy: body, answers, descriptions | `richtext` | Defaults are plain HTML (`<p>…</p>`). **Never put inline `style=` in a richtext default**; it silently overrides the block's style settings |
| A destination | `url` | Setting ID is always `link` |
| 2–4 visible choices: style, alignment, position | `radio` | Renders as pills |
| 5+ choices, or any option group | `select` | |
| On/off | `checkbox` | Label states the "on" meaning |
| Bounded number with a unit | `range` | Always give `min`, `max`, `step`, `unit`, `default` |
| Display values like "10K", "−57 lbs", "4.9" | `text` | Never `range`. Ranges can't hold units or signs |
| Four-sided spacing | `padding` | Values may be numbers or `var()` (§18.3) |
| Four-corner radius | `corner_radius` | Same |
| Image | `image_picker` | Alt text lives **in the picker**. Never add a separate alt-text field |
| Uploaded video | `video_picker` | See §9.2 on the coming combined picker |
| Image-or-video from the Fluid media library | `media_picker` | Renders via `<fluid-media-widget>` (§9.3) |
| Products, packs, collections, menus | `product`, `variant`, `product_list`, `enrollment_pack`, `collection`, `category`, `link_list` | Resolved to Liquid objects |
| Group headers | `header` with `content` | One per logical group |

Not used in section or block schemas: raw `color`/`color_background` (palette-only rule), `font_picker` (theme settings only), `html` except in `custom_liquid`, and the `border` composite type (split it into Border toggle, width and palette color instead).

`plaintext` is being introduced as a setting type. Until the Fluid docs describe it, keep using `text`.

### 4.2 Standard setting IDs and labels

Use these IDs and labels exactly. Labels are Title Case.

| Purpose | ID | Type | Label |
|---|---|---|---|
| Primary text of a text block | `text` | `text` / `richtext` | Text |
| Button/link label | `text` | `text` | Button Text / Link Text |
| Destination | `link` | `url` | Link |
| New tab | `open_new_tab` | `checkbox` | Open in New Tab |
| Semantic heading level | `heading_tag` | `select` | Heading Level |
| Typography preset | `text_style` | `select` → `text_presets` | Text Style |
| Text color | `color` | `select` → `background_colors` | Color |
| Background color | `background_color` | `select` → `background_colors` | Background Color |
| Alignment | `alignment` | `radio` | Alignment |
| Readable width | `max_width` | `select` | Max Width |
| Visual variant | `style` | `radio` | Style |
| Manual typography switch | `override_typography` | `checkbox` | Override Text Style |
| Font family override | `font_family` | `select` → `font_families` | Font Family |
| Font size override | `font_size` | `range` (px) | Font Size |
| Font weight override | `font_weight` | `select` | Font Weight |
| Border on/off | `show_border` | `checkbox` | Show Border |
| Border width | `border_width` | `range` (px) | Border Width |
| Border color | `border_color` | `select` → `background_colors` | Border Color |
| Corner radius | `border_radius` | `corner_radius` | Corner Radius |
| Inner padding | `padding` | `padding` | Padding |
| Image | `image` | `image_picker` | Image |
| Video | `video` | `video_picker` | Video |
| Aspect ratio | `aspect_ratio` | `select` | Aspect Ratio |
| Media fit | `fit` | `radio` | Fit |
| Focal point | `object_position` | `select` | Focal Point |
| Icon preset | `icon` | `select` | Icon |
| Custom icon | `icon_image` | `image_picker` | Custom Icon |
| Person name | `name` | `text` | Name |
| Person role/location | `role` | `text` | Role or Location |
| Photo of a person | `avatar` | `image_picker` | Photo |
| Star rating | `rating` | `range` 0–5 | Rating |
| Emphasized item | `featured` | `checkbox` | Featured |
| Hover effect | `hover_effect` | `select` | Hover Effect |
| Section-level prefixed copies | `button_*`, `card_*`, `container_*`, `section_*` | | Prefix the label too ("Card Padding") |

Never use: `show` / `visible` / `enabled` toggles on inline blocks (deleting the block hides it), numbered series (`feature_1…feature_6`, `link_1_url…link_12_url`; use repeatable blocks), `url` vs `link` vs `button_url` synonyms, `ghost` (use `text`), `new_tab`, `open_in_new_tab`, `is_verified`/`show_verified_badge` (use `verified`), `star_rating`/`stars`/`star_count` (use `rating`), `author`/`author_name` (use `name`).

### 4.3 Block type names and display names

- `type` is snake_case and singular: `heading`, `faq_item`, `product_card`. Use the canonical names in §6. Aliases found in the surveyed themes are listed there for migration only.
- `name` is Title Case and is what editors see in Layers: "Heading", "FAQ Item", "Product Card".
- Declare block types in picker-friendly order within a section's `"blocks"` array: text blocks → action blocks → media → content items → commerce → utility (`custom_liquid` last).

### 4.4 Control order inside a block

Every block's settings follow this header order. Omit groups that don't apply; never reorder them.

1. **Content:** the text, media or resource the block shows. No header needed if it's the only group.
2. **Style:** Text Style / Color / Alignment / Max Width, or the block's visual variant.
3. **Manual Overrides:** the `override_typography` switch plus the controls it reveals.
4. **Media Display:** aspect, fit, focal point, overlay.
5. **Shape:** border and corner radius (and padding/background where the block is a box).
6. **Hover:** buttons and link-bearing blocks.
7. **Layout:** button width only.
8. **Link:** for blocks where the link is secondary (images, icons, cards).
9. **Visibility:** the optional affiliate visibility control (§14.1).

### 4.5 Order inside a section

Content settings → **Layout** → **Card / Item Style** (section-level styling for repeated items) → **Container** → **Section Shell**. Section Shell is always last, and **Section Corner Radius is the last setting in the schema**. See §15.1.

### 4.6 Conditional controls

Use `visible_if` to hide controls that don't apply. The syntax is a Liquid expression string:

```json
"visible_if": "{{ block.settings.show_border }}"
"visible_if": "{{ block.settings.hover_effect == 'colors' }}"
"visible_if": "{{ section.settings.background_image != blank }}"
"visible_if": "{{ block.settings.overlay_opacity > 0 }}"
```

All four forms (`block.settings`, `section.settings`, `==`, `>`, `or`) are used in production themes.

### 4.7 Limits

- `"limit": 1` on block types that can appear once per section, such as a section's intro heading or a pull quote.
- Repeatable items get a practical `limit` (§12 gives each family's recommendation). Use `max_blocks` at section level when the layout breaks past a total count.
- If the markup fetches a block with `section.blocks | where: 'type', 'heading' | first`, that type **must** have `limit: 1`. Otherwise the extra blocks silently don't render.

### 4.8 `info` text

Add `info` whenever a merchant can't infer behavior from the label. That covers recommended image sizes, what "blank" does, which metafield feeds a row, what "Theme Default" means, and units. Keep it to one sentence.

---

## 5. Shared Control Groups

Paste these groups wherever a block spec references them. `{…}` placeholders are the only values a block may change, and each block spec says what to put there. Inside **section-level** copies, replace `block.settings` with `section.settings` in `visible_if` and add the ID prefix (e.g. `card_`).

### CG-TEXT-STYLE: preset-first typography

- **Text Style:** a theme preset (H1 … Fine Print). The preset sets family, size, weight, line height and responsive scaling.
- **Color:** a theme palette swatch. Each block type has its own default preset: Primary for headings, eyebrows and quotes; Body for body text; Muted for fine print.
- **Alignment:** Auto (follows the section) / Left / Center / Right.

```json
{ "type": "header", "content": "Style" },
{ "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "{text_style}",
  "info": "Theme typography preset. Edit presets in Theme Settings → Typography." },
{ "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "{color|var(--clr-body)}" },
{ "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
  "options": [
    { "value": "inherit", "label": "Auto" },
    { "value": "left", "label": "Left" },
    { "value": "center", "label": "Center" },
    { "value": "right", "label": "Right" }
  ] }
```

### CG-MAX-WIDTH

```json
{ "type": "select", "id": "max_width", "label": "Max Width", "default": "none",
  "info": "Limits line length for readability.",
  "options": [
    { "value": "none", "label": "Full Width" },
    { "value": "75ch", "label": "Wide" },
    { "value": "60ch", "label": "Medium" },
    { "value": "40ch", "label": "Narrow" }
  ] }
```

### CG-TYPE-OVERRIDES: the "Manual Settings" escape hatch

Off by default. When on, it reveals Font Family / Font Size / Font Weight, which replace the Text Style's values. Tablet and mobile sizes still scale automatically from the desktop size (§3.4).

```json
{ "type": "header", "content": "Manual Overrides" },
{ "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false,
  "info": "Leave off to follow the Text Style preset. Use only for intentional one-offs." },
{ "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "{font|var(--ff-body)}",
  "visible_if": "{{ block.settings.override_typography }}" },
{ "type": "range", "id": "font_size", "label": "Font Size", "min": {min}, "max": {max}, "step": 1, "unit": "px", "default": {size},
  "info": "Desktop size. Tablet and mobile scale automatically.",
  "visible_if": "{{ block.settings.override_typography }}" },
{ "type": "select", "id": "font_weight", "label": "Font Weight", "default": "{weight|400}",
  "visible_if": "{{ block.settings.override_typography }}",
  "options": [
    { "value": "300", "label": "Light" },
    { "value": "400", "label": "Regular" },
    { "value": "500", "label": "Medium" },
    { "value": "600", "label": "Semi Bold" },
    { "value": "700", "label": "Bold" },
    { "value": "800", "label": "Extra Bold" }
  ] }
```

Size ranges by block: heading 16–120 (default 36), body 12–32 (16), eyebrow/label 11–20 (12), quote 14–48 (20), button 14–24 (16). No block allows text below 11px (§3.3).

### CG-BORDER: on/off border plus corner radius

There's no border-style (solid/dashed/dotted) choice. A border is either on or off.

```json
{ "type": "header", "content": "Shape" },
{ "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false },
{ "type": "range", "id": "border_width", "label": "Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
  "visible_if": "{{ block.settings.show_border }}" },
{ "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
  "visible_if": "{{ block.settings.show_border }}" },
{ "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" }
```

A blank Corner Radius falls back to the theme default for that element (`--radius-media` for media, 4px for blocks, 8px for cards).

### CG-BOX: a block that is a visible box

Use it for badges, announcements, callouts and a standalone container. It's CG-BORDER with a background and padding in front.

```json
{ "type": "header", "content": "Shape" },
{ "type": "select", "id": "background_color", "label": "Background Color", "options": "background_colors", "default": "{bg|transparent}" },
{ "type": "padding", "id": "padding", "label": "Padding" },
{ "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false },
{ "type": "range", "id": "border_width", "label": "Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
  "visible_if": "{{ block.settings.show_border }}" },
{ "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
  "visible_if": "{{ block.settings.show_border }}" },
{ "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" }
```

### CG-MEDIA-DISPLAY: shared by image, video, media, gallery and card images

```json
{ "type": "header", "content": "Media Display" },
{ "type": "select", "id": "aspect_ratio", "label": "Aspect Ratio", "default": "{ratio|auto}",
  "options": [
    { "value": "auto", "label": "Original" },
    { "value": "1/1", "label": "Square (1:1)" },
    { "value": "4/5", "label": "Portrait (4:5)" },
    { "value": "3/4", "label": "Portrait (3:4)" },
    { "value": "2/3", "label": "Portrait (2:3)" },
    { "value": "9/16", "label": "Vertical (9:16)" },
    { "value": "4/3", "label": "Landscape (4:3)" },
    { "value": "3/2", "label": "Landscape (3:2)" },
    { "value": "16/9", "label": "Widescreen (16:9)" },
    { "value": "21/9", "label": "Ultrawide (21:9)" }
  ] },
{ "type": "radio", "id": "fit", "label": "Fit", "default": "cover",
  "info": "Cover fills the frame and may crop. Contain shows the whole image.",
  "options": [ { "value": "cover", "label": "Cover" }, { "value": "contain", "label": "Contain" } ] },
{ "type": "select", "id": "object_position", "label": "Focal Point", "default": "center",
  "visible_if": "{{ block.settings.fit == 'cover' }}",
  "options": [
    { "value": "center", "label": "Center" },
    { "value": "top", "label": "Top" },
    { "value": "bottom", "label": "Bottom" },
    { "value": "left", "label": "Left" },
    { "value": "right", "label": "Right" }
  ] },
{ "type": "range", "id": "overlay_opacity", "label": "Overlay Opacity", "min": 0, "max": 90, "step": 5, "unit": "%", "default": 0 },
{ "type": "select", "id": "overlay_color", "label": "Overlay Color", "options": "background_colors", "default": "var(--clr-black)",
  "visible_if": "{{ block.settings.overlay_opacity > 0 }}" }
```

There is no "fill/stretch" fit, because it distorts. There are no fixed-height or max-width sliders: size comes from the layout column plus Aspect Ratio. There's no lazy-load toggle, because `media_tag` lazy-loads by default.

### CG-LINK: an optional link on a non-button block

```json
{ "type": "header", "content": "Link" },
{ "type": "url", "id": "link", "label": "Link" },
{ "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false,
  "visible_if": "{{ block.settings.link != blank }}" }
```

The accessible name comes from visible text, or from the image's alt text in the picker. Don't add a separate "accessible label" field.

### CG-BUTTON-HOVER

```json
{ "type": "header", "content": "Hover" },
{ "type": "select", "id": "hover_effect", "label": "Hover Effect", "default": "theme",
  "info": "Theme Default follows Theme Settings → Button Hover.",
  "options": [
    { "value": "theme", "label": "Theme Default" },
    { "value": "colors", "label": "Change Colors" },
    { "value": "darken", "label": "Darken" },
    { "value": "lighten", "label": "Lighten" },
    { "value": "fill", "label": "Fill (outline → filled)" },
    { "value": "lift", "label": "Lift (shadow)" },
    { "value": "underline", "label": "Underline" },
    { "value": "none", "label": "None" }
  ] },
{ "type": "select", "id": "hover_background_color", "label": "Hover Background", "options": "background_colors", "default": "var(--clr-secondary)",
  "visible_if": "{{ block.settings.hover_effect == 'colors' }}" },
{ "type": "select", "id": "hover_text_color", "label": "Hover Text Color", "options": "background_colors", "default": "var(--clr-white)",
  "visible_if": "{{ block.settings.hover_effect == 'colors' }}" },
{ "type": "select", "id": "hover_border_color", "label": "Hover Border Color", "options": "background_colors", "default": "var(--clr-secondary)",
  "visible_if": "{{ block.settings.hover_effect == 'colors' }}" }
```

Custom theme hovers (e.g. "Pulse", "Scale Up") live in the theme's `button_hover_style` list and are reached through "Theme Default". Don't add them per button.

### CG-CARD: section-level styling for repeated items

Repeated items (cards, testimonials, features, steps, reviews, stats) get **no per-item styling**. Styling 12 items one at a time is unusable. The section carries one Card group, placed after Layout. Items may carry one `featured` checkbox, and the section defines what Featured looks like.

```json
{ "type": "header", "content": "Card" },
{ "type": "select", "id": "card_background_color", "label": "Card Background", "options": "background_colors", "default": "var(--clr-white)" },
{ "type": "padding", "id": "card_padding", "label": "Card Padding" },
{ "type": "checkbox", "id": "show_card_border", "label": "Show Card Border", "default": false },
{ "type": "range", "id": "card_border_width", "label": "Card Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
  "visible_if": "{{ section.settings.show_card_border }}" },
{ "type": "select", "id": "card_border_color", "label": "Card Border Color", "options": "background_colors", "default": "var(--clr-light)",
  "visible_if": "{{ section.settings.show_card_border }}" },
{ "type": "corner_radius", "id": "card_border_radius", "label": "Card Corner Radius" },
{ "type": "select", "id": "card_shadow", "label": "Card Shadow", "default": "none",
  "options": [
    { "value": "none", "label": "None" },
    { "value": "var(--shadow-sm)", "label": "Small" },
    { "value": "var(--shadow-md)", "label": "Medium" },
    { "value": "var(--shadow-lg)", "label": "Large" }
  ] },
{ "type": "select", "id": "card_hover_effect", "label": "Card Hover", "default": "none",
  "info": "Applies when the card has a link.",
  "options": [
    { "value": "none", "label": "None" },
    { "value": "lift", "label": "Lift" },
    { "value": "border", "label": "Border Color" },
    { "value": "zoom", "label": "Zoom Image" }
  ] },
{ "type": "select", "id": "card_hover_border_color", "label": "Card Hover Border", "options": "background_colors", "default": "var(--clr-primary)",
  "visible_if": "{{ section.settings.card_hover_effect == 'border' }}" }
```

When items support `featured`, append:

```json
{ "type": "select", "id": "featured_background_color", "label": "Featured Card Background", "options": "background_colors", "default": "var(--clr-primary)" },
{ "type": "select", "id": "featured_text_color", "label": "Featured Card Text", "options": "background_colors", "default": "var(--clr-white)" }
```

### CG-SECTION-TYPE: typography for text inside repeated items

This section-level group goes after CG-CARD. It styles the **fields inside items** (titles, body text, attributions), because those fields aren't blocks and have no Style group of their own. Add one line per role the section's items use:

```json
{ "type": "header", "content": "Item Typography" },
{ "type": "select", "id": "item_title_style", "label": "Title Style", "options": "text_presets", "default": "text-h4" },
{ "type": "select", "id": "item_title_color", "label": "Title Color", "options": "background_colors", "default": "var(--clr-primary)" },
{ "type": "select", "id": "item_text_style", "label": "Text Style", "options": "text_presets", "default": "text-body" },
{ "type": "select", "id": "item_text_color", "label": "Text Color", "options": "background_colors", "default": "var(--clr-body)" },
{ "type": "select", "id": "item_accent_color", "label": "Accent Color", "options": "background_colors", "default": "var(--clr-primary)",
  "info": "Icons, numbers, stars and labels inside items." }
```

### CG-ICON-STYLE: section-level icon styling for repeated icons

```json
{ "type": "header", "content": "Icons" },
{ "type": "range", "id": "icon_size", "label": "Icon Size", "min": 16, "max": 96, "step": 2, "unit": "px", "default": 32 },
{ "type": "select", "id": "icon_color", "label": "Icon Color", "options": "background_colors", "default": "var(--clr-primary)",
  "info": "Applies to preset icons and single-color SVGs." },
{ "type": "select", "id": "icon_background", "label": "Icon Background", "default": "none",
  "options": [
    { "value": "none", "label": "None" },
    { "value": "circle", "label": "Circle" },
    { "value": "rounded", "label": "Rounded Square" }
  ] },
{ "type": "select", "id": "icon_background_color", "label": "Icon Background Color", "options": "background_colors", "default": "var(--clr-light)",
  "visible_if": "{{ section.settings.icon_background != 'none' }}" }
```

### CG-AFFILIATE-VISIBILITY: optional, on any block

Shows or hides a block based on whether a rep is attributed. It works through [affiliate hydration](https://docs.fluid.app/themes/affiliate-hydration) markers, so it's safe on cached pages. See §14.

```json
{ "type": "header", "content": "Visibility" },
{ "type": "radio", "id": "affiliate_visibility", "label": "Show To", "default": "all",
  "info": "Shopping with a rep = visitor arrived through a rep's link.",
  "options": [
    { "value": "all", "label": "Everyone" },
    { "value": "affiliate", "label": "Shopping With a Rep" },
    { "value": "no_affiliate", "label": "No Rep" }
  ] }
```

---

## 6. Block Family Taxonomy

Canonical types are what you build. Aliases are what the surveyed themes called the same thing. Map aliases to the canonical type in new work, but **don't rename existing block types in live themes**.

| Family | Canonical type(s) | Aliases seen (merge into canonical) | Shared core | Section-level styling |
|---|---|---|---|---|
| **Text** | `heading` | title, main_heading, hero_title, top_heading, heading_accent, statement | text + Heading Level + CG-TEXT-STYLE | — |
| | `eyebrow` | overline, kicker, tagline, label (as text), pre_heading, sub | text + CG-TEXT-STYLE | — |
| | `text` | body, description, paragraph, lead, lede, intro, subtext, body_text, closing, closing_line, note | richtext + CG-TEXT-STYLE + Max Width | — |
| | `subheading` | subhead, subtitle, hero_subtitle | **= `text`** with Text Style Body Large | — |
| | `quote` | pullquote, inline_quote, closing_quote, statement (quoted) | text + name + role + CG-TEXT-STYLE | — |
| | `fine_print` | footnote, disclaimer, fine_print, copyright, legal | richtext + CG-TEXT-STYLE (Fine Print) | — |
| **Action** | `button` | cta, cta_button, primary_button, secondary_button, card_button | full button (§8.1) | — |
| | `link` | text_link, learn_more | text + link + underline | — |
| | `social_link` | social, social_icon | network + link | CG-ICON-STYLE |
| | commerce variants | add_to_cart, buy_now, enroll, cart_button, account_button, rep_link | `button` + extras (§13) | — |
| **Media** | `image` | hero_image, content_image, product_image, background_image_media | image + CG-MEDIA-DISPLAY + CG-BORDER + CG-LINK | — |
| | `video` | video_card (simple) | video + playback + CG-MEDIA-DISPLAY + CG-BORDER | — |
| | `media` | fluid_media | media_picker + embed type (§9.3) | — |
| | `ugc_video` | ugc, ugc_item, shot, customer video | **= `video`** + creator/caption; styling at section | Card |
| | `gallery_item` | gallery_image, slide, carousel_item | image + caption + link | Card / Media |
| | `before_after` | slide_before + slide_after (pair) | two images + labels | Media |
| **Icon & Logo** | `icon` | feature_icon, icon_item | icon preset or custom + size + color + link | CG-ICON-STYLE when repeated |
| | `logo` | logo_item, press_logo, partner, store_badge | image + text fallback + link | Logo Wall |
| **Structure** | `divider` | separator, rule, spacer | line on/off + spacing | — |
| | `custom_liquid` | html, embed | code | — |
| **Content items** | `feature` | benefit, pillar, principle, value, value_prop, belief, point, feature_card, benefit_card | icon + title + text (+ link) | Card, Item Typography, Icons |
| | `list_item` | bullet, bullet_item, benefit_item, included_item, check_item | text (+ icon) | Icons |
| | `card` | featured_card, image_card, media_card, split_card, panel | image + eyebrow + title + text + button | Card |
| | `testimonial` | quote_card, testimonial_item, customer_story | quote + name + role + photo (+ rating, result) | Card |
| | `review` | review_card, text_review | rating + title + body + name + date + verified | Card |
| | `press_quote` | press_item, quote_item | logo + quote + source | Card |
| | `stat` | stat_item, number, metric, figure, data_point, result | prefix + value + suffix + label | Item Typography |
| | `step` | process_step, timeline_point, milestone, phase, chapter | number + title + text (+ image) | Card, Item Typography |
| | `faq_item` | accordion_item, accordion, faq, question, details_block | question + answer + open | Accordion |
| | `trust_item` | trust_badge, guarantee, assurance, cert, trust | icon + title + subtitle | Icons |
| | `badge` | tag, chip, pill, label (as chip) | text + icon + colors | — |
| | `rating` | stars, star_rating | source + rating + text | Item Typography |
| | `team_member` | member, expert, doctor, leader, author, bio_card | photo + name + role + bio | Card |
| | `ingredient` | compound, active, nutrient | image + name + amount + description | Card |
| | `comparison_row` | row, comparison_column | feature + ours/theirs values | Table |
| | `tab` | panel, tab_content | label + tab key | Tabs |
| **Commerce** | `product_card` | product, product_item, pack (product), regimen, offer | product picker + overrides | Card + Card Button |
| | `enrollment_card` | pack, enrollment_pack, tier, plan | enrollment_pack picker + overrides | Card + Card Button |
| | `collection_tile` | category_card, tile, shop_all_card, path_card | collection/category + overrides | Card |
| **Affiliate** | `affiliate_banner` | affiliate, rep_attribution | hydration markers + fallbacks | Section text color |
| | `affiliate_bio` | rep_card | hydration markers + fallbacks | Card |

**Pairs that look different but share a core:**
- **icon vs social_link vs trust_item.** All render an icon. social_link adds `network` + `link`. trust_item adds a title/subtitle. Styling is section-level CG-ICON-STYLE for all three.
- **image vs logo vs gallery_item.** Same picker and link. logo drops Media Display (it's always *contain*, height set by the section) and adds a text fallback. gallery_item adds a caption.
- **video vs ugc_video.** Same picker and playback. ugc_video defaults to 9:16, moves display/shape to the section, and adds creator/caption fields.
- **testimonial vs review vs quote.** All carry quoted text plus attribution.
  - review requires `rating` and adds `title`, `date` and `verified`.
  - testimonial has a photo and role, with optional rating and result.
  - quote is a single `limit: 1` text block.
- **feature vs stat vs step.** feature is icon-led. stat is number-led and has no icon. step is ordered and numbered.
- **faq_item vs accordion_item.** Identical. Use `faq_item`. Product-page accordions aren't blocks; they're metafield rows in the resource section (§12.9, §16.2).
- **button vs link vs link-bearing blocks.** See §8.3.

---

## 7. Text Blocks

Text blocks own their typography and color: every text block has CG-TEXT-STYLE and CG-TYPE-OVERRIDES. Each block's Color defaults to a real palette preset:

| Block | Default Color |
|---|---|
| `heading`, `eyebrow`, `quote` | Primary (`var(--clr-primary)`) |
| `text`, `subheading` | Body (`var(--clr-body)`) |
| `fine_print` | Muted (`var(--clr-muted)`) |

On a dark background, the editor changes each text block's Color, for example to White. Section presets for dark sections should ship with those colors already set.

### 7.1 `heading`

**Purpose:** A heading at a chosen semantic level. The level (h1–h6) controls meaning and SEO. **Text Style** controls how it looks. Keep the two independent.

**Plain-English controls:**
- **Text:** a single line. Use inline italic for accent words, which CSS styles with the theme's accent font.
- **Heading Level:** H1 (page title, one per page) / H2 (section) / H3 / H4 / H5 / H6 / Paragraph (not a heading).
- *Style:* **Text Style** (default H2), **Color** (Primary), **Alignment** (Auto), **Max Width**.
- *Manual Overrides:* **Override Text Style** → Font Family / Font Size / Font Weight.

```json
{
  "type": "heading",
  "name": "Heading",
  "limit": 1,
  "settings": [
    { "type": "text", "id": "text", "label": "Text", "default": "Your heading here" },
    { "type": "select", "id": "heading_tag", "label": "Heading Level", "default": "h2",
      "info": "Sets meaning for SEO and screen readers, not size. Use one H1 per page.",
      "options": [
        { "value": "h1", "label": "H1 — Page Title" },
        { "value": "h2", "label": "H2 — Section" },
        { "value": "h3", "label": "H3 — Subsection" },
        { "value": "h4", "label": "H4" },
        { "value": "h5", "label": "H5" },
        { "value": "h6", "label": "H6" },
        { "value": "p", "label": "Paragraph (not a heading)" }
      ] },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-h2",
      "info": "Theme typography preset. Edit presets in Theme Settings → Typography." },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-primary)" },
    { "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
      "options": [ { "value": "inherit", "label": "Auto" }, { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
    { "type": "select", "id": "max_width", "label": "Max Width", "default": "none", "info": "Limits line length for readability.",
      "options": [ { "value": "none", "label": "Full Width" }, { "value": "75ch", "label": "Wide" }, { "value": "60ch", "label": "Medium" }, { "value": "40ch", "label": "Narrow" } ] },
    { "type": "header", "content": "Manual Overrides" },
    { "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false,
      "info": "Leave off to follow the Text Style preset. Use only for intentional one-offs." },
    { "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "var(--ff-heading)",
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "range", "id": "font_size", "label": "Font Size", "min": 16, "max": 120, "step": 1, "unit": "px", "default": 36,
      "info": "Desktop size. Tablet and mobile scale automatically.", "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "select", "id": "font_weight", "label": "Font Weight", "default": "700", "visible_if": "{{ block.settings.override_typography }}",
      "options": [ { "value": "300", "label": "Light" }, { "value": "400", "label": "Regular" }, { "value": "500", "label": "Medium" }, { "value": "600", "label": "Semi Bold" }, { "value": "700", "label": "Bold" }, { "value": "800", "label": "Extra Bold" } ] }
  ]
}
```

Render: `<{{ tag }} class="{{ text_style }} …" {{ block.fluid_attributes }}>{{ block.settings.text }}</{{ tag }}>`. Don't wrap richtext in a heading tag, and don't use `| replace: '<p>'` tricks; they produce nested headings. Drop `limit` when the section is a free-form content stack.

**Deltas:**
- **Two-tone / accent heading** (Oliabo `line_1`/`line_2`, Make Wellness `heading_accent`): don't create a second block type. Use inline italic in the one heading. The theme's `em` style in headings uses `var(--ff-accent)`.
- **Hero heading:** default `heading_tag` = `h1` and `text_style` = `text-h1`.

### 7.2 `eyebrow`

**Purpose:** A short label above a heading, such as "NEW" or "CLINICALLY STUDIED". It renders as a `<p>`, never as `<h5>`, so it doesn't break the heading outline.

**Plain-English controls:** Text · Style (Text Style default Eyebrow, Color, Alignment) · Manual Overrides.

```json
{
  "type": "eyebrow",
  "name": "Eyebrow",
  "limit": 1,
  "settings": [
    { "type": "text", "id": "text", "label": "Text", "default": "Eyebrow label" },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-eyebrow",
      "info": "Theme typography preset. Edit presets in Theme Settings → Typography." },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-primary)" },
    { "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
      "options": [ { "value": "inherit", "label": "Auto" }, { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
    { "type": "header", "content": "Manual Overrides" },
    { "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false,
      "info": "Leave off to follow the Text Style preset. Use only for intentional one-offs." },
    { "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "var(--ff-body)",
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "range", "id": "font_size", "label": "Font Size", "min": 11, "max": 20, "step": 1, "unit": "px", "default": 12,
      "info": "Desktop size. Tablet and mobile scale automatically.", "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "select", "id": "font_weight", "label": "Font Weight", "default": "600", "visible_if": "{{ block.settings.override_typography }}",
      "options": [ { "value": "300", "label": "Light" }, { "value": "400", "label": "Regular" }, { "value": "500", "label": "Medium" }, { "value": "600", "label": "Semi Bold" }, { "value": "700", "label": "Bold" }, { "value": "800", "label": "Extra Bold" } ] }
  ]
}
```

Uppercase and letter-spacing belong to the Eyebrow preset in CSS, not to a block setting.

### 7.3 `text` (body copy)

**Purpose:** General formatted copy. It replaces `description`, `body`, `paragraph`, `lead`, `intro`, `subtext` and the rest. There is one body block.

**Plain-English controls:**
- **Text:** a rich-text editor. The toolbar handles bold, italic, links, lists, and its own style/color presets.
- *Style:* Text Style (default Body), Color, Alignment, Max Width.
- *Manual Overrides.*

```json
{
  "type": "text",
  "name": "Text",
  "settings": [
    { "type": "richtext", "id": "text", "label": "Text", "default": "<p>Body text here. Tell customers what makes this different.</p>" },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-body",
      "info": "Theme typography preset. Edit presets in Theme Settings → Typography." },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-body)" },
    { "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
      "options": [ { "value": "inherit", "label": "Auto" }, { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
    { "type": "select", "id": "max_width", "label": "Max Width", "default": "none", "info": "Limits line length for readability.",
      "options": [ { "value": "none", "label": "Full Width" }, { "value": "75ch", "label": "Wide" }, { "value": "60ch", "label": "Medium" }, { "value": "40ch", "label": "Narrow" } ] },
    { "type": "header", "content": "Manual Overrides" },
    { "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false,
      "info": "Leave off to follow the Text Style preset. Use only for intentional one-offs." },
    { "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "var(--ff-body)",
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "range", "id": "font_size", "label": "Font Size", "min": 12, "max": 32, "step": 1, "unit": "px", "default": 16,
      "info": "Desktop size. Tablet and mobile scale automatically.", "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "select", "id": "font_weight", "label": "Font Weight", "default": "400", "visible_if": "{{ block.settings.override_typography }}",
      "options": [ { "value": "300", "label": "Light" }, { "value": "400", "label": "Regular" }, { "value": "500", "label": "Medium" }, { "value": "600", "label": "Semi Bold" }, { "value": "700", "label": "Bold" }, { "value": "800", "label": "Extra Bold" } ] }
  ]
}
```

Render inside `<div class="rte {{ text_style }}">` so theme rich-text styles apply.

### 7.4 `subheading`: delta of `text`

Same schema as `text` with these changes:
- `"type": "subheading"`, `"name": "Subheading"`, `"limit": 1`.
- `text` default `<p>A supporting line that expands on the heading.</p>`.
- `text_style` default `text-body-lg`.

Subheading is only a separately named block so editors recognize it in the picker. It has no special controls.

### 7.5 `quote` (pull quote)

**Purpose:** One featured quotation with attribution. This is a single-block text element. For repeated customer quotes, use `testimonial` (§12.4).

**Plain-English controls:** Quote · Name · Role or Source · Style (Text Style default Quote, Color, Alignment, Show Quote Marks) · Manual Overrides.

```json
{
  "type": "quote",
  "name": "Quote",
  "limit": 1,
  "settings": [
    { "type": "textarea", "id": "text", "label": "Quote", "default": "This changed the way our whole family starts the day." },
    { "type": "text", "id": "name", "label": "Name", "default": "Jordan Lee" },
    { "type": "text", "id": "role", "label": "Role or Source", "info": "e.g. 'Customer since 2022' or 'Wellness Weekly'." },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-quote",
      "info": "Theme typography preset. Edit presets in Theme Settings → Typography." },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-primary)" },
    { "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
      "options": [ { "value": "inherit", "label": "Auto" }, { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
    { "type": "checkbox", "id": "show_quote_marks", "label": "Show Quote Marks", "default": true },
    { "type": "header", "content": "Manual Overrides" },
    { "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false,
      "info": "Leave off to follow the Text Style preset. Use only for intentional one-offs." },
    { "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "var(--ff-accent)",
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "range", "id": "font_size", "label": "Font Size", "min": 14, "max": 48, "step": 1, "unit": "px", "default": 20,
      "info": "Desktop size. Tablet and mobile scale automatically.", "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "select", "id": "font_weight", "label": "Font Weight", "default": "400", "visible_if": "{{ block.settings.override_typography }}",
      "options": [ { "value": "300", "label": "Light" }, { "value": "400", "label": "Regular" }, { "value": "500", "label": "Medium" }, { "value": "600", "label": "Semi Bold" }, { "value": "700", "label": "Bold" }, { "value": "800", "label": "Extra Bold" } ] }
  ]
}
```

Render as `<figure><blockquote>…</blockquote><figcaption>…</figcaption></figure>`. The attribution uses `text-label` in the muted color.

### 7.6 `fine_print`

**Purpose:** Disclaimers, footnotes, FDA statements, legal lines. It replaces `footnote`, `disclaimer`, `note` and `copyright`.

```json
{
  "type": "fine_print",
  "name": "Fine Print",
  "settings": [
    { "type": "richtext", "id": "text", "label": "Text", "default": "<p>*These statements have not been evaluated by the Food and Drug Administration.</p>",
      "info": "Keep it factual. Links are allowed." },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-fine-print",
      "info": "Theme typography preset. Edit presets in Theme Settings → Typography." },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-muted)" },
    { "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
      "options": [ { "value": "inherit", "label": "Auto" }, { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
    { "type": "select", "id": "max_width", "label": "Max Width", "default": "none", "info": "Limits line length for readability.",
      "options": [ { "value": "none", "label": "Full Width" }, { "value": "75ch", "label": "Wide" }, { "value": "60ch", "label": "Medium" }, { "value": "40ch", "label": "Narrow" } ] }
  ]
}
```

Fine Print intentionally has no Manual Overrides group.

---

## 8. Action Blocks (Buttons & Links)

### 8.1 `button`: the canonical button

**Purpose:** A call to action. **Every** button in every theme uses this control set, including section-level buttons and card buttons (§8.5). The full set includes hover styling. Specialized commerce buttons (§13) are this block plus extras.

**Plain-English controls (builder order):**
- *Content:*
  - **Button Text**
  - **Link**
  - **Open in New Tab**
  - **Icon:** None / Arrow / Chevron / External / Plus
  - **Icon Position:** Before / After
- *Style:*
  - **Style:** Filled / Outline / Text Only
  - **Text Style:** default Button preset
  - **Background Color:** Filled only
  - **Text Color**
  - **Padding**
- *Manual Overrides:* Font Family / Font Size / Font Weight.
- *Shape:*
  - **Show Border**, then Border Width and Border Color. Outline always draws a border; the toggle adds one to Filled.
  - **Corner Radius**
- *Hover:*
  - **Hover Effect:** Theme Default / Change Colors / Darken / Lighten / Fill / Lift / Underline / None
  - Hover Background, Hover Text Color and Hover Border Color, shown for Change Colors.
- *Layout:* **Width:** Fit Text / Full Width.

```json
{
  "type": "button",
  "name": "Button",
  "settings": [
    { "type": "text", "id": "text", "label": "Button Text", "default": "Shop Now" },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false },
    { "type": "select", "id": "icon", "label": "Icon", "default": "none",
      "options": [
        { "value": "none", "label": "None" },
        { "value": "arrow_right", "label": "Arrow" },
        { "value": "chevron_right", "label": "Chevron" },
        { "value": "external", "label": "External Link" },
        { "value": "plus", "label": "Plus" }
      ] },
    { "type": "radio", "id": "icon_position", "label": "Icon Position", "default": "after",
      "visible_if": "{{ block.settings.icon != 'none' }}",
      "options": [ { "value": "before", "label": "Before" }, { "value": "after", "label": "After" } ] },

    { "type": "header", "content": "Style" },
    { "type": "radio", "id": "style", "label": "Style", "default": "filled",
      "options": [ { "value": "filled", "label": "Filled" }, { "value": "outline", "label": "Outline" }, { "value": "text", "label": "Text Only" } ] },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-button" },
    { "type": "select", "id": "background_color", "label": "Background Color", "options": "background_colors", "default": "var(--clr-primary)",
      "visible_if": "{{ block.settings.style == 'filled' }}" },
    { "type": "select", "id": "text_color", "label": "Text Color", "options": "background_colors", "default": "var(--clr-white)" },
    { "type": "padding", "id": "padding", "label": "Padding" },

    { "type": "header", "content": "Manual Overrides" },
    { "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false,
      "info": "Leave off to follow the Button text preset." },
    { "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "var(--ff-body)",
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "range", "id": "font_size", "label": "Font Size", "min": 14, "max": 24, "step": 1, "unit": "px", "default": 16,
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "select", "id": "font_weight", "label": "Font Weight", "default": "600", "visible_if": "{{ block.settings.override_typography }}",
      "options": [ { "value": "400", "label": "Regular" }, { "value": "500", "label": "Medium" }, { "value": "600", "label": "Semi Bold" }, { "value": "700", "label": "Bold" } ] },

    { "type": "header", "content": "Shape" },
    { "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false,
      "info": "Outline buttons always show a border." },
    { "type": "range", "id": "border_width", "label": "Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
      "visible_if": "{{ block.settings.show_border or block.settings.style == 'outline' }}" },
    { "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
      "visible_if": "{{ block.settings.show_border or block.settings.style == 'outline' }}" },
    { "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" },

    { "type": "header", "content": "Hover" },
    { "type": "select", "id": "hover_effect", "label": "Hover Effect", "default": "theme",
      "info": "Theme Default follows Theme Settings → Button Hover.",
      "options": [
        { "value": "theme", "label": "Theme Default" },
        { "value": "colors", "label": "Change Colors" },
        { "value": "darken", "label": "Darken" },
        { "value": "lighten", "label": "Lighten" },
        { "value": "fill", "label": "Fill (outline → filled)" },
        { "value": "lift", "label": "Lift (shadow)" },
        { "value": "underline", "label": "Underline" },
        { "value": "none", "label": "None" }
      ] },
    { "type": "select", "id": "hover_background_color", "label": "Hover Background", "options": "background_colors", "default": "var(--clr-secondary)",
      "visible_if": "{{ block.settings.hover_effect == 'colors' }}" },
    { "type": "select", "id": "hover_text_color", "label": "Hover Text Color", "options": "background_colors", "default": "var(--clr-white)",
      "visible_if": "{{ block.settings.hover_effect == 'colors' }}" },
    { "type": "select", "id": "hover_border_color", "label": "Hover Border Color", "options": "background_colors", "default": "var(--clr-secondary)",
      "visible_if": "{{ block.settings.hover_effect == 'colors' }}" },

    { "type": "header", "content": "Layout" },
    { "type": "radio", "id": "width", "label": "Width", "default": "auto",
      "options": [ { "value": "auto", "label": "Fit Text" }, { "value": "full", "label": "Full Width" } ] }
  ]
}
```

**Button size comes from its Text Style.** The label's font size comes from the Text Style preset (default: the theme's **Button** preset). The button's default padding is set in `em`, so the whole button scales with it: pick a larger Text Style and the button gets bigger. Changing the theme's Button preset resizes every button that uses it. The **Padding** control is an intentional override: once an editor sets it, that button's padding is fixed in px.

Buttons have no `limit`. Sections that can't fit more than a few may set one.

**Not included, on purpose:**
- **Size presets (XS–XL).** Text Style handles size, as described above.
- **Fixed width/height sliders.**
- **Mobile full width.** CSS handles mobile (§18.6).
- **Alignment.** It belongs to the section or button group, not the button.

**Rendering:** colors are written as **CSS custom properties**, never as direct `background-color`. An inline `background-color` beats `:hover` rules, which is why no surveyed theme's inline-styled button could hover. Put the markup in one `components/button` partial that every button calls. See §18.4 for the full component and CSS.

**Presets:** a primary and a secondary button in an intro stack:

```json
{ "type": "button", "settings": { "text": "Shop Now", "style": "filled" } },
{ "type": "button", "settings": { "text": "Learn More", "style": "outline", "text_color": "var(--clr-primary)" } }
```

### 8.2 `link`: text link

**Purpose:** A lighter-weight call to action, rendered as a plain `<a>` with no box. It shares Content with `button` but has no box styling. Hover is simpler: a color shift and an underline.

```json
{
  "type": "link",
  "name": "Link",
  "settings": [
    { "type": "text", "id": "text", "label": "Link Text", "default": "Learn More" },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false },
    { "type": "select", "id": "icon", "label": "Icon", "default": "arrow_right",
      "options": [
        { "value": "none", "label": "None" },
        { "value": "arrow_right", "label": "Arrow" },
        { "value": "chevron_right", "label": "Chevron" },
        { "value": "external", "label": "External Link" }
      ] },
    { "type": "radio", "id": "icon_position", "label": "Icon Position", "default": "after",
      "visible_if": "{{ block.settings.icon != 'none' }}",
      "options": [ { "value": "before", "label": "Before" }, { "value": "after", "label": "After" } ] },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-body" },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-primary)" },
    { "type": "radio", "id": "underline", "label": "Underline", "default": "hover",
      "options": [ { "value": "always", "label": "Always" }, { "value": "hover", "label": "On Hover" }, { "value": "never", "label": "Never" } ] },
    { "type": "header", "content": "Manual Overrides" },
    { "type": "checkbox", "id": "override_typography", "label": "Override Text Style", "default": false },
    { "type": "select", "id": "font_family", "label": "Font Family", "options": "font_families", "default": "var(--ff-body)",
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "range", "id": "font_size", "label": "Font Size", "min": 12, "max": 32, "step": 1, "unit": "px", "default": 16,
      "visible_if": "{{ block.settings.override_typography }}" },
    { "type": "select", "id": "font_weight", "label": "Font Weight", "default": "600", "visible_if": "{{ block.settings.override_typography }}",
      "options": [ { "value": "400", "label": "Regular" }, { "value": "500", "label": "Medium" }, { "value": "600", "label": "Semi Bold" }, { "value": "700", "label": "Bold" } ] },
    { "type": "header", "content": "Hover" },
    { "type": "select", "id": "hover_color", "label": "Hover Color", "options": "background_colors", "default": "var(--clr-secondary)" }
  ]
}
```

### 8.3 Blocks whose main job is linking (but aren't buttons)

The survey found 134 non-button blocks with a link: cards, tiles, logos, images, icons, nav items and product cards. Give them the smallest set that fits:

| Kind of block | Link controls | Hover lives |
|---|---|---|
| Whole-surface link: image, logo, icon, tile, card without visible CTA | CG-LINK (`link`, `open_new_tab`) | Section `card_hover_effect` (CG-CARD), or logo-wall hover |
| Card with a visible CTA (product card, editorial card, pack card) | `button_text` + `link` + `open_new_tab` on the item | Section-level **Card Button** group (§8.5): all cards' buttons share one style |
| Nav, footer and legal links | `text` + `link` + `open_new_tab` only | Section/navbar CSS |
| Standalone link in a content stack | `link` block (§8.2) | Block |
| Standalone CTA | `button` block (§8.1) | Block |

Rule of thumb: **if the editor would ever want the link to look like a button, it gets the button control set**, either as a `button` block or as a section-level Card Button group. Never create a third, partial button style.

### 8.4 `social_link`

**Purpose:** One social profile icon. It's an `icon` with a network preset and a link. Use one block per network so editors can reorder them. Style the whole row at section level (CG-ICON-STYLE + Hover Color).

```json
{
  "type": "social_link",
  "name": "Social Link",
  "limit": 12,
  "settings": [
    { "type": "select", "id": "network", "label": "Network", "default": "instagram",
      "options": [
        { "value": "instagram", "label": "Instagram" },
        { "value": "facebook", "label": "Facebook" },
        { "value": "tiktok", "label": "TikTok" },
        { "value": "youtube", "label": "YouTube" },
        { "value": "x", "label": "X (Twitter)" },
        { "value": "linkedin", "label": "LinkedIn" },
        { "value": "pinterest", "label": "Pinterest" },
        { "value": "threads", "label": "Threads" },
        { "value": "snapchat", "label": "Snapchat" },
        { "value": "whatsapp", "label": "WhatsApp" },
        { "value": "custom", "label": "Custom" }
      ] },
    { "type": "url", "id": "link", "label": "Link",
      "info": "Leave blank to use the company profile URL from admin (Facebook, X, Instagram, Pinterest, YouTube)." },
    { "type": "image_picker", "id": "icon_image", "label": "Custom Icon", "info": "SVG recommended.",
      "visible_if": "{{ block.settings.network == 'custom' }}" },
    { "type": "text", "id": "label", "label": "Accessible Label", "info": "Defaults to the network name.",
      "visible_if": "{{ block.settings.network == 'custom' }}" }
  ]
}
```

Section-level styling uses CG-ICON-STYLE, plus:

```json
{ "type": "select", "id": "icon_hover_color", "label": "Icon Hover Color", "options": "background_colors", "default": "var(--clr-secondary)" }
```

Social links always open in a new tab with `rel="noopener"`, so that isn't a setting. The blank-link fallback reads `company.instagram_url`, `company.facebook_url`, `company.twitter_url`, `company.pinterest_url` and `company.youtube_url`. Don't use one block holding eight URL fields (Yoli footer pattern): it can't be reordered.

### 8.5 Section-level buttons (Card Button group)

Prefer `button` blocks. Use a section-level group only when **one button style applies to many items**, such as the CTA on every product card. Copy the button's Style, Shape and Hover settings, prefixed `card_button_`, with labels prefixed "Button". Item-level `button_text` stays on the item.

```json
{ "type": "header", "content": "Card Button" },
{ "type": "checkbox", "id": "show_card_button", "label": "Show Button", "default": true },
{ "type": "text", "id": "card_button_text", "label": "Default Button Text", "default": "Shop Now", "info": "Items can override this." },
{ "type": "radio", "id": "card_button_style", "label": "Button Style", "default": "filled",
  "options": [ { "value": "filled", "label": "Filled" }, { "value": "outline", "label": "Outline" }, { "value": "text", "label": "Text Only" } ] },
{ "type": "select", "id": "card_button_background_color", "label": "Button Background", "options": "background_colors", "default": "var(--clr-primary)" },
{ "type": "select", "id": "card_button_text_color", "label": "Button Text Color", "options": "background_colors", "default": "var(--clr-white)" },
{ "type": "select", "id": "card_button_border_color", "label": "Button Border Color", "options": "background_colors", "default": "var(--clr-primary)" },
{ "type": "corner_radius", "id": "card_button_border_radius", "label": "Button Corner Radius" },
{ "type": "select", "id": "card_button_hover_effect", "label": "Button Hover Effect", "default": "theme",
  "options": [ { "value": "theme", "label": "Theme Default" }, { "value": "colors", "label": "Change Colors" }, { "value": "darken", "label": "Darken" }, { "value": "lighten", "label": "Lighten" }, { "value": "fill", "label": "Fill (outline → filled)" }, { "value": "lift", "label": "Lift (shadow)" }, { "value": "underline", "label": "Underline" }, { "value": "none", "label": "None" } ] },
{ "type": "select", "id": "card_button_hover_background_color", "label": "Button Hover Background", "options": "background_colors", "default": "var(--clr-secondary)",
  "visible_if": "{{ section.settings.card_button_hover_effect == 'colors' }}" },
{ "type": "select", "id": "card_button_hover_text_color", "label": "Button Hover Text", "options": "background_colors", "default": "var(--clr-white)",
  "visible_if": "{{ section.settings.card_button_hover_effect == 'colors' }}" },
{ "type": "radio", "id": "card_button_width", "label": "Button Width", "default": "full",
  "options": [ { "value": "auto", "label": "Fit Text" }, { "value": "full", "label": "Full Width" } ] }
```

For a section with a single fixed CTA, use the same pattern with the `button_` prefix. Don't use the `primary_button_*` / `button_one_*` / `button_1_*` naming schemes; use two `button` blocks.

---

## 9. Media Blocks

All media renders with the [`media_tag`](https://docs.fluid.app/themes/media-tag) filter. It builds `srcset`, lazy-loads, and picks `<img>` or `<video>`. **Alt text comes from the picker:** `alt: block.settings.image.alt | default: ''`. There is never a separate alt-text setting.

### 9.1 `image`

**Plain-English controls:**
- *Content:* **Image** (DAM picker; alt text is set in the picker) and **Caption** (optional).
- *Media Display:* **Aspect Ratio**, **Fit** (Cover / Contain), **Focal Point**, **Overlay Opacity** → Overlay Color.
- *Shape:* **Show Border** → Border Width / Border Color, then **Corner Radius**.
- *Link:* **Link**, **Open in New Tab**.

```json
{
  "type": "image",
  "name": "Image",
  "settings": [
    { "type": "image_picker", "id": "image", "label": "Image",
      "info": "JPG, PNG, WebP or SVG. 2000px wide recommended. Set alt text in the picker." },
    { "type": "text", "id": "caption", "label": "Caption", "info": "Optional. Shown below the image." },
    { "type": "header", "content": "Media Display" },
    { "type": "select", "id": "aspect_ratio", "label": "Aspect Ratio", "default": "auto",
      "options": [
        { "value": "auto", "label": "Original" }, { "value": "1/1", "label": "Square (1:1)" }, { "value": "4/5", "label": "Portrait (4:5)" },
        { "value": "3/4", "label": "Portrait (3:4)" }, { "value": "2/3", "label": "Portrait (2:3)" }, { "value": "9/16", "label": "Vertical (9:16)" },
        { "value": "4/3", "label": "Landscape (4:3)" }, { "value": "3/2", "label": "Landscape (3:2)" }, { "value": "16/9", "label": "Widescreen (16:9)" },
        { "value": "21/9", "label": "Ultrawide (21:9)" }
      ] },
    { "type": "radio", "id": "fit", "label": "Fit", "default": "cover",
      "info": "Cover fills the frame and may crop. Contain shows the whole image.",
      "options": [ { "value": "cover", "label": "Cover" }, { "value": "contain", "label": "Contain" } ] },
    { "type": "select", "id": "object_position", "label": "Focal Point", "default": "center",
      "visible_if": "{{ block.settings.fit == 'cover' }}",
      "options": [ { "value": "center", "label": "Center" }, { "value": "top", "label": "Top" }, { "value": "bottom", "label": "Bottom" }, { "value": "left", "label": "Left" }, { "value": "right", "label": "Right" } ] },
    { "type": "range", "id": "overlay_opacity", "label": "Overlay Opacity", "min": 0, "max": 90, "step": 5, "unit": "%", "default": 0 },
    { "type": "select", "id": "overlay_color", "label": "Overlay Color", "options": "background_colors", "default": "var(--clr-black)",
      "visible_if": "{{ block.settings.overlay_opacity > 0 }}" },
    { "type": "header", "content": "Shape" },
    { "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false },
    { "type": "range", "id": "border_width", "label": "Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" },
    { "type": "header", "content": "Link" },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false,
      "visible_if": "{{ block.settings.link != blank }}" }
  ]
}
```

Render: `{{ block.settings.image | media_tag: sizes: '(min-width: 1024px) 50vw, 100vw', alt: block.settings.image.alt, class: 'x__img' }}` inside a wrapper that carries `aspect-ratio`, `object-fit`, `object-position`, border, radius and `::after` overlay. Show a placeholder when the image is blank; don't render an empty `<img>`. For above-the-fold hero images, pass `loading: 'eager', fetchpriority: 'high'`.

### 9.2 `video` (simple uploaded video)

**Plain-English controls:**
- *Content:* **Video** (DAM picker) and **Poster Image** (optional; defaults to the first frame).
- *Playback:* **Playback:** Ambient (autoplay, muted, no controls) / Click to Play (controls). **Loop.**
- *Media Display*, *Shape:* same as image. Aspect Ratio defaults to 16:9.

```json
{
  "type": "video",
  "name": "Video",
  "settings": [
    { "type": "video_picker", "id": "video", "label": "Video", "info": "MP4, MOV or WebM from the Fluid media library." },
    { "type": "image_picker", "id": "poster", "label": "Poster Image", "info": "Optional. Defaults to the video's first frame." },
    { "type": "header", "content": "Playback" },
    { "type": "radio", "id": "playback", "label": "Playback", "default": "click",
      "options": [ { "value": "ambient", "label": "Ambient (autoplay, muted)" }, { "value": "click", "label": "Click to Play" } ] },
    { "type": "checkbox", "id": "loop", "label": "Loop", "default": true },
    { "type": "header", "content": "Media Display" },
    { "type": "select", "id": "aspect_ratio", "label": "Aspect Ratio", "default": "16/9",
      "options": [
        { "value": "auto", "label": "Original" }, { "value": "1/1", "label": "Square (1:1)" }, { "value": "4/5", "label": "Portrait (4:5)" },
        { "value": "9/16", "label": "Vertical (9:16)" }, { "value": "4/3", "label": "Landscape (4:3)" }, { "value": "16/9", "label": "Widescreen (16:9)" },
        { "value": "21/9", "label": "Ultrawide (21:9)" }
      ] },
    { "type": "radio", "id": "fit", "label": "Fit", "default": "cover",
      "options": [ { "value": "cover", "label": "Cover" }, { "value": "contain", "label": "Contain" } ] },
    { "type": "range", "id": "overlay_opacity", "label": "Overlay Opacity", "min": 0, "max": 90, "step": 5, "unit": "%", "default": 0 },
    { "type": "select", "id": "overlay_color", "label": "Overlay Color", "options": "background_colors", "default": "var(--clr-black)",
      "visible_if": "{{ block.settings.overlay_opacity > 0 }}" },
    { "type": "header", "content": "Shape" },
    { "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false },
    { "type": "range", "id": "border_width", "label": "Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" }
  ]
}
```

**Rendering:**
- **Ambient:** `media_tag: autoplay: true, muted: true, loop: true`. `playsinline` is added automatically.
- **Click to Play:** `media_tag: controls: true`, plus the `poster` URL when one is set.
- Respect `prefers-reduced-motion`: don't autoplay when it's set.

> **Picker note:** Fluid may soon merge the image and video pickers into one. Until it does, keep `image` and `video` as separate blocks with the IDs above. When the combined picker ships, build one `media` block: combined picker, then Playback shown only for video, then Media Display, then Shape. Existing `image`/`video` blocks stay as they are.

### 9.3 `media` (Fluid media library widget)

**Purpose:** Embeds any Fluid media-library item (video, image or document) through `<fluid-media-widget>`, with inline, popover or modal playback. This is the only picker in use today that holds either an image or a video. It matches the standalone `blocks/fluid_media` in Make Wellness/Puralta/TM3, with CG-BORDER swapped in.

```json
{
  "type": "media",
  "name": "Media",
  "settings": [
    { "type": "media_picker", "id": "media", "label": "Media", "info": "Pick from the Fluid media library." },
    { "type": "select", "id": "embed_type", "label": "Embed Type", "default": "auto",
      "options": [
        { "value": "auto", "label": "Use Media's Default" },
        { "value": "inline", "label": "Inline (plays in place)" },
        { "value": "popover", "label": "Popover" },
        { "value": "modal", "label": "Modal (full screen)" }
      ] },
    { "type": "header", "content": "Media Display" },
    { "type": "select", "id": "aspect_ratio", "label": "Aspect Ratio", "default": "16/9", "info": "Applies to Inline embeds.",
      "options": [
        { "value": "auto", "label": "Original" }, { "value": "16/9", "label": "Widescreen (16:9)" }, { "value": "1/1", "label": "Square (1:1)" },
        { "value": "4/3", "label": "Landscape (4:3)" }, { "value": "4/5", "label": "Portrait (4:5)" }, { "value": "9/16", "label": "Vertical (9:16)" },
        { "value": "21/9", "label": "Ultrawide (21:9)" }
      ] },
    { "type": "header", "content": "Shape" },
    { "type": "select", "id": "background_color", "label": "Background Color", "options": "background_colors", "default": "transparent",
      "info": "Shows while the media loads." },
    { "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false },
    { "type": "range", "id": "border_width", "label": "Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" }
  ]
}
```

**Rendering:**
- If `media.fluid_media_id` is present, output `<fluid-media-widget media-id="…" embed-type="…" responsive="true" data-fluid-widget="true">`.
- Otherwise fall back to `media_tag` with `alt: media.alt`. The base block passes `alt: ""`, which is a bug.

### 9.4 `ugc_video`: delta of `video`

**Purpose:** Customer or creator vertical video in a carousel or grid.

**Changes from `video`:**
- **Remove** Media Display and Shape from the item. They move to the section so every tile matches: section `aspect_ratio` defaults to `9/16`, plus section Playback and CG-CARD.
- **Add** fields for the creator, caption, original post and an optional tagged product.
- Video may be a `video_picker`, or a `media_picker` when the section plays in a popover.

```json
{
  "type": "ugc_video",
  "name": "UGC Video",
  "limit": 16,
  "settings": [
    { "type": "video_picker", "id": "video", "label": "Video", "info": "Vertical 9:16 recommended." },
    { "type": "image_picker", "id": "poster", "label": "Poster Image", "info": "Optional. Defaults to the first frame." },
    { "type": "text", "id": "name", "label": "Creator Name or Handle", "default": "@happycustomer" },
    { "type": "text", "id": "caption", "label": "Caption" },
    { "type": "url", "id": "link", "label": "Original Post", "info": "Optional link to the creator's post." },
    { "type": "product", "id": "product", "label": "Tagged Product", "info": "Optional. Shows a shop link on the tile." }
  ]
}
```

Section-level Playback for ugc sections has three choices:
- **Hover to Play** (muted preview)
- **Ambient** (autoplay all, muted)
- **Click to Open** (popover with sound)

### 9.5 `gallery_item`: delta of `image`

Carousel and gallery slides. Keep Content and Link on the item. Move Media Display and Shape to the section so all slides match.

```json
{
  "type": "gallery_item",
  "name": "Gallery Image",
  "limit": 24,
  "settings": [
    { "type": "image_picker", "id": "image", "label": "Image", "info": "Set alt text in the picker." },
    { "type": "text", "id": "caption", "label": "Caption" },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false, "visible_if": "{{ block.settings.link != blank }}" }
  ]
}
```

Section: a CG-MEDIA-DISPLAY copy (prefix `image_`, e.g. `image_aspect_ratio`) + `image_border_radius`, `gap`, and for carousels `autoplay` (checkbox) and `show_arrows`/`show_dots` (checkboxes).

### 9.6 `before_after`

One block holds both images. Don't split before and after into two blocks (Make Wellness `slide_before`/`slide_after`).

```json
{
  "type": "before_after",
  "name": "Before & After",
  "limit": 8,
  "settings": [
    { "type": "image_picker", "id": "before_image", "label": "Before Image", "info": "Set alt text in the picker." },
    { "type": "image_picker", "id": "after_image", "label": "After Image", "info": "Use the same size and framing as Before." },
    { "type": "text", "id": "before_label", "label": "Before Label", "default": "Before" },
    { "type": "text", "id": "after_label", "label": "After Label", "default": "After" },
    { "type": "text", "id": "caption", "label": "Caption", "info": "Optional, e.g. '12 weeks, daily use'." }
  ]
}
```

Section-level settings:
- `aspect_ratio` (default `4/5`)
- `border_radius`
- `initial_position` (range 5–95, default 50, unit %)
- `show_labels`
- `label_background_color` and `label_text_color`
- `handle_color`

Alt text falls back to the label: `before_image.alt | default: before_label`.

---

## 10. Icon & Logo Blocks

### 10.1 `icon`

**Purpose:** One icon, either a theme preset (inline SVG using `currentColor`) or an uploaded custom icon. When icons repeat inside items (features, trust items), the item has only `icon` / `icon_image`, and size and color live in section-level CG-ICON-STYLE.

```json
{
  "type": "icon",
  "name": "Icon",
  "settings": [
    { "type": "select", "id": "icon", "label": "Icon", "default": "check",
      "options": [
        { "value": "none", "label": "None" }, { "value": "check", "label": "Check" }, { "value": "check_circle", "label": "Check Circle" },
        { "value": "star", "label": "Star" }, { "value": "heart", "label": "Heart" }, { "value": "leaf", "label": "Leaf" },
        { "value": "shield", "label": "Shield" }, { "value": "truck", "label": "Truck (Shipping)" }, { "value": "return", "label": "Return" },
        { "value": "lock", "label": "Lock (Secure)" }, { "value": "sparkle", "label": "Sparkle" }, { "value": "droplet", "label": "Droplet" },
        { "value": "bolt", "label": "Bolt" }, { "value": "award", "label": "Award" }, { "value": "clock", "label": "Clock" },
        { "value": "gift", "label": "Gift" }, { "value": "globe", "label": "Globe" }, { "value": "user", "label": "Person" }
      ] },
    { "type": "image_picker", "id": "icon_image", "label": "Custom Icon", "info": "Overrides the preset. SVG recommended." },
    { "type": "header", "content": "Style" },
    { "type": "range", "id": "size", "label": "Icon Size", "min": 16, "max": 128, "step": 2, "unit": "px", "default": 32 },
    { "type": "select", "id": "color", "label": "Color", "options": "background_colors", "default": "var(--clr-primary)",
      "info": "Applies to preset icons and single-color SVGs." },
    { "type": "radio", "id": "alignment", "label": "Alignment", "default": "inherit",
      "options": [ { "value": "inherit", "label": "Auto" }, { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
    { "type": "header", "content": "Link" },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false, "visible_if": "{{ block.settings.link != blank }}" }
  ]
}
```

Implement presets in one `components/icon` partial (`{% render 'icon', name: block.settings.icon, size: 32 %}`) that outputs inline SVG with `fill`/`stroke="currentColor"` and `aria-hidden="true"`. Use a `select` for the icon list; an 11-option `radio` is unusable.

### 10.2 `logo`

**Purpose:** A brand, press or partner logo, or an app-store badge. It's an image with no display controls: logos always use *contain*, and the section sets their height.

```json
{
  "type": "logo",
  "name": "Logo",
  "limit": 24,
  "settings": [
    { "type": "image_picker", "id": "image", "label": "Logo", "info": "SVG or transparent PNG. Set alt text (the brand name) in the picker." },
    { "type": "text", "id": "text", "label": "Text Fallback", "info": "Shown when no logo image is set." },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false, "visible_if": "{{ block.settings.link != blank }}" }
  ]
}
```

Section-level "Logos" group:

```json
{ "type": "header", "content": "Logos" },
{ "type": "range", "id": "logo_height", "label": "Logo Height", "min": 16, "max": 120, "step": 2, "unit": "px", "default": 40 },
{ "type": "checkbox", "id": "logo_grayscale", "label": "Grayscale", "default": false, "info": "Logos return to full color on hover." },
{ "type": "range", "id": "logo_opacity", "label": "Logo Opacity", "min": 20, "max": 100, "step": 5, "unit": "%", "default": 100 }
```

---

## 11. Structure Blocks

### 11.1 `divider`

**Purpose:** A horizontal rule and/or vertical spacing between blocks. Turning the line off makes it a spacer, so there is no separate spacer block.

```json
{
  "type": "divider",
  "name": "Divider",
  "settings": [
    { "type": "checkbox", "id": "show_line", "label": "Show Line", "default": true, "info": "Turn off to use this as a spacer." },
    { "type": "select", "id": "color", "label": "Line Color", "options": "background_colors", "default": "var(--clr-light)",
      "visible_if": "{{ block.settings.show_line }}" },
    { "type": "range", "id": "thickness", "label": "Thickness", "min": 1, "max": 8, "step": 1, "unit": "px", "default": 1,
      "visible_if": "{{ block.settings.show_line }}" },
    { "type": "select", "id": "width", "label": "Line Width", "default": "100%", "visible_if": "{{ block.settings.show_line }}",
      "options": [ { "value": "100%", "label": "Full Width" }, { "value": "75%", "label": "75%" }, { "value": "50%", "label": "50%" }, { "value": "25%", "label": "25%" }, { "value": "48px", "label": "Short Accent" } ] },
    { "type": "range", "id": "space_above", "label": "Space Above", "min": 0, "max": 160, "step": 4, "unit": "px", "default": 16 },
    { "type": "range", "id": "space_below", "label": "Space Below", "min": 0, "max": 160, "step": 4, "unit": "px", "default": 16 }
  ]
}
```

Spacing scales like section padding on smaller screens (§18.6). The line aligns with the block alignment of its section.

### 11.2 Spacer, container, and card-with-children

- **Spacer:** not a default block. Spacing between blocks comes from the section's `gap`. Spacing around sections comes from Section Padding. A one-off gap is a `divider` with Show Line off.
- **Container with child blocks / card with child blocks:** inline blocks can't contain other blocks.
  - For repeated items, use a **content item block** (§12). One block holds all of an item's fields: image, title, text and button. Never use the "divider marker + sibling blocks" workaround (a "+ New Step" block followed by `step_heading`/`step_text` blocks).
  - For a true nesting container, use a standalone block with `{% content_for 'blocks' %}` (Appendix A).
- **Arranging whole sections side by side** (feature panel + sidebar, five-panel showcase): use a **section-slots container section** (§17), not a block.

### 11.3 `custom_liquid`

An escape hatch for one-off HTML/Liquid. It goes last in a section's block list, with `limit: 1`.

```json
{
  "type": "custom_liquid",
  "name": "Custom Liquid",
  "limit": 1,
  "settings": [
    { "type": "html", "id": "code", "label": "Custom HTML / Liquid",
      "info": "Advanced. Supports Liquid. Don't paste full HTML documents (<html>, <head>, <body>)." }
  ]
}
```

---

## 12. Content Item Blocks (Repeaters)

Content items are the repeatable units of grids, carousels and lists.

- **Each item is one block holding all of its fields.** Items have no Style, Shape or Hover groups.
- **Styling lives on the section:**
  - CG-CARD for the item surface
  - CG-SECTION-TYPE for the fields inside items
  - CG-ICON-STYLE for icons
  - Card Button (§8.5) for CTAs
- The one allowed per-item emphasis control is `featured`.
- Use `text` for titles, `richtext` for bodies, and `textarea` for quoted customer words.

Recommended limits and preset counts:

| Family | `limit` | Preset items |
|---|---|---|
| feature | 12 | 3–4 |
| list_item | 12 | 3–4 |
| card | 12 | 3 |
| testimonial | 12 | 3 |
| review | 12 | 4 |
| press_quote | 8 | 3 |
| stat | 6 | 3–4 |
| step | 8 | 3–4 |
| faq_item | 20 | 4–5 |
| trust_item | 6 | 3–4 |
| team_member | 12 | 3 |
| ingredient | 12 | 3–4 |
| comparison_row | 20 | 5–6 |
| product_card | 12 | 3–4 |
| enrollment_card | 4 | 3 |
| collection_tile | 12 | 3–4 |

### 12.1 `feature` (icon card)

Replaces benefit, pillar, principle, value, value_prop, belief, point and feature_card.

**Fields:** Icon · Custom Icon · Label (optional kicker, e.g. "01" or "Step one") · Title · Text · Link · Link Text.

```json
{
  "type": "feature",
  "name": "Feature",
  "limit": 12,
  "settings": [
    { "type": "select", "id": "icon", "label": "Icon", "default": "check",
      "options": [
        { "value": "none", "label": "None" }, { "value": "check", "label": "Check" }, { "value": "check_circle", "label": "Check Circle" },
        { "value": "star", "label": "Star" }, { "value": "heart", "label": "Heart" }, { "value": "leaf", "label": "Leaf" },
        { "value": "shield", "label": "Shield" }, { "value": "truck", "label": "Truck (Shipping)" }, { "value": "return", "label": "Return" },
        { "value": "lock", "label": "Lock (Secure)" }, { "value": "sparkle", "label": "Sparkle" }, { "value": "droplet", "label": "Droplet" },
        { "value": "bolt", "label": "Bolt" }, { "value": "award", "label": "Award" }, { "value": "clock", "label": "Clock" },
        { "value": "gift", "label": "Gift" }, { "value": "globe", "label": "Globe" }, { "value": "user", "label": "Person" }
      ] },
    { "type": "image_picker", "id": "icon_image", "label": "Custom Icon", "info": "Overrides the preset. SVG recommended." },
    { "type": "text", "id": "eyebrow", "label": "Label", "info": "Optional short kicker, e.g. '01'." },
    { "type": "text", "id": "title", "label": "Title", "default": "Premium quality" },
    { "type": "richtext", "id": "text", "label": "Text", "default": "<p>Describe the benefit in one or two sentences.</p>" },
    { "type": "url", "id": "link", "label": "Link", "info": "Optional. Makes the card clickable." },
    { "type": "text", "id": "link_text", "label": "Link Text", "info": "Optional visible link. Leave blank to make the whole card clickable.",
      "visible_if": "{{ block.settings.link != blank }}" }
  ]
}
```

Section groups: Layout (columns, gap, alignment) → CG-CARD → CG-SECTION-TYPE → CG-ICON-STYLE.

**Delta, image-led feature:** replace `icon`/`icon_image` with `{ "type": "image_picker", "id": "image", "label": "Image" }` and add section `image_aspect_ratio`. At that point it's usually a `card` (§12.3).

### 12.2 `list_item` (bullet)

```json
{
  "type": "list_item",
  "name": "List Item",
  "limit": 12,
  "settings": [
    { "type": "text", "id": "text", "label": "Text", "default": "Third-party tested for purity" },
    { "type": "select", "id": "icon", "label": "Icon", "default": "check",
      "options": [ { "value": "check", "label": "Check" }, { "value": "check_circle", "label": "Check Circle" }, { "value": "star", "label": "Star" }, { "value": "leaf", "label": "Leaf" }, { "value": "sparkle", "label": "Sparkle" }, { "value": "none", "label": "None (bullet)" } ] }
  ]
}
```

Section: CG-ICON-STYLE (icon size default 18) + `item_text_style`.

### 12.3 `card` (editorial card)

```json
{
  "type": "card",
  "name": "Card",
  "limit": 12,
  "settings": [
    { "type": "image_picker", "id": "image", "label": "Image", "info": "Set alt text in the picker." },
    { "type": "text", "id": "eyebrow", "label": "Label" },
    { "type": "text", "id": "title", "label": "Title", "default": "Card title" },
    { "type": "richtext", "id": "text", "label": "Text", "default": "<p>A short supporting description.</p>" },
    { "type": "text", "id": "button_text", "label": "Button Text", "info": "Leave blank to make the whole card clickable." },
    { "type": "url", "id": "link", "label": "Link" },
    { "type": "checkbox", "id": "open_new_tab", "label": "Open in New Tab", "default": false, "visible_if": "{{ block.settings.link != blank }}" },
    { "type": "checkbox", "id": "featured", "label": "Featured", "default": false, "info": "Uses the section's Featured Card colors." }
  ]
}
```

Section groups: Layout → a CG-MEDIA-DISPLAY copy prefixed `image_` (aspect, fit, focal point) → CG-CARD (+ featured colors) → CG-SECTION-TYPE → Card Button (§8.5).

### 12.4 `testimonial`

**Differs from review:** a testimonial is a story. It has a photo and role, an optional star row, and an optional result stat. It has no title, date or verified flag.

```json
{
  "type": "testimonial",
  "name": "Testimonial",
  "limit": 12,
  "settings": [
    { "type": "textarea", "id": "quote", "label": "Quote", "default": "I finally found something that fits into my routine and actually works." },
    { "type": "text", "id": "name", "label": "Name", "default": "Jordan L." },
    { "type": "text", "id": "role", "label": "Role or Location", "info": "e.g. 'Customer since 2022' or 'Austin, TX'." },
    { "type": "image_picker", "id": "avatar", "label": "Photo", "info": "Square crop. Initials show when blank." },
    { "type": "range", "id": "rating", "label": "Rating", "min": 0, "max": 5, "step": 1, "default": 5, "info": "0 hides the stars." },
    { "type": "image_picker", "id": "image", "label": "Card Image", "info": "Optional product or lifestyle photo." },
    { "type": "header", "content": "Result (Optional)" },
    { "type": "text", "id": "result_value", "label": "Result", "info": "e.g. '−18 lbs' or '3x energy'." },
    { "type": "text", "id": "result_label", "label": "Result Label", "info": "e.g. 'in 12 weeks'." }
  ]
}
```

Section groups: Layout/Carousel → CG-CARD → CG-SECTION-TYPE (`item_text_style` default `text-quote`; accent color drives stars and results).

### 12.5 `review`: delta of testimonial

**Changes:**
- `rating` is required (min 1).
- **Add** `title`, `date` and `verified`.
- **Remove** `image` and the Result group.
- `role` becomes `meta` ("Location or Product Used").
- `quote` becomes `body`.

```json
{
  "type": "review",
  "name": "Review",
  "limit": 12,
  "settings": [
    { "type": "range", "id": "rating", "label": "Rating", "min": 1, "max": 5, "step": 1, "default": 5 },
    { "type": "text", "id": "title", "label": "Review Title", "default": "Better than I expected" },
    { "type": "textarea", "id": "body", "label": "Review", "default": "Tastes great and I noticed a difference within the first week." },
    { "type": "text", "id": "name", "label": "Name", "default": "Sam R." },
    { "type": "text", "id": "meta", "label": "Location or Product Used" },
    { "type": "text", "id": "date", "label": "Date", "info": "Displayed as typed, e.g. 'March 2026'." },
    { "type": "checkbox", "id": "verified", "label": "Verified Buyer", "default": true },
    { "type": "image_picker", "id": "avatar", "label": "Photo", "info": "Optional. Initials show when blank." }
  ]
}
```

Add a section-level `verified_label` text setting (default "Verified Buyer").

### 12.6 `press_quote`

```json
{
  "type": "press_quote",
  "name": "Press Quote",
  "limit": 8,
  "settings": [
    { "type": "image_picker", "id": "logo", "label": "Publication Logo", "info": "SVG or transparent PNG." },
    { "type": "textarea", "id": "quote", "label": "Quote", "default": "A standout in a crowded category." },
    { "type": "text", "id": "source", "label": "Source", "info": "Shown when no logo is set, and as the logo's alt fallback." },
    { "type": "url", "id": "link", "label": "Article Link" }
  ]
}
```

Section groups: Logos (§10.2) + CG-SECTION-TYPE.

### 12.7 `stat`

**Differs from feature:** number-led, with no icon. Every part is `text`, so values like "10K+", "−57" or "4.9★" work.

```json
{
  "type": "stat",
  "name": "Stat",
  "limit": 6,
  "settings": [
    { "type": "text", "id": "prefix", "label": "Prefix", "info": "e.g. '$' or '#'." },
    { "type": "text", "id": "value", "label": "Value", "default": "10,000", "info": "Keep it short. This is the big number." },
    { "type": "text", "id": "suffix", "label": "Suffix", "info": "e.g. '+', '%' or 'K'." },
    { "type": "text", "id": "label", "label": "Label", "default": "Happy customers" },
    { "type": "textarea", "id": "description", "label": "Description", "info": "Optional supporting line." },
    { "type": "text", "id": "source", "label": "Source", "info": "Optional citation, shown as fine print." }
  ]
}
```

Section groups: Layout → CG-CARD (optional) → Item Typography: `item_value_style` (default `text-h1`), `item_text_style` (default `text-body-sm`), `item_accent_color` (value color) → `show_dividers` checkbox.

A count-up animation, if used, must respect `prefers-reduced-motion`. It's a section checkbox (`animate_numbers`), not per stat.

### 12.8 `step`

**Differs from list_item:** ordered and numbered, with a title, body and optional image.

```json
{
  "type": "step",
  "name": "Step",
  "limit": 8,
  "settings": [
    { "type": "text", "id": "number", "label": "Number or Label", "info": "Leave blank to auto-number. Use 'Week 1' etc. for timelines." },
    { "type": "text", "id": "title", "label": "Title", "default": "Mix one scoop" },
    { "type": "richtext", "id": "text", "label": "Text", "default": "<p>Add to 12 oz of cold water and shake.</p>" },
    { "type": "image_picker", "id": "image", "label": "Image", "info": "Optional." }
  ]
}
```

Section groups: Layout (`orientation` radio: Horizontal / Vertical Timeline) → "Step Number" group (`number_style` radio: Circle / Plain / None; `number_background_color`; `number_text_color`) → CG-CARD → CG-SECTION-TYPE.

### 12.9 `faq_item`

`accordion_item` is the same block. Use `faq_item` for FAQ sections.

```json
{
  "type": "faq_item",
  "name": "FAQ Item",
  "limit": 20,
  "settings": [
    { "type": "text", "id": "question", "label": "Question", "default": "What's your return policy?" },
    { "type": "richtext", "id": "answer", "label": "Answer", "default": "<p>We offer a 30-day money-back guarantee on every order.</p>" },
    { "type": "checkbox", "id": "open_by_default", "label": "Open by Default", "default": false }
  ]
}
```

Section-level "Accordion" group:
- `icon_style` radio: Chevron / Plus-Minus
- `icon_position` radio: Right / Left
- `allow_multiple` checkbox ("Allow Multiple Open")
- `divider_color`
- `item_title_style` (question, default `text-h5`) and `item_text_style` (answer)

Render with `<details>`/`<summary>` so the accordion works without JS and is keyboard accessible.

**Product pages:** PDP accordions (How to Use, Ingredients, Description) are **not** blocks. They are metafield-bound rows in a zero-block resource section (§16.2).

### 12.10 `trust_item`

```json
{
  "type": "trust_item",
  "name": "Trust Item",
  "limit": 6,
  "settings": [
    { "type": "select", "id": "icon", "label": "Icon", "default": "truck",
      "options": [ { "value": "truck", "label": "Truck (Shipping)" }, { "value": "return", "label": "Return" }, { "value": "lock", "label": "Lock (Secure)" }, { "value": "shield", "label": "Shield" }, { "value": "leaf", "label": "Leaf" }, { "value": "star", "label": "Star" }, { "value": "award", "label": "Award" }, { "value": "check_circle", "label": "Check Circle" }, { "value": "none", "label": "None" } ] },
    { "type": "image_picker", "id": "icon_image", "label": "Custom Icon", "info": "Overrides the preset. SVG recommended." },
    { "type": "text", "id": "title", "label": "Title", "default": "Free shipping" },
    { "type": "text", "id": "subtitle", "label": "Subtitle", "info": "Optional, e.g. 'On orders over $50'." },
    { "type": "url", "id": "link", "label": "Link" }
  ]
}
```

Section: CG-ICON-STYLE + CG-SECTION-TYPE. Certification or payment logos use `logo` (§10.2) instead.

### 12.11 `badge`

A small chip, e.g. "New", "Best Seller", "HSA Eligible". It usually appears once or twice inside a content stack, so it carries its own colors.

```json
{
  "type": "badge",
  "name": "Badge",
  "limit": 3,
  "settings": [
    { "type": "text", "id": "text", "label": "Badge Text", "default": "New" },
    { "type": "select", "id": "icon", "label": "Icon", "default": "none",
      "options": [ { "value": "none", "label": "None" }, { "value": "check", "label": "Check" }, { "value": "star", "label": "Star" }, { "value": "sparkle", "label": "Sparkle" }, { "value": "leaf", "label": "Leaf" }, { "value": "award", "label": "Award" } ] },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-label" },
    { "type": "select", "id": "background_color", "label": "Background Color", "options": "background_colors", "default": "var(--clr-accent)" },
    { "type": "select", "id": "text_color", "label": "Text Color", "options": "background_colors", "default": "var(--clr-white)" },
    { "type": "header", "content": "Shape" },
    { "type": "checkbox", "id": "show_border", "label": "Show Border", "default": false },
    { "type": "select", "id": "border_color", "label": "Border Color", "options": "background_colors", "default": "var(--clr-primary)",
      "visible_if": "{{ block.settings.show_border }}" },
    { "type": "corner_radius", "id": "border_radius", "label": "Corner Radius" }
  ]
}
```

Badges have a fixed 1px border when on, which is why there's no width setting. Badges on product cards are an item field (`badge_text`) styled at section level, not this block.

### 12.12 `rating`

```json
{
  "type": "rating",
  "name": "Rating",
  "limit": 1,
  "settings": [
    { "type": "radio", "id": "source", "label": "Rating Source", "default": "manual",
      "info": "Product Data works only on product templates or with a product picker in the section.",
      "options": [ { "value": "product", "label": "Product Data" }, { "value": "manual", "label": "Manual" } ] },
    { "type": "range", "id": "rating", "label": "Rating", "min": 0, "max": 5, "step": 0.5, "default": 5,
      "visible_if": "{{ block.settings.source == 'manual' }}" },
    { "type": "text", "id": "rating_text", "label": "Rating Text", "default": "4.9 · 1,200+ reviews" },
    { "type": "url", "id": "link", "label": "Link", "info": "Optional, e.g. #reviews." },
    { "type": "header", "content": "Style" },
    { "type": "select", "id": "star_color", "label": "Star Color", "options": "background_colors", "default": "var(--clr-accent)" },
    { "type": "select", "id": "text_style", "label": "Text Style", "options": "text_presets", "default": "text-label" }
  ]
}
```

`product.ratings` / `product.reviews` exist on product templates. Verify their shape on the store before binding. When unavailable, fall back to Manual.

### 12.13 `team_member`

```json
{
  "type": "team_member",
  "name": "Team Member",
  "limit": 12,
  "settings": [
    { "type": "image_picker", "id": "avatar", "label": "Photo", "info": "Square or 4:5 crop. Set alt text in the picker." },
    { "type": "text", "id": "name", "label": "Name", "default": "Dr. Alex Morgan" },
    { "type": "text", "id": "role", "label": "Role", "default": "Chief Science Officer" },
    { "type": "text", "id": "credentials", "label": "Credentials", "info": "Optional, e.g. 'PhD, Nutritional Biochemistry'." },
    { "type": "richtext", "id": "bio", "label": "Bio" },
    { "type": "url", "id": "link", "label": "Profile Link" }
  ]
}
```

### 12.14 `ingredient`

```json
{
  "type": "ingredient",
  "name": "Ingredient",
  "limit": 12,
  "settings": [
    { "type": "image_picker", "id": "image", "label": "Image" },
    { "type": "text", "id": "name", "label": "Name", "default": "Ashwagandha" },
    { "type": "text", "id": "amount", "label": "Amount", "info": "Optional, e.g. '600 mg'." },
    { "type": "richtext", "id": "text", "label": "Description", "default": "<p>Supports a healthy stress response.</p>" },
    { "type": "checkbox", "id": "featured", "label": "Featured", "default": false }
  ]
}
```

A supplement-facts **table** is product data: render it from a metafield in the resource section, not from blocks.

### 12.15 `comparison_row`

Tri-state values (check / x / text) beat a boolean pair, because they can show "500 mg vs 50 mg".

```json
{
  "type": "comparison_row",
  "name": "Comparison Row",
  "limit": 20,
  "settings": [
    { "type": "text", "id": "feature", "label": "Feature", "default": "Clinically studied ingredients" },
    { "type": "header", "content": "Our Column" },
    { "type": "radio", "id": "ours", "label": "Value", "default": "check",
      "options": [ { "value": "check", "label": "Check" }, { "value": "x", "label": "X" }, { "value": "text", "label": "Text" } ] },
    { "type": "text", "id": "ours_text", "label": "Text", "visible_if": "{{ block.settings.ours == 'text' }}" },
    { "type": "header", "content": "Their Column" },
    { "type": "radio", "id": "theirs", "label": "Value", "default": "x",
      "options": [ { "value": "check", "label": "Check" }, { "value": "x", "label": "X" }, { "value": "text", "label": "Text" } ] },
    { "type": "text", "id": "theirs_text", "label": "Text", "visible_if": "{{ block.settings.theirs == 'text' }}" }
  ]
}
```

Section settings: `ours_label`, `theirs_label`, `ours_highlight_color`, `check_color`, `x_color`, `row_divider_color`.

### 12.16 `tab`

Tabbed sections declare `tab` blocks (label and key) plus the content items, each of which gets a `tab_key` select with the same fixed keys.

```json
{
  "type": "tab",
  "name": "Tab",
  "limit": 6,
  "settings": [
    { "type": "text", "id": "label", "label": "Tab Label", "default": "Overview" },
    { "type": "select", "id": "tab_key", "label": "Tab Slot", "default": "tab_1",
      "options": [ { "value": "tab_1", "label": "Tab 1" }, { "value": "tab_2", "label": "Tab 2" }, { "value": "tab_3", "label": "Tab 3" }, { "value": "tab_4", "label": "Tab 4" }, { "value": "tab_5", "label": "Tab 5" }, { "value": "tab_6", "label": "Tab 6" } ] }
  ]
}
```

Each content item in a tabbed section gets `{ "type": "select", "id": "tab_key", "label": "Show in Tab", … same options … }` as its first setting.

---

## 13. Commerce Blocks

Prices print through the platform's member-aware price output: `product.price`, variant `display_price`, `money`. Never offer a "price override" text field, because it breaks member pricing. The cart and checkout run through the FairShare SDK (`data-fluid-*` attributes). Never add the SDK script to a theme.

### 13.1 `product_card`

**Fields:**
- **Product** (picker). It fills image, title, price, link and add-to-cart.
- **Badge Text** and **Tag**.
- An *Overrides* group, where blank means use product data.
- **Button Text** override.

```json
{
  "type": "product_card",
  "name": "Product Card",
  "limit": 12,
  "settings": [
    { "type": "product", "id": "product", "label": "Product",
      "info": "Fills image, name, price, link and add to cart. Fields below override when filled." },
    { "type": "text", "id": "badge_text", "label": "Badge Text", "info": "Optional, e.g. 'Best Seller'." },
    { "type": "header", "content": "Overrides (Blank = Product Data)" },
    { "type": "text", "id": "title", "label": "Title" },
    { "type": "textarea", "id": "description", "label": "Short Description" },
    { "type": "image_picker", "id": "image", "label": "Image" },
    { "type": "image_picker", "id": "image_hover", "label": "Hover Image" },
    { "type": "text", "id": "button_text", "label": "Button Text", "info": "Overrides the section's default button text." }
  ]
}
```

Section groups:
1. Layout
2. **Product Display**:
   - `show_price`, `show_compare_price`, `show_rating`, `show_description`, `show_subscription_price` (checkboxes)
   - `image_aspect_ratio`
3. **Card Button** (§8.5), plus:
   - `button_action` radio: Add to Cart / Go to Product
   - `open_cart_after_add` checkbox
   - `loading_text` ("Adding…")
   - `sold_out_text`
4. CG-CARD
5. `badge_background_color` / `badge_text_color`
6. CG-SECTION-TYPE

Source alternatives at section level: `collection` or `product_list` pickers, with a `source` radio (Collection / Pick Products / Blocks). Use `visible_if` to show the matching picker.

**Add-to-cart markup:**

```liquid
<button type="button" class="btn …"
  data-fluid-add-to-cart="{{ p.selected_or_first_available_variant.id }}"
  data-fluid-quantity="1"
  {% if section.settings.open_cart_after_add %}data-fluid-open-cart-after-add{% endif %}
  data-fluid-loading-text="{{ section.settings.loading_text | escape }}"
  {% unless p.available %}disabled{% endunless %}>{{ label | escape }}</button>
```

### 13.2 `enrollment_card`

```json
{
  "type": "enrollment_card",
  "name": "Enrollment Pack",
  "limit": 4,
  "settings": [
    { "type": "enrollment_pack", "id": "enrollment_pack", "label": "Enrollment Pack",
      "info": "Fills name, image, price and enroll button. Fields below override when filled." },
    { "type": "text", "id": "badge_text", "label": "Badge Text", "info": "Optional, e.g. 'Most Popular'." },
    { "type": "checkbox", "id": "featured", "label": "Featured", "default": false },
    { "type": "header", "content": "Overrides (Blank = Pack Data)" },
    { "type": "text", "id": "title", "label": "Title" },
    { "type": "image_picker", "id": "image", "label": "Image" },
    { "type": "richtext", "id": "description", "label": "Description" },
    { "type": "textarea", "id": "features", "label": "Included / Features", "info": "One per line." },
    { "type": "text", "id": "button_text", "label": "Button Text" },
    { "type": "url", "id": "fallback_link", "label": "Fallback Link", "info": "Used only when no pack is selected." }
  ]
}
```

Enroll markup: `<button data-fluid-add-enrollment-pack="{{ pack.id }}">`. Dynamic bundle packs also need `data-fluid-bundle-selections`. In JS, `FairShareSDK.addEnrollmentPack(packId)` takes the **pack** ID and rethrows on error. Section groups mirror product_card: `show_price`, `show_included_products`, Card Button, CG-CARD with featured colors.

### 13.3 `collection_tile`

```json
{
  "type": "collection_tile",
  "name": "Collection Tile",
  "limit": 12,
  "settings": [
    { "type": "collection", "id": "collection", "label": "Collection", "info": "Fills image, title and link." },
    { "type": "header", "content": "Overrides (Blank = Collection Data)" },
    { "type": "image_picker", "id": "image", "label": "Image" },
    { "type": "text", "id": "title", "label": "Title" },
    { "type": "text", "id": "subtitle", "label": "Subtitle" },
    { "type": "text", "id": "button_text", "label": "Button Text" },
    { "type": "url", "id": "link", "label": "Link", "info": "Overrides the collection link." }
  ]
}
```

Use `category` in place of `collection` for category tiles. Section: image aspect + CG-CARD (with `card_hover_effect`) + Card Button.

### 13.4 Specialized buttons

Each one is the **full `button` schema (§8.1)**, with `link` removed where the action replaces it, plus the extras below. Default text changes accordingly.

| Type | Extra settings (after Content) | Markup / behavior |
|---|---|---|
| `add_to_cart` | `product` or `variant` picker · `quantity` (range 1–10, default 1) · `purchase_type` radio (One-Time / Subscribe) · `loading_text` · `sold_out_text` · `open_cart_after_add` | `<button data-fluid-add-to-cart="{{variant.id}}" data-fluid-quantity data-fluid-subscribe data-fluid-subscription-plan-id data-fluid-loading-text data-fluid-open-cart-after-add>`. Disabled when unavailable |
| `buy_now` | same as add_to_cart | JS: `await FairShareSDK.addCartItems(variantId, {quantity})`. **Check the result:** it resolves `undefined` on failure. Then `FairShareSDK.checkout()`. Wrap in `FairShareSDK.withButtonLoading(btn, fn)` |
| `enroll_button` | `enrollment_pack` picker · `loading_text` · `fallback_link` | `data-fluid-add-enrollment-pack="{{pack.id}}"` (+ `data-fluid-bundle-selections` for dynamic packs) |
| `cart_button` | `icon` radio (Bag / Cart / Basket) · `icon_size` · a "Cart Count" group (`show_count`, `count_background_color`, `count_text_color`) | `<button data-fluid-cart="open" aria-haspopup="dialog">` + the cart count element. Remove Text Style/Width |
| `account_button` | `display` radio (Icon / Label / Both) · `label` · `icon_size` | Use the documented member account tag/links (see member storefront docs) |
| `rep_link` | `link_target` radio (Rep's Site / Custom URL) | `data-fluid-affiliate-href="my_site_url"` + CG-AFFILIATE-VISIBILITY defaulted to "Shopping With a Rep" |

Theme-specific actions (e.g. Yoli's market-based `link_type` URL resolver, video-modal "film" buttons) stay in the section that needs them. Don't add them to the canonical button.

---

## 14. Affiliate & Personalization

Storefront pages are cached and served to everyone, so **Liquid can't know who the rep or member is**. Affiliate-aware content is rendered with [hydration](https://docs.fluid.app/themes/affiliate-hydration). The server outputs stable placeholders and corporate-configured fallbacks. The FairShare SDK fills in the rep's details in the browser.

The two-state model still holds:
- **Default state:** no rep attributed. Corporate configures it.
- **Affiliate state:** the visitor arrived via a rep link. Corporate configures what shows; the rep's own profile values fill it in.

Both states are built from these documented primitives. The old `affiliate_settings` / `affiliate_editable` schema keys are not part of the platform contract, so don't use them.

| Need | Use |
|---|---|
| Rep's name / email / initials in text | `<fluid-affiliate-name>Fallback</fluid-affiliate-name>`, `<fluid-affiliate-email>`, `<fluid-affiliate-initials>` |
| Rep avatar image | `<img data-fluid-affiliate-src="avatar" data-fluid-affiliate-alt="name" alt="" data-fluid-affiliate-show-if="avatar" style="display:none">` (never put an avatar URL in `src`) |
| Link to the rep's site | `<a data-fluid-affiliate-href="my_site_url">` |
| Rep username inside a URL | `href="/{{ username }}/shop"`. Anonymous visitors fall back to `home` |
| Show only when attributed | `data-fluid-affiliate-show-if="affiliate"` + `style="display:none"` (pre-hide to avoid a flash) |
| Hide when attributed | `data-fluid-affiliate-hide-if="affiliate"` |
| Signed-in rep check | `affiliate.logged_in_rep_for_store`, never `affiliate.name != blank` (that's a sentinel on cached pages) |

**Never** branch on `{% if affiliate.name %}` / `{% if affiliate.avatar %}` in cached templates. Several surveyed themes do, and it's always true or always false.

### 14.1 CG-AFFILIATE-VISIBILITY on any block

Render the block's outer element with:
- `data-fluid-affiliate-show-if="affiliate" style="display:none"` when the value is `affiliate`
- `data-fluid-affiliate-hide-if="affiliate"` when it's `no_affiliate`

This lets corporate build both states from ordinary blocks. For example: one "Shop with our team" heading for no rep, one "Shop with your guide" heading for reps.

### 14.2 `affiliate_banner` (rep attribution line)

Based on Puralta `announcement_bar` → `affiliate` block, the one fully docs-compliant implementation found.

```json
{
  "type": "affiliate_banner",
  "name": "Rep Attribution",
  "limit": 1,
  "settings": [
    { "type": "text", "id": "prefix", "label": "Text Before Name", "default": "You're shopping with" },
    { "type": "text", "id": "name_fallback", "label": "Name Fallback", "default": "our team",
      "info": "Shown while the rep loads, and when the rep has no display name." },
    { "type": "checkbox", "id": "show_avatar", "label": "Show Rep Photo", "default": true },
    { "type": "checkbox", "id": "link_to_rep_site", "label": "Link to Rep's Site", "default": true },
    { "type": "text", "id": "anonymous_text", "label": "Message When No Rep", "info": "Leave blank to show nothing when no rep is attributed." }
  ]
}
```

The sibling content blocks in the same bar get CG-AFFILIATE-VISIBILITY, so shoppers see one message, not two. Section: `avatar_size` range + a `text_color` select (the rep line has no Style group of its own).

### 14.3 `affiliate_bio` (rep card)

```json
{
  "type": "affiliate_bio",
  "name": "Rep Card",
  "limit": 1,
  "settings": [
    { "type": "text", "id": "heading_prefix", "label": "Heading", "default": "Your wellness guide" },
    { "type": "text", "id": "name_fallback", "label": "Name Fallback", "default": "Our team" },
    { "type": "checkbox", "id": "show_avatar", "label": "Show Rep Photo", "default": true },
    { "type": "checkbox", "id": "show_initials_fallback", "label": "Show Initials When No Photo", "default": true },
    { "type": "richtext", "id": "note", "label": "Note", "default": "<p>Have questions? I'm happy to help you choose.</p>",
      "info": "Shown under the rep's name." },
    { "type": "text", "id": "button_text", "label": "Button Text", "default": "Visit My Site",
      "info": "Links to the rep's personal site. Leave blank to hide." },
    { "type": "checkbox", "id": "only_when_attributed", "label": "Only Show When Shopping With a Rep", "default": true }
  ]
}
```


### 14.4 Member-aware content (pilot)

Member storefront is in limited pilot. Where it's enabled:
- `{% member %}…{% else %}…{% endmember %}` swaps member and guest content.
- `{% member_name %}` greets the member.

There's no `member` object in storefront Liquid, so `{% if member %}` is always false. Prices are already member-aware. Don't add member blocks to default sections unless the user asks.

---

## 15. Sections

### 15.1 Section Base (every content section)

The base is appended **after** the section's content settings and its Layout, Card and Item groups, in this order: **Container → Section Shell**. **Section Corner Radius is always the last setting.**

There's no section-level text-color group for block-based sections. Each text block carries its own Color (§7), and repeated items take their text colors from CG-SECTION-TYPE. Only **zero-block resource sections** (§16) add a Colors group, because their text isn't in blocks.

```json
{ "type": "header", "content": "Container" },
{ "type": "select", "id": "container_max_width", "label": "Content Width", "default": "1280px",
  "options": [
    { "value": "960px", "label": "Narrow (960px)" },
    { "value": "1280px", "label": "Default (1280px)" },
    { "value": "1440px", "label": "Wide (1440px)" },
    { "value": "100%", "label": "Full Width" }
  ] },
{ "type": "padding", "id": "container_padding", "label": "Container Padding" },
{ "type": "select", "id": "container_background_color", "label": "Container Background", "options": "background_colors", "default": "transparent" },
{ "type": "image_picker", "id": "container_background_image", "label": "Container Background Image" },
{ "type": "range", "id": "container_overlay_opacity", "label": "Container Overlay Opacity", "min": 0, "max": 90, "step": 5, "unit": "%", "default": 0,
  "visible_if": "{{ section.settings.container_background_image != blank }}" },
{ "type": "select", "id": "container_overlay_color", "label": "Container Overlay Color", "options": "background_colors", "default": "var(--clr-black)",
  "visible_if": "{{ section.settings.container_overlay_opacity > 0 }}" },
{ "type": "checkbox", "id": "show_container_border", "label": "Show Container Border", "default": false },
{ "type": "range", "id": "container_border_width", "label": "Container Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
  "visible_if": "{{ section.settings.show_container_border }}" },
{ "type": "select", "id": "container_border_color", "label": "Container Border Color", "options": "background_colors", "default": "var(--clr-light)",
  "visible_if": "{{ section.settings.show_container_border }}" },
{ "type": "corner_radius", "id": "container_border_radius", "label": "Container Corner Radius" },

{ "type": "header", "content": "Section Shell" },
{ "type": "text", "id": "anchor_id", "label": "Anchor ID", "info": "Optional. Lets links jump here with #anchor-id. Lowercase, no spaces." },
{ "type": "padding", "id": "section_padding", "label": "Section Padding", "info": "Desktop values. Tablet and mobile scale automatically." },
{ "type": "select", "id": "background_color", "label": "Background Color", "options": "background_colors", "default": "transparent" },
{ "type": "image_picker", "id": "background_image", "label": "Background Image", "info": "2400px wide recommended." },
{ "type": "select", "id": "background_position", "label": "Background Focal Point", "default": "center",
  "visible_if": "{{ section.settings.background_image != blank }}",
  "options": [ { "value": "center", "label": "Center" }, { "value": "top", "label": "Top" }, { "value": "bottom", "label": "Bottom" }, { "value": "left", "label": "Left" }, { "value": "right", "label": "Right" } ] },
{ "type": "range", "id": "overlay_opacity", "label": "Overlay Opacity", "min": 0, "max": 90, "step": 5, "unit": "%", "default": 0,
  "visible_if": "{{ section.settings.background_image != blank }}" },
{ "type": "select", "id": "overlay_color", "label": "Overlay Color", "options": "background_colors", "default": "var(--clr-black)",
  "visible_if": "{{ section.settings.overlay_opacity > 0 }}" },
{ "type": "checkbox", "id": "show_section_border", "label": "Show Section Border", "default": false },
{ "type": "range", "id": "section_border_width", "label": "Section Border Width", "min": 1, "max": 10, "step": 1, "unit": "px", "default": 1,
  "visible_if": "{{ section.settings.show_section_border }}" },
{ "type": "select", "id": "section_border_color", "label": "Section Border Color", "options": "background_colors", "default": "var(--clr-light)",
  "visible_if": "{{ section.settings.show_section_border }}" },
{ "type": "corner_radius", "id": "section_border_radius", "label": "Section Corner Radius" }
```

- The page background is a page/theme setting, not a section control.
- Default section padding is 64 / 24 / 64 / 24 (`fluid-theme-presets-v2.md` §3). Apply it in CSS when the padding value is blank.
- A section may drop the Container group only when it has no inner content box, such as a full-bleed marquee.

### 15.2 Standard Layout group

Pick only the settings the section needs, in this order:

```json
{ "type": "header", "content": "Layout" },
{ "type": "radio", "id": "content_alignment", "label": "Content Alignment", "default": "left",
  "info": "Text blocks set to Auto follow this.",
  "options": [ { "value": "left", "label": "Left" }, { "value": "center", "label": "Center" }, { "value": "right", "label": "Right" } ] },
{ "type": "radio", "id": "media_position", "label": "Media Position", "default": "left",
  "options": [ { "value": "left", "label": "Left" }, { "value": "right", "label": "Right" } ] },
{ "type": "select", "id": "media_width", "label": "Media Width", "default": "50",
  "options": [ { "value": "40", "label": "40%" }, { "value": "50", "label": "50%" }, { "value": "60", "label": "60%" } ] },
{ "type": "radio", "id": "vertical_alignment", "label": "Vertical Alignment", "default": "center",
  "options": [ { "value": "start", "label": "Top" }, { "value": "center", "label": "Center" }, { "value": "end", "label": "Bottom" } ] },
{ "type": "range", "id": "columns", "label": "Columns", "min": 1, "max": 6, "step": 1, "unit": "col", "default": 3,
  "info": "Desktop. Tablet and mobile collapse automatically." },
{ "type": "range", "id": "gap", "label": "Gap", "min": 0, "max": 80, "step": 4, "unit": "px", "default": 24 },
{ "type": "select", "id": "min_height", "label": "Minimum Height", "default": "auto",
  "options": [ { "value": "auto", "label": "Fit Content" }, { "value": "50vh", "label": "Half Screen" }, { "value": "75vh", "label": "Three-Quarter Screen" }, { "value": "100vh", "label": "Full Screen" } ] }
```

**Carousel** sections add these after Layout:
- `autoplay` checkbox
- `autoplay_speed` range, 3–10 s
- `show_arrows` and `show_dots` checkboxes
- `loop` checkbox

Here `columns` means slides per view on desktop.

### 15.3 Section archetypes

| Archetype | Blocks accepted (declare in this order) | Section groups after content |
|---|---|---|
| **Rich text / intro** | eyebrow, heading, subheading, text, button, link, badge, rating, divider, custom_liquid | Layout (content_alignment) → Base |
| **Hero** | eyebrow, heading, subheading, text, button, link, badge, rating, trust_item | **Hero Media**: `image`, `video` (`video_picker`, ambient), plus the CG-MEDIA-DISPLAY overlay subset. Then Layout (content_alignment, vertical_alignment, min_height) → Base |
| **Split (media + content)** | intro blocks | **Media**: `image`, `video` or `media` + CG-MEDIA-DISPLAY + CG-BORDER, all section-level. Then Layout (media_position, media_width, vertical_alignment) → Base |
| **Grid** (features, cards, stats, trust, team, ingredients) | intro blocks + one or two item types | Layout (content_alignment, columns, gap) → CG-CARD → CG-SECTION-TYPE → CG-ICON-STYLE (if icons) → Base |
| **Carousel** (testimonials, reviews, UGC, gallery, products) | intro blocks + item type | Layout + Carousel → CG-CARD → CG-SECTION-TYPE → Base |
| **FAQ** | intro blocks + faq_item | Layout → Accordion → Base |
| **Logo wall / marquee** | intro blocks + logo | Layout (columns) → Logos → `marquee` checkbox + `marquee_speed` → Base |
| **Product grid** | intro blocks + product_card | Source (collection / product_list / blocks) → Layout → Product Display → Card Button → CG-CARD → Base |
| **Comparison** | intro blocks + comparison_row | Table colors → Base |
| **Announcement bar** | text (message), link, affiliate_banner | Section Shell only (plus the rep line's `text_color`) |

**Hero media is a section setting, not a block,** because it defines the layout rather than sitting in the content stack. Never add both a section-level heading/text setting **and** a heading/text block for the same copy. Make Wellness has 50 sections with this duplicate.

**Intro stack plus items:** render intro-type blocks in the header area and item-type blocks in the grid, each in their saved order:

```liquid
<div class="x__intro">
  {%- for block in section.blocks -%}
    {%- case block.type -%}
      {%- when 'eyebrow', 'heading', 'subheading', 'text', 'button', 'link', 'badge', 'rating' -%}
        {%- render 'block_intro', block: block -%}
    {%- endcase -%}
  {%- endfor -%}
</div>
<div class="x__grid">
  {%- for block in section.blocks -%}
    {%- if block.type == 'feature' -%} … {%- endif -%}
  {%- endfor -%}
</div>
```

### 15.4 Presets

- Every section has at least one preset, and its blocks show a realistic, complete example. Never ship a blank one.
- Preset setting keys must match declared IDs.
- Use the preset `category` field to group sections in the picker: Hero · Text & Media · Social Proof · Product · Collection · Enrollment · Content · FAQ · Promotion · Footer & Navigation.
- Remember that presets refill empty sections on every render (§2.5).

---

## 16. Resource Sections (Zero-Block, Metafield-Driven)

### 16.1 Principles

1. **No `"blocks"` array.** All content comes from the resource plus metafields. One template then serves every product, pack or post.
2. **`enabled_on`** restricts the section to its template: `{"templates": ["product"]}`, `["enrollment_pack"]`, `["post"]`, `["collection"]`, `["category"]`. Use only documented template types (`blog` isn't one).
3. **Section settings are display options, labels and binding switches**, not content. For example: "Show Rating", "Ingredients Dropdown Label", "Show Sticky Add-to-Cart".
4. **Metafields** are read by literal dot path, the same way on every resource: `product.metafields.custom.how_to_use`, `variant.metafields.custom.swatch_color`, `enrollment_pack.metafields.custom.whats_included`, `post.metafields.custom.read_time`.
   - Assign each one once at the top.
   - Guard every row so it disappears when the metafield is blank.
   - Document the binding in the toggle's `info`.
   - Never add editable namespace/key settings.
   - Full rules and diagnostics: `/themes/theme-metafields-skill.md`. It's written around products, but the access pattern, guard pattern and schema conventions apply unchanged to enrollment packs and posts.
   - Use each metafield according to its **type**. Values arrive typed, so don't coerce them:

     | Metafield type | Typical use in the section | Render |
     |---|---|---|
     | Rich text | Accordion body, description, ingredients | Raw inside `<div class="rte">` |
     | Single-line / multi-line text | Eyebrow, badge, meta line, note | `\| escape`. Multi-line: split on newlines for lists |
     | Number / decimal | Servings, supply days, read time | Print directly, adding units in the markup |
     | Boolean | Show/hide a badge or row | Use it as the condition |
     | URL | Secondary link, video link | `href="{{ mf \| escape }}"` |
     | File / image | Badge art, swatch image, comparison chart | `{{ mf \| media_tag: alt: … }}` |
     | JSON / list | Benefits list, nutrition rows, FAQ pairs | `{% for item in mf %}` over the parsed value |
     | Color | Swatch color | Print into CSS with a `\| default:` fallback |
5. **Variant state** comes from the URL (`?variant_id=`, `?option_value_ids=`). Read prices from `variant.variant_countries` filtered by `localization.country.iso_code`. `selected_or_first_available_variant` has no price table.

### 16.2 Product header: canonical settings groups

Order:
1. Media
2. Product Information
3. Price & Purchase
4. Add to Cart (Card Button pattern, prefix `cta_`)
5. one group per **metafield-backed row**
6. Trust & Payment
7. Sticky Bar
8. **Colors:** `title_color`, `text_color`, `accent_color`. Resource sections have no text blocks, so the section colors its own fields.
9. Container
10. Section Shell

```json
{
  "name": "Product Header",
  "tag": "section",
  "enabled_on": { "templates": ["product"] },
  "settings": [
    { "type": "header", "content": "Media" },
    { "type": "radio", "id": "thumbnail_position", "label": "Thumbnails", "default": "bottom",
      "options": [ { "value": "bottom", "label": "Below" }, { "value": "left", "label": "Left" }, { "value": "none", "label": "Hidden" } ] },
    { "type": "select", "id": "image_aspect_ratio", "label": "Image Aspect Ratio", "default": "1/1",
      "options": [ { "value": "1/1", "label": "Square (1:1)" }, { "value": "4/5", "label": "Portrait (4:5)" }, { "value": "auto", "label": "Original" } ] },
    { "type": "select", "id": "media_background_color", "label": "Media Background", "options": "background_colors", "default": "var(--clr-light)" },

    { "type": "header", "content": "Product Information" },
    { "type": "text", "id": "eyebrow", "label": "Eyebrow", "info": "Optional. Overridden by the custom.eyebrow metafield when set." },
    { "type": "select", "id": "title_style", "label": "Title Style", "options": "text_presets", "default": "text-h2" },
    { "type": "checkbox", "id": "show_rating", "label": "Show Rating", "default": true },
    { "type": "checkbox", "id": "show_short_description", "label": "Show Short Description", "default": true },

    { "type": "header", "content": "Price & Purchase" },
    { "type": "checkbox", "id": "show_compare_price", "label": "Show Compare-At Price", "default": true },
    { "type": "text", "id": "onetime_label", "label": "One-Time Label", "default": "One-time purchase" },
    { "type": "text", "id": "subscribe_label", "label": "Subscribe Label", "default": "Subscribe & save" },
    { "type": "checkbox", "id": "show_quantity", "label": "Show Quantity Selector", "default": true },

    { "type": "header", "content": "Add to Cart" },
    { "type": "text", "id": "cta_text", "label": "Button Text", "default": "Add to Cart" },
    { "type": "text", "id": "cta_loading_text", "label": "Loading Text", "default": "Adding…" },
    { "type": "text", "id": "soldout_text", "label": "Sold-Out Text", "default": "Sold Out" },
    { "type": "select", "id": "cta_background_color", "label": "Button Background", "options": "background_colors", "default": "var(--clr-primary)" },
    { "type": "select", "id": "cta_text_color", "label": "Button Text Color", "options": "background_colors", "default": "var(--clr-white)" },
    { "type": "select", "id": "cta_hover_effect", "label": "Button Hover Effect", "default": "theme",
      "options": [ { "value": "theme", "label": "Theme Default" }, { "value": "colors", "label": "Change Colors" }, { "value": "darken", "label": "Darken" }, { "value": "lighten", "label": "Lighten" }, { "value": "lift", "label": "Lift (shadow)" }, { "value": "none", "label": "None" } ] },
    { "type": "select", "id": "cta_hover_background_color", "label": "Button Hover Background", "options": "background_colors", "default": "var(--clr-secondary)",
      "visible_if": "{{ section.settings.cta_hover_effect == 'colors' }}" },
    { "type": "checkbox", "id": "open_cart_after_add", "label": "Open Cart After Adding", "default": true },

    { "type": "header", "content": "How to Use Dropdown" },
    { "type": "checkbox", "id": "show_how_to_use", "label": "Show How to Use", "default": true,
      "info": "Content comes from the product's custom.how_to_use metafield. The row hides on products without it." },
    { "type": "text", "id": "how_to_use_label", "label": "Dropdown Label", "default": "How to Use" },
    { "type": "checkbox", "id": "how_to_use_open", "label": "Expanded by Default", "default": false },

    { "type": "header", "content": "Trust & Payment" },
    { "type": "text", "id": "payment_note", "label": "Secure Checkout Note", "default": "Secure checkout" },
    { "type": "checkbox", "id": "pay_visa", "label": "Visa", "default": true,
      "info": "Turn on only the methods your payment processor accepts." },
    { "type": "checkbox", "id": "pay_mastercard", "label": "Mastercard", "default": true },

    { "type": "header", "content": "Sticky Bar" },
    { "type": "checkbox", "id": "show_sticky_bar", "label": "Show Sticky Add-to-Cart Bar", "default": true }
  ],
  "presets": [ { "name": "Product Header" } ]
}
```

The Colors group (step 8) plus Container and Section Shell from §15.1 follow; they're omitted above for length. Reference implementations: `tm3/sections/tm3v2_pdp_hero` (zero-block, six guarded metafields), `puralta/sections/pdp_header`, and `makewellness/sections/product_header_variant_group` (variant metafields for swatches).

```liquid
{%- assign mf_how_to_use = product.metafields.custom.how_to_use | strip -%}
{%- assign show_how_to_use = false -%}
{%- if section.settings.show_how_to_use and mf_how_to_use != blank -%}{%- assign show_how_to_use = true -%}{%- endif -%}
…
{%- if show_how_to_use -%}
  <details class="x__row"{% if section.settings.how_to_use_open %} open{% endif %}>
    <summary>{{ section.settings.how_to_use_label | default: 'How to Use' | escape }}</summary>
    <div class="rte">{{ mf_how_to_use }}</div>
  </details>
{%- endif -%}
```

Rich-text metafields output raw inside `.rte`. Plain-text metafields going into attributes or headings get `| escape`.

### 16.3 Other resource sections

| Section | Data | Typical settings |
|---|---|---|
| **Enrollment pack header** (`enrollment_pack`) | `enrollment_pack.title`, `description`, `images_array`, `price`, `enrollment_fee`, `membership_products`, `subscription_products`, `agreements`, `metafields` | Show fee, show included products, product list layout, Enroll button (Card Button pattern, prefix `cta_`), agreement note, Base. Enroll via `data-fluid-add-enrollment-pack` |
| **Blog post header** (`post`) | `post.title`, `post_author`, `post_date`, `image_url`, `category`, `summary`, `metafields` | Show Author / Date / Category / Featured Image, `date_format` select, image aspect ratio, Base |
| **Post body** (`post`) | `post.description` (body HTML) | Content Width (Narrow / Medium / Wide), typography via `.rte`, Base |
| **Collection / category main** | `collection.products` / `category.products` | Layout (columns, gap), Product Display, Card Button, CG-CARD, filters ([shop-tag-filters](https://docs.fluid.app/themes/shop-tag-filters)), Base |

Enrollment packs and posts have metafields, just like products. Their header sections read `enrollment_pack.metafields.<namespace>.<key>` and `post.metafields.<namespace>.<key>` with the same literal-path + guard + `info` pattern (§16.1). They use each value according to its type: an enrollment header might render a "What's included" rich-text metafield and a savings badge; a post header might render a read-time number and a subtitle.

---

## 17. Layout Containers (Section Slots)

Use a **container section** when whole sections must sit side by side or in a composed grid: feature panel + sidebar, five-panel showcase. This replaces the old idea of a "container block" for page layout. Full contract: [section-slots](https://docs.fluid.app/themes/section-slots).

- The container is an ordinary section. It declares `"slots": [{ "id": "main", "name": "Main Content" }, …]` in its schema and renders each slot once with a **literal** `{% section_slot 'main' %}`.
- Child sections need no slot-specific markup. Style the generated wrapper with direct-child selectors: `.grid > [data-fluid-section-slot="main"]`.
- Use **container queries** (`container: name / inline-size`) instead of viewport media queries, so layouts adapt when nested.
- Limits:
  - 25 children per slot
  - 100 descendants per root container
  - 4 container levels
  - one parent per child
  - no cycles
- Navbar and footer can't be slot children.
- Keep slot IDs stable. When adding a slot to a container already in use, initialize `"new_slot": []` in every saved placement.
- **Confirm the environment supports container rendering and editor authoring before building one.** It isn't available everywhere.

---

## 18. Rendering Rules

### 18.1 Section skeleton

```liquid
{%- assign s = section.settings -%}
{%- capture pt -%}{% render 'css_len', v: s.section_padding.top, d: 64 %}{%- endcapture -%}
{%- capture pb -%}{% render 'css_len', v: s.section_padding.bottom, d: 64 %}{%- endcapture -%}
{%- capture pl -%}{% render 'css_len', v: s.section_padding.left, d: 24 %}{%- endcapture -%}
{%- capture pr -%}{% render 'css_len', v: s.section_padding.right, d: 24 %}{%- endcapture -%}

{%- style -%}
  .fx-intro.section-{{ section.id }} {
    --pad-t: {{ pt }}; --pad-b: {{ pb }}; --pad-l: {{ pl }}; --pad-r: {{ pr }};
    padding: var(--pad-t) var(--pad-r) var(--pad-b) var(--pad-l);
    background-color: {{ s.background_color | default: 'transparent' }};
  }
  /* container, overlay, border, radius … see Section Base rules below */
{%- endstyle -%}

<div class="fx-intro section-{{ section.id }}"{% if s.anchor_id != blank %} id="{{ s.anchor_id | handleize }}"{% endif %}>
  <div class="fx-intro__container">
    {%- for block in section.blocks -%}
      {%- case block.type -%}
        {%- when 'heading' -%} …
      {%- endcase -%}
    {%- endfor -%}
  </div>
</div>
```

Rules:
- **Scope** every CSS rule to `.<prefix>.section-{{ section.id }}`. Use one short, unique class prefix per section.
- **One `{% style %}` block per section**, at the top. Prefer CSS custom properties over repeated inline styles.
- **Don't output `section.fluid_attributes`.** Fluid wraps the section. If the schema sets `"tag": "section"`, don't write another `<section>` inside it.
- **Overlays** go in `::before` or `::after`, only when opacity > 0. Keep the overlay behind content (`> * { position: relative }`).
- **Background images** are real CSS (`background-image: url({{ img | image_url: width: 2400 }})`), or a `media_tag` absolutely positioned behind the content. Don't use `data-bg` + JavaScript painting, which doesn't refresh in the editor.

### 18.2 Block rendering rules

- `{{ block.fluid_attributes }}` goes on the **outermost** element of every block, inline or standalone. The element should be the same size as the rendered block, so the editor's selection matches what the merchant sees.
- **Guard empty content:** `{%- if block.settings.text != blank -%}`. Never render empty wrappers, labels or dividers.
- **Escape** plain text that lands in attributes or button/link labels (`| escape`). Headings and rich text output unescaped, because they carry editor formatting.
- **Colors:** print the value directly, with the block's default preset as the fallback: `color: {{ block.settings.color | default: 'var(--clr-body)' }};`.
- **Every declared setting must be read by the markup.** A control that does nothing is a bug. The survey found 19 sections declaring button settings they never used.
- For fixed-position blocks fetched with `section.blocks | where: 'type', 'x' | first`, the type must have `limit: 1`.

### 18.3 Composite values: `padding` and `corner_radius`

Each side can be a number (px), a linked preset string (`var(--padding-md)`), or blank. **Never append `px` blindly.** Use one helper component:

```liquid
{%- comment -%}
  components/css_len/index.liquid
  v: raw value (number, "var(--x)", or blank)   d: default number (px)
  Outputs a valid CSS length.
{%- endcomment -%}
{%- assign _v = v | append: '' | strip -%}
{%- if _v == '' -%}{%- assign _v = d | append: '' -%}{%- endif -%}
{%- if _v contains 'var(' or _v contains 'px' or _v contains '%' or _v contains 'em' -%}{{ _v }}{%- else -%}{{ _v }}px{%- endif -%}
```

Corner radius: capture `tl`/`tr`/`br`/`bl` the same way, with the element's theme default as `d` (0 for sections, 4 for blocks, 8 for cards, the `--radius-media` value for media).

### 18.4 Button component

```liquid
{%- comment -%}
  components/button/index.liquid
  Params: text, link, new_tab, style (filled|outline|text), text_style, bg, fg, bd, show_border, bw,
          radius (corner_radius obj), padding (padding obj), hover, hbg, hfg, hbd, width (auto|full),
          icon, icon_position, override, font_family, font_size, font_weight,
          tag ('a'|'button'), attrs (e.g. block.fluid_attributes), data (extra data-fluid-* attributes)
{%- endcomment -%}
{%- if text != blank -%}
  {%- assign _style = style | default: 'filled' -%}
  {%- assign _hover = hover | default: 'theme' -%}
  {%- if _hover == 'theme' -%}{%- assign _hover = settings.button_hover_style | default: 'darken' -%}{%- endif -%}
  {%- assign _bw = 0 -%}
  {%- if show_border or _style == 'outline' -%}{%- assign _bw = bw | default: 1 -%}{%- endif -%}
  {%- assign _tag = tag | default: 'a' -%}
  {%- capture _vars -%}
    --btn-bg: {{ bg | default: 'var(--clr-primary)' }}; --btn-fg: {{ fg | default: 'var(--clr-white)' }};
    --btn-bd: {{ bd | default: 'var(--clr-primary)' }}; --btn-bw: {{ _bw }}px;
    --btn-hbg: {{ hbg | default: 'var(--clr-secondary)' }}; --btn-hfg: {{ hfg | default: 'var(--clr-white)' }}; --btn-hbd: {{ hbd | default: 'var(--clr-secondary)' }};
    {%- comment -%} Only sides the editor set are emitted; unset sides keep the em defaults in CSS, so the button scales with its Text Style {%- endcomment -%}
    {%- if padding.top != blank -%}--btn-pt: {% render 'css_len', v: padding.top %};{%- endif -%}
    {%- if padding.right != blank -%}--btn-pr: {% render 'css_len', v: padding.right %};{%- endif -%}
    {%- if padding.bottom != blank -%}--btn-pb: {% render 'css_len', v: padding.bottom %};{%- endif -%}
    {%- if padding.left != blank -%}--btn-pl: {% render 'css_len', v: padding.left %};{%- endif -%}
    {%- if radius -%}border-radius: {% render 'css_len', v: radius.tl, d: 4 %} {% render 'css_len', v: radius.tr, d: 4 %} {% render 'css_len', v: radius.br, d: 4 %} {% render 'css_len', v: radius.bl, d: 4 %};{%- endif -%}
    {%- if override -%}font-family: {{ font_family }}; font-size: {{ font_size }}px; font-weight: {{ font_weight }};{%- endif -%}
  {%- endcapture -%}
  <{{ _tag }} class="btn btn--{{ _style }} btn--hover-{{ _hover }} {{ text_style | default: 'text-button' }}{% if width == 'full' %} btn--full{% endif %}"
    style="{{ _vars | strip_newlines }}"
    {%- if _tag == 'a' %} href="{{ link | default: '#' }}"{% if new_tab %} target="_blank" rel="noopener"{% endif %}{% else %} type="button"{% endif %}
    {{ data }} {{ attrs }}>
    {%- if icon != blank and icon != 'none' and icon_position == 'before' -%}{% render 'icon', name: icon, size: 16 %}{%- endif -%}
    <span>{{ text | escape }}</span>
    {%- if icon != blank and icon != 'none' and icon_position != 'before' -%}{% render 'icon', name: icon, size: 16 %}{%- endif -%}
  </{{ _tag }}>
{%- endif -%}
```

```css
.btn { display:inline-flex; align-items:center; justify-content:center; gap:.5em; min-height:44px;
  padding:var(--btn-pt,.875em) var(--btn-pr,1.75em) var(--btn-pb,.875em) var(--btn-pl,1.75em);
  background:var(--btn-bg); color:var(--btn-fg); border:var(--btn-bw,0) solid var(--btn-bd); text-decoration:none; cursor:pointer;
  transition:background-color .2s, color .2s, border-color .2s, box-shadow .2s, transform .2s, filter .2s; }
.btn--outline { background:transparent; color:var(--btn-fg); }
.btn--text { background:transparent; border-color:transparent; padding-inline:0; min-height:0; }
.btn--full { width:100%; }
.btn--hover-colors:hover { background:var(--btn-hbg); color:var(--btn-hfg); border-color:var(--btn-hbd); }
.btn--hover-darken:hover { filter:brightness(.9); }
.btn--hover-lighten:hover { filter:brightness(1.1); }
.btn--hover-fill.btn--outline:hover { background:var(--btn-bd); color:var(--btn-hfg); }
.btn--hover-lift:hover { transform:translateY(-2px); box-shadow:var(--shadow-md); }
.btn--hover-underline:hover { text-decoration:underline; text-underline-offset:.2em; }
.btn:focus-visible { outline:2px solid currentColor; outline-offset:3px; }
.btn[disabled] { opacity:.5; cursor:not-allowed; }
@media (prefers-reduced-motion: reduce) { .btn { transition:none; } .btn--hover-lift:hover { transform:none; } }
```

A block calls it like this:

```liquid
{% render 'button', text: b.text, link: b.link, new_tab: b.open_new_tab, style: b.style, text_style: b.text_style,
  bg: b.background_color, fg: b.text_color, bd: b.border_color, show_border: b.show_border, bw: b.border_width,
  radius: b.border_radius, padding: b.padding, hover: b.hover_effect, hbg: b.hover_background_color, hfg: b.hover_text_color,
  hbd: b.hover_border_color, width: b.width, icon: b.icon, icon_position: b.icon_position, override: b.override_typography,
  font_family: b.font_family, font_size: b.font_size, font_weight: b.font_weight, attrs: block.fluid_attributes %}
```

Theme-level hover classes such as `btn--hover-pulse` and `btn--hover-scale-up` are defined once in global CSS and are reached through `settings.button_hover_style`.

### 18.5 Text block output

```liquid
{%- assign b = block.settings -%}
{%- capture st -%}
  color: {{ b.color | default: 'var(--clr-primary)' }};
  {%- if b.alignment != blank and b.alignment != 'inherit' -%}text-align: {{ b.alignment }};{%- endif -%}
  {%- if b.max_width != blank and b.max_width != 'none' -%}max-width: {{ b.max_width }};{%- endif -%}
  {%- if b.override_typography -%}
    {%- assign fs_floor = settings.font_size_body | default: 16 | times: 1.125 | round -%}
    {%- assign fs_t = b.font_size | times: 0.8 | round | at_least: fs_floor | at_most: b.font_size -%}
    {%- assign fs_m = b.font_size | times: 0.65 | round | at_least: fs_floor | at_most: b.font_size -%}
    font-family: {{ b.font_family }}; font-weight: {{ b.font_weight }};
    --fs-d: {{ b.font_size }}px; --fs-t: {{ fs_t }}px; --fs-m: {{ fs_m }}px;
  {%- endif -%}
{%- endcapture -%}
{%- assign tag = b.heading_tag | default: 'h2' -%}
<{{ tag }} class="blk-heading {{ b.text_style | default: 'text-h2' }}{% if b.override_typography %} fs-override{% endif %}"
  style="{{ st | strip_newlines }}" {{ block.fluid_attributes }}>{{ b.text }}</{{ tag }}>
```

```css
.fs-override { font-size: var(--fs-d); }
@media (max-width: 1023px) { .fs-override { font-size: var(--fs-t); } }
@media (max-width: 767px)  { .fs-override { font-size: var(--fs-m); } }
```

When a section's Content Alignment is center and a block's Alignment is Auto, the block inherits `text-align` from the container. Max Width blocks also need `margin-inline: auto` under center alignment.

### 18.6 Responsive behavior: CSS only, never schema

Every section must work at **375, 768, 1024 and 1440 px** with no editor input. Breakpoints come from `fluid-theme-presets-v2.md`:

- Desktop: ≥ 1024px
- Tablet: 768–1023px
- Mobile: ≤ 767px

| Concern | Required behavior |
|---|---|
| **Typography** | Automatic: presets larger than Body scale ×0.80 tablet and ×0.65 mobile, never below their hierarchy floor; everything else stays flat. Inputs are at least 16px. Full spec in **§3.4**. Manual overrides scale the same way (§18.5). |
| **Section padding** | Vertical padding scales **×0.75 tablet, ×0.5 mobile**. Horizontal section padding becomes `min(value, gutter)` (gutter 20px tablet / 16px mobile). |
| **Container gutter** | Container inline padding is never less than the gutter: 24 / 20 / 16px. Text never touches the screen edge. Full-bleed media belongs on the section shell, not the container. |
| **Grids** | Desktop uses `columns`. Tablet uses `min(columns, 2)`, computed in Liquid with `| at_most: 2`. Mobile uses 1 column for content cards, or 2 columns for compact items (logos, stats, trust items, icons). |
| **Split layouts** | Stack below 768px with media first. The desktop `media_position` doesn't change mobile order. |
| **Carousels** | Slides per view: `columns` desktop, 2 tablet, ~1.15 mobile (a peek of the next slide) with `scroll-snap`. Swipe on touch; arrows are optional on touch. |
| **Hero height** | `min_height` uses `svh` on mobile (`min-height: 75svh`) so browser chrome doesn't clip it. Content never overflows; the hero grows. |
| **Buttons** | Min 44×44px tap target. Button groups wrap. In a stacked mobile hero, a primary CTA may go full width through section CSS. |
| **Images** | Give `media_tag` an accurate `sizes`, e.g. `(min-width: 1024px) 33vw, (min-width: 768px) 50vw, 100vw`. Above-the-fold heroes use `loading: 'eager', fetchpriority: 'high'`. Aspect ratios hold at every width. |
| **Tables** (comparison) | Horizontal scroll inside a wrapper below 768px, with the first column sticky. |
| **Motion** | Autoplay, marquees, count-ups and hover transforms stop under `prefers-reduced-motion: reduce`. |
| **Slots and nested layouts** | Use container queries, not viewport queries (§17). |

### 18.7 Accessibility baseline

- One `h1` per page, and a logical heading order. Eyebrows are never headings.
- All images carry the picker's alt text. Purely decorative images use `alt=""`.
- Visible focus states on every button, link and summary.
- Links opening in new tabs get `rel="noopener"`.
- Accordions use `<details>`/`<summary>`. Tabs use `role="tablist"`/`tab`/`tabpanel` with arrow-key support.
- Color contrast: when a section's colors are changed, text must stay readable. The defaults must pass WCAG AA.

---

## 19. Anti-Patterns Found in the Surveyed Themes

Don't reproduce these. Fix them only when the user asks.

| # | Anti-pattern | Where seen | Do instead |
|---|---|---|---|
| 1 | Option groups whose values are class names (`bg-primary`) printed into CSS | Make Wellness (≈530 settings) | `var(--clr-*)` values (§3.1) |
| 2 | Selects pointing at option groups that don't exist | Yoli `brand_colors`, Make Wellness `padding_x`/`padding_y` | Define the group, or use one that exists |
| 3 | Palette/weight lists pasted inline into sections | Oliabo (835), Yoli, TM3 v2 | `"options": "background_colors"` |
| 4 | Inline `style=` inside richtext defaults | ≈470 blocks | Plain HTML defaults; style via settings |
| 5 | Same copy as both a section setting and a block | Make Wellness (50 sections) | Blocks only |
| 6 | "+ New Step" marker blocks followed by sibling sub-blocks | TM3, Puralta, Make Wellness | One item block with all fields (§12) |
| 7 | Numbered field series (`feature_1…6`, `link_1…12`, `card_1…8_button_*`) | Yoli, Oliabo, Make Wellness | Repeatable blocks |
| 8 | Per-item font/color selects on repeaters | Oliabo, Yoli, Make Wellness `-bt` | CG-CARD + CG-SECTION-TYPE |
| 9 | `show` checkbox on inline blocks | Yoli (≈250) | Delete the block to hide it |
| 10 | Separate alt-text fields | Oliabo 175, Make Wellness 110, TM3 34 | Picker alt |
| 11 | Text/URL fields instead of image or video pickers | Make Wellness 127, Oliabo 28 | `image_picker` / `video_picker` / `media_picker` |
| 12 | Raw `color` pickers or hex text fields on blocks | Oliabo, Make Wellness | Palette select |
| 13 | `range` for display numbers | TM3 proof/testimonials | `text` |
| 14 | Buttons with inline `background-color` (hover can't work) | `blocks/button` in 3 themes | CSS-variable button (§18.4) |
| 15 | Settings declared but never read | 19 Make Wellness CTA sections | Read every setting or remove it |
| 16 | Mobile/desktop duplicate settings | Yoli 616, Oliabo 333, Make Wellness 166 | CSS (§18.6) |
| 17 | `{% if affiliate.name %}` / eager avatar `src` in cached templates | Make Wellness layout; Puralta/TM3/Oliabo navbars | Hydration markers (§14) |
| 18 | `section.fluid_attributes` on an inner `<section>` with `"tag": "section"` | Make Wellness, Puralta, TM3 | Let Fluid wrap the section |
| 19 | `px` appended to linked `var()` padding/radius values | TM3 (88 files), Make Wellness (84) | `css_len` helper (§18.3) |
| 20 | `where \| first` lookups without `limit: 1` | common | Add the limit |
| 21 | Block-driven PDPs, one template per product | Yoli 36, Make Wellness 20, Oliabo 12 | Zero-block resource sections (§16) |
| 22 | `<h5>` eyebrows; `replace: '<p>'` into an `<h2>` | Puralta, TM3, Make Wellness | `eyebrow` as `<p>`; heading as `text` + tag |
| 23 | Invalid schema JSON (merge-conflict markers) | Oliabo `testimonials-video-text` | `fluid theme lint --json` before push |
| 24 | Undocumented `enabled_on` template type `"blog"` | Yoli, Oliabo | Documented types only |
| 25 | `request.locale` | Yoli layout | `localization.language.iso_code` |
| 26 | Hard-coded media URLs and copy in Liquid | Make Wellness `exp-hero` | Settings with defaults |
| 27 | Border style selects (solid/dashed/dotted) | Yoli, old spec | On/off border (CG-BORDER) |
| 28 | Four ways to do an accent heading (`line_1/line_2`, `heading_accent` block, `heading_part1/2/3`, `<em>`) | all | Inline italic in one heading |

---

## 20. Pre-Ship Checklist

- [ ] Schema is valid JSON. `fluid theme lint --json` is clean.
- [ ] Every block and setting ID follows §4.2. No shipped ID was renamed.
- [ ] Every color is `"options": "background_colors"`, every font is `"options": "font_families"`, and every Text Style is `"options": "text_presets"`. Every default is a value in its group.
- [ ] No mobile, tablet or desktop settings. No `show` toggles on blocks. No alt-text fields. No border-style selects.
- [ ] Settings order: Content → Style → Manual Overrides → Media Display → Shape → Hover → Layout → Link → Visibility (blocks), and Content → Layout → Card → Item Typography → Container → Section Shell (sections; zero-block resource sections add Colors before Container), with Section Corner Radius last.
- [ ] `{{ block.fluid_attributes }}` is on every block's outer element. `section.fluid_attributes` isn't used.
- [ ] Every setting is read by the markup. Every optional value is guarded. Every CSS interpolation has `| default:`.
- [ ] Buttons use the shared component with CSS variables, and hover works.
- [ ] Resource sections have zero blocks, `enabled_on` set, and metafields bound by literal path with guards and `info`.
- [ ] Affiliate content uses hydration markers only.
- [ ] A preset exists with realistic content. The section is never blank.
- [ ] Verified in `fluid theme dev` at 375 / 768 / 1024 / 1440 px, with the console clean, keyboard focus visible and reduced motion respected.

---

## Appendix A — Packaging a Block as a Standalone Theme Block

Standalone blocks are supported by the platform, but **none of the surveyed themes use them**. Build them only when the theme already does or the user asks. The same canonical schema works in both forms.

**File:** `blocks/heading/index.liquid` holds markup + `{% schema %}`. The schema is the block's `name`, `settings` and `presets`, without `type`. The folder name is the type.

```liquid
{%- assign b = block.settings -%}
<{{ b.heading_tag | default: 'h2' }} class="blk-heading {{ b.text_style }}" {{ block.fluid_attributes }}>{{ b.text }}</{{ b.heading_tag | default: 'h2' }}>

{% schema %}
{
  "name": "Heading",
  "settings": [ …same settings array as §7.1… ],
  "presets": [ { "name": "Heading" } ]
}
{% endschema %}
```

**Section side:**

```liquid
<div class="fx-stack">{% content_for 'blocks' %}</div>

{% schema %}
{
  "name": "Content Stack",
  "blocks": [ { "type": "@theme" } ],
  "presets": [ { "name": "Content Stack", "blocks": [ { "type": "heading" }, { "type": "text" }, { "type": "button" } ] } ]
}
{% endschema %}
```

Rules:
- `{ "type": "@theme" }` accepts every public standalone block. `{ "type": "heading" }` accepts only the named block, and a named reference has no `name` or `settings`.
- Prefix a folder with `_` (e.g. `_product_card`) to keep it out of `@theme`, then reference it by exact name.
- **Never also loop `section.blocks`** for blocks that `content_for 'blocks'` renders, or they render twice. `{% render block %}` only renders Droplet app blocks.
- Standalone blocks can't see `section.settings`. Any section-level styling must reach them through CSS custom properties set on the section root (e.g. `--card-radius`).
- **Nesting:** a standalone block may accept children (`"blocks": [{ "type": "@theme" }]` + `{% content_for 'blocks' %}` in its own template). The limit is two levels. This is the only way to build a true `container` or card-with-children block.
- **Fixed placement:** `{% content_for 'block', type: '_product_card', id: 'featured', closest.product: product %}`. The block reads `closest.product`.
- Each standalone block needs at least one preset to be addable from the editor.
- A section can mix `@theme`, named references and inline block definitions in its `blocks` array.

---

## Appendix B — Reference Implementations in the Surveyed Themes

Copy patterns from these, not whole files. Paths are relative to `/Users/lane/themes/`.

| Pattern | File |
|---|---|
| Palette option groups with swatch labels + CSS variables | `puralta/config/settings_schema.json`, `puralta/layouts/theme.liquid` |
| Docs-compliant typography presets (role / refs / unit) | `yoli/config/settings_schema.json` |
| Complete section shell (Container + Section Shell), var-aware padding | `puralta/sections/hero_centered/index.liquid` |
| Smallest complete modern section | `tm3/sections/tm3_proof_band/index.liquid` |
| Hover-capable button via CSS variables | `tm3/components/v2_button/index.liquid` + `tm3/assets/tm3v2.css` |
| Theme-level button hover setting | `puralta/config/settings_schema.json` (group `button_hover`) |
| Text link component | `puralta/components/link/index.liquid` |
| Image block + media_tag | `puralta/sections/rich_content/index.liquid` |
| Fluid media widget block | `puralta/blocks/fluid_media/index.liquid` |
| UGC carousel | `puralta/sections/ugc_carousel`, `tm3/sections/tm3v2_ugc_carousel` |
| LCP-tuned hero video/image | `tm3/sections/tm3v2_hero/index.liquid` |
| Icon card grid with section-level Card/Icon/Typography groups | `tm3/sections/product_benefits/index.liquid` |
| Reviews | `tm3/sections/tm3v2_pdp_reviews/index.liquid` |
| Testimonials | `oliabo/sections/revamp-proof-marquee`, `tm3/sections/tm3_testimonials` |
| Stats | `tm3/sections/stats_bar/index.liquid` |
| Steps | `tm3/sections/tm3_steps/index.liquid` |
| FAQ | `tm3/sections/faq_accordion/index.liquid` |
| Comparison table (tri-state) | `tm3/sections/comparison_table/index.liquid` |
| Enrollment packs | `tm3/sections/enrollment_showcase/index.liquid` |
| Product carousel + Card Button group | `tm3/sections/tm3v2_product_carousel/index.liquid` |
| Zero-block, metafield-driven PDP | `tm3/sections/tm3v2_pdp_hero/index.liquid` |
| Variant-metafield swatches | `makewellness/sections/product_header_variant_group/index.liquid` |
| Affiliate hydration (rep attribution) | `puralta/sections/announcement_bar/index.liquid` |
| Social links, one block per network | `puralta/sections/main_footer/index.liquid` |
| Logo wall | `makewellness/sections/logo_showcase/index.liquid` |
| Commerce data attributes | `makewellness/sections/product_hero`, `tm3/sections/tm3v2_opportunity_banner` |

---

## Appendix C — What Changed From v2.0

| v2.0 | v3.0 |
|---|---|
| "Supersedes current docs where they conflict" | The Fluid docs are authoritative for platform behavior. This doc standardizes controls |
| Theme/Template/Section/Block hierarchy diagram | Removed; see [overview](https://docs.fluid.app/themes/overview) and [developer-guide](https://docs.fluid.app/themes/developer-guide) |
| Two-Zone section pattern (resource zone + block zone) | Resource sections have **zero blocks**; resource data + metafields (§16) |
| `"options": "{{ theme.color_presets }}"` / `text_style_presets` | Option groups: `background_colors`, `font_families`, `text_presets` (§3) |
| "Custom…" color option on blocks | Palette only. Add a theme preset instead |
| Always-visible "Advanced Typography" overrides | Hidden behind **Override Text Style** (CG-TYPE-OVERRIDES) |
| Heading as `richtext` + Heading Level | Heading as `text` + Heading Level (§7.1) |
| `subheading` with Eyebrow/Subtitle style | Separate `eyebrow` and `subheading` blocks (subheading = `text` delta) |
| Image: separate Alt Text field, Max Width % and Fixed Height sliders, Fill fit | Alt from the picker. Aspect Ratio + Fit (Cover/Contain) + Focal Point |
| Border Style solid/dashed/dotted | Border on/off (CG-BORDER) |
| Button: 8 style presets, Size XS–XL, fixed width/height sliders, no working hover | Style radio + palette colors + full hover group + Width; CSS-variable rendering |
| `social_links` block with 8 URL fields | `social_link` block per network + section-level icon styling (same shape as `icon`) |
| `spacer` block | `divider` with Show Line off |
| `container` / `card` blocks with child blocks | Content item blocks + section CG-CARD. True nesting = standalone blocks (Appendix A). Section layout = section slots (§17) |
| Per-item card appearance on testimonials | Section-level CG-CARD for all repeaters |
| `affiliate_settings` / `affiliate_editable`; "MySite will be deprecated" | Hydration markers + CG-AFFILIATE-VISIBILITY (§14) |
| Block Picker UI grouping (Basic/Layout/Content/…) | Block declaration order (§4.3) + preset `category` for sections (§15.4) |
| Library in `library/blocks/` | Inline blocks first-class (§2.1) |
| — | New: mobile policy (§2.3, §18.6), shared control groups (§5), families + deltas (§6), content items (§12), commerce buttons (§13.4), rendering helpers (§18), anti-patterns (§19) |

---

## Appendix D — Open Items

1. **`plaintext` setting type.** It's being added to the platform. Keep using `text` until the docs describe it, then update §4.1.
2. **Combined image/video picker.** When it ships, add a `media` block using the combined picker (§9.2 note). Keep the existing `image`/`video` IDs.
3. **The "None" palette entry** (`transparent` in `background_colors`, §3.2). Verify in the editor on first use.
4. **`product.ratings` / `product.reviews` shape.** Verify on a store before the `rating` block's Product Data source relies on it.
5. **Separate specs still needed:** Navigation/navbar (mega menus, locale selector: see [navbar-locale-selector](https://docs.fluid.app/themes/navbar-locale-selector), [navigation-menus](https://docs.fluid.app/themes/navigation-menus)), Footer, Forms/email capture (Droplet integrations), Cart drawer ([cart-feedback](https://docs.fluid.app/themes/cart-feedback)), Product bundles ([product-bundles](https://docs.fluid.app/themes/product-bundles)), Member storefront pages.
