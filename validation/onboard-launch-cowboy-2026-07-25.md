# Onboard + Launch hardening: Cowboy validation

Date: 2026-07-25  
Test source: <https://cowboy.com>  
Priority routes:

- Home: <https://cowboy.com/>
- Shop: <https://cowboy.com/collections/bikes>
- PDP: <https://cowboy.com/products/e-bike-cowboy-cruiser>
- Second PDP check: <https://cowboy.com/products/e-bike-cowboy-cross>

## Scope and safety boundary

This pass hardened the reusable onboard-and-launch workflow, its skills, and the
Mist capabilities they depend on. It did not write to a Fluid company or merge
to production. No disposable company was identified, so the Cowboy test was
limited to public/read-only source analysis and local automated tests. A live
theme push, product import, and end-to-end workflow run remain mandatory before
calling the launch path production-proven.

## What the Cowboy baseline revealed

Observed from Cowboy's live sitemap and public pages during this pass:

| Finding                                        |                                                           Observed result | Why it matters                                                     |
| ---------------------------------------------- | ------------------------------------------------------------------------: | ------------------------------------------------------------------ |
| URLs in sitemap                                |                                                                       373 | A collection-page crawl is not a site inventory.                   |
| Product-shaped sitemap routes                  |                                                                       343 | This is the discovered denominator, not an arbitrary tool cap.     |
| Live product routes                            |                                                                       324 | These require one-to-one import identities.                        |
| Stale routes redirecting to home               |                                                                        19 | HTTP 200 alone would falsely count these as products.              |
| Product Markdown pages missing a primary image |                                                                       108 | Markdown cannot be the only product-data source.                   |
| Duplicate-title groups                         |                                                                        55 | Title fallback can collapse distinct parts into one Fluid product. |
| Product types observed                         | 278 spare parts, 34 accessories, 5 bikes, 3 tools, 3 services, 1 software | “The bike collection” is far from the full product list.           |

All 343 advertised product routes returned an HTTP response during the bounded
probe. The 19 stale routes were detected from final-URL and product-evidence
checks, not from status alone. The live/excluded split is time-sensitive and
must be recomputed at the start of a real run.

Cowboy advertises AI-friendly Markdown, but its root Markdown is a short content
summary that omits the visual hierarchy and global chrome. Initial rendered
captures were also invalid as parity evidence because a geo dialog obscured the
home page and the shop capture was blank/overlaid. A screenshot existing is not
the same as a clean visual baseline.

## Decisions made

### 1. Catalog completion is now its own strict gate

The workflow builds `source-catalog.json` before product writes. Discovery is a
union of sitemap children, structured APIs when available, all collection
pagination, and every unique PDP. Each route is recorded as a live product or an
evidence-backed exclusion. The manifest path, observation time, and SHA-256 are
passed to the importer.

Why: product import cannot prove completeness when it discovers and grades its
own denominator in the same write step.

The `fluid-product-admin-import` playbook is now published in this community
repository under the exact slug the workflow calls. A fresh Mist installation
therefore receives the same catalog and payload contract from the managed
community-skill refresh; it no longer depends on an unrelated local skill
checkout.

### 2. Product identity is source-based, never title-based

Every live `source_id`/canonical source URL maps to one distinct Fluid product
ID in a persisted checkpoint. Duplicate titles are reported and an ambiguous
recovery match stops for review.

Why: Cowboy has 55 duplicate-title groups. “Front Wheel” and “Pedals” are
legitimate compatibility variants, not duplicates to discard.

### 3. Visual truth uses three evidence layers

- Markdown for copy and simple catalog facts.
- Rendered HTML/CSS for DOM, global chrome, tokens, fonts, and structured data.
- Clean, exact-viewport, full-page screenshots for visual hierarchy.

The required matrix is home, shop, and PDP at 1440×900 and 390×844. Every
source capture records requested URL, final URL, status, and overlay handling.
Every local capture reports viewport width, document width, horizontal overflow,
route status, and runtime logs.

Why: Cowboy's Markdown and obscured screenshots independently looked
“successful” while both were insufficient for pixel-parity work.

### 4. Managed Mist capabilities are the fresh-machine contract

The skills now use:

- `crawl` for Firecrawl v2 rendered source evidence and constrained overlay
  actions;
- `start_preview` for the bundled CLI, dependency setup, port allocation, and
  long-lived server lifecycle;
