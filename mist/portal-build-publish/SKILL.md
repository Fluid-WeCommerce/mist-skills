---
name: Portal Build & Publish
description: Create a Fluid OS portal end to end through the API — pre-flight for duplicates, approval-gated creation, audit the canonical seed for Fluid's own marketing assets, curate the company's real media and product CTAs, write the widget tree, verify, and publish only when told. Use when a user asks to create, build, seed, or publish a Fluid OS portal / portal app. API-only; do not use the CLI.
icon: layout-dashboard
---

# Goal

Create a Fluid OS portal for {{company.name}} end to end through the API, seeded with the
company's OWN media and products rather than Fluid's canonical marketing placeholders, and
publish it only on explicit instruction.

`fluid portal scaffold` does not exist on CLI 0.1.14 and has no self-update path, which is why
the older create-portal-app flow is blocked. The `create_portal_app` TOOL hits Fluid's
transactional endpoint and works today. Do not use the CLI anywhere in this skill.

# Steps

## 1. Pre-flight

- `GET /api/company/fluid_os/definitions`. Refuse to create a duplicate display name
  (case-insensitive) — offer to open the existing portal instead.
- Ask the user for the display name. Never invent or derive it: the tool refuses a name the
  agent chose, and the approval card title must match it exactly. Ask, then END THE TURN.

## 2. Approval gate

- `human_in_the_loop` with source `agent`, title EXACTLY the display name, and a fresh
  `suggestion_id` of `portal-create:<name>:<random suffix>`. End the turn.
- On approval, call `create_portal_app` with `approval_id` and `confirm_create: true`.
  Approvals are single-use and expire 15 minutes after the click.

## 3. Report the real ids

Never state ids before the tool returns them.

The tool creates a definition, a Home screen, an 11-item Main Navigation (only "Home" has a
`screen_id` — the other ten resolve to nothing until screens exist), an EMPTY Mobile Navigation,
a Company Theme from the brand colors, and a Default Profile scoped to `admin` + `rep`.

The definition record has no `url` or `preview_url`, and `definition_slug` is null. Do not
compose a link. Access is admin Portal Builder, or Mist's sidebar after a refresh. There is no
live URL until a version is published.

## 4. Audit the seed for foreign assets — required

`GET /api/company/fluid_os/definitions/{id}/screens/{screenId}`

The canonical seed embeds **Fluid's own marketing assets** under ImageKit company `980191006` —
a "We Commerce" hero video and a "Welcome to We-Commerce" banner background. Resolve the active
company id with `GET /api/company/v1/companies/me`, then flag every media URL whose company
segment is not that id, and replace all of them. Also treat a non-company-scoped
`/s3/tr:n-video_poster/...` poster as foreign.

## 5. Curate real media

- `GET /api/v202604/company/media` — use `video_url` verbatim; posters are
  `<video_url>/ik-thumbnail.jpg`.
- `GET /api/v202604/company/products/{id}` — use `canonical_url` VERBATIM for CTAs. Slugs can
  carry a UUID suffix, so a hand-composed product URL will 404.
- Match assets to brand voice. Draw copy from each asset's own caption instead of inventing
  claims.
- If the library has no image assets, do not invent one — use a semantic background token and
  say so.

## 6. Write the tree

`PATCH /api/company/fluid_os/definitions/{id}/screens/{screenId}` with
`{ screen: { component_tree: [...] } }`.

This REPLACES the whole tree — send the complete structure including widgets you didn't change.

Widget types in the seed: `ContainerWidget`, `LayoutWidget` (`sectionLayout` is `single-column`
or `2c-equal`), `VideoWidget`, `ListWidget`, `MySiteWidget`, `ToDoWidget`, `CalendarWidget`,
`RecentActivityWidget`.

- Keep `ListWidget.dataSource` intact — it's a live rep-most-viewed API preset.
- Colors are semantic tokens (`primary`, `muted`, `background`, `foreground`), never hex.
- Vertical 9:16 social clips inside `displayFit: "cover"` at a fixed height crop to a narrow
  band. Prefer `contain` or a taller `fixedHeight`, and say so rather than assuming it looks
  right.

## 7. Verify, then publish only when told

- `GET /api/company/fluid_os/definitions` — confirm `has_pending_changes: true`.
- State plainly that no one has SEEN the page. API acceptance is not visual confirmation. Offer
  a Portal Builder preview first.
- Publish: `POST /api/company/fluid_os/definitions/{id}/versions` with body `{}`.
- Confirm the new version is active, `has_pending_changes` is false, and the published manifest
  embeds the company's media rather than the seed's.
- Name the previous version id as the rollback target. If the published version is the FIRST
  version of the definition, say plainly that there is no rollback target.
- Re-read `GET /api/company/fluid_os/definitions` after publishing and report any OTHER
  definition whose `active` flag changed as a side effect — only one definition is active per
  company, so publishing a new portal DEACTIVATES the previously active one.

# Honesty rules

- Never claim a portal is live, published, or visible before the API says so.
- Re-read definition state before asserting it. A portal can be published outside this chat, so
  a stale reading becomes a false claim.
- If the local project doesn't exist yet, say the sidebar needs a refresh. Don't pretend to have
  dispatched work to a project chat that isn't there.

# QA criteria

- Zero media URLs referencing a company id other than the active company.
- Every CTA link matches a `canonical_url` returned by the products API.
- The active version's manifest contains the curated media.
- `has_pending_changes` is false after publish.
