---
name: clone-system-pages
description: >-
  Build the Fluid system routes a storefront needs but a source site rarely
  exposes in navigation — 404 not-found, 503 maintenance, and generic content
  pages. Use late in a theme build, after the shell and core pages are stable.
---

# Clone System Pages

Call `run_skill("themes/clone-page-to-liquid")` first for each route you build.
This skill supplies the system-page contracts.

Follow
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
in full. This file adds system-page semantics.

## These pages are found differently

System pages are not in the navigation and usually not in the sitemap. Reach
each source page deliberately:

- **404** — request a deliberately nonexistent path on the source domain, e.g.
  `/<random-token-that-cannot-exist>`. Confirm the response is a real 404 and
  not a soft-200 redirect to home. Capture whatever the source actually renders.
- **503 / maintenance** — almost never observable live. Do not fabricate a
  source capture. Build a shell-consistent maintenance page from
  `shell_contract` tokens and mark it `no_source_evidence`.
- **generic content page** — pick one real source content page that is NOT a
  policy document (About, Our Story, Sustainability, FAQ). Policy pages are
  owned by the content-import step; this route proves the reusable
  content-page template.

An honest `no_source_evidence` on 503 is correct. Claiming a source capture you
could not take is a hard failure.

## Fluid template contract

- **404** → `error_page/404`. The scaffold ships a working default; treat it as
  a starting point to restyle, not a file to leave untouched.
- **503** → `error_page/503`, same treatment.
- **content page** → `page/default` using the scaffold's `main_page` section,
  with body content dynamic from the Fluid page record.

Error templates read `error.status_code` and the localized `error.*` strings.
Keep those bindings and the localization filters — do not replace a translated
string with a hardcoded English literal to match a screenshot.

## What a good system page requires

Error pages must carry the full shell. A bare error page on a themed store is
the most common tell that a clone was rushed:

- global header/navigation and footer render, and navigation works
- brand typography, color tokens, and logo match the rest of the theme
- the status code and message are readable at both viewports
- a primary recovery CTA returns to `/`, plus, where the source offers them,
  search and popular-destination links
- no base-theme filler copy or default illustration remains

For the content page:

- title, body, and any hero image render from the Fluid page record
- body typography reuses the post/body contract where one exists
- the template renders correctly for a second, different content page

## Required interaction proof

- request a nonexistent path against the local preview and confirm the themed
  404 renders — not a stack trace, a blank page, or an unstyled default
- confirm the 404 recovery CTA resolves to a live route
- confirm header navigation works from the error page
- render the 503 template and confirm it does not error
- confirm the content-page template renders a second page record

## System-page pass

In addition to the shared gate:

- a nonexistent local path returns the themed 404 with full shell
- the 503 template renders without error and is shell-consistent
- the content-page template renders two different page records
- 503 is honestly marked `no_source_evidence` when the source never exposed one
- localization bindings are preserved

Return one `PAGE_OUTPUT` per route built, plus the source 404 evidence (or the
reason it could not be captured), and the reusable content-page contract.
