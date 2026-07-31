---
name: Create an alternate home page
description: Create an alternate home page layout in the portal — same widget vocabulary as the partner home, different section arrangement. Use when asked for a second home, home variant, alternate layout, or an A/B home page.
icon: layout-panel-left
category: Portal
preview: hero,panels3,text,split,text,tiles4,text,tiles4
---

# Create an alternate home page

Creates the **Home v3 (alternate)** page in a FluidOS portal for a company that wants a second home layout to compare or A/B.

Suggested slug: `home-v3` · An alternate home layout variant — same widget vocabulary, different section arrangement to A/B against the others.

The finished layout, top to bottom:

- CarouselWidget _(Give a friend $10. Get $10 back.)_
- **ROW [3c-equal]** → TextWidget · QuickShareWidget · TextWidget · QuickLinksWidget · TextWidget · VideoWidget · VideoWidget · TextWidget · TextWidget · TextWidget · TextWidget · QuickLinksWidget
- TextWidget _(Real people. Real routines. Real results.)_
- **ROW [2c-equal]** → LayoutWidget · LayoutWidget
- TextWidget _(Content ready to share)_
- ListWidget _(7 items, 4 col)_
- TextWidget _(From the journal)_
- ListWidget _(8 items, 4 col)_

The full `component_tree` is in the reference below — it is a working
page, not a sketch: every row, column and widget placement is already
right. Your job is to place it on the target definition and swap the
placeholders for the company's real content.

## Steps

1. **Find the target definition.** Ask which portal if it is ambiguous.
   `GET {{company.api_base}}/api/company/fluid_os/definitions` lists them;
   note the definition id and its navigation ids.
2. **Create the screen shell**, then PUT the tree — the POST requires
   `component_tree` to be a hash, so it cannot carry the array form:
   ```
   POST .../definitions/<DEF_ID>/screens
     { "screen": { "name": "<Page name>", "slug": "home-v3", "component_tree": {} } }
   PUT  .../definitions/<DEF_ID>/screens/<SCREEN_ID>
     { "screen": { "component_tree": <the array from the reference, verbatim> } }
   ```
3. **Swap the placeholders** — see the legend below. Pull real media from
   `GET /api/company/media?per_page=200` and real products from
   `GET /api/company/v1/products`. Do not leave `picsum.photos` images or
   `REPLACE_*` strings on a page you hand back.
4. **Add a nav item** pointing at the new screen, including a `slug` —
   without one it renders as a non-clickable section header:
   ```
   POST .../navigations/<NAV_ID>/navigation_items
     { "navigation_item": { "label": "<Label>", "slug": "home-v3",
        "position": <n>, "screen_id": <id>, "source": "user" } }
   ```
5. **Publish**: `POST .../definitions/<DEF_ID>/versions` with `{}`.
6. **Verify visually** in `admin.fluid.app/portal-builder/<DEF_ID>` and on
   the live portal. The JSON never tells the whole truth.

## Placeholders to replace

| Placeholder                                              | Replace with                                      |
| -------------------------------------------------------- | ------------------------------------------------- |
| `https://picsum.photos/seed/...`                         | Real images from the company's media library      |
| `https://REPLACE-WITH-YOUR-CDN/video.mp4`                | Real video URLs (the poster is a placeholder too) |
| `REPLACE_PRODUCT_ID`                                     | A real product id                                 |
| `Featured Product N` / `$00.00`                          | Real product title and price                      |
| `REPLACE_PRODUCT_URL` / `REPLACE_TARGET_URL`             | Real product or post URLs                         |
| `YOUR_COMPANY_ID`                                        | The destination company id                        |
| `[Brand]`, `[Product Name]`, `[science]`, `[supplement]` | The company's real copy                           |
| `Jordan Rivera`                                          | A real rep or contributor name                    |

## Before you hand it back

- Every top-level section must sit inside the single page-wrapper
  LayoutWidget that the template already provides — do not lift sections
  out of it, or the live portal will stretch each one to full viewport height.
- No fabricated numbers. If a widget wants earnings, ranks or counts and
  there is no real data, use an honest empty state.
- For widget-level detail, layout rules and the gotchas that break pages
  on the live portal, run the **Portal page authoring** skill.
