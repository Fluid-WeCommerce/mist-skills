# Special Sections — the exceptions logical CSS can't auto-mirror

Logical properties (Phase 2) mirror the box model — margins, padding, alignment, insets.
They do **not** flip content that encodes direction in markup, JS, transforms, or fixed
geometry. Walk this checklist against the target, and for each one either fix it or flag it
for review.

## Checklist

| Component | What breaks in RTL | Fix |
|---|---|---|
| **Carousels / sliders** | Slides advance the wrong way; prev/next arrows point wrong; scroll/translate math assumes LTR. | Reverse slide order or the transform sign in RTL; swap prev/next; if using `scroll-snap`, verify it honors `dir`. |
| **Image ↔ text splits** | "Image left, text right" should become "image right, text left". Often driven by `flex-direction: row` + physical order. | Rely on logical order; if hardcoded, add an RTL rule to reverse `flex-direction` or the DOM order. |
| **Step / progress indicators** | Steps 1→2→3 must run right→left; connector lines point wrong. | Reverse visual order and connector direction under `[dir=rtl]`. |
| **Directional icons** | Arrows, chevrons, back/forward, "next", carets stay pointing LTR. | Mirror with `[dir=rtl] .icon { transform: scaleX(-1); }` for glyphs that encode direction. **Do NOT mirror** non-directional icons (logos, checkmarks, stars, brand marks). |
| **Breadcrumbs** | Separator direction (`Home › Shop`) points the wrong way; order stays LTR. | Reverse order and flip/replace the separator under RTL. |
| **Hardcoded position** | Elements placed with literal `left:`/`right:`, absolute badges, drawer/slide-in panels, tooltips. | Convert to `inset-inline-*`; verify off-canvas panels slide from the correct edge. |
| **Transforms / animations** | `translateX(...)`, slide-in keyframes move the wrong direction. | Negate the X translation under RTL, or express motion in logical terms. |
| **Background position / sprites** | `background-position: left` and sprite offsets don't follow `dir`. | Add RTL overrides where the asset is directional. |
| **Shadows / gradients** | Directional `box-shadow`/`linear-gradient(to right, …)` may look off. | Judgment call — mirror only if the direction is meaningful. |

## Bidi (mixed-direction content)

Even in an RTL layout, these stay **left-to-right** and must not reverse:
- Numbers, prices, phone numbers, dates
- Code, URLs, email addresses
- Latin-script brand names and embeds

Wrap or isolate them (`dir="ltr"`, `unicode-bidi: isolate`, or `<bdi>`) if they leak.

## How to work this phase

1. Grep the theme/component CSS and JS for the LTR tells: `left`, `right`, `translateX`,
   `flex-direction: row`, `text-align: left`, `float`, `scaleX`, arrow/chevron icon names.
2. For each hit, decide: already handled by logical CSS? needs an `[dir=rtl]` override?
   or is it a non-directional element to leave alone?
3. Fix the directional ones; list anything ambiguous for the review checkpoint.
