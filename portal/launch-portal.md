---
name: Launch the Portal
description: Stand up the logged-in customer/partner portal in one guided run — pick the portal app and the pages, then a workflow builds them in parallel from working layouts, reconciles navigation, publishes, and verifies. Use when asked to launch, build or set up a portal, a customer portal, a rep portal, or the logged-in experience.
icon: rocket
category: portal
---

# Goal

Get {{company.name}} a real, published portal — the logged-in half of the
business — without anyone dragging widgets around a builder for an
afternoon. This skill collects the two decisions that actually matter
(which portal app, which pages), then hands off to the `launch-portal`
workflow, which builds every page in parallel from working
`component_tree` templates, reconciles the navigation, publishes a
version, and verifies the published state against the API.

**Trigger** whenever the user expresses intent to build or launch the
logged-in experience: "launch the portal", "build a customer portal",
"set up the rep portal", "we need a portal", "what do customers see when
they log in", "build the logged-in experience".

Storefront pages are a different thing. If the user wants a marketing or
product page on the public site, that is `create_page` and a theme — not
this skill. Say so and stop.

# Step 0 — Gather everything BEFORE asking anything

Run these in parallel. Every one of them removes a question you would
otherwise have to ask.

1. `fluid_api` → `GET {{company.api_base}}/api/company/fluid_os/definitions`
   — the company's portal apps. Each carries `id`, `name`, `active` and
   `has_pending_changes`. This is the list the user picks from.
2. For the `active: true` definition (if there is one), `GET
   .../definitions/<DEF_ID>/screens` — what already exists. A company
   with three screens already built needs a different conversation than
   an empty one.
3. `GET .../definitions/<DEF_ID>/navigations` — the navigation and its
   items, so the workflow can reconcile rather than guess.
4. `GET {{company.api_base}}/api/company/media?per_page=200` — real media
   for placeholder swaps.
5. `GET {{company.api_base}}/api/company/v1/products` — real products.
6. `GET {{company.api_base}}/api/droplet_installations` — installed
   droplets. The page templates embed droplet-backed nodes; without this
   the builders cannot tell "remap the UUID" from "delete the node".

If step 1 returns nothing, the company has no portal app at all. That is
fine — offer to create one, and pass `definition_id: "NEW"`.

Before opening the panel, give the user two or three sentences on what
you found: which portal app is live, what is already on it, and how much
real content exists to build with. If the media library is empty, say so
now — the pages will ship with honest empty states rather than invented
numbers, and it is much better for them to hear that up front than to
discover it in the handoff.

# Step 1 — The panel (one `steps` call)

Keep it short. Two decisions, three at most.

1. `portal_app` — `single_select`, `skippable: false`.
   "Which portal are we building?" One option per definition from Step 0,
   labelled with its name and annotated `(live)` for the active one and
   `(N screens)` where screens exist. Add a final
   `Create a new portal app` option. Option ids are the definition ids as
   strings; the new-app option's id is `NEW`.

2. `pages` — `multi_select`, `mode: opt_out` (pre-checked; the user
   trims). The five available pages, with the id on the left — these ids
   are the workflow's contract, so do not rename them:

   | id                  | Label                      | Description to show                                                      |
   | ------------------- | -------------------------- | ------------------------------------------------------------------------ |
   | `partner-home`      | Partner home               | The daily driver for a rep — hero, share kit, ready-to-post content      |
   | `customer-home`     | Customer home              | Account quicklinks, rewards, learn videos, member perks, shop rows       |
   | `partner-dashboard` | Partner dashboard (Today)  | A focused "what do I do today" cockpit — advice ring, action row         |
   | `affiliate`         | Affiliate page             | Share tools and earnings context — QR/share card, product and earnings   |
   | `home-alternate`    | Alternate home             | A second home layout to A/B against the primary                          |

   Pre-check by audience, not all five: a company whose people are reps
   wants `partner-home` + `partner-dashboard` + `affiliate`; a
   customer-facing brand wants `customer-home`. Leave `home-alternate`
   **unchecked** — it is a comparison layout and only makes sense
   alongside a primary home. Infer the audience from what you saw in
   Step 0 (does the company have reps? enrollment packs?) and say which
   way you leaned in the panel intro.

3. `confirm_overwrite` — `single_select`, only when Step 0 found existing
   screens whose slugs collide with the pages being built.
   "`<slug>` already exists. Update it in place, or build alongside it?"
   with ids `update` / `alongside`.

Call `steps`, then END YOUR TURN and wait for the answers message.

# Step 2 — Hand off to the workflow

Build `page_positions` from the chosen pages, in this order — the
everyday home first, the cockpit second, share tools third, and the
alternate layout last, because it is the one a user should reach for
deliberately:

```
partner-home | customer-home  → 1
partner-dashboard             → 2
affiliate                     → 3
home-alternate                → last
```

Number them contiguously from 1 over only the pages actually chosen.

Then start the run and end your turn:

```
run_workflow({
  slug: "launch-portal",
  context: {
    definition_id: "<portal_app answer, or NEW>",
    navigation_id: <navigation id from Step 0, or null when creating a new app>,
    pages: ["partner-home", "partner-dashboard", "affiliate"],
    page_positions: { "partner-home": 1, "partner-dashboard": 2, "affiliate": 3 },
    company_id: <company id>,
    audience: "partner" | "customer" | "both",
    on_slug_collision: "update" | "alongside"
  }
})
```

`pages` is the load-bearing key: the workflow derives one boolean flag
per page from it and skips the steps for pages nobody asked for. A page
missing from that array is not built.

# What the workflow does, so you can set expectations

Tell the user this in a sentence or two — a run takes a while and they
should know what they are waiting on:

1. **Resolve the app** — confirms the definition, inventories existing
   screens, navigation, media, products and installed droplets once, so
   the parallel builders don't each rediscover it.
2. **Build the pages in parallel** — up to five at once, each from a
   working layout, each swapping placeholders for the company's real
   content.
3. **Reconcile the navigation** — deletes duplicate items the parallel
   builders created, gives every item a slug (an item without one
   renders as a dead ALL-CAPS header, which is the most common way a
   portal page ships invisible), and assigns contiguous positions.
4. **Publish** — `POST .../versions` and read `has_pending_changes` back
   to prove it took.
5. **Verify** — an independent read-only reviewer refetches every screen
   and fails the run on any surviving `picsum.photos`, `REPLACE_*` or
   foreign droplet UUID.

Every step is QA-reviewed against acceptance criteria by a reviewer that
never sees the builder's transcript, and reworked automatically on
failure.

# Ground rules

- **Never fabricate portal data.** If a widget wants earnings, ranks or
  counts and the company has none, it ships an honest empty state. A
  portal that lies about someone's earnings is worse than an empty one.
- **Don't ask what the API already told you.** Definitions, screens,
  navigation, media, products and droplets all come from Step 0. The
  panel exists for the two things Fluid cannot know: which app, and
  which pages.
- **One portal app per run.** If the user wants pages on two different
  definitions, run the workflow twice.
- For widget vocabulary, layout rules and the gotchas that silently
  break a live portal page, read the **Portal page authoring** skill.
