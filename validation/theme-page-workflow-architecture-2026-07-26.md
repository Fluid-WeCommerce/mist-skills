# Theme page workflow architecture — 2026-07-26

## Decision

Keep **Copy Theme** as the user-facing outcome and final acceptance boundary,
but do not use it as one agent-sized implementation task or one rigid
site-shape contract.

Use a two-layer skill architecture:

1. `themes/clone-page-to-liquid` owns the universal visual-copy mechanics for
   one source route and one Fluid route: source evidence, Liquid
   implementation, managed preview, DOM/log inspection, visual comparison,
   refinement, and evidence output.
2. Thin page-type skills own semantics: route classification, canonical
   template family, minimum real Fluid resources, required interactions, and
   page-specific judgment. The first set is Home, Shop, Product, Category, and
   Collection. Blog, Post, Content, Cart, Search, 404, and other system-page
   skills should follow from real traces.

The workflow composes those page skills as a dependency graph:

```text
brand + route discovery
        |
global tokens + shell
        |
Home specialist -> universal visual core
        |
Shop specialist -> universal visual core
        |
PDP specialist -> universal visual core
        |
Collection specialist -> universal visual core
        |
content/system specialists
        |
link + regression gate
```

The home route is first because it establishes typography, brand tokens,
announcement/header/navigation/footer, container widths, breakpoints, and the
primary editorial section language.

The Shop route is a second semantic gate, not just another Home-like page.
Home does not prove dynamic product cards, canonical PDP links, filters,
sorting, search, pagination, mobile drawers, or empty/loading/error states.
It also does not make catalog completeness a prerequisite for visual work.
Shop and PDP reuse existing Fluid data or reconcile a bounded source-backed
preview set; complete catalog migration stays on the separate data track.

## Execution unit

One worker owns one source route mapped to one Fluid route. It must return the
shared `PAGE_OUTPUT` contract with durable source/local evidence, classified
stable/resource/dynamic/external landmarks, copy hashes, media readiness,
interaction proof, material deltas, and an honest
pass/needs_adjudication/blocked result.

The shared contract lives in
`themes/page-clone/references/pixel-perfect-page.md`. Page-archetype skills may
add semantic requirements but may not weaken its evidence floor.

The first concrete skills are:

- `themes/clone-page-to-liquid`
- `themes/clone-home-page`
- `themes/clone-shop-page`
- `themes/clone-product-page`
- `themes/clone-category-page`
- `themes/clone-collection-page`

Continue forward-testing across materially different storefronts. Add or
change specialist rules only when the evidence shows a repeated semantic
need; do not grow the universal skill into an encyclopedic site importer.

## Page taxonomy

The target is representative template and state coverage, not one bespoke
template for every URL.

1. Shared shell: announcement, header, nav, footer, tokens, fonts, menus.
2. Home: one canonical route, every section and responsive state.
3. Catalog lists:
   - all-products/shop
   - collection index
   - collection detail
   - category index/detail when distinct
   - search results and no-results
4. Catalog detail:
   - canonical PDP
   - representative variant, subscription, sold-out, and promotional states
5. Editorial:
   - blog index, including subdomain discovery
   - post detail with author/date/taxonomy/related content
   - static content template families
6. System/commerce:
   - cart empty/filled
   - 404
   - maintenance/503 when theme-controlled
   - account/auth states only where the storefront owns them
7. Final linker: canonical Fluid URLs, menus, template defaults, live route
   health, responsive regression, and cold-cache checks.

## Workflow composition

Mist workflows currently support a DAG of skill/prompt steps. A step can call
`run_workflow`, but that child run is fire-and-forget: the parent cannot await
its output, enforce its evidence, cancel it as one unit, or gate dependents on
its final status.

Therefore the current production-safe design is one parent workflow with
page-skill steps and explicit `dependsOn` edges. Do not emulate composition by
launching detached child workflows from a step.

## Parallelism boundary

Do not run several page agents against one mutable theme checkout merely
because Home and Shop passed. Different template files still share tokens,
sections, snippets, config, generated theme state, Git history, and one dev
server. Per-file write queues do not prevent two workers from making
incompatible assumptions about a shared component.

Safe fan-out requires:

1. a named integration commit after Home and Shop pass
2. one isolated Git worktree/branch per page archetype
3. an explicit ownership manifest for template, section, snippet, and config
   paths; shared shell paths are read-only unless the integrator grants a lock
4. at most three workers, each with its own preview port and evidence namespace
5. a linker step that merges/cherry-picks the page commits, resolves conflicts,
   reruns the full theme audit, recaptures Home and Shop regressions, and then
   verifies every canonical route

