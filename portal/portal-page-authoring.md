---
name: Portal page authoring
description: How to build a FluidOS portal screen that actually renders — widget vocabulary, layout rules, the screen/nav/publish API, and the gotchas that silently break pages on the live portal. Read this before hand-building any portal page; the "Create a … page" skills already follow it.
icon: layout-template
category: Portal
---

# Portal page authoring

Everything here was verified against the live builder and a live portal
(`*.portal.fluid.app`). The rules that look fussy are the ones that cost
a rebuild when ignored.

Company: {{company.name}} · API base: {{company.api_base}}

## 1. The shape of a page

A screen's `component_tree` is a tree of widget nodes:

```json
{ "id": "unique-id", "type": "LayoutWidget", "props": { ... } }
```

**Wrap every page in ONE single-column LayoutWidget.** This is not
cosmetic. The SDK's `ScreenRenderer` wraps every _top-level_ node in
`h-full w-full`; on the live portal the screen sits in a fixed-height
flex container, so each top-level section stretches to ~100vh and you
get enormous empty gaps. The builder does not impose that height, so it
looks fine there and broken in production.

```json
{
  "id": "page",
  "type": "LayoutWidget",
  "props": {
    "sectionLayout": "single-column",
    "gapSize": "none",
    "padding": 0,
    "children": [
      /* all sections, columnIndex 0 */
    ]
  }
}
```

Sections then read as: hero → header → row → header → row → closer.
A **section header** is a single-column LayoutWidget holding two
TextWidgets: a small ALL-CAPS eyebrow, then a large title (`4xl`) with a
one-line description.

## 2. Columns

Columns come from a LayoutWidget's `props.sectionLayout`; each child
carries a `columnIndex` (0, 1, 2…).

| sectionLayout                      | result                                            |
| ---------------------------------- | ------------------------------------------------- |
| `single-column`                    | stacked — headers, full-width widgets             |
| `2c-left-wider` / `2c-right-wider` | two columns, one dominant                         |
| `2c-equal`                         | two equal columns                                 |
| `3c-equal`                         | three equal columns — **the default content row** |

**`sectionLayout` maxes out at 3 columns.** For a 4-across grid the only
option is a `ListWidget` with `columns: 4` (arbitrary int) plus
`imageAspectRatio: portrait | square | landscape`.

## 3. Widget vocabulary

25 widgets are registered (`packages/portal/sdk/src/core/default-widget-registry.ts`).
The ones that carry real pages:

- **CarouselWidget** — full-bleed hero/banner. `carouselHeight` **must be
  a px string** (`"440px"`), never a token. `editorialFrame: false` +
  gradient overlay = warm lifestyle hero; `editorialFrame: true` +
  `overlayType: solid` = bold dark marquee. Editorial heroes bottom-align
  their overlay content — lift it with `padding` (max 10 = 40px).
- **VideoWidget** — the rich video card. Use `displayMode: "card"` +
  `useCustomUrl: true` + `src` (mp4) + `poster`. Survives narrow columns;
  inline mode is cramped. Cards are locked 16:9.
- **ListWidget** — product/media/post grid. `columns` int + `items[]`.
  The reliable choice for static grids.
- **QuickShareWidget** — the per-rep share card (QR + unique link). The
  _only_ widget that can produce a real per-partner share action. Keep
  `showBuyButton: false` on tool pages.
- **QuickLinksWidget** — labeled icon rows. `layout: "list"`, explicit
  `link1..link8`.
- **TextWidget** — also your card primitive (see §5).
- **PointsWidget / ToDoWidget / CalendarWidget / RecentActivityWidget** —
  fill with the viewer's live data. No authored items, no link-out.

## 4. Linking and routing

- **LinkWidget** is a real button: `{ linkType: "screen", screenSlug:
"the-hub", text, variant: "secondary", size: "lg" }`.
- **ListWidget tile → share page**: `shareable_type: "Medium"` + `id`
  routes to `/share/media/{id}` (asset + Download + unique share link).
  The tile's `imageUrl` must be an image — for a video, use its frame.
- **ListWidget tile → external URL**: `shareable_type:
"EnrollmentPack"` + `canonical_url: "<url>"` opens that URL in a new
  tab. This is the only external-link mechanism.
- No widget CTA can open a native share sheet. Carousel/List/Nested
  buttons are plain anchors that navigate.

## 5. Colour, text and cards — the traps

- **`muted` / `secondary` / `accent` are near-white SURFACE tokens, not
  text colours.** `descriptionColor: "muted"` is near-white on white =
  invisible. The only legible text colours are **`foreground`**
  (near-black) and **`background`** (white, on dark surfaces).
  De-emphasise with size and weight, never a faded colour.
