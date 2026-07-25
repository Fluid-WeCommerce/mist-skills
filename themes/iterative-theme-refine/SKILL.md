---
name: Iterative Theme Refine
description: >-
  Screenshot-based iterative refinement loop that runs AFTER theme-clone. Each
  round captures paired screenshots (source site vs the cloned theme's preview),
  the model eyeballs the diff, edits the top 1-3 discrepancies, and re-checks.
  Caps at 5 iterations and produces a documented remaining-diff report if the
  cap is reached before "close enough." Use this when a clone needs to be
  tightened to a real visual match — not a one-shot pass.
icon: refresh-cw
---

# Iterative Theme Refine

You are refining a freshly-cloned Fluid theme against its source site. This skill
is the **iteration loop** — deliberately narrow, deliberately capped. It reuses
`themes/theme-refine` as the underlying recipe book (colors, spacing, section
recipes) but drives it as a hard-bounded screenshot → compare → fix → re-screenshot
loop.

The active Fluid company is already selected in Mist Desktop. All Fluid API calls
go through `fluid_api(path, method, body)` (token injected automatically) and the
`fluid` CLI is already authenticated. Never ask for credentials.

## When to use this vs `themes/theme-refine`

- **This skill**: after `themes/theme-clone` has scaffolded a first pass and you
  need a bounded, self-terminating tighten-up. Runs on autopilot inside the
  `onboard-launch-company` workflow.
- **`themes/theme-refine`**: everything else — legacy migrations, wide audits,
  hand-driven polish. Deeper recipe book; no iteration cap.

If this skill hits the cap without acceptance, it deliberately hands back a
documented diff for a human (or a follow-up `themes/theme-refine` run) to
finish. That is *success* — silent looping-forever is the anti-pattern.

## Loop

```
┌───────────────────────────────────────────────────────────┐
│  Round N (start N = 1, cap N ≤ 5)                          │
│                                                            │
│  1. Screenshot SOURCE     ─ crawl(SOURCE_URL, screenshot)  │
│  2. Screenshot CLONE      ─ screenshot_preview             │
│  3. Compare visually       ─ eyeball both images           │
│     ├─ close enough? ───────────────► DONE (report ✓)      │
│     └─ diffs remain?                                       │
│  4. Pick TOP 1-3 issues    ─ prioritize: layout > color >  │
│                              spacing > type > polish       │
│  5. Fix them               ─ edit theme files, apply the   │
│                              relevant themes/theme-refine  │
│                              recipe                        │
│  6. Preview refreshes on save (fluid theme dev is running) │
│  7. Increment N. If N > 5 → STOP + diff report.            │
└───────────────────────────────────────────────────────────┘
```

## Preflight

Before entering the loop, verify:

1. `SOURCE_URL` is in the manager step context (the workflow passes it) OR ask
   the user once. Never guess.
2. The theme preview is running. Look for the `<preview><available>true` flag.
   If not, call `start_preview` and wait for the URL to come up (max 60 s).
3. The theme's homepage renders — do a first `screenshot_preview` and check
   the returned image is not a blank/error screen. A dead preview is a
   fail-fast, not a rework — return early with `PREVIEW_NOT_READY`.

## Phase A — CODE parity gate (runs BEFORE any screenshot round)

**Screenshots are the granular FINAL pass, not the first tool you reach for.** Pixel
comparison is slow and can only see one viewport at a time; structural problems (missing
sections, wrong order, broken routes, hardcoded values) are faster and more reliably
caught in code. Do not start the screenshot loop until a CODE review believes the theme
is at parity:

1. **Structural parity per template.** For each template type (home, product, collection,
   blog, cart, static pages): compare the source page's structure (crawl the source URL —
   the markdown/HTML output shows its section order and content blocks) against the
   theme's template + sections. Every source section is present, in the source's order;
   no placeholder/leftover base-theme sections the source doesn't have.
2. **Token discipline.** Brand colors/fonts wired as theme tokens (settings), not
   hardcoded hex/font-family sprinkled in section CSS.
