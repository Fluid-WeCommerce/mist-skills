# Pixel-perfect page reconstruction contract

This is the universal visual-copy contract for every Fluid page-clone skill.
Page-type skills supply semantics, resource requirements, canonical template
families, and interactions. This contract supplies evidence, implementation,
preview, comparison, and refinement mechanics.

The unit of work is **one source route mapped to one local Fluid route**. Do not
hide unfinished routes behind a broad “site clone complete” statement.

## Required inputs

Resolve these before editing:

- `source_url`: the exact public route to copy
- `built_path`: the exact local Fluid preview route
- `page_contract`: the page-type skill's semantic/template/interaction contract
- `manifest_key`: the entry under `clone-manifest.json.visual_routes`
- `project_path`: the active Fluid theme checkout
- `viewports`: one or more declared source/local comparison cells
- `data_contract`: resources the page-type skill says must already render
- `comparison_policy`: explicit `copy`, `geometry`, and `media` modes derived
  from the source dossier plus the page-type contract

In an onboarding workflow, read them from caller context, dependency output,
and `clone-manifest.json`. Do not ask a sleeping user to repeat known inputs.
When run standalone and an input is genuinely missing, ask only for that input.

## 1. Inspect before implementing

Call `crawl` for the exact source route at every declared viewport:

```json
{
  "url": "<source_url>",
  "formats": ["markdown", "html", "screenshot"],
  "only_main_content": false,
  "capture_page_evidence": true,
  "screenshot_options": {
    "full_page": true,
    "quality": 90,
    "viewport": { "width": "<declared-width>", "height": "<declared-height>" }
  }
}
```

The default benchmark cells are `1440 × 900` and `390 × 844`, but they are
workflow defaults rather than platform laws. Use the returned final URL and
HTTP status. A redirect to the homepage is not proof that a requested detail
route exists.

If a cookie, country, age, or newsletter overlay obscures content, inspect the
returned HTML, repeat with one concrete click selector, and record the action.
Never delete every dialog or guess a selector.

Open the retained source pixels before reusing them or issuing a verdict. Record
`baseline_admissibility` for each viewport as `usable`, `contaminated`,
`needs_adjudication`, or `invalid`, with observations and the recovery
attempted. Compare the decoded screenshot dimensions with the sidecar's signed
rendered-document dimensions, but use judgment rather than a universal ratio:
sticky stitching can make the bitmap legitimately longer or shorter. Signs
such as repeated fixed overlays, duplicated scroll cells, large blank/blurred
regions, clipped content, or a screenshot whose visible page cannot be
reconciled with its DOM/landmarks make the pixels contaminated acceptance
evidence.

Interpret Mist's signed source result before interpreting comparison metrics:

- `usable` plus `eligibleForVisualPass:true`: the pixels may be reviewed.
- `contaminated`: Mist attributed visible obstruction to a rendered overlay.
  Inspect the reported selector/rectangle, perform one concrete dismissal when
  safe, and recapture.
- `needs_adjudication`: serialized dialog/overlay markup exists, but Mist could
  not prove that a reported repeated pixel region belongs to it. Inspect the
  retained pixels, DOM candidate, and region geometry. Recapture after a
  concrete observed action when possible; otherwise keep this outcome.
- `invalid`: the evidence is missing, corrupt, mixed, or hash-invalid.

A tool envelope with `isError:false` says only that capture and comparison
completed. It cannot make `eligibleForVisualPass:false` acceptable.

Dismiss one observed overlay with a concrete selector and recapture when
possible. If a clean full-page capture is not possible, retain the contaminated
artifact for provenance and use clean bounded landmark/viewport cells for
visual review. Return `needs_adjudication` when current provenance is valid but
no admissible visual baseline exists; return `blocked` for mixed, corrupt,
missing, or hash-invalid evidence. Never classify a consent surface as
`external` and then call the whole page a pass while its repeated pixels still
obscure the source.

Persist the exact source bundle returned by Mist: screenshot local path,
timestamp, SHA-256, byte count, decoded dimensions, requested viewport, final
URL/status, overlay handling, and the matching `page_evidence` path/SHA-256.
That JSON sidecar binds ordered rendered copy, landmarks, and live responsive
media sources to the screenshot pixels and viewport. A hosted URL, prose label,
or screenshot without its matching sidecar is not durable page-clone evidence.

## 2. Build a source truth table

For every visible semantic landmark, store this in route order:

```json
{
  "id": "stable-landmark-id",
  "source_selector": "<selector inspected from rendered HTML>",
  "built_selector": "[data-section-id=\"...\"]",
  "visible_copy": ["Exact heading", "Exact supporting text", "Exact CTA"],
  "links": [{ "label": "Exact label", "href": "/exact-target" }],
  "media": [],
  "desktop_geometry": {},
  "mobile_geometry": {},
  "interaction_states": []
}
```

Also classify every landmark as `stable`, `resource`, `dynamic`, or `external`
and record the evidence for that classification. `visible_copy` is exact source
wording, punctuation, capitalization, price formatting, and CTA text—not a
summary. Normalize only runs of whitespace when comparing. Never “improve”
stable source copy or substitute generic base-theme text.

