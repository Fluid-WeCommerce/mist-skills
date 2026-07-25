---
name: Iterative Theme Refine
description: >-
  Evidence-driven refinement after theme-clone. Repeatedly captures semantic
  source-vs-preview pairs for home, shop, and PDP at desktop and mobile, fixes
  the highest-impact root causes, and exits with either a strict visual pass or
  an itemized needs-review report after five rounds.
icon: refresh-cw
---

# Iterative Theme Refine

Refine a freshly cloned Fluid theme against its live source. This skill is the bounded
driver; `themes/theme-refine` is the recipe book for canonical fixes.

The active Fluid company is already selected in Mist Desktop. Fluid API auth and CLI
profile context are injected. Never ask for credentials.

## Outcome semantics

- `pass`: home, shop/collection, and representative PDP meet the visual pass bar at
  desktop and mobile; required structural/runtime gates pass.
- `cap-reached`: the five-round budget ended with itemized evidence. This is a valid,
  honest output, but it is **needs review**, not a clean flagship-workflow pass.
- `preview-not-ready`: the local preview could not render after one restart/recovery
  attempt.

The onboarding workflow may use `cap-reached` as diagnostic output, but its strict final
gate must not present it as near-pixel-perfect success.

## Preflight

1. Read `website_url`, theme project, and any selected source route context. Never guess a
   company or source domain.
2. Read `clone-manifest.json`. It must have `visual_routes` entries for:
   - `home`
   - `shop`
   - `pdp`
3. Each visual route must name a source URL, built path, and one landmark mapping for every
   visible priority section.
4. Start or reuse the theme preview. Record its port and confirm each built priority route
   returns a real page.
5. Read
   `themes/theme-clone/references/dev-preview-visual-diff.md` and use its
   managed-browser semantic landmark protocol. Source evidence is valid only
   when its requested/final route, status, viewport, and overlay handling are
   recorded.
6. Validate all six `source_evidence` objects before spending a visual round.
   Each must reference a real `.mist-desktop/source-baselines/` file and carry
   `captured_at`, `sha256`, positive `bytes`, decoded `width`/`height`,
   `requested_viewport`, `final_url`, `status`, and `overlay_handling`. Run
   `git hash-object --no-filters -- <relative-path>` through `run_cli` and
   compare the raw-byte digest. A hosted URL, `crawl:1440x900`, chat attachment
   ID, missing file, or digest mismatch is not a baseline. Recapture only
   invalid cells with managed `crawl`, persist its returned evidence object,
   and re-read the manifest before continuing.

## Phase A — code and data parity gate

Run this before the first visual round.

### 1. Priority-template structure

Compare the manifest with:

- `home_page/default/index.liquid`
- the shop/collection template actually serving the source-equivalent route
- `product/default/index.liquid`

Every source landmark must have a built section instance in the same order. The PDP begins
with the scaffold's canonical product-data section (`product_hero` in current starters,
`main_product` in older starters). Do not hand-roll product/variant/cart wiring.

### 2. Source content and product data

- Real source copy is present; no base-theme placeholder survives.
- Every content image points to the Fluid DAM, not the source CDN.
- The representative PDP renders a real imported product with the expected title, price,
  currency, image gallery, option axes, variants, and add-to-cart id.
- The shop/collection renders real imported products rather than decorative cards.

### 3. Brand discipline

Read the injected `<brand_voice>` (`brand.md`) and `clone-manifest.json` tokens. Confirm:

- section CSS has no raw brand hex/font-family literals;
- all global color/font slots are populated in `settings_data.json`;
- source font licensing/substitution is recorded;
- authored copy follows the brand guide; source strings win.

### 4. Deterministic health

- Run `python3 scripts/theme_audit.py` on every touched Liquid file.
- Load every priority route and inspect the dev log for Liquid/server errors.
- At 390px, assert `document.scrollWidth <= innerWidth`.

Fix Phase A findings and re-run until it reports:

```text
CODE_PARITY: pass
```

Do not spend visual rounds rediscovering missing sections, placeholder copy, broken product
data, or invalid schema.

## Phase B — five visual rounds

Each round captures **all three priority routes**, not one page type. That makes the five
rounds actual refinement rounds rather than a page-coverage lottery.

For `N = 1..5`:

