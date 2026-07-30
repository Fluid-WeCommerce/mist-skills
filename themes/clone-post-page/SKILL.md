---
name: clone-post-page
description: >-
  Recreate a source blog post / article detail page as the Fluid `post` route
  with real post content, byline, date, rich body formatting, inline media, and
  related-post rails. Use after the blog index establishes the post-card
  contract.
---

# Clone Post Page

Call `run_skill("themes/clone-page-to-liquid")` first. Supply this post-detail
contract to the universal visual-copy loop.

Follow
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
in full. This file adds post-detail semantics.

## Pick a representative post

Do not clone the shortest or newest post by default. Choose one that exercises
the most body formatting the source supports, and record why it was chosen.
Prefer a post containing several of: multiple heading levels, a pull quote,
a bulleted or numbered list, an inline image with caption, an embedded video,
a product callout/shoppable card, a table, and a code or recipe block.

Inventory a second, structurally different post to confirm the template is
general and not fitted to one article. Clone one; verify the template renders
the other without layout collapse.

## Minimum data contract

Reuse the posts created or migrated by `themes/clone-blog-page`. If the chosen
source post is not yet in Fluid, create it through documented v202604 contracts
with real title, author, publish date, hero image, and full body — a truncated
body cannot prove body typography.

## Fluid template contract

- Build `post/default` using the scaffold's `main_post` section.
- Keep title, author, publish/updated date, hero image, body, tags, and
  canonical URL dynamic.
- Body content must render from the stored post body. Do not transcribe the
  article into Liquid markup — that produces one hardcoded article and a broken
  template for every other post.
- Reuse `shell_contract` typography; define body-copy rules (measure, leading,
  heading scale, list and blockquote styling) once as reusable classes.
- Related-posts and newsletter rails reuse the blog card contract rather than a
  second card implementation.

## Post-specific inventory

Capture and compare:

- breadcrumb and back-to-blog affordance
- title, subtitle/deck, and hero treatment (full-bleed vs contained)
- byline block: author name, avatar, role, publish date, updated date
- reading time and share controls
- body measure (max line length) and vertical rhythm — the single most visible
  difference between a real article page and an approximation
- every body element type present: headings, lists, quotes, captions, inline
  links, tables, embeds
- inline and end-of-post CTAs, including shoppable product callouts
- author bio card
- related/recommended posts rail
- comments or social embeds, classified as `external`

## Required interaction proof

- confirm the post route returns 200 from a real Fluid post record
- exercise share controls and any table-of-contents anchors
- confirm one related-post card resolves to another live post route
- confirm the back-to-blog link reaches the Fluid blog index
- verify inline media loads at both viewports

## Post pass

In addition to the shared gate:

- the body renders from stored post data, not hardcoded markup
- a second, structurally different post renders correctly in the same template
- body typography matches the source's measure and rhythm at both viewports
- byline and date formatting match the source exactly
- inline images, captions, and embeds are present and load

Return the universal `PAGE_OUTPUT` plus the chosen post ID and rationale, the
verification post ID, the body-typography contract, and any source body element
Fluid cannot express.