Until Mist can create, scope, and reconcile those isolated page worktrees, keep
the page implementation steps sequential. The desired dependency graph is not
authorization for nondeterministic concurrent writes.

A future first-class composed-workflow step should provide:

- awaited child terminal status
- parent/child cancellation and restart propagation
- typed child inputs and outputs
- inherited company/project ownership
- evidence receipt aggregation
- child revision pinning
- bounded child concurrency and cost

## Model routing decision

Model choice is an empirical page-build decision, not a vendor preference. The
initial diversity trials are complete enough to stop the open-ended model
tournament and finish the product:

- `openai/gpt-5.6-sol` is the default Home, Shop, PDP, and universal-page
  builder/refiner.
- `google/gemini-3.6-flash` handles fast source discovery and bounded,
  independent, read-only page QA after the builder's final change.
- `anthropic/claude-opus-5` is the escalation path for unusually difficult
  structural/media reconstruction or a QA disagreement that cannot be
  adjudicated from current evidence.
- Kimi and Fable remain available tools, but are not default golden-route gates.

Observed all-SOL creation on the retained Taft trial took 7:46 for Home, 8:55
for Shop, and 8:29 for PDP (25:10 total). Representative bounded SOL refinements
took 5:04-5:53; a deep structural recovery took 12:57. Read-only QA took
approximately 1:42-2:44 per page. These are operational baselines, not a
controlled performance guarantee: record first-render time, total time,
rework rounds, tool failures, and signed receipts for every retained run.

Gemini QA may never pass from prose or a successful comparison call. It must
inspect the current attached pixels, DOM, interactions, console/server logs,
and signed comparison receipts. Machine hard failures stop the page. Geometry
and variable-media diagnostics go to the page specialist; unresolved material
deltas return `needs_adjudication`. Escalate to Opus only with the exact failed
contract and current evidence, never by starting an unbounded second clone.

## Performance and resilience

- Keep workflow concurrency at three initially. Parallelism begins after the
  two golden gates; ten simultaneous model turns are not a speed strategy.
- Use one managed preview per project.
- Cache and reuse successful source evidence instead of recrawling.
- Limit remote crawl/upload concurrency to three.
- Persist every successful artifact so slow Wi-Fi resumes missing cells.
- Capture one viewport at a time on lower-end machines.
- Serve responsive DAM media so mobile does not download desktop video when a
  mobile source exists.

## Evidence implementation

Mist Desktop PR #7323 adds the first enforceable source-vs-preview comparison
surface. Stacked PR #7324 adds a viewport-bound rendered source sidecar and
ordered-copy evidence. Stacked PR #7326 adds native, embedded, responsive,
custom-element, and open-shadow-root video inventory plus source/local count,
identification, orientation, and playback evidence.
`compare_preview_to_source` requires the matching screenshot and page-evidence
paths, rejects mixed captures, and returns a signed receipt with source/local
copy hashes alongside geometry, coverage, bounded pixel diagnostics, HTTP
status, horizontal overflow, capture truncation, media readiness, and video
parity.

The universal workflow requests `copy_mode:"diagnostic"` because the generic
runner cannot know which text is stable and which is resource-backed, dynamic,
or external. The page specialist must classify those landmarks. Stable cells
must then match exactly; a specialist may use `copy_mode:"exact"` for a cell
known to be entirely stable. Fixed 1440 × 900 and 390 × 844 cells remain the
current onboarding benchmark defaults, not platform-wide requirements.

Mist Desktop PR #7325 independently aligns GPT-5.6 Sol/Terra/Luna, Gemini 3.6
Flash, Kimi K3, Opus 5, and Fable 5 with their live 1M-class context windows.
Without it, several candidates compact near the legacy 128k fallback and the
benchmark measures infrastructure bias rather than model capability.

The receipt is necessary evidence, not a universal visual oracle. Raw pixel
scores vary with antialiasing, dynamic video frames, source personalization,
viewport reflow, and resource state. Review must still reconcile stable
landmark identity/order/copy, geometry, interactions, variable-data policy, and
the attached source/local images. A universal five-percent geometry rule or
minor-count cap produces false passes and false failures; the specialist makes
that judgment and must surface unresolved material deltas as
`needs_adjudication`.

Video parity is not byte identity after a URL-changing Fluid DAM transfer;
signed source-to-DAM asset lineage remains a separate gap. The next Surface API
increments should add that lineage, structured landmark matching, and
workflow-authored variable-copy classifications rather than model-authored
ignores.