Record the ordered normalized strings and a SHA-256 of their JSON encoding as
`source_copy_sha256`. Record the local strings and hash after implementation.
Stable-copy hashes should match. Resource/dynamic/external differences must
name the source string, local string, reason, classification evidence, and the
page-type reviewer that accepted or rejected the difference.

Inspect source HTML for all of:

- `img` plus `srcset`/lazy variants
- `picture source`
- `video`, nested `source`, `poster`, autoplay, loop, muted, and playsinline
- desktop/mobile media-query variants
- SVGs and icons
- headings, buttons, links, prices, badges, labels, and empty states
- menus, drawers, accordions, tabs, carousels, filters, and forms

Markdown is copy assistance, not visual or media truth. Rendered HTML and
screenshots decide.

## 3. Preserve priority media

The page-type skill declares priority media. Every declared priority source
image and video belongs in the route manifest with its exact source URL,
landmark, viewport, and expected behavior. Other observed media remains in the
evidence dossier and may be classified as dynamic/external; it is not silently
discarded or automatically promoted to a universal blocker.

Use direct remote DAM ingestion first:

```text
dam_upload({ url: "<exact-public-url>", create_media: true })
```

Do not omit a video merely because it looks large. Do not infer a size ceiling
from a previous run. If DAM reports an actual size rejection, call
`compress_media({ url: "<exact-public-url>", ... })`, then immediately upload
the returned temporary path with `dam_upload({ path: ... })` before it expires.
Record original bytes, compressed bytes, settings, and the DAM URL.

For responsive video, implement explicit desktop/mobile `source media`
selection or an equivalent deterministic pattern. QA must prove the live
`currentSrc`, decoded dimensions, and readiness at both widths. A poster image
is a fallback, not a substitute for a source video.

## 4. Implement with Fluid primitives and real data

- Reuse the canonical base-theme section/component when it can express the
  source accurately.
- Extract a shared component only when two routes really share behavior.
- Keep dynamic Fluid resources dynamic. Do not hard-code product cards,
  collection membership, prices, inventory, signed-in state, or blog records
  just to match one screenshot.
- Preserve source section order and responsive composition.
- Use source copy and DAM assets. Remove every unrelated starter placeholder.
- Keep page templates structural; section presets own blocks.
- Do not hand-roll the canonical PDP data section.
- Push theme files before `create_page`; creating a page first can create
  application-theme templates that a later push treats as orphans.

Fix root causes in this order:

1. wrong source/data mapping
2. missing or reordered landmarks
3. wrong asset/font
4. wrong container/grid geometry
5. component details
6. micro-spacing

Arbitrary offsets that only line up one screenshot are a regression, not a fix.
Never move a whole section, page body, or footer to a hardcoded viewport-specific
`top`/`left` coordinate; fix it in place; clamp the page to an arbitrary height;
hide, crop, or overflow-clip source content; or otherwise change layout solely
to satisfy a screenshot or height metric. Mobile footer groups may collapse
only as real accessible disclosures whose closed and opened states are both
exercised. The rendered-evidence sidecar's signed `document.height` is the
source geometry truth; a stitched full-page screenshot may be shorter or taller
because sticky elements are captured more than once.

## 5. Run the local proof loop

Start one managed preview with `start_preview`; let Mist own the port. Do not
spawn a second theme server with `run_cli`.

Before comparison:

1. `preview_state` — confirm local environment and exact route
2. `read_local_server_logs` — zero unresolved Liquid/runtime errors
3. `read_preview_console` — zero unresolved exceptions or failed priority assets

For every declared viewport:

1. `compare_preview_to_source(source_path:<source_path>, source_evidence_path:<page_evidence_path>, copy_mode:<exact-or-diagnostic>, geometry_mode:<strict-or-diagnostic>, media_mode:<strict-or-diagnostic>, mode:"full", path:<built_path>, width:<declared-width>, height:<declared-height>)`
2. `read_preview_dom(path:<built_path>, mode:"all")`
3. inspect critical crops with `screenshot_preview(mode:"viewport", ...)` when
   needed
4. exercise page-contract controls with `interact_preview`
5. recapture the changed state and rerun the affected signed comparison

`compare_preview_to_source` is the final source/local image capture for the
route. It must return a signed Agent Surface receipt for each viewport with
bound screenshot/sidecar hashes. Use exact copy mode for a stable-copy cell.
Use diagnostic mode when the dossier proves resource/dynamic/external copy; the
receipt must still itemize mismatches and cannot itself declare semantic
acceptance. A screenshot path, worker-authored metric, or prose comparison is
not an equivalent substitute. Mixed captures, wrong route/viewport evidence,
HTTP failures, capture truncation, and unresolved priority media remain hard
failures. Pixel and height deltas are evidence for specialist review, not
universal verdicts.

Select policy from evidence rather than whichever mode is easiest to pass:

- `geometry_mode:"diagnostic"` is the normal page-specialist policy because
  full-page height and pixel severity require landmark-aware visual judgment.
  Use `strict` only when the page contract explicitly declares the entire
  document-height threshold to be a hard requirement.
- `media_mode:"strict"` applies only when every compared source image/video
  layer is stable and required. Use `media_mode:"diagnostic"` when the dossier
  proves resource, dynamic, external, consent, review, experiment, or
  personalized media. Priority media declared by the page contract is still a
  hard requirement regardless of this parity policy.
- `copy_mode:"exact"` remains machine-enforced for stable cells. Diagnostic
  copy requires an itemized, evidence-backed classification for every mismatch.

A successful diagnostic call proves that the evidence is current, bound, and
available for review. It does not prove that the page is visually acceptable.
The page specialist must open the attached source/local pixels, inspect DOM and
landmarks, and either fix or explicitly adjudicate every material diagnostic.
The reviewer must also re-check `baseline_admissibility`; a signed comparison
against contaminated or `needs_adjudication` source pixels cannot produce
`pass`, even when the tool returned `isError:false` and local runtime, geometry,
and interactions are healthy.
Likewise, a failed/refused `interact_preview` call is a hard failure for a
required control. Rerun it successfully from an inspected rendered selector;
never drop the failed call from the verdict or infer success from markup alone.

If the running Mist build does not return the comparison fields required by
the page contract, report `needs_adjudication: tooling upgrade required`. Do
not reinterpret absent machine evidence as a pass.

Treat its pixel metrics as diagnostics, not a universal pass threshold.
Antialiasing, dynamic video frames, and source personalization can move raw
pixel scores. Inspect the attached source and local images, reconcile rendered
DOM/copy and landmarks, and itemize the cause of every material delta. A signed
receipt proves what was compared; it does not excuse a visually poor result.

Exact viewport tools make manually collapsing Mist sidebars unnecessary.
Interactive work may visibly drive the user’s pane; background workflow work
uses the isolated project-scoped preview and must not hijack it.

Compare source and local landmarks by identity, never equal scroll offset.
Check:

- presence and order
- exact normalized visible copy
- primary media and breakpoint source
- color and typography
- width, height, padding, gap, crop, and focal point
- controls, radii, dividers, shadows, and icon scale
- desktop-to-mobile composition
- expected interactions

After each meaningful fix, recapture only the affected route/viewports. The
final proof must be newer than the final code change.

## 6. Evidence outcome

Hard requirements:

- every declared source/local evidence cell is current and durable
- every source cell used for visual acceptance has
  `baseline_admissibility:"usable"` and
  `eligibleForVisualPass:true`; contaminated or `needs_adjudication` cells
  require a clean recapture, clean bounded replacement cells, or a non-pass
  outcome
- every declared viewport has a signed comparison receipt for the exact route
- requested and final routes match and local HTTP status is 200
- every stable landmark exists once, in order, with no unrelated placeholder
- every stable-copy cell is exact; every variable difference is classified
- page-contract priority media is DAM-backed and ready
- page-contract interactions were exercised from rendered selectors
- no horizontal overflow at the page contract's narrow viewport
- console and server logs have no unresolved route/runtime/asset errors
- every required interaction completed successfully; no failed/refused
  page-contract tool call was omitted from the verdict
- `theme_audit.py` passes for touched theme files

The page-type reviewer judges responsive equivalence, resource/dynamic content,
third-party surfaces, geometry, and visual severity. Return:

- `pass` — hard requirements pass and no unreviewed material delta remains
- `needs_adjudication` — evidence is valid but a documented judgment remains
- `blocked` — a hard requirement failed

Do not use a universal minor-count or geometry percentage as a substitute for
page-type judgment. “Looks good,” a successful build/tool call, or prose
without signed evidence is never a pass.

## Performance and resilience

- Reuse current durable source baselines; do not recrawl successful cells.
- Keep at most three remote crawls/uploads in flight.
- Persist each successful artifact immediately.
- On slow Wi-Fi, resume missing cells rather than restarting the route.
- Keep one local preview and one capture active on lower-end computers.
- Use responsive DAM assets and avoid shipping desktop media to mobile when the
  source provides a mobile variant.

## Required output

End with:

```text
PAGE_OUTPUT: {
  page_contract,
  source_url,
  built_path,
  source_status,
  local_status,
  source_copy_sha256,
  local_copy_sha256,
  baseline_admissibility:[],
  comparison_policy:{copy,geometry,media},
  classified_copy_differences:[],
  source_evidence:[],
  local_evidence:[],
  comparison_receipts:[],
  landmarks_total,
  landmarks_matched,
  priority_media:{expected,ready,failed,pending},
  interactions:[],
  blockers:[],
  material_deltas:[],
  accepted_exceptions:[],
  runtime_errors:[],
  tool_failures:[],
  status:"pass"|"needs_adjudication"|"blocked",
  next
}
```

When the page-type skill's repair budget expires with valid evidence, return
`needs_adjudication`. Never turn budget exhaustion into a pass.