3. **Lint + render health.** The theme lints clean (`fluid theme dev` output has no
   Liquid errors), and every template ROUTE renders without a 500/blank — check the dev
   server log tail and load each route in the preview.
4. **Verdict.** Grade explicitly: `CODE_PARITY: pass` or a list of structural fixes.
   Fix and re-review (this inner loop is cheap — no screenshots). Only when code parity
   passes do you enter the screenshot rounds below.

A screenshot round that starts before code parity just burns rounds discovering
structural problems one viewport at a time.

## Phase B — Round protocol (screenshot refinement — the granular final pass)

For each round `N` from 1 to 5:

### 1. Capture paired screenshots

Call these in this order (never in parallel — the second depends on the first's
save):

```
source = crawl(SOURCE_URL, formats: ["screenshot"])
        → returns a Firecrawl-hosted PNG URL
clone  = screenshot_preview()
        → returns an inline PNG the model can see + a saved path
```

**Refine EVERY template TYPE, not just the homepage.** A homepage-only refine is how a
clone ships looking generic-branded on its product and collection pages — the exact way
this disappoints. Across the run you MUST capture and compare one instance of each template
the source has:

1. Homepage (`/`) — establishes the design language; do it first.
2. **Product-detail page (PDP)** — a real product URL. This is the highest-value page and
   the one most often skipped. The cloned `product/default` template is what EVERY product
   renders through, so matching it once fixes all products. Treat a PDP that's structurally
   different from the source (wrong hero/gallery layout, missing benefit/ingredient/review
   sections, generic instead of the source's section order) as a **major**.
3. Collection / category listing.
4. Blog index + one post (only if the source has published articles).
5. Cart and each distinct static page (about / FAQ / contact / policies).

Rotate one template per round and **track which types you've covered** — a type you never
screenshotted is a blind spot, not a pass. `STEP_OUTPUT.pages_verified` must list at least
one of each existing type; a run that only verified `/` does NOT satisfy this skill. If 5
rounds can't both cover every type AND fix all majors, prioritize covering every type once,
then hand remaining majors to the cap report.

**Route health before you diff.** Before comparing a template, confirm its URL renders a
real page (not a 500/blank) using a real browser (`crawl`/`screenshot_preview`), and — when
using an HTTP client — a faithful `Accept: text/html,…` header (a bare browser UA still
sends `Accept: */*`, which the product route rejects). A page that only "renders" as an
error screen is a major, not a pass.

Also **dismiss overlays first** — source sites fire promo popups/cookie banners that will
otherwise fill your screenshot and make the comparison meaningless. Close them (or use the
crawl tool's screenshot, which handles most) before capturing.

### 2. Compare

Look at both images side by side. Score each dimension **major / minor / ok**:

| Dimension        | major example                                       | minor example                             |
|------------------|-----------------------------------------------------|-------------------------------------------|
| **Content**      | clone shows copy that isn't on the source — base-theme boilerplate ("Your Logo", "Built different", "NEW DROP"), an invented headline, a wrong CTA label, wrong nav items | punctuation/casing drift, a trailing period |
| **Layout**       | hero is 1-column on source, 2-column on clone       | slight offset in gutter width             |
| **Color**        | clone brand color visibly wrong hue                 | 2-3% saturation drift                     |
| **Typography**   | wrong font family, wrong weight                     | 1-2px size drift on body copy             |
| **Spacing**      | section padding off by > 24px                       | 4-8px drift                               |
| **Imagery**      | missing hero image, wrong crop, placeholder shown   | slight aspect ratio drift                 |
| **Polish**       | missing badge/pill, wrong icon                      | corner radius drift                       |

**Close enough** = zero majors AND ≤ 2 minors per page you screenshotted this run.
Don't set the bar lower — the point is a real match, not "shipped it."

**Content outranks everything else.** Fix content majors first and never trade one
away for a form fix. A page with perfect spacing and the wrong words is a worse
outcome than the reverse: wrong padding reads as unfinished, wrong copy reads as
a different company. If you run out of rounds with a content major open, that is
NOT a pass — report it as such (see §7).

Read the words in both screenshots. The other six dimensions all describe form, so
a clone can score `ok` across the whole table while saying something the source
never said — which is exactly how a generic apparel template shipped as a clone of
an e-bike brand.

### 3. If close enough → DONE

Emit a short PASS report:

```
STATUS: pass
Rounds used: N / 5
Pages verified: [/, /products, ...]
Remaining minors (acceptable): [short bulleted list]
```

Include the STEP_OUTPUT marker (see workflow-orchestrator docs) so the workflow
forwards a clean summary to the launch-readiness step.

### 4. Otherwise pick the TOP 1-3 issues

Priority order (fix higher first — a layout fix often resolves downstream
spacing/color drift):

1. Layout — wrong column count, wrong section order, missing whole sections
2. Color — brand primary/secondary/accent tokens off
3. Typography — font family / weight / global size scale
4. Spacing — section padding, gutter, vertical rhythm
5. Imagery — missing / wrong assets
6. Polish — badges, icons, radii, shadows

Cap at 3 fixes per round: more edits per round starves the compare step. Each
edit should map to a specific `themes/theme-refine` recipe (Section Shell,
theme-token dropdown, richtext block, etc.). Do not freestyle CSS if a recipe
exists — the recipes exist because they survive future refactors.

### 5. Apply fixes

Edit the theme files locally. The `fluid theme dev` watcher rebuilds on save,
so the next round's `screenshot_preview` reflects the new state. If a fix
requires an API push (theme config: colors / fonts), push it and wait ≥ 2 s
before the next screenshot so the dev server picks up the config change.

### 6. Increment and continue

Log per-round output as:

```
Round N: fixed [issue1, issue2]. Still remaining: [issue3, issue4].
```

Keep it terse — the workflow QA step reads this.

### 7. Cap reached

If any **content** major is still open, the loop did not succeed. Report
`STATUS: cap-reached-content` and list the offending strings — the workflow treats
that as a failure of this step rather than an honest stopping point.

If `N > 5` without a pass, emit a CAP report:

```
STATUS: cap-reached
Rounds used: 5 / 5
Pages verified: [/, ...]

Remaining majors:
  - <one line each — layout / color / etc.>

Remaining minors:
  - <one line each>

Suggested next step:
  Run themes/theme-refine directly for a deeper hand-driven pass, or
  ship as-is and prioritize the majors first in the launch-readiness
  step.
```

This is **not a failure** for the workflow — the acceptance criterion is
"passes OR documented diff at the cap." A silent forever-loop is the failure.

## Rules

- **Never skip a screenshot.** No "I remember what it looked like last round."
  Every round captures fresh source + clone. The whole differentiator is
  visual grounding, not narrative.
- **Never edit more than 3 issues per round.** Overshooting breaks the
  attribution — you won't know which edit caused which change.
- **Never claim pass without a `screenshot_preview` that turn.** Acceptance
  requires evidence from the current round, not "step 2 already looked good."
- **Preview must stay hot.** If it dies mid-run, restart it and burn a round
  re-checking baseline before continuing.
- **Report every round.** The workflow's QA turn reads this log.

## Deep recipes

For the actual "how do I fix this specific class of issue" details — Section
Shell wrapping, richtext blocks, theme-token dropdowns, canonical image blocks,
scroll-snap over Splide, etc. — read `themes/theme-refine`'s recipe sections
directly. This skill deliberately does not restate them; it's the driver, not
the recipe book.

## STEP_OUTPUT

End the run with a `STEP_OUTPUT:` block the workflow can forward:

```
STEP_OUTPUT:
{
  "status": "pass" | "cap-reached" | "preview-not-ready",
  "rounds_used": <int>,
  "pages_verified": [<url paths>],
  "remaining_majors": [<strings>],
  "remaining_minors": [<strings>]
}
```
