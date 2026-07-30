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

### Also check `captureGeometry.status` — a second, separate failure mode

`admissibility` reports whether an overlay obscured the pixels. It says nothing
about whether the DOM extraction succeeded. Check `captureGeometry.status`
independently:

- `"exact"` (`heightDelta: 0`) — the document stopped moving before capture.
- `"dynamic-height"` (non-zero `heightDelta`) — the page was still growing while
  it was captured, typically lazy-loaded media or an entrance animation.

A `dynamic-height` capture is not merely imprecise; its section and media
extraction can be near-empty while the screenshot still looks complete.
Measured across 30 captures of five storefronts, 29 were `exact` and averaged
17 sections; the single `dynamic-height` capture (heightDelta 855) returned
**4 sections and 1 media element** for a page whose desktop twin returned 17 and
66. The screenshot looked fine, so nothing downstream noticed until the media
inventory could not be built and QA burned a rework round on it.

So: when `captureGeometry.status` is not `"exact"`, do NOT build an inventory
from that cell. Recapture it — waiting for network idle and scrolling the page
to force lazy content first. If it stays dynamic after one honest retry, record
the exact `heightDelta`, section count, and media count, and treat that
viewport's structural inventory as unavailable rather than reporting four
sections as if they were the page.

Section and media counts also drift between clean captures of the same page
(one home page returned 13, 17, and 19 sections across three `exact` desktop
captures). Compare by identity — landmark order, distinct media URLs — never by
tally. A tally that collapses by 4x, though, is a broken capture, not drift.

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

### Verify at a width you did not build against

Build-and-verify at exactly the same two widths hides overflow that a visitor
hits one pixel away. Observed live: a header and footer stretched 16px wider
than the page with a negative left margin looked correct at exactly 1440 and
390, and produced 7px of horizontal scroll at 1441.

So after the declared benchmark viewports pass, probe one width that is NOT a
width you compared against — 1441 is enough. Compare the reported document
width against the viewport width; any positive difference is real overflow.

### Media counts are not stable across captures

Compare media by DISTINCT URL, never by total element-instance count. Measured
on one real storefront home page, three captures taken minutes apart returned
34, 35, and 37 `rendered.media` entries while the set of distinct media URLs
was identical (15) in all three: a decorative animated element is cloned a
nondeterministic number of times, and srcless entries move with it.

So an instance-count equality holds only against the sidecars retained by the
same capture, and is meaningless against a recapture. When a reviewer
recaptures and sees a different total, that is normal animation behavior and
not a finding. The real invariants are the set of distinct media URLs and the
presence of every priority item the page contract names — check those instead.

The same caution applies to any other count you might be tempted to assert
across captures: carousel slides mid-rotation, lazy-loaded grid rows, and
consent/popup surfaces all vary. Assert on identity and presence, not tallies.

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
