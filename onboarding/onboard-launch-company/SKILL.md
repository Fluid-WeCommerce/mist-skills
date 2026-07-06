---
name: Onboard & Launch Company
description: >-
  Guided end-to-end company onboarding flow: collect the company website URL,
  auto-detect available Connect integrations (Shopify / Exigo / ByDesign / etc.
  droplets) or fall back to public scraping, then fire the flagship
  onboard-launch-company workflow — which clones the site into a theme,
  iteratively refines it against screenshots, imports products, ticks off the
  Getting Started checklist, discovers UGC, and delivers a real launch-readiness
  review. Use this to launch a brand-new company in one sitting.
icon: rocket
---

# Onboard & Launch Company

You are helping the active company go from "signed up" to "ready to launch" in one
sitting. Your job in this chat is narrow: **collect the two inputs the workflow
needs (website URL + product-import path), then fire `run_workflow`**. The
workflow itself does the heavy lifting across dedicated agent chats.

The active Fluid company is already selected in Mist Desktop — `fluid_api(path,
method, body)` targets it and injects the token. Never ask for a store URL or
API key.

Trigger examples: "onboard this company", "launch this store", "let's go end to
end on {{company.name}}", "run the flagship onboarding".

## Step 0 — Detect Connect availability up front

Before asking anything, discover which Connect integrations the company can
actually use so the picker isn't padded with dead options.

```
GET /api/droplets       — list of installed droplets
```

The Connect-eligible droplet names today are: **Shopify**, **Exigo**, **ByDesign**,
**Pillars**, **Infotrax**. Match on `droplet.name` (case-sensitive). For each,
capture: `uuid`, `name`, and `is_connected`.

- If ≥ 1 droplet is `is_connected: true` → mark that provider as "already
  connected" — the workflow can pull products/customers directly.
- If ≥ 1 droplet exists but none is connected → mark as "available, needs
  connection." Include it in the picker; note that the connection flow will
  interrupt the workflow at the products step.
- If none of the Connect droplets are installed → the picker only offers
  "scrape public product pages" or "manual entry (stub)."

Also GET `/api/settings/companies/{active_id}` (or the equivalent company-detail
route) to check whether the company already has a `website_url` set. If so,
suggest it as the default — do not silently reuse it, but pre-fill.

## Step 1 — Steps panel

Call `steps` with title `Onboard {{company.name}}` and these steps, then END
YOUR TURN and wait for answers:

1. `website_url` — text_input "What's the company's current public website?"
   Pre-fill from `/api/settings/companies/{id}` if available. Skippable: false.
   Validation: must look like an http(s) URL — if the user types garbage, use
   `steps_answer` to re-prompt.

2. `products_source` — single_select "Where should we pull products from?"
   Options depend on Step 0's discovery. Always include at least the last two:

   - When a Connect droplet is `is_connected: true`, add ONE option with id
     `connect_<slug>` (e.g. `connect_shopify`), label
     `Connect: <Name> (already linked)`, description "Pull products +
     customers directly from your existing <Name> integration. Fastest path."
   - When a Connect droplet exists but is not connected, add ONE option per
     droplet with id `connect_<slug>`, label `Connect: <Name>`,
     description "Link your <Name> account during the products step. Mid-flow
     interruption."
   - Always: id `scrape`, label `Scrape public product pages`, description
     "Extract products from the company's website. Works even without an
     existing e-commerce platform."
   - Always: id `manual`, label `Manual entry (stub only)`, description
     "The workflow creates a placeholder product. You'll add real products
     later by hand."

3. `confirm` — single_select "Ready to run the flagship onboarding? This
   spawns 7 dedicated agent chats and takes ~15-30 minutes." Options: id
   `go` label `Yes, launch it`, id `cancel` label `Not yet`.

Keep this to three steps. Anything else (Connect credentials, brand info
prompts, etc.) belongs INSIDE the workflow, not this picker.

## Step 2 — Fire the workflow

Only if the user picked `go`. Call `run_workflow` with:

```
workflow_slug: "onboard-launch-company"
context: {
  "website_url": <answer from step 1>,
  "connect_provider": <null | "shopify" | "exigo" | "bydesign" | "pillars" | "infotrax">,
  "connect_droplet_uuid": <uuid from Step 0, or null>,
  "products_source": "connect" | "scrape" | "manual"
}
```

Derive `connect_provider` from the `products_source` answer:
- id starts with `connect_` → provider is the slug after the prefix
- id is `scrape` or `manual` → provider is `null`

`run_workflow` returns immediately with a run plan; the progress card renders
in this chat and updates as steps advance. End your turn after the tool call —
do NOT narrate the plan or predict outcomes. The card does that live.

## Step 3 — After the run kicks off

Send one final short message: 1-2 lines confirming what got kicked off and
that the run continues in the background. Example:

> The onboarding run is live — 7 steps, ~15-30 min. Follow the progress card
> above; I'll be here when it lands.

Do not poll `workflow_status` unsolicited. When the user asks, use it.

## Rules

- Never collect a Fluid API key or store URL — the active company is set.
- Never guess at the website URL or Connect provider — always confirm via
  the steps panel.
- Never fire `run_workflow` without an explicit `go` answer in Step 1.
- If `run_workflow` returns unavailable (no active project context), tell
  the user the workflow needs a project selected in the sidebar and stop.
- If the user cancels in Step 1, respond with one line ("no worries — ping
  me when you're ready") and stop. Do not re-prompt.

## API & sequencing gotchas (from live onboarding runs)

These are non-obvious and cost real time when rediscovered. Bake them in.

- **Create pages via `POST /api/company/pages`.** The `/api/company/v1/pages`
  variant 404s. `html_code` compiles async — re-GET (or re-PATCH) if the body
  comes back empty. Deleting a page and reusing its slug tombstones the slug;
  always use a fresh slug.
- **Push theme edits BEFORE creating pages.** Creating a page auto-generates
  an `application_theme_template` in the active theme. A subsequent
  `theme push` then tries to delete those orphans and can fail or clobber. Do
  all theme pushes first, then create pages. Orphaned templates are removable
  via `DELETE /api/application_theme_templates/:id`.
- **Cloud Armor throttles page-create bursts.** A rapid run of POST-with-body
  requests gets persistently 403'd by the prod WAF (GET stays 200), and a
  short cooldown doesn't clear it. Space page creates out; don't hammer.
- **Products create as `status:draft`** even with `active:true` → PATCH
  `{product:{status:"active"}}` after each. Options only materialize via
  `option_attrs` (product = names, variant = values). Collection membership is
  `PATCH product {collection_ids:[...]}` — `collections/{id}/add_product` 404s.
- **Storefront status checks MUST use a real headless browser.** Prod Cloud
  Armor returns 500/302 to curl/HTTP clients even with a browser UA, while a
  real browser gets 200. Never conclude a route is broken from a curl status.
