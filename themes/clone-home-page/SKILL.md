---
name: clone-home-page
description: >-
  Reconstruct one storefront home page in a Fluid theme with exact copy,
  responsive media, navigation states, and desktop/mobile evidence. Use
  standalone or as the home-page hard gate in onboarding.
---

# Clone Home Page

Own exactly one golden route: the canonical source homepage mapped to the
Fluid theme home route.

Call `run_skill("themes/clone-page-to-liquid")` first and follow its universal
visual-copy loop. This skill supplies only Home semantics and its page contract.

Follow
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
in full. This file adds homepage-specific requirements.

## Resolve scope

In workflow mode, read `context.website_url`,
`clone-manifest.json.visual_routes.home`, prior shell-step output, and the
current local theme. Use `/` as the built path unless the manifest proves a
different canonical home path.

Standalone, ask for the source URL only if it is absent. Confirm the active
theme before editing an existing project.

## Homepage discovery

The homepage establishes the shared storefront shell, but it is not permission
to invent the rest of the site.

Inventory:

- announcement/utility bars
- desktop and mobile header/navigation
- logo/icon treatment
- every homepage section in exact order
- every exact heading, paragraph, CTA, badge, and link
- image, picture, video, poster, and responsive source variants
- carousels, tabs, accordions, drawers, hover states, and auto-rotation
- newsletter/social/footer content visible on home

The route manifest must contain one landmark for every visible section. A
hero-only or above-the-fold reconstruction is a failure.

If rendered crawl HTML omits `<head>`, fetch the raw canonical page and its real
stylesheet links. Reconcile fonts/colors with `brand.md` and the prior shell
step. Source stylesheet evidence wins over eyeballing.

## Shell contract

Verify the existing shell rather than duplicating it inside home sections:

- typography tokens and licensed/substituted font decision
- page-width and spacing scale
- announcement/header/nav/footer sections
- desktop menu behavior
- mobile disclosure/drawer behavior
- logo, icon, utility controls, and exact link labels/targets

Fix shell defects that block homepage fidelity and report them in
`PAGE_OUTPUT.shell_changes`. Do not clone the header or footer into each page
template.

Record a reusable `shell_contract` for later page skills: token names, shared
section/component paths, menu source, breakpoints, container widths, and
interaction selectors.

## Homepage implementation

- Preserve exact source section order and copy.
- Use the source's real home-specific media; do not replace motion with a poster.
- Keep product/collection/editor data dynamic when a section represents live
  Fluid resources.
- Reuse a section only where its schema can express the source at both widths.
- Give every template section instance a stable unique ID.
- Remove unrelated starter sections and filler copy.
- Match desktop and mobile crops independently.

The home page may introduce reusable product cards or editorial cards, but
record their contract. The following shop step will test whether they actually
work with a full catalog.

## Required interaction proof

At minimum:

- open and close the mobile navigation from an inspected selector
- exercise every homepage disclosure/tab control
- verify carousel controls where present
- verify every primary CTA points to the source-equivalent Fluid route

Static screenshots cannot prove these states.

## Keep media delivery bounded

Use the verified delivery URLs recorded in `clone-manifest.json` for homepage
media. Never embed binary image or video bytes as `data:`/base64 in Liquid,
CSS, JSON, or JavaScript to bypass a broken asset URL. That fallback inflates
theme resources, makes every theme-dev update expensive, and hides the actual
delivery failure.

If a required delivery URL does not render, diagnose the DAM response, URL
escaping, theme markup, and browser network failure. Repair the delivery path
or leave the media as a named major; do not convert the binary into source
code. Small authored SVG/CSS interface icons are not media fallbacks and remain
allowed.

## Preserve honest document geometry

Build the page with normal responsive flow. Never absolutely or fixed-position
the full page, a whole section, or the footer at a hardcoded pixel coordinate;
clamp an arbitrary page height; apply overflow clipping to hide content; or
remove/crop a source landmark to force a screenshot-height metric. Those are
evidence-gaming failures even if a comparison number improves.

Use the signed rendered-evidence sidecar's `document.height` as source geometry
truth. A full-page screenshot can have a different decoded height because a
provider stitched viewports or repeated sticky chrome. A mobile footer may use
accordions only when they are semantic, accessible disclosures and QA exercises
the real closed and opened states.

## Materialize the shared audit

This page skill intentionally does not declare another skill's script as its
own asset. Mist sandboxes assets to their owning skill directory.

Before the final audit, call `run_skill("themes/theme-clone")` to materialize
that skill's bundled `theme_audit.py`. Use the exact materialized script path
returned by the tool and run it only against the touched theme files. Do not
restart the broad theme-clone workflow or weaken this page's narrower gate.

## Homepage pass

In addition to the shared gate:

- signed `compare_preview_to_source` receipts prove the exact source-home to
  local `/` pair at 1440 × 900 and 390 × 844 after the final home code change,
  bind each source screenshot to its rendered-evidence sidecar, and report
  exact, non-truncated ordered copy. If the signed source final URL redirects or
  localizes to another pathname (for example `/en-us`), pass that pathname as
  `source_route` while keeping `path:"/"`; source and Fluid pathnames are a
  deliberate mapping, not required to be identical
- every homepage section is present once and ordered correctly
- hero and all below-the-fold priority media match at both widths
- no touched Liquid, CSS, JSON, or JavaScript file contains an inline binary
  `data:`/base64 media fallback
- normal responsive document flow is preserved: no viewport-specific hardcoded
  page/section/footer coordinate, fixed or absolute whole-section relocation,
  arbitrary height clamp, overflow clipping, or hidden/cropped source content
  is used to satisfy screenshot geometry
- all exact homepage wording is reconciled from source HTML to local DOM
- header/navigation/footer are visually and interactively valid
- no base-theme marketing filler remains
- `PAGE_OUTPUT.shell_contract` is complete enough for later page workers

Return an honest `needs_adjudication` when the universal evidence is sound but
a Home-specific responsive/dynamic judgment remains. Do not label that a pass.
