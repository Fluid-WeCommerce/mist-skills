# Theme page workflow architecture — 2026-07-26

## Decision

Keep **Copy Theme** as the user-facing outcome and final acceptance boundary.
Do not use it as one agent-sized implementation task.

Execute the theme track as a dependency graph of page-scoped skills that all
inherit one strict pixel-perfect page contract:

```text
source/data evidence
        |
global tokens + shell
        |
home golden route
        |
shop/all-products golden route
        |
        +----------------+----------------+----------------+
        |                |                |                |
catalog lists       product detail   editorial pages   system states
        |                |                |                |
        +----------------+----------------+----------------+
                         |
                link + regression gate
```

The home route is first because it establishes typography, brand tokens,
announcement/header/navigation/footer, container widths, breakpoints, and the
primary editorial section language.

The shop route is a second hard gate, not just another fan-out task. Home does
not prove dynamic product cards, catalog completeness, canonical PDP links,
filters, sorting, search, pagination, mobile drawers, or empty/loading/error
states. Parallel page work starts only after both home and shop pass.

## Execution unit

One worker owns one source route mapped to one Fluid route. It must return the
shared `PAGE_OUTPUT` contract with durable source/local evidence, exact copy
hashes, media readiness, interaction proof, majors/minors, and an honest
pass/needs-review/cap-reached result.

The shared contract lives in
`themes/page-clone/references/pixel-perfect-page.md`. Page-archetype skills may
add requirements but may not weaken it.

The first two concrete skills are:

- `themes/clone-home-page`
- `themes/clone-shop-page`

Do not author every remaining archetype from theory before these two
generalize. Forward-test them across materially different storefronts, record
recurring failures, then extract collection/category/blog/PDP/post/system-page
rules from actual traces.

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

A future first-class composed-workflow step should provide:

- awaited child terminal status
- parent/child cancellation and restart propagation
- typed child inputs and outputs
- inherited company/project ownership
- evidence receipt aggregation
- child revision pinning
- bounded child concurrency and cost

## Model benchmark

Model choice is an empirical page-build decision, not a vendor preference.
Never let candidate models edit the same checkout.

For each source site/model cell:

1. Create an isolated company and theme.
2. Reuse one frozen source evidence snapshot for all candidates.
3. Run the same home skill, tool access, turn limits, and QA thresholds.
4. Use a fixed independent evaluator that did not build the candidate.
5. Keep the final artifact and every signed evidence receipt.

Measure:

- wall-clock time to first render and hard pass
- builder and reviewer model/tool calls
- rework rounds and terminal failures
- exact copy missing/extra/mismatch counts
- source landmarks matched
- priority media ready/failed/pending
- desktop/mobile visual majors and minors
- landmark geometry error
- horizontal overflow and runtime errors
- interaction checks passed
- approximate cost when available

Initial diversity matrix:

| Source           | Why it matters                                            |
| ---------------- | --------------------------------------------------------- |
| flourist.com     | Editorial food imagery, typography, commerce storytelling |
| vervecoffee.com  | Dense merchandising, product rails, motion/media          |
| partner.co       | Membership and branded commerce behavior                  |
| calderalab.com   | Premium editorial PDP/home composition                    |
| dimebeautyco.com | Promotion-heavy beauty storefront and responsive nav      |
| taftclothing.com | Fashion imagery, variants, strong visual identity         |

Start with two contrasting sites and two builders. Expand only after the test
harness produces durable, comparable results. A prose reviewer verdict without
the required evidence is not a benchmark result.

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

## Known product gap

Mist can require signed receipts proving that a reviewer opened source images,
captured the local route, read rendered DOM, exercised controls, and inspected
logs. It still lacks a first-class source-vs-preview comparison receipt that
computes exact copy reconciliation and quantitative visual difference itself.

Until that exists, the new contract is materially harder to bluff, but it is
not the final Surface API. The next SDK increment should produce a signed
comparison receipt rather than accepting model-authored “pixel perfect” prose.
