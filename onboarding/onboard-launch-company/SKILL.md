---
name: Onboard & Launch Company
description: >-
  Guided end-to-end company onboarding flow: collect the company website URL,
  auto-detect available Connect integrations (Shopify / Exigo / ByDesign / etc.
  droplets) or fall back to public scraping, then fire the flagship
  onboard-launch-company workflow — which imports products FIRST (so the theme
  renders a real catalog), clones the site into a theme through page-scoped
  hard gates beginning with home and shop, iteratively refines it against screenshots,
  reconciles onboarding info, discovers UGC, and delivers a real
  launch-readiness review. Runs against the ALREADY-SELECTED active company — it does NOT create a
  company; it populates the existing one from its website. Use when the user says
  "onboard from <url>", "onboard this company", or "launch this store".
icon: rocket
---

# Onboard & Launch Company

You are helping the active company go from "signed up" to "ready to launch" in one
sitting. Your job in this chat is narrow: **collect the scoped launch inputs
(run scope, website URL, product-import path, theme target, and optional content),
then fire `run_workflow`**. The
workflow itself does the heavy lifting across dedicated agent chats.

The active Fluid company is already selected in Mist Desktop — `fluid_api(path,
method, body)` targets it and injects the token. Never ask for a store URL or
API key.

Trigger examples: "onboard from https://acme.com", "onboard this company",
"launch this store", "let's go end to end on {{company.name}}", "run the flagship
onboarding". When the user gives a URL ("onboard from <url>"), take it as the
`website_url` — pre-fill it in the Step 1 panel, but still SHOW the step so the user
can confirm or change the source URL (never silently skip the "pull from" question).

**This is a RUN, not an authoring task.** Execute the steps below now — collect the
inputs and fire the workflow. Do NOT offer to save, diff, summarize, or edit this
skill; that only applies when authoring in a Skill project, not here.

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

Finally, GET `/api/application_themes` to list the company's existing themes
(capture `id` + `name`). This populates the "clone into an existing theme or
create a new one" question in Step 1. If the company has no themes yet, the only
option is "create new."

## Step 1 — Steps panel

Call `steps` with title `Onboard {{company.name}}` and these steps, then END
YOUR TURN and wait for answers:

1. `run_scope` — single_select "What should this run do?" Skippable: false. Gates
   which downstream tracks execute. Brand + country **data gathering always runs and
   is QA'd first** (it drives everything below), so every option includes it.
   - id `full`, label `Full onboarding (recommended)`, description "Gather + QA
     brand/business/country data, clone & refine the theme, import products, tick off
     Getting Started."
   - id `data_theme`, label `Data + theme (no products)`, description "Gather + QA the
     data, then clone & refine the theme. Skip product import."
   - id `theme_only`, label `Theme only`, description "Clone & refine the theme. Still
     gathers + QAs brand colors/fonts/countries first (they drive the theme), but skips
     the business/KYC push and products."
   - id `data_only`, label `Data onboarding only`, description "Gather, QA, and push
     brand/business/country data. No theme, no products."

2. `website_url` — text_input "What URL should we pull the store from? (the live
   site to clone the theme + import products/pages/collections from)" Skippable:
   false. **Always include this step and always show it** — even when the user said
   "onboard from <url>" or the company already has a website on file. Pre-fill the
   field with that value (the `<url>` they gave, else `/api/settings/companies/{id}`'s
   website) as a SUGGESTION, but keep the step visible so the user can confirm or
   change the source — the site to pull from is not necessarily the company's stored
   URL. Do NOT silently skip it. Validation: must look like an http(s) URL — if the
   user types garbage, use `steps_answer` to re-prompt.

3. `products_source` — single_select "Where should we pull products from?"
   `show_if: { step_id: "run_scope", any_of: ["full"] }` (only when products are in
   scope). Options depend on Step 0's discovery. Always include at least the last two:
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

4. `theme_target` — single_select "Clone into an existing theme, or create a new
   one?" `show_if: { step_id: "run_scope", any_of: ["full", "data_theme", "theme_only"] }`
   (only when the theme is in scope). Ask upfront (not mid-workflow) so the run stays
   walk-away.
   - Always: id `new`, label `Create a new theme (recommended)`, description "Scaffold a
     fresh theme for {{brand}} — keeps the clone isolated and safe to iterate."
   - For each existing theme from Step 0, add id `existing_<theme_id>`, label
     `Clone into: <theme name>`, description "Refine this existing theme instead of
     creating a new one." If the company has no themes, only `new` is offered.