- `screenshot_preview` for exact local full-page captures;
- `interact_preview` for constrained localhost disclosure/tab checks;
- preview state, browser console, and server logs for diagnosis.

Global Fluid CLI, Playwright, Node, and user-owned browser installs are not
prerequisites inside Mist. A project-local browser harness remains an optional
standalone fallback.

Why: this computer had a stale `/opt/homebrew/bin/fluid` Ruby shim. Agent
`run_cli fluid ...` used that ambient executable even though Mist ships a valid
Node CLI. The hardened resolver now selects Mist's bundled CLI deterministically.

### 5. Task routing is cross-vendor and evidence-driven

The workflow currently routes:

- Gemini 3.6 Flash to high-volume extraction/content tasks;
- GPT-5.6 Sol to implementation, reconciliation, and adversarial reasoning;
- Claude Opus 5 to critical visual/build turns and independent visual review;
- Kimi K3 to bounded mechanical QA, always with a stronger reviewer on
  launch-critical claims.

Why: provider preference is not a quality strategy. Extraction, implementation,
visual judgment, and cheap deterministic checks have different requirements.
The strict QA turn uses a different model on critical steps to reduce correlated
self-grading.

This is a reasoned routing baseline, not a completed model bake-off. A real
disposable-company run should record per-step runtime, rework count, cost, and QA
outcome before changing the routing.

### 6. A budget cap cannot become a pass

Five visual-refinement rounds ending with major differences now report
`cap-reached`/needs-review and fail the flagship gate. Missing or stale evidence,
blank/obscured captures, unresolved catalog routes, and partial batches also fail.

Why: the previous vocabulary allowed “we stopped trying” to be interpreted as
“the result is acceptable.”

## Performance and resilience choices

- Workflow concurrency is capped at three live steps.
- Source fetches are bounded, retried with exponential backoff/jitter, and
  checkpointed for resume.
- Product writes start at two concurrent requests; media work starts at five
  and backs off on 429/5xx.
- Local visual capture is serialized on lower-end computers.
- Images are streamed/uploaded per item instead of holding a catalog in memory.
- Missing matrix cells resume after a network interruption; completed evidence
  is not blindly recaptured.
- The confirmation UI no longer promises a 20–40 minute full run. Large
  catalogs and five visual rounds can take hours.

## Local verification completed

- Workflow JSON parses and passes the current Mist Desktop
  `WorkflowDefinitionSchema`.
- Workflow invariants: 25 unique steps, strict final gate, all steps have
  explicit worker and QA model routing, maximum parallelism 3.
- Mist visual-capability branch: TypeScript passes; OxLint has zero findings;
  all 149 Jest suites pass (1,783 tests), including Firecrawl request
  construction, exact/full-page capture, overflow reporting, constrained
  preview interaction, screenshot attachment, and safe-mode policy.
- Mist bundled-CLI branch: TypeScript passes; OxLint has zero findings; all 147
  Jest suites pass (1,776 tests), including resolver tests proving an ambient
  stale `fluid` executable is ignored.
- Product-import skill passes the Codex skill validator.
- The published catalog now passes a dependency-free validator that rejects
  duplicate JSON keys, duplicate skill/workflow slugs or paths, missing files,
  missing references, and malformed workflow JSON. This caught and fixed a
  pre-existing merged manifest object that silently hid the Smart Dashboard
  entry behind Checkout Funnel Diagnosis.
- All changed JSON files parse and `git diff --check` is clean.

## Deliberately unresolved before production

1. Run the full workflow against a named disposable Fluid company, including
   import, theme push/activation, page creation, and rollback/cleanup.
2. Exercise the managed Firecrawl v2 screenshot request with Mist's injected
   production credential; no Firecrawl key was present in the shell.
3. Capture the final 6/6 Cowboy source matrix after dismissing the geo overlay,
   then compare it to the built theme through all refinement rounds.
4. Verify all 324 currently-live Cowboy products import one-to-one and all 19
   stale routes remain explicit exclusions. Recompute these counts at run time.
5. Confirm source images, option axes, variants, exact EUR pricing, and DAM URLs
   across the full destination, not only a sample.
6. Measure the four proposed model routes on the same source and store the
   per-step latency, cost, rework, and independent QA scores.

These are live-environment validations, not permission to weaken the gates.
