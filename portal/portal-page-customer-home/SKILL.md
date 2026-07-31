---
name: Create a customer home page
description: Create the customer-facing home page in the portal — account quicklinks, rewards, learn videos, member perks and shop rows. Use when asked to add a customer home, customer portal page, or member home.
icon: user-round
category: portal
preview: hero,header,split-left,header,media3,header,panels3,header,tiles4
---

# Create a customer home page

Creates the **Customer Home** page in a FluidOS portal for a customer (not a rep) landing in the portal.

Suggested slug: `customer-home` · The customer's home: account quicklinks + rewards, learn videos, member perks, shop the collection, community, journal.

The finished layout, top to bottom:

- CarouselWidget _(Beautiful skin is a ritual, not a chance.)_
- **HEADER** · `MY [BRAND]` — Welcome back.
- **ROW [2c-left-wider]** → QuickLinksWidget · LayoutWidget
- **HEADER** · `LEARN` — Master your ritual.
- **ROW [3c-equal]** → VideoWidget · VideoWidget · VideoWidget
- **HEADER** · `MEMBER PERKS` — Being a member pays.
- **ROW [3c-equal]** → LayoutWidget · LayoutWidget · LayoutWidget
- **HEADER** · `THE COLLECTION` — Loved by members.
- ListWidget _(4 items, 4 col)_
- LinkWidget
- **HEADER** · `COMMUNITY` — #MyBrand
- ListWidget _(3 items, 3 col)_
- **ROW [3c-equal]** → MakeAVideoCta · VideoWidget · VideoWidget
- **HEADER** · `THE JOURNAL` — Skin science, decoded.
- ListWidget _(4 items, 4 col)_
- CarouselWidget _(Good skin is better shared.)_

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
     { "screen": { "name": "<Page name>", "slug": "customer-home", "component_tree": {} } }
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
     { "navigation_item": { "label": "<Label>", "slug": "customer-home",
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

- `droplet.ugc.drp_fuwamfg3licz1l4yocpkjos12t9vhcrh.MakeAVideoCta`

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
