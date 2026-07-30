---
name: clone-blog-page
description: >-
  Recreate a source blog / journal / news index as the Fluid `post_page` route
  with real post records, author and date metadata, category filtering,
  pagination, and responsive evidence. Handles blogs that live on a subdomain,
  a subpath, or an external publishing platform.
---

# Clone Blog Page

Call `run_skill("themes/clone-page-to-liquid")` first. Supply this blog-index
contract to the universal visual-copy loop.

Follow
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
in full. This file adds blog-index semantics.

## Find the blog — it is often not on the main domain

A blog is the page type most likely to sit outside the storefront. Search in
this order and stop at the first that resolves to a real post list:

1. rendered header/footer navigation links labeled Blog, Journal, Stories,
   News, Learn, Guides, Recipes, or the brand's own coined name
2. `/blog`, `/blogs/news`, `/journal`, `/stories`, `/learn` on the source domain
3. `sitemap.xml` and any `sitemap-blog*.xml` / `sitemap-posts*.xml` child
4. a subdomain — `blog.<domain>`, `journal.<domain>`, `learn.<domain>`
5. an external platform the brand links to (Shopify `/blogs/*`, Substack,
   Medium, WordPress, Contentful-backed marketing site)

Record which of these produced the blog and the final canonical URL. A blog on
another host is still this brand's blog: clone its content into Fluid rather
than linking out, unless the caller explicitly scoped it out.

If the source genuinely has no blog, return `status:"needs_adjudication"` with
the routes you checked. Do not invent posts, and do not silently retarget the
step at a press page or a help center — say which one you found instead.

## Distinguish index from taxonomy

Prove which route you are cloning:

- the all-posts index
- one category/tag archive
- a featured/editorial landing page that links into the blog
- a single post (that belongs to `themes/clone-post-page`)

Shopify-style sources expose `/blogs/<handle>` as a per-blog index; a brand may
have several. Clone the primary one and record the others in `PAGE_OUTPUT`.

## Minimum data contract

Reuse existing Fluid posts. If none exist, create at least three source-backed
preview posts through documented v202604 contracts so the list, its pagination
affordance, and its card variants can actually render. Each preview post needs
a real title, author, publish date, excerpt, and hero image taken from the
source — a list of placeholder rows proves nothing about card layout.

Record all created post IDs. Do not await a full content migration; the
`content-import` step owns bulk post migration.

## Fluid template contract

- Build `post_page/default` using the scaffold's `main_post_list` section.
  In a fresh base theme this template is an auto-generated empty placeholder —
  replacing it is expected, not a destructive edit.
- Keep post title, author, publish date, excerpt, reading time, tags/category,
  hero image, and canonical post URL dynamic. Never hardcode a post row.
- Reuse the shell's typography and container scale from `shell_contract`
  instead of introducing a second editorial type system.
- Add a category/tag filter only where the source exposes one, bound to real
  Fluid taxonomy rather than a static list of labels.

## Blog-specific inventory

Capture and compare:

- page title, editorial intro, and any featured/hero post treatment
- card grid: columns, gap, aspect ratio, image crop, hover behavior
- exact per-card field order — most sources show image → category → title →
  excerpt → author/date, but confirm rather than assume
- author rendering: name only, name + avatar, or byline with role
- date format exactly as the source prints it (`Mar 4, 2026` vs `04.03.26`)
- reading-time or post-length badges
- category/tag chips and their selected state
- pagination, load-more, or infinite scroll
- newsletter capture module, which is very common on blog indexes
- empty and single-post states where reachable

## Required interaction proof

- follow one card through to its real Fluid post route and confirm a 200
- exercise pagination / load-more where present
- exercise category filtering where present, and confirm the list changes
- open and close the mobile navigation from an inspected selector

## Blog pass

In addition to the shared gate:

- the discovered blog location and discovery method are recorded
- author and date metadata render from real post records at both viewports
- at least three distinct posts render with correct card field order
- one card resolves to a live Fluid post route
- no placeholder or lorem post content remains

Return the universal `PAGE_OUTPUT` plus the resolved blog source location,
created post IDs, the reusable post-card contract for
`themes/clone-post-page`, and any additional blog indexes left unmigrated.