- **A "card" is ONE styled TextWidget**, not a CardWidget:
  `{ title, description, titleFontSize: "lg", descriptionFontSize: "sm",
both foreground, background: "secondary", padding: 6, borderRadius:
"xl", borderWidth: "none" }`. A CardWidget wrapping a single TextWidget
  renders a dead gap (its wrapper is `flex flex-col gap-6` with a
  `flex-1` content slot). Reserve CardWidget for genuine multi-child stacks.
- **Never ship an empty or whitespace-only TextWidget title** — it
  renders the literal placeholder "This is a text widget". There is no
  spacer widget; rely on section stacking.
- A **dark band** = a TextWidget header with `background: "foreground"`
  and text `background`, immediately followed by a LayoutWidget with the
  same `foreground` background. Sections stack with zero gap, so the two
  merge into one seamless near-black band.

## 6. Full-bleed vs inset

The portal renders the tree edge-to-edge — there is no page max-width.
The `padding` prop is uniform only (`p-{n}`), so it can't do
left-right-only inset.

- **Inset a section**: add `className: "px-6 sm:px-10"`. LayoutWidget,
  TextWidget, ListWidget and CarouselWidget all pass `className` to their
  root. Inset sections keep `borderRadius: "xl"`.
- **Full-bleed sections** (hero, dark bands) get no `className` inset and
  `borderRadius: "none"` — square edges, flush to the viewport.
- **Vertical rhythm**: sections stack flush. Add a bottom margin via
  `className` on the LAST element of each section only (headers get
  none, so the gap lands between section groups, not between a header
  and its row).

**CRITICAL — only Tailwind classes that appear in
`packages/portal/widgets/src` compile on the live portal.** Arbitrary
classes are silently dead. Verified working: `px-6`, `px-10`, `mb-8`,
`mb-6`, `pt-8`, `mt-12`. Verified **dead**: `mb-12`, `mb-10`, `mb-16`,
`mx-6`, `mx-10`. Use `mb-8` for section spacing. Because `mx-*` is dead,
an inset _coloured_ card needs a transparent, padded outer LayoutWidget
wrapping an inner coloured one — padding alone won't inset the colour.

## 7. Data-source widgets

- Widgets auto-fetch tenant data and **ignore static props** when a
  `dataSource` is present. For a reliable static grid use a plain
  ListWidget with no `dataSource` block.
- `dataSource` is a **top-level sibling of `props`**, not inside it.
- Only four presets carry the rep's auth: `rep-most-shared`,
  `rep-most-viewed`, `customer-orders`, `customer-subscriptions`.
  Custom API endpoints get no auth — relative URLs resolve against the
  portal's own origin (returning the SPA shell), and absolute Fluid URLs
  return 401. A true auto-feed needs a preset added in code.

## 8. Creating the screen (API)

Use the company's Fluid API with a partner token that has `fluid_os` scope.

**Create** — the POST requires `component_tree` to be a _hash_, so create
a shell first and PUT the real tree (array form is accepted on PUT):

```
POST {{company.api_base}}/api/company/fluid_os/definitions/<DEF_ID>/screens
  { "screen": { "name": "Home", "slug": "home", "component_tree": {} } }

PUT  {{company.api_base}}/api/company/fluid_os/definitions/<DEF_ID>/screens/<SCREEN_ID>
  { "screen": { "component_tree": [ <page wrapper node> ] } }
```

**Nav item** — a nav item **without a `slug` renders as a non-clickable
uppercase section header**. Always include one matching the screen slug:

```
POST .../navigations/<NAV_ID>/navigation_items
  { "navigation_item": { "label": "Home", "slug": "home",
                         "position": <n>, "screen_id": <id>, "source": "user" } }
```

Most definitions have two navigations (web and mobile) — add to both if
the page should appear in each. `PUT /navigations/<id>` with `screen_ids`
only **reorders** existing items; it cannot add one.

**Publish** — `POST .../definitions/<DEF_ID>/versions` with `{}`.
(There is no `/publish` endpoint; it 404s.)

## 9. Always verify visually

The JSON never tells the whole truth, and the builder and the live portal
diverge (see §1). After publishing, open
`admin.fluid.app/portal-builder/<DEF_ID>` **and** the live portal, and
scroll — the live portal flashes its default theme before the real one
applies, so a screenshot taken immediately can be stale.

## 10. Integrity

Never fabricate metrics on a partner-facing page. Earnings, ranks and
counts must come from real data or be honest empty states — invented
numbers on a live rep portal mislead real people. Prefer non-metric
content over a plausible-looking fake number.
