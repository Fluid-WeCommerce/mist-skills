---
name: clone-page-to-liquid
description: >-
  Visually copy any public source URL into one declared Fluid Liquid route
  using durable source pixels/DOM, a fast managed preview loop, responsive
  comparison, and honest evidence. Use as the universal visual implementation
  layer beneath page-type skills; it deliberately does not define Home, Shop,
  PDP, category, collection, blog, or system-page semantics.
---

# Clone Page to Liquid

Build one declared page well. This skill owns visual reconstruction only. The
calling page-type skill owns resource semantics, canonical template choice,
required interactions, and the minimum data needed to render.

Read
[`../page-clone/references/pixel-perfect-page.md`](../page-clone/references/pixel-perfect-page.md)
for the detailed evidence and implementation loop.

## 1. Declare the page job

Resolve before editing:

```text
source_url
built_path
page_contract
project_path
viewports
data_contract
comparison_policy
```

The caller owns `page_contract` and `data_contract`. Do not infer a template
family, source route, Fluid route, resource model, required control, universal
`/shop`, `/products/*`, or fixed site-page set. Default benchmark viewports are
`1440×900` and `390×844` only when the caller did not declare alternatives.

Map one source route to one local Fluid route. Record redirects/localization
as source evidence without forcing the source and Fluid pathnames to match.

## 2. Capture an evidence dossier

For every declared viewport, call `crawl` once with rendered HTML, Markdown,
full-page screenshot, and page evidence. Retain the exact Mist-generated files
and receipts.

Open each retained source image and record `baseline_admissibility`. Repeated
fixed overlays, duplicated/blank stitched cells, clipping, or pixels that
cannot be reconciled with signed DOM/landmarks are contaminated. Recapture
after one concrete overlay action or use clean bounded landmark cells; without
admissible source pixels, return `needs_adjudication` rather than a visual pass.

Read the signed source-admissibility fields literally:

- `status:"usable"` with `eligibleForVisualPass:true` may enter visual review.
- `status:"contaminated"` means Mist attributed obstructing pixels to a
  rendered overlay; inspect the named selector/geometry, dismiss that concrete
  surface when safe, and recapture.
- `status:"needs_adjudication"` means Mist found a plausible serialized
  dialog/overlay signal but could not attribute visible pixels to it. Open the
  retained image, inspect the reported DOM candidate and repeated-region
  geometry, then either dismiss a concrete rendered surface and recapture or
  preserve the result as `needs_adjudication`.

`isError:false` only means the capture/comparison operation completed. It does
not override `eligibleForVisualPass:false`, and it never turns
`needs_adjudication` into a visual pass.

Classify each visible landmark:

- `stable` — shell/editorial wording and media that should match
- `resource` — product, collection, account, or other Fluid-backed data
- `dynamic` — inventory, personalization, rotation, timestamp, experiment
- `external` — third-party widget, review feed, social embed, consent surface

Record evidence for the classification. A model may not label a difficult
section “dynamic” merely to avoid copying it.

The dossier is descriptive. It proves what the source rendered; it does not
decide which sections or interactions are semantically required. It must not
require named page types, two specific viewport sizes, or exhaustive identity
with ephemeral third-party content as platform-wide laws.

## 3. Verify the caller's render contract

Read the page-type skill's `page_contract` and `data_contract`. Confirm its
required Fluid resources exist and the exact local route renders them. If data
is missing, return the missing contract to the caller; do not invent product,
collection, category, blog, account, or cart behavior inside this universal
visual skill.

## 4. Implement the Liquid route

Inspect the current scaffold and canonical Fluid template/section contracts
before writing. Reuse Fluid primitives where they express the source; create a
new section or snippet when they do not.

Preserve:

- stable landmark order, wording, typography, media, and responsive intent
- real Fluid resource bindings rather than screenshot-only fake cards
- canonical returned Fluid paths rather than composed slugs
- accessible interaction semantics
- normal responsive document flow

Do not embed binary media, freeze whole pages into absolute coordinates, hide
source content to improve a metric, or duplicate the shared shell per template.

## 5. Run the fast proof loop

Use one Mist-owned `start_preview`. Never start a second theme server.

For each declared viewport:

1. Inspect `preview_state`, server logs, console, and rendered DOM.
2. Run `compare_preview_to_source` with an explicit geometry and media policy
   derived from the dossier and page contract.
3. Use `copy_mode:"exact"` when all compared copy is stable.
4. Use `copy_mode:"diagnostic"` when the dossier proves resource/dynamic copy;
   itemize every difference instead of calling the page exact.
5. Use `geometry_mode:"diagnostic"` for normal page-specialist review. Use
   `geometry_mode:"strict"` only when the page contract explicitly makes the
   whole-document height threshold a hard requirement.
6. Use `media_mode:"strict"` only when every compared source image/video layer
   is stable and required. Use `media_mode:"diagnostic"` when the dossier proves
   resource, dynamic, external, consent, review, or personalized layers; the
   page contract's priority media remains independently hard-required.
7. Exercise relevant controls with `interact_preview`.
8. Fix the highest-impact root cause and recapture only this route/viewport.

Reuse valid source evidence. Do not recrawl unchanged source cells or restart a
full site workflow for one page correction.

Diagnostic comparison success means Mist captured and signed evidence. It is
never by itself a visual pass. The page specialist must first require
`source.admissibility.status:"usable"` and
`source.admissibility.eligibleForVisualPass:true`, then open the attached
pixels, reconcile landmarks/DOM/media, and adjudicate every reported material
delta. A completed comparison with source status `needs_adjudication` remains
ineligible for pass.
A failed or refused page-contract interaction is a hard failure until the
reviewer reruns it successfully from an inspected rendered selector. Do not
omit the failure from the final verdict or substitute a prose claim.

## 6. Separate facts from judgment

Hard failures:

- wrong company/project/route
- stale, mixed, missing, or hash-invalid evidence
- unsafe or unbounded writes
- market/currency mismatch for preview resources
- broken Liquid, non-200 route, truncated capture/copy/media evidence,
  horizontal overflow, console/server exception, failed priority media
- missing/reordered stable landmark or unrelated starter content
- inaccessible or fake controls; failed/refused page-contract tool interactions

Specialist judgment:

- responsive reflow equivalence
- resource/dynamic copy differences
- A/B, geo, consent, review, or social-widget variability
- closest honest Fluid behavior when the source has no platform equivalent
- visual severity and whether a documented exception is acceptable

The builder reports findings. An independent reviewer inspects current pixels,
DOM, interactions, and logs. If evidence is valid but a material judgment
remains, return `needs_adjudication`; never force a false pass or fail solely
because a universal numeric threshold was not met.

## Output

End with:

```text
PAGE_OUTPUT: {
  source_url,
  built_path,
  page_contract,
  viewports:[],
  template_paths:[],
  data_contract:{required:[],resolved:[],missing:[]},
  evidence_dossier:{source:[],local:[],comparison_receipts:[]},
  baseline_admissibility:[],
  comparison_policy:{geometry,media,copy},
  stable_landmarks:{expected,matched,missing:[],reordered:[]},
  variable_landmarks:{resource:[],dynamic:[],external:[]},
  interactions:[],
  blockers:[],
  material_deltas:[],
  accepted_exceptions:[],
  runtime_errors:[],
  tool_failures:[],
  timing:{first_render_seconds,total_seconds,rework_rounds},
  status:"pass"|"needs_adjudication"|"blocked",
  next
}
```

`pass` means zero hard failures and no unreviewed material delta. It does not
mean mathematical pixel identity.