1. Reuse the validated source files from the manifest and run the matched
   `screenshot_preview` local capture matrix for home, shop, and PDP. Recrawl a
   source cell only when its URL/content changed or its durable evidence failed
   preflight; persist the replacement evidence object immediately.
2. For each route, compare full-page pairs and every named landmark pair at desktop and
   mobile.
3. Read the metrics JSON for geometry, typography, colors, document overflow, route status,
   and headings.
4. Score every finding:

| Dimension    | Major                                            | Minor                        |
| ------------ | ------------------------------------------------ | ---------------------------- |
| Structure    | missing/reordered section, wrong grid/hero model | small container-width drift  |
| Content/data | wrong copy/product/price/variant, placeholder    | harmless formatting delta    |
| Imagery      | missing/wrong asset or crop                      | slight focal/aspect drift    |
| Typography   | wrong family/weight/hierarchy                    | small size/line-height drift |
| Color        | wrong theme role or visibly wrong palette        | small derived-tone drift     |
| Spacing      | page rhythm or landmark height materially wrong  | local 4–8px drift            |
| Interaction  | nav, selector, cart, or CTA broken               | non-blocking polish          |

5. Select the top three **root causes**, not merely three CSS declarations. A bad
   `container_max_width` token that affects eight sections is one root cause; fix all its
   direct manifestations together.
6. Apply the smallest canonical fix using `themes/theme-refine`.
7. Run `theme_audit.py` on every file changed in the round.
8. Confirm the local preview is healthy.
9. Capture all three routes again in the next round. Never reuse an earlier image after a
   code change.

Log:

```text
Round N
Fixed root causes: [...]
Home: major X / minor Y
Shop: major X / minor Y
PDP: major X / minor Y
Evidence: diff/<route>/<files>, diff/<route>/<route>-metrics.json
```

## Pass bar

A route passes when:

- zero major findings remain;
- no visible source landmark is missing or reordered;
- copy, product data, and primary imagery match;
- geometry is within 5% for priority landmarks unless responsive reflow explains it;
- at most two itemized minor findings remain;
- desktop and mobile were captured after the final code change;
- route status is 200, mobile has no document overflow, and the dev log is clean.

The skill passes only when **home, shop, and PDP all pass in the same final round**.

Then run one structural/route-health smoke pass over other source page types (blog/post,
cart, static pages when present). These do not consume a visual round unless a priority
route shares the same broken section.

## Autonomous source-fidelity decisions

When this skill runs in an explicitly unattended workflow, do not stop for routine visual
choices. Use the source site as the authority for structure, copy, image selection, crop,
spacing, and ordering while preserving Fluid's editor architecture and product/cart/locale
hooks.

Record an item for a human only when:

- the source relies on a third-party experience Fluid cannot reproduce;
- a proprietary asset/font license is unclear;
- matching would require breaking canonical Fluid behavior;
- the source itself is inconsistent or A/B testing materially different variants.

## Recovery

- Preview died: restart once on the recorded port, reload all priority routes, continue
  without counting a round until a screenshot has been produced.
- Source overlay: dismiss via a visible control and record it; only hide by selector when
  no control works.
- Source landmark changed: inspect the current rendered DOM, update only that manifest
  selector, then capture again.
- A fix regressed another route: revert or correct that root cause in the same round; the
  all-route capture prevents a local improvement from being called a global pass.

## STEP_OUTPUT

End with:

```text
STEP_OUTPUT:
{
  "status": "pass" | "cap-reached" | "preview-not-ready",
  "code_parity": "pass" | "failed",
  "rounds_used": <int>,
  "priority_routes": {
    "home": {"desktop":"pass|fail","mobile":"pass|fail","majors":[],"minors":[]},
    "shop": {"desktop":"pass|fail","mobile":"pass|fail","majors":[],"minors":[]},
    "pdp": {"desktop":"pass|fail","mobile":"pass|fail","majors":[],"minors":[]}
  },
  "pages_smoke_tested": [<paths>],
  "evidence_paths": [<screenshot and metrics paths>],
  "audit": {"passed": true, "files": [<paths>]},
  "remaining_majors": [<strings>],
  "remaining_minors": [<strings>],
  "remaining_for_human": [<strings>]
}
```
