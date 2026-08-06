---
name: Create a partner dashboard (Today)
description: Create a 'Today' partner dashboard page in the portal — advice ring, a three-widget action row, a product to sell today, calendar and activity. Use when asked for a today page, partner dashboard, daily cockpit, or action page.
icon: layout-dashboard
category: Portal
preview: hero,droplet,panels3,tiles5,cta,header,media3,header,panels3
---

# Create a partner dashboard (Today)

Creates the **Today — Partner dashboard** page in a FluidOS portal for a partner who wants a focused 'what do I do today' cockpit.

Suggested slug: `today` · A focused 'what to do today' cockpit: hero, advice ring, a 3-widget action row, a sell-this-week video row, and closing tasks.

The finished layout, top to bottom:

- CarouselWidget _(One thoughtful move is enough.)_
- Stories _(Fresh advice)_
- **ROW [3c-equal]** → LayoutWidget · LayoutWidget · LayoutWidget
- ListWidget _(5 items, 5 col)_
- CarouselWidget _(Small, clear, human. That is enough to build)_
- **HEADER** · `` — Three product stories. Three ways in.
- **ROW [3c-equal]** → VideoWidget · VideoWidget · VideoWidget
- **HEADER** · `` — That's enough for today.
- **ROW [3c-equal]** → LayoutWidget · LayoutWidget · LayoutWidget
- TextWidget

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
     { "screen": { "name": "<Page name>", "slug": "today", "component_tree": {} } }
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
     { "navigation_item": { "label": "<Label>", "slug": "today",
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

## Droplet nodes in this template

This template embeds droplet-backed nodes whose UUIDs belong to the
company it was exported from:

- `droplet.advice.drp_e5grnigflrffisqhuvqorhagdld9hw8j.Stories`

They will not resolve on another company. Before posting the tree:

1. `GET {{company.api_base}}/api/droplet_installations` on the target company.
2. If the same droplet is installed, **replace the UUID segment** in the
   node `type` with the target company's `droplet_uuid`.
3. If it is not installed, **delete the node entirely** — leaving it in
   renders nothing and confuses the page.

## Before you hand it back

- Every top-level section must sit inside the single page-wrapper
  LayoutWidget that the template already provides — do not lift sections
  out of it, or the live portal will stretch each one to full viewport height.
- No fabricated numbers. If a widget wants earnings, ranks or counts and
  there is no real data, use an honest empty state.
- For widget-level detail, layout rules and the gotchas that break pages
  on the live portal, run the **Portal page authoring** skill.
