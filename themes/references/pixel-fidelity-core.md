# Pixel-fidelity core

Use this contract for every page-specific clone or refinement skill.

## Evidence is a matched pair

A visual claim requires both:

1. fresh source evidence at an exact route and viewport; and
2. fresh Fluid preview evidence at the matching route and viewport after the
   latest code change.

Record requested URL, final URL, status, viewport, full-page dimensions,
capture time, local path, byte count, and SHA-256. A hosted URL, chat attachment,
DOM summary, model memory, or worker prose is not a screenshot receipt.

Keep source and preview evidence in the owning company/theme project so another
reviewer can reproduce the decision. Background work may inspect an isolated
preview, but interactive work should present the route and scroll state in Mist.

## Content, DOM, and pixels are separate truth layers

- Markdown/structured data proves copy and product facts.
- Rendered HTML, computed styles, and the accessibility tree prove structure,
  tokens, semantics, and visible media.
- Screenshots prove visual order, geometry, crop, color, and responsive state.

No layer substitutes for another. In particular, a screenshot cannot prove
exact hidden copy or source URLs, and an HTML excerpt cannot prove the rendered
page is visible and unobscured.

Before visual judgment, require the signed source-admissibility result to be
`status:"usable"` with `eligibleForVisualPass:true`. `isError:false` means the
tool completed, not that the source is visually admissible.

## Required viewports

Use 1440×900 and 390×844 for the golden Home, Shop, and PDP routes. Capture the
full page and retain the requested viewport separately from decoded image
dimensions. A responsive reflow is valid; horizontal overflow, clipped content,
duplicate navigation, or a desktop layout merely scaled down is not.

After constrained interaction, record the action and capture the resulting
state. Inspect the DOM before dismissing overlays so a cookie, geo, newsletter,
or age gate is not mistaken for source content.

## Copy and brand

Source strings win. Preserve capitalization, punctuation, prices, product
names, CTA labels, promotion language, navigation, and legal/footer wording.
Base-theme placeholder copy is a major defect.

Use `brand.md` for authored gaps only. Typography requires the real family,
weight, style, source stylesheet/font file, and license decision. Never call a
font substitution pixel-perfect without naming the deviation.

## Media and video

Enumerate media from rendered DOM/sidecars and retained HTML/CSS. Do not sample
grids, galleries, rails, `<source>` candidates, responsive variants, posters,
or videos. Keep responsive URLs as candidates on the owning semantic media item
so completeness does not force duplicate DAM uploads. Preserve video autoplay,
loop, muted, playsinline, controls, type, poster, and desktop/mobile source
behavior.

Use Fluid DAM delivery for the clone. If a video is too large, use Mist's
compression capability and retain the original source-to-delivery receipt;
never silently replace it with a still image.

## Page-specific parity

Compare landmarks in source order. A page does not pass if any visible module is
missing, reordered, duplicated, or filled with generic content.

- Home: announcement, navigation, hero state, editorial modules, collections,
  brand story, social/proof, newsletter, footer.
- Shop/list: title/copy, chips or subnavigation, filters, sort, product count,
  grid density, cards, pagination/load-more, editorial insertions, rails.
- PDP: gallery/media, title/price/reviews, options/variants, quantity/cart,
  shipping/policies, details/accordions, comparison/education, cross-sells,
  reviews, footer.

## Pass bar

Require:

- zero major structure, content/data, imagery, typography, color, spacing, or
  interaction findings;
- correct route content rather than a 200 fallback or home template;
- clean preview console and server logs;
- no mobile overflow;
- final screenshots captured after the final code change;
- structured evidence receipts, not a prose declaration.

At most two itemized cosmetic minors may remain per route. Missing/wrong copy,
product data, assets, sections, or interactions are never minor.