5. `extras` — multi_select (mode `opt_in` — empty by default) "Add any optional content
   steps?" Off unless picked.
   - id `import_brand_social`, label `Import the brand's own YouTube + TikTok videos`,
     description "Find the company's official social accounts, register them in Fluid, and
     pull THEIR videos into the DAM + Media (the brand's own content)."
   - id `discover_ugc`, label `Discover UGC about the brand (TikTok)`, description "Search
     TikTok for other people's content about the brand and pull the best picks into the
     DAM. Different from the brand's own content above."

6. `confirm` — single_select "Ready to run? This spawns dedicated agent chats and continues
   in the background. Runtime depends on catalog size, source-site speed, and visual QA
   rounds; a large full run can take hours." Options: id `go` label `Yes, launch it`, id
   `cancel` label `Not yet`.

Keep this to these steps. Anything else (Connect credentials, brand info prompts, etc.)
belongs INSIDE the workflow, not this picker.

## Step 2 — Fire the workflow

Only if the user picked `go`. Call `run_workflow` with:

```
workflow_slug: "onboard-launch-company"
context: {
  "website_url": <answer from step 1>,
  "connect_provider": <null | "shopify" | "exigo" | "bydesign" | "pillars" | "infotrax">,
  "connect_droplet_uuid": <uuid from Step 0, or null>,
  "products_source": "connect" | "scrape" | "manual" | null,
  "theme_target": "new" | "existing" | null,
  "theme_id": <null | existing theme id>,
  "run_scope": "full" | "data_theme" | "theme_only" | "data_only",
  "extras": <string[] — the `extras` multi_select ids, e.g. ["import_brand_social", "discover_ugc"]; [] if none>,
  "build_theme": <bool>,
  "import_products": <bool>,
  "push_business_data": <bool>,
  "import_brand_social": <bool>,
  "discover_ugc": <bool>
}
```

`run_scope` and `extras` are the raw inputs the engine keys off to derive the run-gating
flags at run start — ALWAYS include both. But you MUST STILL pass every boolean flag
(`build_theme`, `import_products`, `push_business_data`, `import_brand_social`, `discover_ugc`) explicitly, set
per the derivation rules below: treat them as REQUIRED, not optional. They are a mandatory
belt-and-suspenders so the run gates correctly even where derivation is unavailable, and an
explicitly-passed flag always wins over the derived value. Do NOT emit a bare `extras` array
without the flags — that was the shape that caused every gated step to skip.

Derive `connect_provider` from the `products_source` answer:

- id starts with `connect_` → provider is the slug after the prefix
- id is `scrape` or `manual` → provider is `null`
- `products_source` skipped (products out of scope) → `products_source: null`, provider `null`

Derive `theme_target` + `theme_id` from the `theme_target` answer:

- id `new` → `theme_target: "new"`, `theme_id: null`
- id `existing_<theme_id>` → `theme_target: "existing"`, `theme_id: <that id>`
- skipped (theme out of scope) → `theme_target: null`, `theme_id: null`

Derive the track flags from `run_scope` (they gate which steps do work via the workflow's
`runIf`):

- `build_theme`: true for `full`, `data_theme`, `theme_only`; false for `data_only`
- `import_products`: true for `full`; false otherwise
- `push_business_data`: false for `theme_only`; true for `full`, `data_theme`, and
  `data_only`. Brand colors, fonts, `brand.md`, and country/locale discovery still run for
  every scope because the theme consumes them. When false, agents must not mutate company,
  onboarding, or KYC fields, and the later onboarding-reconciliation step is skipped.
  (brand + country gathering always runs regardless of scope — it drives the theme)

Derive the extras flags from the `extras` multi_select:

- `import_brand_social`: true iff selected; `discover_ugc`: true iff selected (both default false)

`run_workflow` returns immediately with a run plan; the progress card renders
in this chat and updates as steps advance. End your turn after the tool call —
do NOT narrate the plan or predict outcomes. The card does that live.

## Step 3 — After the run kicks off

Send one final short message: 1-2 lines confirming what got kicked off and
that the run continues in the background. Example:

> The onboarding run is live and will continue in the background. Follow the
> progress card above; I'll be here when it lands.

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

## API & sequencing gotchas

These are non-obvious and cost real time when rediscovered. Bake them in.

- **Read the live schema before writes.** Use `query_docs` against
  `/openapi/api-reference/storefront-v2026-04.yaml`. Catalog/content CRUD is
  `/api/v202604/company/{products,categories,collections,posts,media,playlists,pages}`;
  do not fall back to `/api/company/v1/*` from memory.
- **Create visible pages through Mist's `create_page` tool.** It coordinates the
  v202604 Page resource, theme template, local dev route, and preview pane.
  Bypassing it with a raw page POST leaves those surfaces out of sync.
- **Push theme edits BEFORE creating pages.** Creating a page auto-generates
  an `application_theme_template` in the active theme. A subsequent
  `theme push` then tries to delete those orphans and can fail or clobber. Do
  all theme pushes first, then create pages. Orphaned templates are removable
  via `DELETE /api/application_theme_templates/:id`.
- **Cloud Armor throttles page-create bursts.** A rapid run of POST-with-body
  requests gets persistently 403'd by the prod WAF (GET stays 200), and a
  short cooldown doesn't clear it. Space page creates out; don't hammer.
- **Product creates need the v202604 nested-attributes payload** — a flat
  `{product:{title,price}}` cannot express country pricing. Pricing lives on
  `variants_attributes[].variant_countries_attributes`; exactly one variant is
  `is_master:true`; use documented raw `status:"active"` + `public:true`. Options
  use `option_attrs` (product = names, variant = values). Collection membership
  is product `collection_ids` or the collection's full-replacement `product_ids`.
- **A company-default subscription plan is attached when product plan attributes
  are omitted.** For a source product with no subscription offer, include the
  non-empty v202604 skip sentinel
  `product_subscription_plans_attributes:[{"_destroy":true}]`. An omitted key or
  empty array triggers the default. Re-read the product and require
  `has_subscription_plans:false` with no active/default join. On the current
  production update path, repair historical joins by returned join ID with
  `active:false,default:false`; its delegated validator drops `_destroy`, so
  physical deletion must not be claimed unless a re-read proves it. Never
  disable the company-wide plan.
- **Three product-payload details that silently or noisily kill an import:**
  - `variant_countries_attributes` needs **`country_id` (integer) + `active`**.
    `country_iso` alone 422s `active is missing, country_id is missing`. Get the
    integer from `GET /api/settings/company_countries` →
    `company_countries[].country.id`; never hard-code an example country's ID.
    This is the classic cause of a catalog with correct titles and no prices.
  - `images_attributes` entries use **`image_url`**, not `url` — `{"url": …}`
    422s `image_url is missing`, which is how a whole catalog ends up on Fluid's
    grey placeholder.
  - **Set options + every variant at CREATE time.** This preserves source
    combinations and avoids a risky repair. If a repair is needed, re-read the
    v202604 PATCH schema and existing nested IDs before writing; never assume a
    legacy PATCH limitation still applies.
  - Omit `description` entirely when the source description is empty. Do not
    send `null` or `""`: the outer validator normalizes the empty string to
    null, then the delegated live create rejects it with
    `422 product.description must be a string` despite nullable-looking
    generated/docs-side shapes.
- **DAM upload supports a local file or a remote URL.** Use `dam_upload` for a
  file already in the sandbox, or `fluid dam upload --url <SOURCE_URL>` for a
  remote source. The underlying `POST https://upload.fluid.app/upload` accepts
  multipart `file` or multipart `external_asset_url` (exact field name; not
  `external_url`) and returns `asset.default_variant_url`. JSON mode is only for
  `b64_json`/`data_uri`. Never keep a source-CDN URL in destination product data.
- **Source catalogs are often bot-walled.** `<site>/products.json` on a modern
  Shopify/Hydrogen storefront returns a Cloudflare 403 "Verifying your
  connection". Check for a `<url>.md` LLM-markdown twin (some storefronts
  advertise one in a banner — it returns clean title/image/price/description),
  otherwise crawl the collection pages and the PDPs.
- **Storefront status checks MUST use a real headless browser.** Prod Cloud
  Armor returns 500/302 to curl/HTTP clients even with a browser UA, while a
  real browser gets 200. Never conclude a route is broken from a curl status.
